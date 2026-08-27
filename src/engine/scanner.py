"""Scanner Engine orchestrating token discovery, safety analysis, scoring, and alerts."""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from loguru import logger
from sqlalchemy import select

from src.analyzers.risk_engine import RiskEngine
from src.collectors.dexscreener import DexScreenerClient
from src.config.settings import get_settings
from src.database.models import MarketData, Signal, Token, Tracking
from src.database.sqlite import get_db_session, init_db
from src.engine.scorer import MomentumScorer, ScoreBreakdown
from src.services.telegram import TelegramService


class ScannerEngine:
    """Core intelligence engine coordinating ingestion, risk assessment, scoring, and alerts."""

    def __init__(
        self,
        dexscreener: Optional[DexScreenerClient] = None,
        risk_engine: Optional[RiskEngine] = None,
        scorer: Optional[MomentumScorer] = None,
        telegram: Optional[TelegramService] = None,
    ):
        self.settings = get_settings()
        self.dexscreener = dexscreener or DexScreenerClient()
        self.risk_engine = risk_engine or RiskEngine()
        self.scorer = scorer or MomentumScorer()
        self.telegram = telegram or TelegramService()
        self._running = False
        self.semaphore = asyncio.Semaphore(self.settings.CONCURRENCY_LIMIT)

    async def initialize(self) -> None:
        """Initializes database schema and verifies connectivity."""
        await init_db()
        logger.info("Scanner Engine initialized successfully.")

    async def close(self) -> None:
        """Closes all underlying HTTP clients."""
        await self.dexscreener.close()
        await self.risk_engine.close()
        await self.telegram.close()

    async def get_processed_address_set(self) -> set[str]:
        """Retrieves set of already indexed token addresses from database."""
        async with get_db_session() as session:
            result = await session.execute(select(Token.address))
            return set(result.scalars().all())

    async def inspect_single_token(
        self,
        token_profile: Dict[str, Any],
        processed_addresses: set[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Inspects one token through the entire safety and momentum evaluation pipeline.
        Protected by concurrency semaphore.
        """
        token_address = token_profile.get("tokenAddress")
        chain = token_profile.get("chainId", "").lower()

        if not token_address or token_address in processed_addresses:
            return None

        # 1. Chain filter
        if chain not in self.settings.supported_chains_set:
            return None

        async with self.semaphore:
            # 2. Pair data lookup
            pair_data = await self.dexscreener.get_best_pair(token_address)
            if not pair_data:
                return None

            # 3. Basic thresholds filter (Volume, MCAP, Age)
            volume_h1 = float(pair_data.get("volume", {}).get("h1", 0.0) or 0.0)
            market_cap = float(pair_data.get("marketCap", 0.0) or 0.0)

            if volume_h1 < self.settings.MIN_VOLUME_USD:
                return None
            if market_cap < self.settings.MIN_MARKET_CAP_USD:
                return None

            # 4. Security & Risk Analysis
            risk_assessment = await self.risk_engine.evaluate_token(chain, token_address, pair_data)
            if not risk_assessment.is_safe:
                logger.warning(
                    f"[SECURITY REJECT] {token_address[:10]}... on {chain.upper()} - "
                    f"Risk Score: {risk_assessment.risk_score} | Reasons: {', '.join(risk_assessment.risk_factors)}"
                )
                return None

            # 5. Momentum Scoring
            score_breakdown: ScoreBreakdown = self.scorer.calculate_score(
                token_profile=token_profile,
                pair_data=pair_data,
                risk_score=risk_assessment.risk_score
            )

            # Age filter check
            if score_breakdown.age_minutes > self.settings.MAX_AGE_MINUTES:
                return None

            # Must qualify for at least WATCHLIST tier
            if not score_breakdown.signal_tier:
                return None

            return {
                "token_profile": token_profile,
                "pair_data": pair_data,
                "risk_assessment": risk_assessment,
                "score_breakdown": score_breakdown,
                "token_address": token_address,
                "chain": chain,
            }

    async def scan_cycle(self) -> int:
        """
        Performs one full scanning cycle:
        1. Fetch newest profiles from DexScreener
        2. Filter & analyze concurrently
        3. Persist valid candidates to SQLite
        4. Broadcast alert to Telegram
        """
        start_time = time.time()
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] SCANNING DEX PROFILES...")

        token_profiles = await self.dexscreener.get_latest_token_profiles()
        if not token_profiles:
            logger.info("[SCANNER] No new token profiles returned.")
            return 0

        processed_addresses = await self.get_processed_address_set()

        # Execute concurrent inspection
        tasks = [
            self.inspect_single_token(profile, processed_addresses)
            for profile in token_profiles
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        candidate_count = 0

        for res in results:
            if not res or isinstance(res, Exception):
                if isinstance(res, Exception):
                    logger.debug(f"Error inspecting token: {res}")
                continue

            item: Dict[str, Any] = res
            token_address = item["token_address"]
            chain = item["chain"]
            pair = item["pair_data"]
            score = item["score_breakdown"]
            risk = item["risk_assessment"]

            pair_address = pair.get("pairAddress", "-")
            dex_url = pair.get("url", f"https://dexscreener.com/{chain}/{token_address}")
            base_token = pair.get("baseToken", {})
            symbol = base_token.get("symbol")
            name = base_token.get("name")

            # Persist to database
            async with get_db_session() as session:
                # Add Token
                token = Token(
                    address=token_address,
                    chain=chain,
                    symbol=symbol,
                    name=name,
                    pair_address=pair_address,
                    url=dex_url,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(token)
                await session.flush()

                # Add MarketData snapshot
                mdata = MarketData(
                    token_id=token.id,
                    price_usd=float(pair.get("priceUsd", 0.0) or 0.0),
                    liquidity_usd=score.liquidity_usd,
                    volume_h1=score.volume_h1,
                    market_cap=score.market_cap,
                    buys_h1=score.buys_h1,
                    sells_h1=score.sells_h1,
                    vpm=score.volume_per_minute,
                    buy_sell_ratio=score.buy_sell_ratio,
                    timestamp=datetime.now(timezone.utc),
                )
                session.add(mdata)

                # Add Signal record
                signal = Signal(
                    token_id=token.id,
                    momentum_score=score.momentum_score,
                    risk_score=score.risk_score,
                    final_score=score.final_score,
                    signal_tier=score.signal_tier,
                    age_minutes=score.age_minutes,
                    alert_sent=self.settings.has_telegram,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(signal)

                # Add Tracking record
                tracking = Tracking(
                    token_id=token.id,
                    entry_market_cap=score.market_cap,
                    current_market_cap=score.market_cap,
                    highest_market_cap=score.market_cap,
                    roi_percent=0.0,
                    checked=False,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(tracking)

            # Send Telegram Alert
            message = self.telegram.format_signal_message(
                token_address=token_address,
                chain=chain,
                pair_address=pair_address,
                dex_url=dex_url,
                score=score,
                risk=risk,
                symbol=symbol,
                name=name,
            )
            await self.telegram.send_message(message)

            candidate_count += 1
            logger.info(
                f"[QUALIFIED] {score.signal_tier} | {chain.upper()} | {symbol or token_address[:10]} | "
                f"Score: {score.final_score}/100 (Risk: {risk.risk_score}) | MCAP: ${int(score.market_cap):,}"
            )

        elapsed = time.time() - start_time
        logger.info(f"[CYCLE COMPLETE] Found {candidate_count} candidates in {elapsed:.2f}s.")
        return candidate_count

    async def run_scanner_loop(self) -> None:
        """Continuous execution loop."""
        self._running = True
        logger.info(
            f"Starting CRYPTO_ALPHA_SNIPER continuous scanner loop "
            f"(Interval: {self.settings.SCAN_INTERVAL_SECONDS}s, Chains: {self.settings.SUPPORTED_CHAINS})."
        )

        while self._running:
            try:
                await self.scan_cycle()
            except asyncio.CancelledError:
                logger.info("Scanner cycle cancelled.")
                break
            except Exception as e:
                logger.error(f"Unhandled exception in scan cycle: {e}")

            try:
                await asyncio.sleep(self.settings.SCAN_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break

    def stop(self) -> None:
        """Signals the scanner loop to terminate."""
        self._running = False

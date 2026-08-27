"""Asynchronous Telegram Alert Dispatcher Service."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

import httpx
from loguru import logger

from src.config.settings import get_settings

if TYPE_CHECKING:
    from src.analyzers.risk_engine import RiskAssessment
    from src.engine.scorer import ScoreBreakdown


class TelegramService:
    """Dispatches formatted crypto momentum and alpha signals to Telegram."""

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.settings = get_settings()
        self._external_client = client is not None
        self.client = client or httpx.AsyncClient(timeout=10.0)

    async def close(self) -> None:
        """Closes the underlying HTTP client if internally created."""
        if not self._external_client and not self.client.is_closed:
            await self.client.aclose()

    def format_signal_message(
        self,
        token_address: str,
        chain: str,
        pair_address: str,
        dex_url: str,
        score: ScoreBreakdown,
        risk: Optional[RiskAssessment] = None,
        symbol: Optional[str] = None,
        name: Optional[str] = None
    ) -> str:
        """Constructs an aesthetic, readable message for Telegram subscribers."""
        tier_icons = {
            "ALPHA_SIGNAL": "🔥 ALPHA SIGNAL",
            "EARLY_SIGNAL": "🚀 EARLY SIGNAL",
            "WATCHLIST": "👀 WATCHLIST",
        }
        header = tier_icons.get(score.signal_tier, "⚡ NEW SIGNAL")
        token_label = f" ({symbol})" if symbol else ""

        # Safety badges
        safety_text = "🛡️ Safety: "
        if risk:
            if risk.risk_score <= 25:
                safety_text += f"🟢 Low Risk ({risk.risk_score}/100)"
            elif risk.risk_score <= 50:
                safety_text += f"🟡 Medium Risk ({risk.risk_score}/100)"
            else:
                safety_text += f"🔴 Elevated Risk ({risk.risk_score}/100)"
        else:
            safety_text += "⚪ Standard Heuristics"

        lines = [
            f"<b>{header}</b>{token_label}",
            "",
            f"⛓️ <b>Chain:</b> {chain.upper()}",
            f"⭐ <b>Alpha Score:</b> {score.final_score}/100 <i>(Momentum: {score.momentum_score})</i>",
            safety_text,
            "",
            f"⏳ <b>Age:</b> {score.age_minutes} mins",
            f"📊 <b>Volume (1h):</b> ${int(score.volume_h1):,}",
            f"⚡ <b>VPM:</b> ${score.volume_per_minute:,.1f}/min",
            f"📈 <b>Buy/Sell Ratio:</b> {score.buy_sell_ratio:.2f}",
            f"💧 <b>Liquidity (LP):</b> ${int(score.liquidity_usd):,}",
            f"💰 <b>Market Cap:</b> ${int(score.market_cap):,}",
            f"🟢 <b>Buys:</b> {score.buys_h1}  |  🔴 <b>Sells:</b> {score.sells_h1}",
            "",
            f"🏦 <b>Pair:</b> <code>{pair_address}</code>",
            f"📍 <b>CA:</b> <code>{token_address}</code>",
            "",
            f"🔗 <a href=\"{dex_url}\">View on DexScreener</a>",
        ]

        if risk and risk.risk_factors:
            lines.append("")
            lines.append("⚠️ <b>Risk Factors:</b>")
            for factor in risk.risk_factors[:3]:
                lines.append(f"• {factor}")

        return "\n".join(lines)

    async def send_message(self, text_message: str, max_retries: int = 3) -> bool:
        """Sends an HTML formatted message to the configured Telegram Chat ID."""
        if not self.settings.has_telegram:
            logger.debug("Telegram credentials not configured. Skipping alert dispatch.")
            return False

        url = f"https://api.telegram.org/bot{self.settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": self.settings.TELEGRAM_CHAT_ID,
            "text": text_message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        backoff = 1.0
        for attempt in range(1, max_retries + 1):
            try:
                response = await self.client.post(url, json=payload)
                if response.status_code == 200:
                    return True
                elif response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", backoff))
                    logger.warning(f"Telegram Rate Limit (429). Retrying after {retry_after}s...")
                    await asyncio.sleep(retry_after)
                else:
                    logger.error(f"Telegram API error (Status {response.status_code}): {response.text}")
                    break
            except Exception as e:
                logger.error(f"Telegram connection error (attempt {attempt}/{max_retries}): {e}")
                await asyncio.sleep(backoff)
                backoff *= 2.0

        return False

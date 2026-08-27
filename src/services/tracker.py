"""Background Performance and PNL Tracker Service."""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from sqlalchemy import select

from src.collectors.dexscreener import DexScreenerClient
from src.config.settings import get_settings
from src.database.models import Token, Tracking
from src.database.sqlite import get_db_session


class PerformanceTracker:
    """Monitors historical candidate tokens and updates their ROI / PNL in the database."""

    def __init__(self, dexscreener_client: Optional[DexScreenerClient] = None):
        self.settings = get_settings()
        self.dexscreener = dexscreener_client or DexScreenerClient()
        self._running = False

    async def update_pending_candidates(self) -> int:
        """
        Polls unchecked or active tracking records and computes latest Market Cap & ROI %.
        """
        updated_count = 0

        async with get_db_session() as session:
            # Query tokens with pending tracking
            stmt = (
                select(Tracking, Token.address)
                .join(Token, Tracking.token_id == Token.id)
                .where(Tracking.checked.is_(False))
                .limit(self.settings.TRACKER_MAX_BATCH_SIZE)
            )
            results = (await session.execute(stmt)).all()

            if not results:
                return 0

            logger.info(f"[TRACKER] Updating {len(results)} candidate tokens...")

            for tracking_record, token_address in results:
                try:
                    best_pair = await self.dexscreener.get_best_pair(token_address)
                    if not best_pair:
                        continue

                    current_mcap = float(best_pair.get("marketCap", 0.0) or 0.0)
                    entry_mcap = tracking_record.entry_market_cap

                    if entry_mcap > 0 and current_mcap > 0:
                        roi = ((current_mcap - entry_mcap) / entry_mcap) * 100.0
                        tracking_record.current_market_cap = current_mcap
                        tracking_record.roi_percent = round(roi, 2)

                        # Update peak marketcap
                        if tracking_record.highest_market_cap is None or current_mcap > tracking_record.highest_market_cap:
                            tracking_record.highest_market_cap = current_mcap

                        tracking_record.checked = True
                        tracking_record.last_checked_at = datetime.now(timezone.utc)
                        updated_count += 1
                        logger.debug(f"[TRACKER] {token_address[:10]}... ROI: {roi:+.1f}% (MCap: ${current_mcap:,.0f})")

                except Exception as e:
                    logger.debug(f"[TRACKER] Failed to update token {token_address}: {e}")

        return updated_count

    async def run_tracker_loop(self) -> None:
        """Runs the periodic tracker worker loop in the background."""
        self._running = True
        logger.info("Background Performance Tracker started.")

        while self._running:
            try:
                updated = await self.update_pending_candidates()
                if updated > 0:
                    logger.info(f"[TRACKER] Completed cycle. Updated {updated} tokens.")
            except asyncio.CancelledError:
                logger.info("Tracker worker task cancelled.")
                break
            except Exception as e:
                logger.error(f"[TRACKER] Error in tracker loop: {e}")

            try:
                await asyncio.sleep(self.settings.TRACKER_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break

    def stop(self) -> None:
        """Stops the tracker loop."""
        self._running = False

"""Data migration script to import legacy JSON files into SQLite database."""

import asyncio
import json
import os
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select

from src.database.models import MarketData, Signal, Token, Tracking
from src.database.sqlite import get_db_session, init_db


def parse_iso_datetime(dt_str: str | None) -> datetime:
    """Safely parse ISO datetime string or fallback to UTC now."""
    if not dt_str:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc)


async def migrate_legacy_data(
    processed_file: str = "data/processed_tokens.json",
    candidates_file: str = "data/candidates.json",
    batch_size: int = 500
) -> None:
    """Migrates processed_tokens.json and candidates.json into SQLite."""
    logger.info("Starting legacy data migration to SQLite...")
    await init_db()

    # 1. Migrate processed tokens
    if os.path.exists(processed_file):
        try:
            with open(processed_file, "r", encoding="utf-8") as f:
                processed_addrs = json.load(f)
            logger.info(f"Loaded {len(processed_addrs)} addresses from {processed_file}")

            async with get_db_session() as session:
                existing_res = await session.execute(select(Token.address))
                existing_set = set(existing_res.scalars().all())

                new_tokens = []
                for addr in processed_addrs:
                    if isinstance(addr, str) and addr not in existing_set:
                        # Guess chain based on format
                        chain = "bsc" if addr.startswith("0x") else "solana"
                        new_tokens.append(
                            Token(
                                address=addr,
                                chain=chain,
                                created_at=datetime.now(timezone.utc),
                            )
                        )
                        existing_set.add(addr)

                if new_tokens:
                    for i in range(0, len(new_tokens), batch_size):
                        batch = new_tokens[i : i + batch_size]
                        session.add_all(batch)
                        await session.flush()
                    logger.info(f"Migrated {len(new_tokens)} base tokens from {processed_file}.")
        except Exception as e:
            logger.error(f"Error migrating {processed_file}: {e}")

    # 2. Migrate candidates
    if os.path.exists(candidates_file):
        try:
            with open(candidates_file, "r", encoding="utf-8") as f:
                candidates = json.load(f)
            logger.info(f"Loaded {len(candidates)} candidate records from {candidates_file}")

            async with get_db_session() as session:
                # Load all token address to id map
                res = await session.execute(select(Token.address, Token.id))
                addr_to_id = dict(res.all())

                # Query existing tracking token_ids to prevent unique constraint violation
                track_res = await session.execute(select(Tracking.token_id))
                existing_tracking_ids = set(track_res.scalars().all())

                migrated_signals = 0
                for item in candidates:
                    addr = item.get("token_address")
                    if not addr:
                        continue

                    token_id = addr_to_id.get(addr)
                    if not token_id:
                        token = Token(
                            address=addr,
                            chain=item.get("chain", "solana"),
                            created_at=parse_iso_datetime(item.get("found_at")),
                        )
                        session.add(token)
                        await session.flush()
                        token_id = token.id
                        addr_to_id[addr] = token_id

                    # Determine signal tier
                    score = item.get("score", 0)
                    if score >= 70:
                        tier = "ALPHA_SIGNAL"
                    elif score >= 55:
                        tier = "EARLY_SIGNAL"
                    else:
                        tier = "WATCHLIST"

                    found_dt = parse_iso_datetime(item.get("found_at"))

                    # Create MarketData
                    mdata = MarketData(
                        token_id=token_id,
                        volume_h1=float(item.get("volume", 0.0) or 0.0),
                        vpm=float(item.get("vpm", 0.0) or 0.0),
                        market_cap=float(item.get("mcap", 0.0) or 0.0),
                        timestamp=found_dt,
                    )
                    session.add(mdata)

                    # Create Signal
                    signal = Signal(
                        token_id=token_id,
                        momentum_score=int(score),
                        risk_score=0,
                        final_score=int(score),
                        signal_tier=tier,
                        age_minutes=int(item.get("age", 0) or 0),
                        alert_sent=True,
                        created_at=found_dt,
                    )
                    session.add(signal)

                    # Create Tracking record only if token not already tracked
                    if token_id not in existing_tracking_ids:
                        tracking = Tracking(
                            token_id=token_id,
                            entry_market_cap=float(item.get("mcap", 0.0) or 0.0),
                            current_market_cap=float(item.get("current_mcap") or 0.0) if item.get("current_mcap") else None,
                            roi_percent=float(item.get("return_percent") or 0.0) if item.get("return_percent") is not None else None,
                            checked=bool(item.get("checked", False)),
                            created_at=found_dt,
                            updated_at=datetime.now(timezone.utc),
                        )
                        session.add(tracking)
                        existing_tracking_ids.add(token_id)
                    migrated_signals += 1

                    if migrated_signals % batch_size == 0:
                        await session.flush()
                        logger.info(f"Imported {migrated_signals}/{len(candidates)} candidate items...")

            logger.info(f"Legacy migration finished successfully. Migrated {migrated_signals} candidate records.")
        except Exception as e:
            logger.error(f"Error migrating {candidates_file}: {e}")


if __name__ == "__main__":
    asyncio.run(migrate_legacy_data())

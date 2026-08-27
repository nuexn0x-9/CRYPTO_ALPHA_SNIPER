"""Database retention manager and automated cleanup utility."""

from datetime import datetime, timedelta, timezone

from loguru import logger
from sqlalchemy import delete, select, text

from src.config.settings import get_settings
from src.database.models import Token
from src.database.sqlite import get_db_session, get_engine


async def purge_expired_records(retention_days: int | None = None) -> int:
    """
    Deletes tokens and cascaded records (market_data, signals, tracking) older than retention_days.
    Returns the number of deleted tokens.
    """
    settings = get_settings()
    days = retention_days if retention_days is not None else settings.DATA_RETENTION_DAYS

    if days <= 0:
        logger.warning(f"[CLEANUP] Retention days is set to {days}. Skipping purge.")
        return 0

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    logger.info(f"[CLEANUP] Purging token records older than {days} days (Cutoff: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S UTC')})...")

    deleted_count = 0
    try:
        async with get_db_session() as session:
            # 1. Identify expired tokens
            expired_stmt = select(Token.id).where(Token.created_at < cutoff_date)
            expired_ids = (await session.execute(expired_stmt)).scalars().all()

            if not expired_ids:
                logger.info("[CLEANUP] No expired records found. Database is clean.")
                return 0

            # 2. Execute delete on Token (cascades to market_data, signals, tracking)
            del_stmt = delete(Token).where(Token.id.in_(expired_ids))
            result = await session.execute(del_stmt)
            deleted_count = result.rowcount

            logger.info(f"[CLEANUP] Successfully purged {deleted_count} expired tokens and their associated history.")

        # 3. Optimize database file
        try:
            engine = get_engine()
            async with engine.begin() as conn:
                await conn.execute(text("PRAGMA optimize;"))
        except Exception as e:
            logger.debug(f"[CLEANUP] PRAGMA optimize skipped: {e}")

    except Exception as e:
        logger.error(f"[CLEANUP] Error during database cleanup: {e}")

    return deleted_count

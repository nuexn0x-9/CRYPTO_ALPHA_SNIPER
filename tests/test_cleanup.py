"""Unit tests for automatic database retention and cleanup."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from src.database.cleanup import purge_expired_records
from src.database.models import Signal, Token, Tracking
from src.database.sqlite import get_db_session


@pytest.mark.asyncio
async def test_purge_expired_records():
    """Verifies that records older than retention period are deleted with cascade."""
    now = datetime.now(timezone.utc)
    old_date = now - timedelta(days=10)   # 10 days old (should be purged if retention=7)
    recent_date = now - timedelta(days=2) # 2 days old (should be retained)

    old_addr = f"OldToken_{uuid.uuid4().hex[:16]}"
    recent_addr = f"RecentToken_{uuid.uuid4().hex[:16]}"

    async with get_db_session() as session:
        # 1. Create an old token
        old_token = Token(
            address=old_addr,
            chain="solana",
            symbol="OLD",
            created_at=old_date,
        )
        session.add(old_token)
        await session.flush()

        old_signal = Signal(
            token_id=old_token.id,
            momentum_score=50,
            risk_score=10,
            final_score=50,
            signal_tier="WATCHLIST",
            created_at=old_date,
        )
        old_tracking = Tracking(
            token_id=old_token.id,
            entry_market_cap=10000.0,
            created_at=old_date,
        )
        session.add_all([old_signal, old_tracking])

        # 2. Create a recent token
        recent_token = Token(
            address=recent_addr,
            chain="solana",
            symbol="RECENT",
            created_at=recent_date,
        )
        session.add(recent_token)
        await session.flush()

        recent_signal = Signal(
            token_id=recent_token.id,
            momentum_score=80,
            risk_score=5,
            final_score=80,
            signal_tier="ALPHA_SIGNAL",
            created_at=recent_date,
        )
        session.add(recent_signal)

    # Execute purge with 7-day retention
    deleted = await purge_expired_records(retention_days=7)
    assert deleted >= 1

    # Verify state in database
    async with get_db_session() as session:
        # Old token should be gone
        old_res = (await session.execute(select(Token).where(Token.address == old_addr))).scalar_one_or_none()
        assert old_res is None

        # Recent token should be preserved
        recent_res = (await session.execute(select(Token).where(Token.address == recent_addr))).scalar_one_or_none()
        assert recent_res is not None
        assert recent_res.symbol == "RECENT"

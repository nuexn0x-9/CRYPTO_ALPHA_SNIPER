"""Unit tests for SQLite database operations and models."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from src.database.models import MarketData, Signal, Token, Tracking


@pytest.mark.asyncio
async def test_database_crud(in_memory_db_session):
    """Tests creating and querying Token, MarketData, Signal, and Tracking entities."""
    session = in_memory_db_session

    # 1. Create Token
    token = Token(
        address="TestAddress123",
        chain="solana",
        symbol="ALPHA",
        name="Alpha Token",
        pair_address="Pair123",
        url="https://dexscreener.com/solana/TestAddress123",
        created_at=datetime.now(timezone.utc),
    )
    session.add(token)
    await session.commit()

    # 2. Query Token
    stmt = select(Token).where(Token.address == "TestAddress123")
    res = (await session.execute(stmt)).scalar_one_or_none()
    assert res is not None
    assert res.symbol == "ALPHA"

    # 3. Add MarketData and Signal
    mdata = MarketData(
        token_id=res.id,
        price_usd=0.005,
        liquidity_usd=25000.0,
        volume_h1=80000.0,
        market_cap=50000.0,
        buys_h1=100,
        sells_h1=30,
        vpm=4000.0,
        buy_sell_ratio=3.33,
    )
    signal = Signal(
        token_id=res.id,
        momentum_score=85,
        risk_score=10,
        final_score=85,
        signal_tier="ALPHA_SIGNAL",
        age_minutes=5,
        alert_sent=True,
    )
    tracking = Tracking(
        token_id=res.id,
        entry_market_cap=50000.0,
        current_market_cap=75000.0,
        roi_percent=50.0,
        checked=True,
    )
    session.add_all([mdata, signal, tracking])
    await session.commit()

    # 4. Verify Tracking ROI
    track_stmt = select(Tracking).where(Tracking.token_id == res.id)
    track_res = (await session.execute(track_stmt)).scalar_one_or_none()
    assert track_res is not None
    assert track_res.roi_percent == 50.0
    assert track_res.checked is True

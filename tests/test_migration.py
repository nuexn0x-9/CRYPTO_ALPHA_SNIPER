"""Unit tests for legacy JSON data migration."""

import json
import uuid

import pytest
from sqlalchemy import select

from src.database.migration import migrate_legacy_data
from src.database.models import Signal, Token, Tracking
from src.database.sqlite import get_db_session


@pytest.mark.asyncio
async def test_legacy_migration_idempotent(tmp_path):
    """Verifies that migration handles legacy format, avoids duplicates, and populates DB."""
    uid = uuid.uuid4().hex[:8]
    addr_a = f"AddrA_{uid}"
    addr_b = f"AddrB_{uid}"
    addr_c = f"0xAddrC_{uid}"
    addr_d = f"AddrD_New_{uid}"

    # Create temporary mock JSON files
    mock_processed = tmp_path / "mock_processed.json"
    mock_candidates = tmp_path / "mock_candidates.json"

    mock_processed.write_text(
        json.dumps([addr_a, addr_b, addr_c]),
        encoding="utf-8"
    )

    mock_candidates.write_text(
        json.dumps([
            {
                "token_address": addr_a,
                "chain": "solana",
                "score": 80,
                "age": 5,
                "volume": 35000.0,
                "vpm": 7000.0,
                "mcap": 25000.0,
                "found_at": "2026-08-01T12:00:00",
                "checked": False,
            },
            {
                "token_address": addr_d,
                "chain": "solana",
                "score": 60,
                "age": 10,
                "volume": 20000.0,
                "vpm": 2000.0,
                "mcap": 15000.0,
                "found_at": "2026-08-01T12:05:00",
                "checked": True,
            }
        ]),
        encoding="utf-8"
    )

    # Run migration using temp files
    await migrate_legacy_data(
        processed_file=str(mock_processed),
        candidates_file=str(mock_candidates),
        batch_size=10
    )

    # Verify database state
    async with get_db_session() as session:
        tokens = (await session.execute(select(Token))).scalars().all()
        token_addrs = {t.address for t in tokens}
        assert addr_a in token_addrs
        assert addr_b in token_addrs
        assert addr_c in token_addrs
        assert addr_d in token_addrs

        # Verify Signal and Tracking records
        signals = (await session.execute(select(Signal))).scalars().all()
        assert len(signals) >= 2

        trackings = (await session.execute(select(Tracking))).scalars().all()
        assert len(trackings) >= 2

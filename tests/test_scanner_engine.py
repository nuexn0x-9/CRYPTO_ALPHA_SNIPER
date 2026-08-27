"""Integration and unit tests for ScannerEngine."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.analyzers.risk_engine import RiskEngine
from src.collectors.dexscreener import DexScreenerClient
from src.engine.scanner import ScannerEngine
from src.services.telegram import TelegramService


@pytest.mark.asyncio
async def test_scanner_engine_initialization(in_memory_db_session):
    """Verifies scanner initializes database schema and closes cleanly."""
    scanner = ScannerEngine()
    await scanner.initialize()
    processed = await scanner.get_processed_address_set()
    assert isinstance(processed, set)
    await scanner.close()


@pytest.mark.asyncio
async def test_scanner_inspect_token_pipeline(in_memory_db_session):
    """Verifies token inspection through the full safety and scoring pipeline."""
    mock_http = MagicMock(spec=httpx.AsyncClient)
    dex_client = DexScreenerClient(client=mock_http)
    risk_engine = RiskEngine(client=mock_http)
    telegram_svc = TelegramService(client=mock_http)

    now_ms = datetime.now(timezone.utc).timestamp() * 1000.0
    recent_created_at = now_ms - (5 * 60 * 1000)  # 5 minutes old

    # Mock DexScreener Pair Data
    dex_client.get_best_pair = AsyncMock(
        return_value={
            "pairAddress": "PairAddress123",
            "url": "https://dexscreener.com/solana/Addr123",
            "pairCreatedAt": recent_created_at,
            "volume": {"h1": 60000.0},
            "liquidity": {"usd": 20000.0},
            "marketCap": 40000.0,
            "txns": {"h1": {"buys": 80, "sells": 20}},
        }
    )

    scanner = ScannerEngine(
        dexscreener=dex_client,
        risk_engine=risk_engine,
        telegram=telegram_svc,
    )
    await scanner.initialize()

    token_profile = {
        "tokenAddress": "Addr123",
        "chainId": "solana",
        "links": ["https://twitter.com/test", "https://t.me/test"],
    }

    result = await scanner.inspect_single_token(token_profile, processed_addresses=set())
    assert result is not None
    assert result["token_address"] == "Addr123"
    assert result["score_breakdown"].final_score > 0
    await scanner.close()

"""Unit tests for DexScreener collector."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.collectors.dexscreener import DexScreenerClient


@pytest.mark.asyncio
async def test_dexscreener_get_latest_token_profiles():
    """Verifies fetching and parsing list of token profiles."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"tokenAddress": "Addr1", "chainId": "solana"},
        {"tokenAddress": "Addr2", "chainId": "bsc"},
    ]
    mock_client.get = AsyncMock(return_value=mock_response)

    client = DexScreenerClient(client=mock_client)
    profiles = await client.get_latest_token_profiles()

    assert len(profiles) == 2
    assert profiles[0]["tokenAddress"] == "Addr1"


@pytest.mark.asyncio
async def test_dexscreener_get_best_pair():
    """Verifies that the highest liquidity + volume pair is selected."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "pairs": [
            {
                "pairAddress": "LowPair",
                "volume": {"h1": 5000.0},
                "liquidity": {"usd": 2000.0},
            },
            {
                "pairAddress": "BestPair",
                "volume": {"h1": 50000.0},
                "liquidity": {"usd": 30000.0},
            },
        ]
    }
    mock_client.get = AsyncMock(return_value=mock_response)

    client = DexScreenerClient(client=mock_client)
    best = await client.get_best_pair("SampleTokenAddress")

    assert best is not None
    assert best["pairAddress"] == "BestPair"

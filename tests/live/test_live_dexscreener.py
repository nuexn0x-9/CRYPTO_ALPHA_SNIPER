"""Live API integration test for DexScreener."""

import os

import pytest

from src.collectors.dexscreener import DexScreenerClient

LIVE_ENABLED = os.getenv("ENABLE_LIVE_TEST", "false").lower() == "true"


@pytest.mark.skipif(not LIVE_ENABLED, reason="Live external API tests disabled by default. Set ENABLE_LIVE_TEST=true to run.")
@pytest.mark.asyncio
async def test_live_dexscreener_endpoint():
    """Performs real HTTP query to DexScreener live API."""
    client = DexScreenerClient()
    profiles = await client.get_latest_token_profiles()
    assert isinstance(profiles, list)
    if profiles:
        first_token = profiles[0].get("tokenAddress")
        assert first_token is not None
        pair = await client.get_best_pair(first_token)
        # Pair could be None or a dict
        if pair:
            assert "pairAddress" in pair
    await client.close()

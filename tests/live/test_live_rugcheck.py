"""Live API integration test for RugCheck."""

import os

import pytest

from src.analyzers.risk_engine import RiskEngine

LIVE_ENABLED = os.getenv("ENABLE_LIVE_TEST", "false").lower() == "true"


@pytest.mark.skipif(not LIVE_ENABLED, reason="Live external API tests disabled by default. Set ENABLE_LIVE_TEST=true to run.")
@pytest.mark.asyncio
async def test_live_rugcheck_solana():
    """Performs real HTTP query to RugCheck API for a well-known Solana token."""
    engine = RiskEngine()
    # USDC Mint Address on Solana
    usdc_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    assessment = await engine.evaluate_token("solana", usdc_address)
    assert assessment is not None
    assert assessment.chain == "solana"
    await engine.close()

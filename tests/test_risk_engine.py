"""Unit tests for RiskEngine."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.analyzers.risk_engine import RiskAssessment, RiskEngine


@pytest.mark.asyncio
async def test_risk_engine_solana_safe_pump_fun():
    """Verifies that pump.fun tokens with revoked authorities are evaluated as safe."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    # Simulate 404 from RugCheck (brand new curve)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_client.get = AsyncMock(return_value=mock_response)

    engine = RiskEngine(client=mock_client)
    assessment: RiskAssessment = await engine.evaluate_token(
        chain="solana",
        token_address="SamplePumpAddress1111111111111111111111pump"
    )

    assert assessment.is_safe is True
    assert assessment.mint_authority_disabled is True
    assert assessment.freeze_authority_disabled is True
    assert assessment.risk_score <= 30


@pytest.mark.asyncio
async def test_risk_engine_solana_danger_mint_authority():
    """Verifies that an enabled mint authority triggers high risk and rejection."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "score": 500,
        "tokenMeta": {
            "mintAuthority": "SomeDevWalletAddress",
            "freezeAuthority": "SomeDevWalletAddress",
        },
        "risks": [
            {"name": "Mint Authority is not revoked", "level": "danger"},
            {"name": "Freeze Authority is not revoked", "level": "danger"},
        ],
        "topHolders": [{"pct": 45.0}],
    }
    mock_client.get = AsyncMock(return_value=mock_response)

    engine = RiskEngine(client=mock_client)
    assessment: RiskAssessment = await engine.evaluate_token(
        chain="solana",
        token_address="DangerousTokenAddress111111111111111111111"
    )

    assert assessment.is_safe is False
    assert assessment.mint_authority_disabled is False
    assert assessment.freeze_authority_disabled is False
    assert assessment.top_holder_concentration_risk is True
    assert assessment.risk_score >= 65
    assert len(assessment.risk_factors) >= 3


def test_risk_engine_bsc_low_liquidity():
    """Verifies that low liquidity on BSC triggers warning."""
    engine = RiskEngine()
    assessment = engine._evaluate_bsc(
        token_address="0x1234567890abcdef1234567890abcdef12345678",
        pair_data={"liquidity": {"usd": 500.0}}
    )
    assert assessment.risk_score >= 25
    assert any("liquidity" in factor.lower() for factor in assessment.risk_factors)

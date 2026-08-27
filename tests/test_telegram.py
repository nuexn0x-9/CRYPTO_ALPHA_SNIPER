"""Unit tests for Telegram formatting service."""

from src.analyzers.risk_engine import RiskAssessment
from src.engine.scorer import ScoreBreakdown
from src.services.telegram import TelegramService


def test_telegram_message_formatting():
    """Verifies that the generated HTML Telegram alert contains key indicators and metrics."""
    service = TelegramService()

    score = ScoreBreakdown(
        momentum_score=85,
        risk_score=15,
        final_score=85,
        signal_tier="ALPHA_SIGNAL",
        volume_h1=95000.0,
        liquidity_usd=30000.0,
        market_cap=60000.0,
        buys_h1=140,
        sells_h1=40,
        buy_sell_ratio=3.5,
        volume_per_minute=9500.0,
        age_minutes=10,
    )

    risk = RiskAssessment(
        chain="solana",
        token_address="6BeyohhmEkxxBsKsne2rLUjkVpx1uQ1jw4KVB9uTpump",
        risk_score=15,
        is_safe=True,
        mint_authority_disabled=True,
        freeze_authority_disabled=True,
    )

    msg = service.format_signal_message(
        token_address="6BeyohhmEkxxBsKsne2rLUjkVpx1uQ1jw4KVB9uTpump",
        chain="solana",
        pair_address="PairAddress123",
        dex_url="https://dexscreener.com/solana/6BeyohhmEkxxBsKsne2rLUjkVpx1uQ1jw4KVB9uTpump",
        score=score,
        risk=risk,
        symbol="ALPHA",
        name="Alpha Token",
    )

    assert "ALPHA SIGNAL" in msg
    assert "SOLANA" in msg
    assert "Alpha Score:</b> 85/100" in msg
    assert "Low Risk" in msg
    assert "95,000" in msg
    assert "6BeyohhmEkxxBsKsne2rLUjkVpx1uQ1jw4KVB9uTpump" in msg

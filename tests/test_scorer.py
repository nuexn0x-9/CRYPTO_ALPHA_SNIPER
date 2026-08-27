"""Unit tests for MomentumScorer engine."""

from datetime import datetime, timezone

from src.engine.scorer import MomentumScorer


def test_scorer_high_momentum_alpha_signal():
    """Verifies that high volume, high ratio, low age token achieves ALPHA_SIGNAL tier."""
    scorer = MomentumScorer()

    now_ms = datetime.now(timezone.utc).timestamp() * 1000.0
    pair_created_at = now_ms - (5 * 60 * 1000)  # 5 minutes old

    token_profile = {
        "tokenAddress": "TestTokenAddress11111111111111111111111111111",
        "chainId": "solana",
        "links": ["https://twitter.com/test", "https://t.me/test"],
    }

    pair_data = {
        "pairCreatedAt": pair_created_at,
        "volume": {"h1": 150000.0},
        "liquidity": {"usd": 25000.0},
        "marketCap": 85000.0,
        "txns": {
            "h1": {
                "buys": 120,
                "sells": 40,
            }
        },
    }

    result = scorer.calculate_score(token_profile, pair_data, risk_score=0)

    # Breakdown verification:
    # Age <= 10 min: +25
    # Volume >= 100k: +20
    # VPM (150k / 5 = 30k) >= 5000: +30
    # Ratio (120 / 40 = 3.0) >= 2.0: +20
    # Liquidity >= 20k: +10
    # Links >= 2: +5
    # Total Momentum = 110 (capped at 100 final)
    assert result.age_minutes == 5
    assert result.volume_h1 == 150000.0
    assert result.buy_sell_ratio == 3.0
    assert result.momentum_score >= 100
    assert result.final_score >= 70
    assert result.signal_tier == "ALPHA_SIGNAL"


def test_scorer_low_volume_filtered():
    """Verifies that an older, low volume token results in low score / None tier."""
    scorer = MomentumScorer()

    now_ms = datetime.now(timezone.utc).timestamp() * 1000.0
    pair_created_at = now_ms - (55 * 60 * 1000)  # 55 minutes old

    token_profile = {
        "tokenAddress": "TestTokenAddress22222222222222222222222222222",
        "chainId": "solana",
        "links": [],
    }

    pair_data = {
        "pairCreatedAt": pair_created_at,
        "volume": {"h1": 5000.0},
        "liquidity": {"usd": 4000.0},
        "marketCap": 15000.0,
        "txns": {
            "h1": {
                "buys": 5,
                "sells": 10,
            }
        },
    }

    result = scorer.calculate_score(token_profile, pair_data, risk_score=0)
    assert result.final_score < 40
    assert result.signal_tier is None


def test_scorer_risk_penalty():
    """Verifies that a high risk score penalizes the final score."""
    scorer = MomentumScorer()

    now_ms = datetime.now(timezone.utc).timestamp() * 1000.0
    pair_created_at = now_ms - (8 * 60 * 1000)

    token_profile = {"tokenAddress": "RiskTestAddress", "chainId": "solana"}
    pair_data = {
        "pairCreatedAt": pair_created_at,
        "volume": {"h1": 55000.0},
        "liquidity": {"usd": 15000.0},
        "marketCap": 30000.0,
        "txns": {"h1": {"buys": 50, "sells": 20}},
    }

    result_safe = scorer.calculate_score(token_profile, pair_data, risk_score=0)
    result_risky = scorer.calculate_score(token_profile, pair_data, risk_score=60)

    assert result_risky.final_score < result_safe.final_score
    assert result_risky.risk_score == 60

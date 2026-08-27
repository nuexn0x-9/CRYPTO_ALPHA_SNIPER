"""Momentum Scorer Engine preserving domain scoring formulas from ALPHA_SNIPER."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.config.settings import get_settings


@dataclass
class ScoreBreakdown:
    """Detailed result of momentum and risk evaluation."""
    momentum_score: int
    risk_score: int
    final_score: int
    signal_tier: Optional[str]  # "ALPHA_SIGNAL", "EARLY_SIGNAL", "WATCHLIST", or None
    volume_h1: float
    liquidity_usd: float
    market_cap: float
    buys_h1: int
    sells_h1: int
    buy_sell_ratio: float
    volume_per_minute: float
    age_minutes: int


class MomentumScorer:
    """Calculates multi-dimensional momentum and composite alpha scores."""

    def __init__(self):
        self.settings = get_settings()

    def calculate_score(
        self,
        token_profile: Dict[str, Any],
        pair_data: Dict[str, Any],
        risk_score: int = 0
    ) -> ScoreBreakdown:
        """
        Calculates momentum score based on token age, volume, VPM, buy/sell ratio,
        liquidity depth, and social presence.
        """
        momentum_score = 0

        # 1. Calculate Age
        pair_created_at = pair_data.get("pairCreatedAt")
        age_minutes = 9999

        if pair_created_at:
            current_ts = datetime.now(timezone.utc).timestamp()
            created_ts = pair_created_at / 1000.0
            diff_seconds = current_ts - created_ts
            if diff_seconds > 0:
                age_minutes = int(diff_seconds / 60)

        # 2. Extract metrics
        volume_h1 = float(pair_data.get("volume", {}).get("h1", 0.0) or 0.0)
        liquidity_usd = float(pair_data.get("liquidity", {}).get("usd", 0.0) or 0.0)
        market_cap = float(pair_data.get("marketCap", 0.0) or 0.0)
        buys_h1 = int(pair_data.get("txns", {}).get("h1", {}).get("buys", 0) or 0)
        sells_h1 = int(pair_data.get("txns", {}).get("h1", {}).get("sells", 0) or 0)

        # 3. Volume Per Minute (VPM)
        effective_age = max(age_minutes, 1)
        volume_per_minute = volume_h1 / effective_age

        # 4. Buy / Sell Ratio
        buy_sell_ratio = 0.0
        if sells_h1 > 0:
            buy_sell_ratio = buys_h1 / sells_h1
        elif buys_h1 > 0:
            buy_sell_ratio = float(buys_h1)

        # ======================================================================
        # CORE SCORING ALGORITHM (Preserved from ALPHA_SNIPER)
        # ======================================================================

        # Age Score (Max 25 pts)
        if age_minutes <= 10:
            momentum_score += 25
        elif age_minutes <= 30:
            momentum_score += 20
        elif age_minutes <= 60:
            momentum_score += 10

        # Volume Score (Max 20 pts)
        if volume_h1 >= 100000:
            momentum_score += 20
        elif volume_h1 >= 50000:
            momentum_score += 15
        elif volume_h1 >= 20000:
            momentum_score += 10

        # Momentum VPM Score (Max 30 pts)
        if volume_per_minute >= 5000:
            momentum_score += 30
        elif volume_per_minute >= 3000:
            momentum_score += 25
        elif volume_per_minute >= 2000:
            momentum_score += 20
        elif volume_per_minute >= 1000:
            momentum_score += 10

        # Buy Pressure Ratio Score (Max 20 pts)
        if buy_sell_ratio >= 2.0:
            momentum_score += 20
        elif buy_sell_ratio >= 1.5:
            momentum_score += 15
        elif buy_sell_ratio >= 1.2:
            momentum_score += 10

        # Liquidity Depth Bonus (Max 10 pts)
        if liquidity_usd >= 20000:
            momentum_score += 10
        elif liquidity_usd >= 10000:
            momentum_score += 5

        # Social Presence Bonus (Max 5 pts)
        links = token_profile.get("links", [])
        if isinstance(links, list) and len(links) >= 2:
            momentum_score += 5

        # ======================================================================
        # COMPOSITE FINAL SCORE & RISK PENALTY
        # ======================================================================
        # Deduct risk penalty if risk score > 20
        risk_penalty = max(0, int((risk_score - 20) * 0.5)) if risk_score > 20 else 0
        final_score = max(0, min(100, momentum_score - risk_penalty))

        # Determine Signal Tier
        signal_tier = None
        if final_score >= self.settings.ALPHA_SIGNAL_SCORE:
            signal_tier = "ALPHA_SIGNAL"
        elif final_score >= self.settings.EARLY_SIGNAL_SCORE:
            signal_tier = "EARLY_SIGNAL"
        elif final_score >= self.settings.WATCHLIST_SCORE:
            signal_tier = "WATCHLIST"

        return ScoreBreakdown(
            momentum_score=momentum_score,
            risk_score=risk_score,
            final_score=final_score,
            signal_tier=signal_tier,
            volume_h1=volume_h1,
            liquidity_usd=liquidity_usd,
            market_cap=market_cap,
            buys_h1=buys_h1,
            sells_h1=sells_h1,
            buy_sell_ratio=round(buy_sell_ratio, 2),
            volume_per_minute=round(volume_per_minute, 2),
            age_minutes=age_minutes,
        )

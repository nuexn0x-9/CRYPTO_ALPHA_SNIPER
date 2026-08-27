"""Security and Risk Evaluation Engine."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from src.config.settings import get_settings


@dataclass
class RiskAssessment:
    """Represents the security analysis result for a token."""
    chain: str
    token_address: str
    risk_score: int = 0  # 0 = Safe, 100 = Critical Danger
    is_safe: bool = True
    mint_authority_disabled: bool = True
    freeze_authority_disabled: bool = True
    lp_locked_or_burned: bool = True
    top_holder_concentration_risk: bool = False
    status: str = "SAFE"
    risk_factors: List[str] = field(default_factory=list)
    raw_report: Dict[str, Any] = field(default_factory=dict)


class RiskEngine:
    """
    Evaluates token safety and security posture across multiple blockchains.
    Integrates with RugCheck API for Solana and heuristic checks for EVM/TON.
    """

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.settings = get_settings()
        self.base_url = self.settings.RUGCHECK_API_BASE.rstrip("/")
        self._external_client = client is not None
        self.client = client or httpx.AsyncClient(
            timeout=10.0,
            headers={
                "User-Agent": "CRYPTO_ALPHA_SNIPER/1.0 (+https://github.com/nuexn0x-9/CRYPTO_ALPHA_SNIPER)",
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        """Closes the underlying HTTP client if internally created."""
        if not self._external_client and not self.client.is_closed:
            await self.client.aclose()

    async def evaluate_token(
        self,
        chain: str,
        token_address: str,
        pair_data: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """
        Executes comprehensive safety checks and returns a RiskAssessment.
        """
        chain_lower = chain.lower()

        if chain_lower == "solana":
            return await self._evaluate_solana(token_address, pair_data)
        elif chain_lower == "bsc":
            return self._evaluate_bsc(token_address, pair_data)
        elif chain_lower == "ton":
            return self._evaluate_ton(token_address, pair_data)
        else:
            return RiskAssessment(
                chain=chain,
                token_address=token_address,
                risk_score=25,
                is_safe=True,
                status="UNSUPPORTED_CHAIN_DEFAULT",
            )

    async def _evaluate_solana(
        self,
        token_address: str,
        pair_data: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """Audits Solana token via RugCheck API and DEX pair metrics."""
        assessment = RiskAssessment(chain="solana", token_address=token_address)
        url = f"{self.base_url}/tokens/{token_address}/report"

        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                assessment.raw_report = data

                # 1. RugCheck score (0 to high)
                raw_score = data.get("score", 0)
                # Normalize score to 0 - 100 scale
                normalized_score = min(int(raw_score / 10), 100) if raw_score > 100 else int(raw_score)
                assessment.risk_score = normalized_score

                # 2. Token Authorities
                token_meta = data.get("tokenMeta", {})
                mint_authority = token_meta.get("mintAuthority")
                freeze_authority = token_meta.get("freezeAuthority")

                if mint_authority is not None:
                    assessment.mint_authority_disabled = False
                    assessment.risk_score = min(assessment.risk_score + 35, 100)
                    assessment.risk_factors.append("Mint Authority is still ENABLED (Infinite mint risk)")

                if freeze_authority is not None:
                    assessment.freeze_authority_disabled = False
                    assessment.risk_score = min(assessment.risk_score + 30, 100)
                    assessment.risk_factors.append("Freeze Authority is still ENABLED (Blacklist risk)")

                # 3. Known Risks / Dangers from RugCheck
                risks = data.get("risks", [])
                for r in risks:
                    name = r.get("name", "")
                    level = r.get("level", "").lower()
                    if level == "danger":
                        assessment.risk_factors.append(f"RugCheck Danger: {name}")
                        assessment.risk_score = min(assessment.risk_score + 25, 100)
                    elif level == "warn":
                        assessment.risk_factors.append(f"RugCheck Warning: {name}")
                        assessment.risk_score = min(assessment.risk_score + 10, 100)

                # 4. Top Holders Concentration
                top_holders = data.get("topHolders", [])
                if top_holders:
                    top_1_pct = float(top_holders[0].get("pct", 0.0) or 0.0)
                    if top_1_pct > 30.0:
                        assessment.top_holder_concentration_risk = True
                        assessment.risk_factors.append(f"Top 1 holder owns {top_1_pct:.1f}% of supply")
                        assessment.risk_score = min(assessment.risk_score + 20, 100)

            elif response.status_code == 404:
                # Newly launched token (Pump.fun curve), not yet indexed by RugCheck
                if token_address.endswith("pump"):
                    assessment.risk_score = 15  # Pump.fun tokens automatically revoke mint/freeze
                    assessment.mint_authority_disabled = True
                    assessment.freeze_authority_disabled = True
                else:
                    assessment.risk_score = 30
                    assessment.risk_factors.append("RugCheck report not yet available")
            else:
                assessment.risk_score = 25
                assessment.risk_factors.append(f"RugCheck API returned status {response.status_code}")

        except Exception as e:
            logger.debug(f"RugCheck lookup error for {token_address}: {e}")
            assessment.risk_score = 20
            assessment.risk_factors.append("RugCheck verification skipped (timeout/error)")

        # Evaluate against configured threshold
        assessment.is_safe = assessment.risk_score <= self.settings.MAX_ALLOWED_RISK_SCORE
        assessment.status = "SAFE" if assessment.is_safe else "REJECTED_DANGEROUS"
        return assessment

    def _evaluate_bsc(
        self,
        token_address: str,
        pair_data: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """Heuristic safety assessment for BSC pairs."""
        assessment = RiskAssessment(chain="bsc", token_address=token_address)

        if pair_data:
            liquidity = float(pair_data.get("liquidity", {}).get("usd", 0.0) or 0.0)
            if liquidity < 2000.0:
                assessment.risk_score += 25
                assessment.risk_factors.append("Low initial liquidity (< $2,000)")
            else:
                assessment.risk_score = 10
        else:
            assessment.risk_score = 30

        assessment.is_safe = assessment.risk_score <= self.settings.MAX_ALLOWED_RISK_SCORE
        assessment.status = "SAFE" if assessment.is_safe else "REJECTED_DANGEROUS"
        return assessment

    def _evaluate_ton(
        self,
        token_address: str,
        pair_data: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """Heuristic safety assessment for TON pairs."""
        assessment = RiskAssessment(chain="ton", token_address=token_address, risk_score=15)
        assessment.is_safe = assessment.risk_score <= self.settings.MAX_ALLOWED_RISK_SCORE
        assessment.status = "SAFE" if assessment.is_safe else "REJECTED_DANGEROUS"
        return assessment

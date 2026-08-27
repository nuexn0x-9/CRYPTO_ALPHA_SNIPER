"""Asynchronous DexScreener API Client with retry and exponential backoff."""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from src.config.settings import get_settings


class DexScreenerClient:
    """Async client for fetching token profiles and pair analytics from DexScreener."""

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.settings = get_settings()
        self.base_url = self.settings.DEXSCREENER_API_BASE.rstrip("/")
        self._external_client = client is not None
        self.client = client or httpx.AsyncClient(
            timeout=12.0,
            headers={
                "User-Agent": "CRYPTO_ALPHA_SNIPER/1.0 (+https://github.com/nuexn0x-9/CRYPTO_ALPHA_SNIPER)",
                "Accept": "application/json",
            },
            follow_redirects=True,
        )

    async def close(self) -> None:
        """Closes the underlying HTTP client if internally created."""
        if not self._external_client and not self.client.is_closed:
            await self.client.aclose()

    async def get_latest_token_profiles(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Fetches the latest token profiles listed on DexScreener.
        Endpoint: /token-profiles/latest/v1
        """
        url = f"{self.base_url}/token-profiles/latest/v1"
        backoff = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        return data
                    return []
                elif response.status_code == 429:
                    logger.warning(f"DexScreener rate limit (429). Backing off for {backoff:.1f}s...")
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                else:
                    logger.warning(f"DexScreener returned status {response.status_code} on attempt {attempt}")
            except httpx.RequestError as e:
                logger.error(f"DexScreener request error (attempt {attempt}/{max_retries}): {e}")
                await asyncio.sleep(backoff)
                backoff *= 1.5
            except Exception as e:
                logger.error(f"Unexpected error in get_latest_token_profiles: {e}")
                break

        return []

    async def get_token_pairs(self, token_address: str, max_retries: int = 2) -> List[Dict[str, Any]]:
        """
        Fetches all trading pairs for a given token address.
        Endpoint: /latest/dex/tokens/{token_address}
        """
        url = f"{self.base_url}/latest/dex/tokens/{token_address}"
        backoff = 0.5

        for _attempt in range(1, max_retries + 1):
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get("pairs", [])
                    return pairs if isinstance(pairs, list) else []
                elif response.status_code == 429:
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
            except Exception as e:
                logger.debug(f"Pair fetch error for {token_address}: {e}")
                await asyncio.sleep(backoff)

        return []

    async def get_best_pair(self, token_address: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the highest liquidity + volume pair for a given token.
        Preserves original ALPHA_SNIPER pair selection criteria.
        """
        pairs = await self.get_token_pairs(token_address)
        if not pairs:
            return None

        best_pair = None
        best_score = -1.0

        for pair in pairs:
            volume_h1 = float(pair.get("volume", {}).get("h1", 0.0) or 0.0)
            liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0.0) or 0.0)
            pair_score = volume_h1 + liquidity_usd

            if pair_score > best_score:
                best_score = pair_score
                best_pair = pair

        return best_pair

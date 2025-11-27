#!/usr/bin/env python3
"""
Provider Fetch Helper - Simplified for HuggingFace Spaces
Direct HTTP calls with retry logic
"""

import httpx
from typing import Dict, Any, Optional


class ProviderFetchHelper:
    """Simple provider fetch helper with retry logic"""

    def __init__(self):
        self.timeout = 15.0

    async def fetch_url(
        self, url: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Fetch data from URL with retry logic

        Args:
            url: URL to fetch
            params: Query parameters
            max_retries: Maximum retry attempts

        Returns:
            Dict with success, data, error keys
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)

                    if response.status_code == 200:
                        return {
                            "success": True,
                            "data": response.json(),
                            "error": None,
                            "status_code": 200,
                        }
                    else:
                        last_error = f"HTTP {response.status_code}"

            except httpx.TimeoutException:
                last_error = "Request timeout"
            except httpx.RequestError as e:
                last_error = str(e)
            except Exception as e:
                last_error = str(e)

        return {"success": False, "data": None, "error": last_error, "status_code": None}

    async def fetch_coingecko_price(self) -> Dict[str, Any]:
        """Fetch price data from CoinGecko"""
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,binancecoin",
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        }
        return await self.fetch_url(url, params)

    async def fetch_fear_greed(self) -> Dict[str, Any]:
        """Fetch Fear & Greed Index"""
        url = "https://api.alternative.me/fng/"
        params = {"limit": "1", "format": "json"}
        return await self.fetch_url(url, params)

    async def fetch_trending(self) -> Dict[str, Any]:
        """Fetch trending coins from CoinGecko"""
        url = "https://api.coingecko.com/api/v3/search/trending"
        return await self.fetch_url(url)


# Singleton instance
_helper_instance = None


def get_fetch_helper() -> ProviderFetchHelper:
    """Get singleton fetch helper instance"""
    global _helper_instance
    if _helper_instance is None:
        _helper_instance = ProviderFetchHelper()
    return _helper_instance

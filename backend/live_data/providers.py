import logging
import aiohttp
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseProvider:
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def _get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
        try:
            session = await self._get_session()
            url = f"{self.base_url}{endpoint}"
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching from {self.name}: {e}")
            raise

class CoinGeckoProvider(BaseProvider):
    def __init__(self):
        super().__init__("CoinGecko", "https://api.coingecko.com/api/v3")
        self.api_key = os.getenv("COINGECKO_API_KEY")

    async def get_market_data(self, vs_currency: str = "usd", ids: str = "bitcoin,ethereum") -> List[Dict]:
        params = {
            "vs_currency": vs_currency,
            "ids": ids,
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        if self.api_key:
            params["x_cg_demo_api_key"] = self.api_key
        
        return await self._get("/coins/markets", params=params)

    async def get_coin_price(self, coin_id: str, vs_currencies: str = "usd") -> Dict:
        params = {"ids": coin_id, "vs_currencies": vs_currencies}
        return await self._get("/simple/price", params=params)

class BinanceProvider(BaseProvider):
    def __init__(self):
        super().__init__("Binance", "https://api.binance.com/api/v3")

    async def get_ticker_price(self, symbol: str) -> Dict:
        # Symbol example: BTCUSDT
        return await self._get("/ticker/price", params={"symbol": symbol.upper()})

    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[List]:
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        return await self._get("/klines", params=params)

class CryptoPanicProvider(BaseProvider):
    def __init__(self):
        super().__init__("CryptoPanic", "https://cryptopanic.com/api/v1")
        self.api_key = os.getenv("CRYPTOPANIC_API_KEY")

    async def get_news(self, filter_type: str = "hot") -> Dict:
        if not self.api_key:
            logger.warning("CryptoPanic API key not set")
            # Fallback to public RSS feed logic elsewhere or return empty
            return {"results": []}
            
        params = {
            "auth_token": self.api_key,
            "filter": filter_type,
            "public": "true"
        }
        return await self._get("/posts/", params=params)

class AlternativeMeProvider(BaseProvider):
    def __init__(self):
        super().__init__("Alternative.me", "https://api.alternative.me")

    async def get_fear_and_greed(self, limit: int = 1) -> Dict:
        return await self._get("/fng/", params={"limit": limit})

# Singleton instances
coingecko_provider = CoinGeckoProvider()
binance_provider = BinanceProvider()
cryptopanic_provider = CryptoPanicProvider()
alternative_me_provider = AlternativeMeProvider()

async def get_all_providers_status():
    results = {}
    # Simple check
    try:
        await coingecko_provider.get_coin_price("bitcoin")
        results["coingecko"] = "online"
    except:
        results["coingecko"] = "offline"

    try:
        await binance_provider.get_ticker_price("BTCUSDT")
        results["binance"] = "online"
    except:
        results["binance"] = "offline"
        
    try:
        await alternative_me_provider.get_fear_and_greed()
        results["alternative_me"] = "online"
    except:
        results["alternative_me"] = "offline"
        
    return results

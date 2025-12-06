"""CoinGecko provider implementation"""
from __future__ import annotations
from typing import List
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_provider import BaseProvider
from core.models import OHLCV, Price


class CoinGeckoProvider(BaseProvider):
    """CoinGecko public API provider"""

    # Symbol to CoinGecko ID mapping
    SYMBOL_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "XRP": "ripple",
        "BNB": "binancecoin",
        "ADA": "cardano",
        "DOT": "polkadot",
        "LINK": "chainlink",
        "LTC": "litecoin",
        "BCH": "bitcoin-cash",
        "MATIC": "matic-network",
        "AVAX": "avalanche-2",
        "XLM": "stellar",
        "TRX": "tron",
    }

    def __init__(self, api_key: str = None):
        super().__init__(
            name="coingecko",
            base_url="https://api.coingecko.com/api/v3",
            timeout=15
        )
        self.api_key = api_key

    def _get_coin_id(self, symbol: str) -> str:
        """Convert symbol to CoinGecko coin ID"""
        symbol = symbol.upper().replace("USDT", "").replace("/USDT", "")
        return self.SYMBOL_MAP.get(symbol, symbol.lower())

    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int) -> List[OHLCV]:
        """Fetch OHLCV data from CoinGecko"""
        coin_id = self._get_coin_id(symbol)

        # CoinGecko OHLC endpoint provides limited data
        # Days: 1, 7, 14, 30, 90, 180, 365, max
        days_map = {
            "1m": 1,
            "5m": 1,
            "15m": 1,
            "1h": 7,
            "4h": 30,
            "1d": 90,
            "1w": 365,
        }
        days = days_map.get(interval, 7)

        url = f"{self.base_url}/coins/{coin_id}/ohlc"
        params = {
            "vs_currency": "usd",
            "days": days
        }

        if self.api_key:
            params["x_cg_pro_api_key"] = self.api_key

        data = await self._make_request(url, params)

        # Parse CoinGecko OHLC format: [timestamp, open, high, low, close]
        ohlcv_list = []
        for candle in data[:limit]:  # Limit results
            ohlcv_list.append(OHLCV(
                timestamp=int(candle[0]),
                open=float(candle[1]),
                high=float(candle[2]),
                low=float(candle[3]),
                close=float(candle[4]),
                volume=0.0  # CoinGecko OHLC doesn't include volume
            ))

        return ohlcv_list

    async def fetch_prices(self, symbols: List[str]) -> List[Price]:
        """Fetch current prices from CoinGecko"""
        # Convert symbols to coin IDs
        coin_ids = [self._get_coin_id(s) for s in symbols]

        url = f"{self.base_url}/simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        }

        if self.api_key:
            params["x_cg_pro_api_key"] = self.api_key

        data = await self._make_request(url, params)

        prices = []
        for coin_id, coin_data in data.items():
            # Find original symbol
            symbol = next(
                (s for s, cid in self.SYMBOL_MAP.items() if cid == coin_id),
                coin_id.upper()
            )

            prices.append(Price(
                symbol=symbol,
                name=coin_id.replace("-", " ").title(),
                price=coin_data.get("usd", 0),
                priceUsd=coin_data.get("usd", 0),
                change24h=coin_data.get("usd_24h_change"),
                volume24h=coin_data.get("usd_24h_vol"),
                marketCap=coin_data.get("usd_market_cap"),
                lastUpdate=datetime.now().isoformat()
            ))

        return prices

    async def fetch_market_data(self) -> dict:
        """Fetch global market data"""
        url = f"{self.base_url}/global"

        if self.api_key:
            params = {"x_cg_pro_api_key": self.api_key}
        else:
            params = None

        data = await self._make_request(url, params)

        if "data" in data:
            return data["data"]
        return data

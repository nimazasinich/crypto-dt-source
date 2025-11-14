"""CoinCap provider implementation"""
from __future__ import annotations
from typing import List
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_provider import BaseProvider
from core.models import OHLCV, Price


class CoinCapProvider(BaseProvider):
    """CoinCap public API provider"""

    # Interval mapping
    INTERVAL_MAP = {
        "1m": "m1",
        "5m": "m5",
        "15m": "m15",
        "1h": "h1",
        "4h": "h4",  # Not directly supported
        "1d": "d1",
        "1w": "w1",  # Not directly supported
    }

    def __init__(self):
        super().__init__(
            name="coincap",
            base_url="https://api.coincap.io/v2",
            timeout=10
        )

    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to CoinCap format (lowercase)"""
        symbol = symbol.upper().replace("/", "").replace("USDT", "").replace("-", "")
        return symbol.lower()

    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int) -> List[OHLCV]:
        """Fetch OHLCV data from CoinCap history endpoint"""
        coin_id = self._normalize_symbol(symbol)
        coincap_interval = self.INTERVAL_MAP.get(interval, "h1")

        url = f"{self.base_url}/assets/{coin_id}/history"
        params = {
            "interval": coincap_interval
        }

        data = await self._make_request(url, params)

        if "data" not in data:
            raise Exception("No data returned from CoinCap")

        # CoinCap history only provides price points, not full OHLCV
        # We'll create synthetic OHLCV from price data
        history = data["data"][:limit]

        ohlcv_list = []
        for point in history:
            price = float(point.get("priceUsd", 0))
            ohlcv_list.append(OHLCV(
                timestamp=int(point.get("time", 0)),
                open=price,
                high=price,
                low=price,
                close=price,
                volume=0.0  # CoinCap history doesn't include volume
            ))

        return ohlcv_list

    async def fetch_prices(self, symbols: List[str]) -> List[Price]:
        """Fetch current prices from CoinCap"""
        url = f"{self.base_url}/assets"
        params = {
            "limit": 100  # Get top 100 to cover most symbols
        }

        data = await self._make_request(url, params)

        if "data" not in data:
            raise Exception("No data returned from CoinCap")

        # Create a set of requested symbols
        requested = {self._normalize_symbol(s) for s in symbols}

        prices = []
        for asset in data["data"]:
            if asset["id"] in requested or asset["symbol"].lower() in requested:
                prices.append(Price(
                    symbol=asset["symbol"],
                    name=asset["name"],
                    price=float(asset["priceUsd"]),
                    priceUsd=float(asset["priceUsd"]),
                    change24h=float(asset.get("changePercent24Hr", 0)),
                    volume24h=float(asset.get("volumeUsd24Hr", 0)),
                    marketCap=float(asset.get("marketCapUsd", 0)),
                    rank=int(asset.get("rank", 0)),
                    lastUpdate=datetime.now().isoformat()
                ))

        return prices

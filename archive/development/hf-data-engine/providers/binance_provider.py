"""Binance provider implementation"""
from __future__ import annotations
from typing import List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_provider import BaseProvider
from core.models import OHLCV, Price


class BinanceProvider(BaseProvider):
    """Binance public API provider"""

    # Binance interval mapping
    INTERVAL_MAP = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
        "1w": "1w",
    }

    def __init__(self):
        super().__init__(
            name="binance",
            base_url="https://api.binance.com",
            timeout=10
        )

    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to Binance format (BTCUSDT)"""
        symbol = symbol.upper().replace("/", "").replace("-", "")
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        return symbol

    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int) -> List[OHLCV]:
        """Fetch OHLCV data from Binance"""
        normalized_symbol = self._normalize_symbol(symbol)
        binance_interval = self.INTERVAL_MAP.get(interval, "1h")

        url = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": normalized_symbol,
            "interval": binance_interval,
            "limit": min(limit, 1000)  # Binance max is 1000
        }

        data = await self._make_request(url, params)

        # Parse Binance kline format
        # [timestamp, open, high, low, close, volume, closeTime, ...]
        ohlcv_list = []
        for candle in data:
            ohlcv_list.append(OHLCV(
                timestamp=int(candle[0]),
                open=float(candle[1]),
                high=float(candle[2]),
                low=float(candle[3]),
                close=float(candle[4]),
                volume=float(candle[5])
            ))

        return ohlcv_list

    async def fetch_prices(self, symbols: List[str]) -> List[Price]:
        """Fetch current prices from Binance 24h ticker"""
        url = f"{self.base_url}/api/v3/ticker/24hr"
        data = await self._make_request(url)

        # Create a set of requested symbols
        requested = {self._normalize_symbol(s) for s in symbols}

        prices = []
        for ticker in data:
            if ticker["symbol"] in requested:
                # Extract base symbol (remove USDT)
                base_symbol = ticker["symbol"].replace("USDT", "")

                prices.append(Price(
                    symbol=base_symbol,
                    name=base_symbol,  # Binance doesn't provide name
                    price=float(ticker["lastPrice"]),
                    priceUsd=float(ticker["lastPrice"]),
                    change24h=float(ticker["priceChangePercent"]),
                    volume24h=float(ticker["quoteVolume"]),
                    lastUpdate=ticker.get("closeTime", 0)
                ))

        return prices

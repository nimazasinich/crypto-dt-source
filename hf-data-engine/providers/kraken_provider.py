"""Kraken provider implementation"""

from __future__ import annotations
from typing import List
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_provider import BaseProvider
from core.models import OHLCV, Price


class KrakenProvider(BaseProvider):
    """Kraken public API provider"""

    # Kraken interval mapping (in minutes)
    INTERVAL_MAP = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "4h": 240,
        "1d": 1440,
        "1w": 10080,
    }

    # Symbol mapping
    SYMBOL_MAP = {
        "BTC": "XXBTZUSD",
        "ETH": "XETHZUSD",
        "SOL": "SOLUSD",
        "XRP": "XXRPZUSD",
        "ADA": "ADAUSD",
        "DOT": "DOTUSD",
        "LINK": "LINKUSD",
        "LTC": "XLTCZUSD",
        "BCH": "BCHUSD",
        "MATIC": "MATICUSD",
        "AVAX": "AVAXUSD",
        "XLM": "XXLMZUSD",
    }

    def __init__(self):
        super().__init__(name="kraken", base_url="https://api.kraken.com/0/public", timeout=10)

    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to Kraken format"""
        symbol = symbol.upper().replace("/", "").replace("USDT", "").replace("-", "")
        return self.SYMBOL_MAP.get(symbol, f"{symbol}USD")

    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int) -> List[OHLCV]:
        """Fetch OHLCV data from Kraken"""
        kraken_symbol = self._normalize_symbol(symbol)
        kraken_interval = self.INTERVAL_MAP.get(interval, 60)

        url = f"{self.base_url}/OHLC"
        params = {"pair": kraken_symbol, "interval": kraken_interval}

        data = await self._make_request(url, params)

        if "error" in data and data["error"]:
            raise Exception(f"Kraken error: {data['error']}")

        # Get the OHLC data (key is the pair name)
        result = data.get("result", {})
        pair_key = next(iter([k for k in result.keys() if k != "last"]), None)

        if not pair_key:
            raise Exception("No OHLC data returned from Kraken")

        ohlc_data = result[pair_key]

        # Parse Kraken OHLC format
        # [time, open, high, low, close, vwap, volume, count]
        ohlcv_list = []
        for candle in ohlc_data[:limit]:
            ohlcv_list.append(
                OHLCV(
                    timestamp=int(candle[0]) * 1000,  # Convert to milliseconds
                    open=float(candle[1]),
                    high=float(candle[2]),
                    low=float(candle[3]),
                    close=float(candle[4]),
                    volume=float(candle[6]),
                )
            )

        return ohlcv_list

    async def fetch_prices(self, symbols: List[str]) -> List[Price]:
        """Fetch current prices from Kraken ticker"""
        # Kraken requires specific pair names
        pairs = [self._normalize_symbol(s) for s in symbols]

        url = f"{self.base_url}/Ticker"
        params = {"pair": ",".join(pairs)}

        data = await self._make_request(url, params)

        if "error" in data and data["error"]:
            raise Exception(f"Kraken error: {data['error']}")

        result = data.get("result", {})

        prices = []
        for pair_key, ticker in result.items():
            # Extract base symbol
            base_symbol = next(
                (s for s, p in self.SYMBOL_MAP.items() if p == pair_key), pair_key[:3]
            )

            # Kraken ticker format: c = last, v = volume, o = open
            last_price = float(ticker["c"][0])
            volume_24h = float(ticker["v"][1]) * last_price  # Volume in quote currency
            open_price = float(ticker["o"])

            # Calculate 24h change percentage
            change_24h = ((last_price - open_price) / open_price * 100) if open_price > 0 else 0

            prices.append(
                Price(
                    symbol=base_symbol,
                    name=base_symbol,
                    price=last_price,
                    priceUsd=last_price,
                    change24h=change_24h,
                    volume24h=volume_24h,
                    lastUpdate=datetime.now().isoformat(),
                )
            )

        return prices

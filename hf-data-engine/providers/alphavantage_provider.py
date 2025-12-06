"""Alpha Vantage provider implementation"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_provider import BaseProvider
from core.models import OHLCV, Price


class AlphaVantageProvider(BaseProvider):
    """Alpha Vantage API provider for stock and crypto data
    
    API Key: 40XS7GQ6AU9NB6Y4
    Documentation: https://www.alphavantage.co/documentation/
    """

    # Symbol mapping for crypto
    CRYPTO_SYMBOL_MAP = {
        "BTC": "BTC",
        "ETH": "ETH",
        "SOL": "SOL",
        "XRP": "XRP",
        "BNB": "BNB",
        "ADA": "ADA",
        "DOT": "DOT",
        "LINK": "LINK",
        "LTC": "LTC",
        "BCH": "BCH",
        "MATIC": "MATIC",
        "AVAX": "AVAX",
    }

    def __init__(self, api_key: str = "40XS7GQ6AU9NB6Y4"):
        super().__init__(
            name="alphavantage",
            base_url="https://www.alphavantage.co/query",
            timeout=20
        )
        self.api_key = api_key

    def _get_crypto_symbol(self, symbol: str) -> str:
        """Convert symbol to Alpha Vantage format"""
        symbol = symbol.upper().replace("USDT", "").replace("/USDT", "").replace("USD", "")
        return self.CRYPTO_SYMBOL_MAP.get(symbol, symbol)

    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int) -> List[OHLCV]:
        """Fetch OHLCV data from Alpha Vantage
        
        Intervals: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        """
        crypto_symbol = self._get_crypto_symbol(symbol)
        
        # Map interval to Alpha Vantage format
        interval_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "1h": "60min",
            "4h": "daily",
            "1d": "daily",
            "1w": "weekly",
        }
        av_interval = interval_map.get(interval, "daily")
        
        # Choose function based on interval
        if av_interval in ["1min", "5min", "15min", "30min", "60min"]:
            function = "CRYPTO_INTRADAY"
        else:
            function = "DIGITAL_CURRENCY_DAILY"
        
        params = {
            "function": function,
            "symbol": crypto_symbol,
            "market": "USD",
            "apikey": self.api_key,
            "outputsize": "full" if limit > 100 else "compact"
        }
        
        if function == "CRYPTO_INTRADAY":
            params["interval"] = av_interval
        
        try:
            data = await self._make_request(self.base_url, params)
            
            # Handle rate limit error
            if "Note" in data or "Information" in data:
                raise Exception("Alpha Vantage API rate limit reached")
            
            # Parse response based on function
            if function == "CRYPTO_INTRADAY":
                time_series_key = f"Time Series Crypto ({av_interval})"
            else:
                time_series_key = "Time Series (Digital Currency Daily)"
            
            if time_series_key not in data:
                raise Exception(f"No time series data found in response: {list(data.keys())}")
            
            time_series = data[time_series_key]
            
            ohlcv_list = []
            for timestamp, values in list(time_series.items())[:limit]:
                # Parse timestamp
                dt = datetime.fromisoformat(timestamp.replace(" ", "T"))
                
                # Extract OHLCV values
                if function == "CRYPTO_INTRADAY":
                    open_price = float(values.get("1. open", 0))
                    high_price = float(values.get("2. high", 0))
                    low_price = float(values.get("3. low", 0))
                    close_price = float(values.get("4. close", 0))
                    volume = float(values.get("5. volume", 0))
                else:
                    # Digital currency daily format
                    open_price = float(values.get("1a. open (USD)", 0))
                    high_price = float(values.get("2a. high (USD)", 0))
                    low_price = float(values.get("3a. low (USD)", 0))
                    close_price = float(values.get("4a. close (USD)", 0))
                    volume = float(values.get("5. volume", 0))
                
                ohlcv_list.append(OHLCV(
                    timestamp=int(dt.timestamp() * 1000),
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume
                ))
            
            return ohlcv_list
        
        except Exception as e:
            self.last_error = f"Alpha Vantage OHLCV fetch error: {str(e)}"
            raise

    async def fetch_prices(self, symbols: List[str]) -> List[Price]:
        """Fetch current crypto prices from Alpha Vantage"""
        prices = []
        
        for symbol in symbols:
            try:
                crypto_symbol = self._get_crypto_symbol(symbol)
                
                params = {
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": crypto_symbol,
                    "to_currency": "USD",
                    "apikey": self.api_key
                }
                
                data = await self._make_request(self.base_url, params)
                
                # Handle rate limit
                if "Note" in data or "Information" in data:
                    raise Exception("Alpha Vantage API rate limit reached")
                
                if "Realtime Currency Exchange Rate" not in data:
                    continue
                
                exchange_data = data["Realtime Currency Exchange Rate"]
                
                price = float(exchange_data.get("5. Exchange Rate", 0))
                last_update = exchange_data.get("6. Last Refreshed", datetime.now().isoformat())
                
                prices.append(Price(
                    symbol=symbol.upper(),
                    name=exchange_data.get("2. From_Currency Name", crypto_symbol),
                    price=price,
                    priceUsd=price,
                    change24h=None,  # Not available in this endpoint
                    volume24h=None,
                    marketCap=None,
                    lastUpdate=last_update
                ))
                
            except Exception as e:
                self.last_error = f"Alpha Vantage price fetch error for {symbol}: {str(e)}"
                continue
        
        return prices

    async def fetch_market_overview(self) -> Dict[str, Any]:
        """Fetch market overview data
        
        Alpha Vantage provides various market overview data
        """
        params = {
            "function": "MARKET_STATUS",
            "apikey": self.api_key
        }
        
        try:
            data = await self._make_request(self.base_url, params)
            return data
        except Exception as e:
            self.last_error = f"Alpha Vantage market overview error: {str(e)}"
            raise

    async def fetch_global_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch global quote for a symbol"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            data = await self._make_request(self.base_url, params)
            
            if "Global Quote" in data:
                return data["Global Quote"]
            return {}
        except Exception as e:
            self.last_error = f"Alpha Vantage global quote error: {str(e)}"
            raise

    async def fetch_crypto_rating(self, symbol: str) -> Dict[str, Any]:
        """Fetch crypto health rating"""
        crypto_symbol = self._get_crypto_symbol(symbol)
        
        params = {
            "function": "CRYPTO_RATING",
            "symbol": crypto_symbol,
            "apikey": self.api_key
        }
        
        try:
            data = await self._make_request(self.base_url, params)
            
            if "Crypto Rating (FCAS)" in data:
                return data["Crypto Rating (FCAS)"]
            return {}
        except Exception as e:
            self.last_error = f"Alpha Vantage crypto rating error: {str(e)}"
            raise

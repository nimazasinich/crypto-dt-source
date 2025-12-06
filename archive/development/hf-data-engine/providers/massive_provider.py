"""Massive.com (APIBricks) provider implementation"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_provider import BaseProvider
from core.models import OHLCV, Price


class MassiveProvider(BaseProvider):
    """Massive.com (APIBricks) API provider for comprehensive financial data
    
    API Key: PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE
    Base URL: https://api.massive.com
    Documentation: https://api.massive.com/docs
    
    Available endpoints:
    - /v3/reference/dividends - Dividend records
    - /v3/reference/splits - Stock splits
    - /v3/quotes - Real-time quotes
    - /v3/trades - Trade data
    - /v3/aggregates - OHLCV aggregates
    """

    def __init__(self, api_key: str = "PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE"):
        super().__init__(
            name="massive",
            base_url="https://api.massive.com",
            timeout=20
        )
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

    async def _make_authenticated_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make authenticated request to Massive API"""
        if not self.circuit_breaker.can_attempt():
            raise Exception(f"Circuit breaker open for {self.name}")

        client = await self.get_client()
        url = f"{self.base_url}{endpoint}"
        
        # Add API key to params (alternative to header)
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        
        start_time = time.time()

        try:
            response = await client.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()

            self.last_latency = int((time.time() - start_time) * 1000)
            self.last_check = datetime.now()
            self.last_error = None
            self.circuit_breaker.record_success()

            return response.json()

        except Exception as e:
            self.last_error = str(e)
            self.circuit_breaker.record_failure()
            raise

    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int) -> List[OHLCV]:
        """Fetch OHLCV aggregates data from Massive API
        
        Args:
            symbol: Stock ticker (e.g., AAPL, TSLA) or crypto symbol
            interval: Time interval (1, 5, 15, 30, 60 for minutes; D for day; W for week)
            limit: Number of candles to fetch
        """
        # Convert interval format
        interval_map = {
            "1m": "1",
            "5m": "5",
            "15m": "15",
            "1h": "60",
            "4h": "240",
            "1d": "D",
            "1w": "W",
        }
        massive_interval = interval_map.get(interval, "60")
        
        endpoint = f"/v3/aggregates/ticker/{symbol}/range/{massive_interval}"
        
        # Calculate date range (last 30 days for example)
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "from": from_date,
            "to": to_date,
            "limit": limit
        }
        
        try:
            data = await self._make_authenticated_request(endpoint, params)
            
            if "results" not in data:
                raise Exception("No results in Massive API response")
            
            ohlcv_list = []
            for candle in data["results"]:
                ohlcv_list.append(OHLCV(
                    timestamp=candle.get("t", 0),  # Unix timestamp in ms
                    open=float(candle.get("o", 0)),
                    high=float(candle.get("h", 0)),
                    low=float(candle.get("l", 0)),
                    close=float(candle.get("c", 0)),
                    volume=float(candle.get("v", 0))
                ))
            
            return ohlcv_list[:limit]
        
        except Exception as e:
            self.last_error = f"Massive OHLCV fetch error: {str(e)}"
            raise

    async def fetch_prices(self, symbols: List[str]) -> List[Price]:
        """Fetch current quotes from Massive API"""
        prices = []
        
        for symbol in symbols:
            try:
                endpoint = f"/v3/quotes/{symbol}"
                
                data = await self._make_authenticated_request(endpoint)
                
                if "results" not in data or not data["results"]:
                    continue
                
                quote = data["results"][0]
                
                # Extract price data
                last_price = float(quote.get("p", 0))  # Last price
                
                prices.append(Price(
                    symbol=symbol.upper(),
                    name=symbol.upper(),
                    price=last_price,
                    priceUsd=last_price,
                    change24h=None,  # Calculate if previous close available
                    volume24h=float(quote.get("s", 0)),  # Size
                    marketCap=None,
                    lastUpdate=datetime.fromtimestamp(quote.get("t", 0) / 1000).isoformat()
                ))
                
            except Exception as e:
                self.last_error = f"Massive price fetch error for {symbol}: {str(e)}"
                continue
        
        return prices

    async def fetch_dividends(self, ticker: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch dividend records
        
        Example response:
        {
          "results": [{
            "ticker": "AAPL",
            "cash_amount": 0.25,
            "currency": "USD",
            "declaration_date": "2024-10-31",
            "ex_dividend_date": "2024-11-08",
            "pay_date": "2024-11-14",
            "record_date": "2024-11-11",
            "dividend_type": "CD",
            "frequency": 4
          }]
        }
        """
        endpoint = "/v3/reference/dividends"
        params = {"limit": limit}
        
        if ticker:
            params["ticker"] = ticker
        
        try:
            data = await self._make_authenticated_request(endpoint, params)
            
            if "results" in data:
                return data["results"]
            return []
        
        except Exception as e:
            self.last_error = f"Massive dividends fetch error: {str(e)}"
            raise

    async def fetch_splits(self, ticker: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch stock split records"""
        endpoint = "/v3/reference/splits"
        params = {"limit": limit}
        
        if ticker:
            params["ticker"] = ticker
        
        try:
            data = await self._make_authenticated_request(endpoint, params)
            
            if "results" in data:
                return data["results"]
            return []
        
        except Exception as e:
            self.last_error = f"Massive splits fetch error: {str(e)}"
            raise

    async def fetch_trades(self, ticker: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent trades for a ticker"""
        endpoint = f"/v3/trades/{ticker}"
        params = {"limit": limit}
        
        try:
            data = await self._make_authenticated_request(endpoint, params)
            
            if "results" in data:
                return data["results"]
            return []
        
        except Exception as e:
            self.last_error = f"Massive trades fetch error: {str(e)}"
            raise

    async def fetch_ticker_details(self, ticker: str) -> Dict[str, Any]:
        """Fetch detailed information about a ticker"""
        endpoint = f"/v3/reference/tickers/{ticker}"
        
        try:
            data = await self._make_authenticated_request(endpoint)
            
            if "results" in data:
                return data["results"]
            return data
        
        except Exception as e:
            self.last_error = f"Massive ticker details error: {str(e)}"
            raise

    async def fetch_market_status(self) -> Dict[str, Any]:
        """Fetch current market status"""
        endpoint = "/v3/marketstatus/now"
        
        try:
            data = await self._make_authenticated_request(endpoint)
            return data
        
        except Exception as e:
            self.last_error = f"Massive market status error: {str(e)}"
            raise


# Import time for the provider
import time
from datetime import timedelta

#!/usr/bin/env python3
"""
CryptoCompare API Client - Comprehensive crypto data with API key authentication
Official API: https://min-api.cryptocompare.com/
"""

import httpx
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# CryptoCompare API Key from .env.example
CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_KEY", "e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f")


class CryptoCompareClient:
    """
    CryptoCompare API Client - Market data, news, social stats, and more
    """
    
    def __init__(self, api_key: str = CRYPTOCOMPARE_API_KEY):
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.api_key = api_key
        self.timeout = 15.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["authorization"] = f"Apikey {self.api_key}"
        return headers
    
    async def get_price(self, symbols: List[str], currency: str = "USD") -> Dict[str, Any]:
        """
        Get current prices for multiple symbols
        
        Args:
            symbols: List of cryptocurrency symbols (e.g., ["BTC", "ETH"])
            currency: Target currency (default: USD)
        
        Returns:
            Price data from CryptoCompare
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                fsyms = ",".join([s.upper() for s in symbols])
                
                response = await client.get(
                    f"{self.base_url}/pricemultifull",
                    params={
                        "fsyms": fsyms,
                        "tsyms": currency
                    },
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                result = {
                    "data": data.get("RAW", {}),
                    "display": data.get("DISPLAY", {}),
                    "source": "CryptoCompare",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info(f"✅ CryptoCompare: Fetched prices for {len(symbols)} symbols")
                return result
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ CryptoCompare API HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ CryptoCompare API failed: {e}")
            raise
    
    async def get_ohlcv(
        self,
        symbol: str,
        currency: str = "USD",
        limit: int = 100,
        aggregate: int = 1
    ) -> Dict[str, Any]:
        """
        Get OHLCV (candlestick) data
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC")
            currency: Target currency (default: USD)
            limit: Number of data points (max 2000)
            aggregate: Data aggregation (e.g., 1 = 1 hour, 24 = 1 day)
        
        Returns:
            OHLCV data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v2/histohour",
                    params={
                        "fsym": symbol.upper(),
                        "tsym": currency.upper(),
                        "limit": limit,
                        "aggregate": aggregate
                    },
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("Response") == "Success":
                    logger.info(f"✅ CryptoCompare: Fetched OHLCV for {symbol}")
                    return {
                        "symbol": symbol.upper(),
                        "data": data.get("Data", {}).get("Data", []),
                        "source": "CryptoCompare",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise Exception(f"CryptoCompare API error: {data.get('Message', 'Unknown error')}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ CryptoCompare OHLCV HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ CryptoCompare OHLCV failed: {e}")
            raise
    
    async def get_news(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get latest crypto news from CryptoCompare
        
        Args:
            limit: Number of news articles (max 200)
        
        Returns:
            News articles
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v2/news/",
                    params={
                        "lang": "EN",
                        "limit": limit
                    },
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("Type") == 100:  # Success
                    articles = data.get("Data", [])
                    logger.info(f"✅ CryptoCompare: Fetched {len(articles)} news articles")
                    return {
                        "articles": articles,
                        "count": len(articles),
                        "source": "CryptoCompare",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise Exception(f"CryptoCompare news error: {data.get('Message', 'Unknown error')}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ CryptoCompare news HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ CryptoCompare news failed: {e}")
            raise
    
    async def get_social_stats(self, coin_id: int) -> Dict[str, Any]:
        """
        Get social statistics for a cryptocurrency
        
        Args:
            coin_id: CryptoCompare coin ID
        
        Returns:
            Social stats (Twitter, Reddit, etc.)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/social/coin/latest",
                    params={"coinId": coin_id},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("Response") == "Success":
                    logger.info(f"✅ CryptoCompare: Fetched social stats for coin {coin_id}")
                    return {
                        "data": data.get("Data", {}),
                        "source": "CryptoCompare",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise Exception(f"CryptoCompare social stats error: {data.get('Message', 'Unknown error')}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ CryptoCompare social stats HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ CryptoCompare social stats failed: {e}")
            raise
    
    async def get_top_exchanges_by_volume(self, symbol: str, currency: str = "USD", limit: int = 10) -> Dict[str, Any]:
        """
        Get top exchanges by trading volume for a symbol
        
        Args:
            symbol: Cryptocurrency symbol
            currency: Target currency
            limit: Number of exchanges to return
        
        Returns:
            Top exchanges data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/top/exchanges/full",
                    params={
                        "fsym": symbol.upper(),
                        "tsym": currency.upper(),
                        "limit": limit
                    },
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("Response") == "Success":
                    exchanges = data.get("Data", {}).get("Exchanges", [])
                    logger.info(f"✅ CryptoCompare: Fetched top {len(exchanges)} exchanges for {symbol}")
                    return {
                        "exchanges": exchanges,
                        "symbol": symbol.upper(),
                        "source": "CryptoCompare",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise Exception(f"CryptoCompare exchanges error: {data.get('Message', 'Unknown error')}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ CryptoCompare exchanges HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ CryptoCompare exchanges failed: {e}")
            raise


# Global instance
cryptocompare_client = CryptoCompareClient()


# Standalone functions for compatibility
async def fetch_cryptocompare_price(symbols: List[str]) -> Dict[str, Any]:
    """Get prices from CryptoCompare"""
    return await cryptocompare_client.get_price(symbols)


async def fetch_cryptocompare_news(limit: int = 50) -> Dict[str, Any]:
    """Get news from CryptoCompare"""
    return await cryptocompare_client.get_news(limit)


async def fetch_cryptocompare_ohlcv(symbol: str, limit: int = 100) -> Dict[str, Any]:
    """Get OHLCV data from CryptoCompare"""
    return await cryptocompare_client.get_ohlcv(symbol, limit=limit)


__all__ = [
    "CryptoCompareClient",
    "cryptocompare_client",
    "fetch_cryptocompare_price",
    "fetch_cryptocompare_news",
    "fetch_cryptocompare_ohlcv"
]

#!/usr/bin/env python3
"""
HuggingFace Crypto Resources API Client
کلاینت برای API منابع کریپتو در HuggingFace Space

این کلاینت برای دسترسی به API منابع کریپتو استفاده می‌شود:
https://really-amin-crypto-api-clean.hf.space

API Endpoints:
- /api/coins/top - برترین ارزها
- /api/trending - ارزهای ترند
- /api/market - خلاصه بازار
- /api/sentiment/global - شاخص ترس و طمع
- /api/resources/stats - آمار منابع
- /api/categories - لیست دسته‌بندی‌ها
- /api/resources/category/{category} - منابع یک دسته
"""

import asyncio
import aiohttp
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HFCryptoAPIClient:
    """
    Client for HuggingFace Crypto Resources API
    کلاینت API منابع کریپتو
    """
    
    BASE_URL = "https://really-amin-crypto-api-clean.hf.space"
    
    def __init__(self, timeout: int = 15):
        """
        Initialize client
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self._session = None
    
    # ===== SYNC METHODS =====
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return self._get("/health")
    
    def get_top_coins(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get top coins by market cap
        دریافت برترین ارزها
        
        Args:
            limit: Number of coins to return (default: 50)
        """
        return self._get("/api/coins/top", params={"limit": limit})
    
    def get_trending(self) -> Dict[str, Any]:
        """
        Get trending coins
        دریافت ارزهای ترند
        """
        return self._get("/api/trending")
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        Get global market overview
        خلاصه کلی بازار
        """
        return self._get("/api/market")
    
    def get_global_sentiment(self, timeframe: str = "1D") -> Dict[str, Any]:
        """
        Get Fear & Greed Index
        شاخص ترس و طمع
        
        Args:
            timeframe: Timeframe (default: "1D")
        """
        return self._get("/api/sentiment/global", params={"timeframe": timeframe})
    
    def get_asset_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get sentiment for specific asset
        احساسات یک ارز خاص
        
        Args:
            symbol: Asset symbol (e.g., "BTC", "ETH")
        """
        return self._get(f"/api/sentiment/asset/{symbol}")
    
    def get_resources_stats(self) -> Dict[str, Any]:
        """
        Get resources database statistics
        آمار منابع
        """
        return self._get("/api/resources/stats")
    
    def get_categories(self) -> Dict[str, Any]:
        """
        Get list of resource categories
        لیست دسته‌بندی‌ها
        """
        return self._get("/api/categories")
    
    def get_resources_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get resources for a specific category
        منابع یک دسته خاص
        
        Args:
            category: Category name (e.g., "rpc_nodes", "market_data_apis")
        """
        return self._get(f"/api/resources/category/{category}")
    
    def get_all_resources(self) -> Dict[str, Any]:
        """
        Get all resources list
        لیست همه منابع
        """
        return self._get("/api/resources/list")
    
    def get_providers(self) -> Dict[str, Any]:
        """
        Get data providers status
        وضعیت provider ها
        """
        return self._get("/api/providers")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status
        وضعیت سیستم
        """
        return self._get("/api/status")
    
    def get_news(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get crypto news
        آخرین اخبار
        
        Args:
            limit: Number of articles to return
        """
        return self._get("/api/news", params={"limit": limit})
    
    def get_ohlcv(self, symbol: str = "BTC", interval: str = "1h", limit: int = 100) -> Dict[str, Any]:
        """
        Get OHLCV data
        داده‌های OHLCV
        
        Args:
            symbol: Asset symbol
            interval: Time interval
            limit: Number of candles
        """
        return self._get("/api/ohlcv", params={
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        })
    
    def _get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make GET request"""
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return {"error": str(e), "success": False}
    
    # ===== ASYNC METHODS =====
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session
    
    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _async_get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make async GET request"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}{endpoint}"
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Async request failed for {endpoint}: {e}")
            return {"error": str(e), "success": False}
    
    async def async_get_top_coins(self, limit: int = 50) -> Dict[str, Any]:
        """Async: Get top coins"""
        return await self._async_get("/api/coins/top", params={"limit": limit})
    
    async def async_get_trending(self) -> Dict[str, Any]:
        """Async: Get trending coins"""
        return await self._async_get("/api/trending")
    
    async def async_get_market_overview(self) -> Dict[str, Any]:
        """Async: Get market overview"""
        return await self._async_get("/api/market")
    
    async def async_get_global_sentiment(self) -> Dict[str, Any]:
        """Async: Get global sentiment"""
        return await self._async_get("/api/sentiment/global")
    
    async def async_get_resources_by_category(self, category: str) -> Dict[str, Any]:
        """Async: Get resources by category"""
        return await self._async_get(f"/api/resources/category/{category}")
    
    # ===== UTILITY METHODS =====
    
    def get_rpc_nodes(self) -> List[Dict[str, Any]]:
        """Get all RPC node resources"""
        data = self.get_resources_by_category("rpc_nodes")
        return data.get("resources", [])
    
    def get_market_data_apis(self) -> List[Dict[str, Any]]:
        """Get all market data API resources"""
        data = self.get_resources_by_category("market_data_apis")
        return data.get("resources", [])
    
    def get_sentiment_apis(self) -> List[Dict[str, Any]]:
        """Get all sentiment API resources"""
        data = self.get_resources_by_category("sentiment_apis")
        return data.get("resources", [])
    
    def get_block_explorers(self) -> List[Dict[str, Any]]:
        """Get all block explorer resources"""
        data = self.get_resources_by_category("block_explorers")
        return data.get("resources", [])
    
    def get_whale_tracking_apis(self) -> List[Dict[str, Any]]:
        """Get all whale tracking API resources"""
        data = self.get_resources_by_category("whale_tracking_apis")
        return data.get("resources", [])
    
    def get_hf_resources(self) -> List[Dict[str, Any]]:
        """Get all HuggingFace resources (models/datasets)"""
        data = self.get_resources_by_category("hf_resources")
        return data.get("resources", [])
    
    def get_fear_greed_index(self) -> int:
        """
        Get current Fear & Greed Index value
        
        Returns:
            int: Fear & Greed Index (0-100)
        """
        data = self.get_global_sentiment()
        return data.get("fear_greed_index", 50)
    
    def get_btc_price(self) -> float:
        """
        Get current Bitcoin price
        
        Returns:
            float: BTC price in USD
        """
        data = self.get_top_coins(limit=1)
        coins = data.get("coins", [])
        if coins:
            return coins[0].get("current_price", 0)
        return 0
    
    def get_total_market_cap(self) -> float:
        """
        Get total crypto market cap
        
        Returns:
            float: Total market cap in USD
        """
        data = self.get_market_overview()
        return data.get("total_market_cap", 0)


# ===== CONVENIENCE FUNCTIONS =====

def get_hf_crypto_client() -> HFCryptoAPIClient:
    """Get a configured HF Crypto API client instance"""
    return HFCryptoAPIClient(timeout=15)


# ===== TEST =====

if __name__ == "__main__":
    # Test the client
    client = HFCryptoAPIClient()
    
    print("=" * 60)
    print("Testing HuggingFace Crypto Resources API Client")
    print("=" * 60)
    
    # Health check
    print("\n1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   Resources loaded: {health.get('resources_loaded', False)}")
    
    # Top coins
    print("\n2. Top 3 Coins:")
    coins = client.get_top_coins(limit=3)
    for coin in coins.get("coins", []):
        print(f"   {coin['name']}: ${coin['current_price']:,.2f}")
    
    # Market overview
    print("\n3. Market Overview:")
    market = client.get_market_overview()
    print(f"   Total Market Cap: ${market.get('total_market_cap', 0):,.0f}")
    print(f"   BTC Dominance: {market.get('market_cap_percentage', {}).get('btc', 0):.2f}%")
    
    # Sentiment
    print("\n4. Fear & Greed Index:")
    sentiment = client.get_global_sentiment()
    print(f"   Index: {sentiment.get('fear_greed_index', 'N/A')}")
    print(f"   Sentiment: {sentiment.get('sentiment', 'N/A')}")
    
    # Resources stats
    print("\n5. Resources Stats:")
    stats = client.get_resources_stats()
    print(f"   Total Resources: {stats.get('total_resources', 0)}")
    print(f"   Total Categories: {stats.get('total_categories', 0)}")
    
    # Trending
    print("\n6. Trending Coins:")
    trending = client.get_trending()
    for i, coin in enumerate(trending.get("coins", [])[:5], 1):
        print(f"   {i}. {coin['name']} ({coin['symbol']})")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

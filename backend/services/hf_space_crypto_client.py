#!/usr/bin/env python3
"""
HuggingFace Space Crypto Resources API Client Service
سرویس کلاینت برای API منابع کریپتو در HuggingFace Space

This service provides access to the external HF Space Crypto Resources API:
https://really-amin-crypto-api-clean.hf.space

Features:
- Market data (top coins, trending)
- Global market overview
- Fear & Greed Index
- Resource database (281 resources in 12 categories)
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from functools import lru_cache

logger = logging.getLogger(__name__)

# Base URL for the HF Space API
HF_CRYPTO_API_BASE_URL = "https://really-amin-crypto-api-clean.hf.space"

# Cache for resources (they don't change frequently)
_resources_cache: Dict[str, Any] = {}
_cache_timestamp: Optional[datetime] = None
CACHE_TTL_SECONDS = 300  # 5 minutes


class HFSpaceCryptoService:
    """
    Service for accessing HuggingFace Space Crypto Resources API
    Follows project patterns with proper error handling and logging
    """
    
    def __init__(self, timeout: int = 15):
        self.base_url = HF_CRYPTO_API_BASE_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def _request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """
        Make async request to HF Space API with proper error handling
        
        Returns standardized response format matching project patterns
        """
        provider = "HFSpaceCryptoAPI"
        start_time = datetime.now(timezone.utc)
        
        try:
            client = await self._get_client()
            url = f"{self.base_url}{endpoint}"
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            response_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            logger.info(f"✅ {provider} - {endpoint} - {response_time_ms:.0f}ms")
            
            return {
                "provider": provider,
                "endpoint": endpoint,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "response_time_ms": response_time_ms,
                "success": True,
                "error": None
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ {provider} - {endpoint} - HTTP {e.response.status_code}")
            return {
                "provider": provider,
                "endpoint": endpoint,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "error_type": "http_error"
            }
        except httpx.TimeoutException:
            logger.error(f"❌ {provider} - {endpoint} - Timeout")
            return {
                "provider": provider,
                "endpoint": endpoint,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": "Request timeout",
                "error_type": "timeout"
            }
        except Exception as e:
            logger.error(f"❌ {provider} - {endpoint} - {str(e)}")
            return {
                "provider": provider,
                "endpoint": endpoint,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(e),
                "error_type": "exception"
            }
    
    # ===== MARKET DATA =====
    
    async def get_top_coins(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get top coins by market cap
        دریافت برترین ارزها بر اساس مارکت کپ
        """
        return await self._request("/api/coins/top", params={"limit": limit})
    
    async def get_trending(self) -> Dict[str, Any]:
        """
        Get trending coins
        دریافت ارزهای ترند
        """
        return await self._request("/api/trending")
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Get global market overview
        خلاصه کلی بازار
        """
        return await self._request("/api/market")
    
    # ===== SENTIMENT =====
    
    async def get_global_sentiment(self, timeframe: str = "1D") -> Dict[str, Any]:
        """
        Get Fear & Greed Index
        شاخص ترس و طمع
        """
        return await self._request("/api/sentiment/global", params={"timeframe": timeframe})
    
    async def get_asset_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get sentiment for specific asset
        احساسات یک ارز خاص
        """
        return await self._request(f"/api/sentiment/asset/{symbol}")
    
    # ===== RESOURCES DATABASE =====
    
    async def get_resources_stats(self) -> Dict[str, Any]:
        """
        Get resources database statistics
        آمار منابع
        """
        return await self._request("/api/resources/stats")
    
    async def get_categories(self) -> Dict[str, Any]:
        """
        Get list of resource categories
        لیست دسته‌بندی‌ها
        """
        return await self._request("/api/categories")
    
    async def get_resources_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get resources for a specific category
        منابع یک دسته خاص
        
        Categories: rpc_nodes, block_explorers, market_data_apis, news_apis,
                   sentiment_apis, onchain_analytics_apis, whale_tracking_apis,
                   hf_resources, free_http_endpoints, cors_proxies
        """
        return await self._request(f"/api/resources/category/{category}")
    
    async def get_all_resources(self) -> Dict[str, Any]:
        """
        Get all resources list
        لیست همه منابع
        """
        return await self._request("/api/resources/list")
    
    # ===== SYSTEM STATUS =====
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return await self._request("/health")
    
    async def get_providers_status(self) -> Dict[str, Any]:
        """Get data providers status"""
        return await self._request("/api/providers")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return await self._request("/api/status")
    
    # ===== CONVENIENCE METHODS =====
    
    async def get_fear_greed_index(self) -> int:
        """
        Get current Fear & Greed Index value
        
        Returns:
            int: Fear & Greed Index (0-100)
        """
        result = await self.get_global_sentiment()
        if result["success"] and result["data"]:
            return result["data"].get("fear_greed_index", 50)
        return 50  # Default neutral
    
    async def get_btc_price(self) -> float:
        """
        Get current Bitcoin price
        
        Returns:
            float: BTC price in USD
        """
        result = await self.get_top_coins(limit=1)
        if result["success"] and result["data"]:
            coins = result["data"].get("coins", [])
            if coins:
                return coins[0].get("current_price", 0)
        return 0
    
    async def get_total_market_cap(self) -> float:
        """
        Get total crypto market cap
        
        Returns:
            float: Total market cap in USD
        """
        result = await self.get_market_overview()
        if result["success"] and result["data"]:
            return result["data"].get("total_market_cap", 0)
        return 0


# ===== SINGLETON INSTANCE =====

_service_instance: Optional[HFSpaceCryptoService] = None


def get_hf_space_crypto_service() -> HFSpaceCryptoService:
    """Get singleton instance of HF Space Crypto Service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = HFSpaceCryptoService()
    return _service_instance


# ===== STANDALONE FUNCTIONS (for collectors compatibility) =====

async def fetch_hf_space_top_coins(limit: int = 50) -> Dict[str, Any]:
    """Fetch top coins from HF Space API"""
    service = get_hf_space_crypto_service()
    return await service.get_top_coins(limit)


async def fetch_hf_space_trending() -> Dict[str, Any]:
    """Fetch trending coins from HF Space API"""
    service = get_hf_space_crypto_service()
    return await service.get_trending()


async def fetch_hf_space_market_overview() -> Dict[str, Any]:
    """Fetch market overview from HF Space API"""
    service = get_hf_space_crypto_service()
    return await service.get_market_overview()


async def fetch_hf_space_sentiment() -> Dict[str, Any]:
    """Fetch global sentiment from HF Space API"""
    service = get_hf_space_crypto_service()
    return await service.get_global_sentiment()


async def fetch_hf_space_resources(category: Optional[str] = None) -> Dict[str, Any]:
    """Fetch resources from HF Space API"""
    service = get_hf_space_crypto_service()
    if category:
        return await service.get_resources_by_category(category)
    return await service.get_resources_stats()


# ===== TEST =====

if __name__ == "__main__":
    async def main():
        service = get_hf_space_crypto_service()
        
        print("=" * 60)
        print("Testing HF Space Crypto Service")
        print("=" * 60)
        
        # Health check
        print("\n1. Health Check:")
        result = await service.health_check()
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Status: {result['data'].get('status')}")
        
        # Top coins
        print("\n2. Top 3 Coins:")
        result = await service.get_top_coins(limit=3)
        if result['success']:
            for coin in result['data'].get('coins', []):
                print(f"   {coin['name']}: ${coin['current_price']:,.2f}")
        
        # Sentiment
        print("\n3. Fear & Greed Index:")
        fgi = await service.get_fear_greed_index()
        print(f"   Index: {fgi}")
        
        # Resources
        print("\n4. Resources Stats:")
        result = await service.get_resources_stats()
        if result['success']:
            print(f"   Total: {result['data'].get('total_resources')}")
            print(f"   Categories: {result['data'].get('total_categories')}")
        
        await service.close()
        print("\n" + "=" * 60)
        print("Tests completed!")
    
    asyncio.run(main())

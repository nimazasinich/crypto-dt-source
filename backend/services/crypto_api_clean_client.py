#!/usr/bin/env python3
"""
Crypto API Clean Client - Integration with HuggingFace Space
https://really-amin-crypto-api-clean-fixed.hf.space

Provides access to 281+ cryptocurrency resources across 12 categories:
- RPC Nodes (24)
- Block Explorers (33)
- Market Data APIs (33)
- News APIs (17)
- Sentiment APIs (14)
- On-chain Analytics APIs (14)
- Whale Tracking APIs (10)
- HuggingFace Resources (9)
- Free HTTP Endpoints (13)
- Local Backend Routes (106)
- CORS Proxies (7)
- Community Sentiment APIs (1)
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from functools import lru_cache

logger = logging.getLogger(__name__)

# Base URL for the Crypto API Clean HF Space
CRYPTO_API_CLEAN_BASE_URL = "https://really-amin-crypto-api-clean-fixed.hf.space"

# Cache for resources (they don't change frequently)
_resources_cache: Dict[str, Any] = {}
_cache_timestamp: Optional[datetime] = None
CACHE_TTL_SECONDS = 300  # 5 minutes


class CryptoAPICleanService:
    """
    Service for accessing Crypto API Clean HuggingFace Space
    Provides comprehensive cryptocurrency resource database access
    """
    
    def __init__(self, timeout: int = 15):
        self.base_url = CRYPTO_API_CLEAN_BASE_URL
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
        Make async request to Crypto API Clean with proper error handling
        
        Returns standardized response format matching project patterns
        """
        provider = "CryptoAPIClean"
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
    
    # ===== RESOURCES DATABASE =====
    
    async def get_resources_stats(self) -> Dict[str, Any]:
        """
        Get resources database statistics
        Returns: total_resources, total_categories, category breakdown
        """
        return await self._request("/api/resources/stats")
    
    async def get_all_resources(self) -> Dict[str, Any]:
        """
        Get complete list of all 281+ resources
        Returns: Full resource database
        """
        return await self._request("/api/resources/list")
    
    async def get_categories(self) -> Dict[str, Any]:
        """
        Get list of all 12 resource categories
        Categories: rpc_nodes, block_explorers, market_data_apis, news_apis,
                   sentiment_apis, onchain_analytics_apis, whale_tracking_apis,
                   hf_resources, free_http_endpoints, cors_proxies, 
                   community_sentiment_apis, local_backend_routes
        """
        return await self._request("/api/categories")
    
    async def get_resources_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get resources for a specific category
        
        Args:
            category: Category name (e.g., 'market_data_apis', 'sentiment_apis')
        """
        return await self._request(f"/api/resources/category/{category}")
    
    # ===== SYSTEM STATUS =====
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return await self._request("/health")
    
    # ===== CONVENIENCE METHODS =====
    
    async def get_total_resources_count(self) -> int:
        """
        Get total number of resources available
        
        Returns:
            int: Total resource count
        """
        result = await self.get_resources_stats()
        if result["success"] and result["data"]:
            return result["data"].get("total_resources", 0)
        return 0
    
    async def get_category_summary(self) -> Dict[str, int]:
        """
        Get summary of resources per category
        
        Returns:
            Dict mapping category names to resource counts
        """
        result = await self.get_resources_stats()
        if result["success"] and result["data"]:
            return result["data"].get("categories", {})
        return {}
    
    async def get_market_data_providers(self) -> List[Dict[str, Any]]:
        """
        Get all market data API providers (33 resources)
        """
        result = await self.get_resources_by_category("market_data_apis")
        if result["success"] and result["data"]:
            return result["data"].get("resources", [])
        return []
    
    async def get_sentiment_providers(self) -> List[Dict[str, Any]]:
        """
        Get all sentiment API providers (14 resources)
        """
        result = await self.get_resources_by_category("sentiment_apis")
        if result["success"] and result["data"]:
            return result["data"].get("resources", [])
        return []
    
    async def get_rpc_nodes(self) -> List[Dict[str, Any]]:
        """
        Get all RPC node providers (24 resources)
        """
        result = await self.get_resources_by_category("rpc_nodes")
        if result["success"] and result["data"]:
            return result["data"].get("resources", [])
        return []
    
    async def get_block_explorers(self) -> List[Dict[str, Any]]:
        """
        Get all block explorer APIs (33 resources)
        """
        result = await self.get_resources_by_category("block_explorers")
        if result["success"] and result["data"]:
            return result["data"].get("resources", [])
        return []


# ===== SINGLETON INSTANCE =====

_service_instance: Optional[CryptoAPICleanService] = None


def get_crypto_api_clean_service() -> CryptoAPICleanService:
    """Get singleton instance of Crypto API Clean Service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = CryptoAPICleanService()
    return _service_instance


# ===== STANDALONE FUNCTIONS (for collectors compatibility) =====

async def fetch_crypto_api_clean_stats() -> Dict[str, Any]:
    """Fetch resource statistics from Crypto API Clean"""
    service = get_crypto_api_clean_service()
    return await service.get_resources_stats()


async def fetch_crypto_api_clean_resources(category: Optional[str] = None) -> Dict[str, Any]:
    """Fetch resources from Crypto API Clean"""
    service = get_crypto_api_clean_service()
    if category:
        return await service.get_resources_by_category(category)
    return await service.get_all_resources()


# ===== TEST =====

if __name__ == "__main__":
    async def main():
        service = get_crypto_api_clean_service()
        
        print("=" * 70)
        print("Testing Crypto API Clean Service")
        print("=" * 70)
        
        # Health check
        print("\n1. Health Check:")
        result = await service.health_check()
        print(f"   Success: {result['success']}")
        
        # Resource stats
        print("\n2. Resource Statistics:")
        result = await service.get_resources_stats()
        if result['success']:
            data = result['data']
            print(f"   Total Resources: {data.get('total_resources')}")
            print(f"   Total Categories: {data.get('total_categories')}")
            print(f"   Categories:")
            for cat, count in data.get('categories', {}).items():
                print(f"     - {cat}: {count}")
        
        # Category summary
        print("\n3. Market Data Providers:")
        providers = await service.get_market_data_providers()
        print(f"   Found {len(providers)} providers")
        
        # Sentiment providers
        print("\n4. Sentiment Providers:")
        providers = await service.get_sentiment_providers()
        print(f"   Found {len(providers)} providers")
        
        await service.close()
        print("\n" + "=" * 70)
        print("Tests completed!")
    
    asyncio.run(main())

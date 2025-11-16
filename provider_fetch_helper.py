#!/usr/bin/env python3
"""
Provider Fetch Helper - Unified provider fetching with failover and circuit breakers
Implements proper provider selection, retry logic, and error handling
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from fastapi import HTTPException
import logging

from provider_manager import ProviderManager, Provider, ProviderStatus

logger = logging.getLogger(__name__)


class ProviderFetchError(Exception):
    """Custom exception for provider fetch failures"""
    def __init__(self, message: str, provider_id: str, error_type: str = "unknown"):
        self.message = message
        self.provider_id = provider_id
        self.error_type = error_type
        super().__init__(self.message)


class ProviderFetchHelper:
    """
    Helper class for fetching data from providers with automatic failover,
    circuit breakers, and metrics tracking
    """
    
    def __init__(self, provider_manager: ProviderManager):
        """
        Initialize the fetch helper
        
        Args:
            provider_manager: ProviderManager instance
        """
        self.manager = provider_manager
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
    async def fetch_from_provider(
        self,
        provider: Provider,
        endpoint_key: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Fetch data from a single provider
        
        Args:
            provider: Provider instance
            endpoint_key: Key for endpoint in provider.endpoints
            params: Query parameters
            headers: HTTP headers
            
        Returns:
            Tuple of (success: bool, data: Optional[Dict], error: Optional[str])
        """
        if not provider.is_available:
            return False, None, f"Provider {provider.name} is not available"
            
        if endpoint_key not in provider.endpoints:
            return False, None, f"Endpoint {endpoint_key} not found in provider {provider.name}"
        
        endpoint = provider.endpoints[endpoint_key]
        url = f"{provider.base_url}{endpoint}"
        
        start_time = time.time()
        
        try:
            await self.manager.init_session()
            
            async with self.manager.session.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            ) as response:
                response_time = (time.time() - start_time) * 1000  # ms
                
                if response.status == 200:
                    data = await response.json()
                    provider.record_success(response_time)
                    logger.info(
                        f"✓ {provider.name} - {endpoint_key} - "
                        f"{response_time:.0f}ms - Success"
                    )
                    return True, data, None
                    
                elif response.status == 429:
                    # Rate limited
                    provider.status = ProviderStatus.RATE_LIMITED
                    error_msg = f"Rate limited (429)"
                    provider.record_failure(error_msg)
                    return False, None, error_msg
                    
                else:
                    error_msg = f"HTTP {response.status}"
                    provider.record_failure(error_msg)
                    return False, None, error_msg
                    
        except asyncio.TimeoutError:
            error_msg = "Request timeout"
            provider.record_failure(error_msg)
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            provider.record_failure(error_msg)
            return False, None, error_msg
    
    async def fetch_with_failover(
        self,
        pool_id: str,
        endpoint_key: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_providers: int = 3
    ) -> Dict[str, Any]:
        """
        Fetch data with automatic failover to next provider
        
        Args:
            pool_id: ID of the provider pool to use
            endpoint_key: Endpoint key to call
            params: Query parameters
            headers: HTTP headers
            max_providers: Maximum number of providers to try
            
        Returns:
            Response data dict
            
        Raises:
            HTTPException: With status 503 if all providers fail
        """
        pool = self.manager.get_pool(pool_id)
        
        if not pool:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service Unavailable",
                    "message": f"Provider pool '{pool_id}' not found",
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }
            )
        
        if not pool.enabled:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service Unavailable",
                    "message": f"Provider pool '{pool_id}' is disabled",
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }
            )
        
        tried_providers = []
        errors = []
        
        for attempt in range(max_providers):
            provider = pool.get_next_provider()
            
            if not provider:
                break
                
            # Avoid retrying the same provider
            if provider.provider_id in tried_providers:
                continue
                
            tried_providers.append(provider.provider_id)
            
            logger.info(
                f"Attempt {attempt + 1}/{max_providers}: "
                f"Trying provider {provider.name}"
            )
            
            success, data, error = await self.fetch_from_provider(
                provider,
                endpoint_key,
                params,
                headers
            )
            
            if success:
                return {
                    "success": True,
                    "data": data,
                    "provider": provider.name,
                    "provider_id": provider.provider_id,
                    "timestamp": datetime.now().isoformat(),
                    "attempts": attempt + 1
                }
            
            errors.append({
                "provider": provider.name,
                "provider_id": provider.provider_id,
                "error": error
            })
            
            # Short delay before next provider
            if attempt < max_providers - 1:
                await asyncio.sleep(self.retry_delay)
        
        # All providers failed
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service Unavailable",
                "message": "All providers failed",
                "pool_id": pool_id,
                "endpoint": endpoint_key,
                "attempts": len(tried_providers),
                "errors": errors,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
        )
    
    async def fetch_from_category(
        self,
        category: str,
        endpoint_key: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch data from any provider in a category
        
        Args:
            category: Provider category (e.g., 'market_data', 'sentiment')
            endpoint_key: Endpoint key to call
            params: Query parameters
            headers: HTTP headers
            
        Returns:
            Response data dict
            
        Raises:
            HTTPException: With status 503 if all providers fail
        """
        # Get all providers in category
        providers = [
            p for p in self.manager.providers.values()
            if p.category == category and p.is_available
        ]
        
        if not providers:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service Unavailable",
                    "message": f"No available providers in category '{category}'",
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }
            )
        
        # Sort by priority (highest first)
        providers.sort(key=lambda p: p.priority, reverse=True)
        
        errors = []
        
        for provider in providers[:3]:  # Try top 3
            logger.info(f"Trying provider {provider.name} from category {category}")
            
            success, data, error = await self.fetch_from_provider(
                provider,
                endpoint_key,
                params,
                headers
            )
            
            if success:
                return {
                    "success": True,
                    "data": data,
                    "provider": provider.name,
                    "provider_id": provider.provider_id,
                    "category": category,
                    "timestamp": datetime.now().isoformat()
                }
            
            errors.append({
                "provider": provider.name,
                "error": error
            })
            
            await asyncio.sleep(self.retry_delay)
        
        # All failed
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service Unavailable",
                "message": f"All providers failed in category '{category}'",
                "category": category,
                "endpoint": endpoint_key,
                "errors": errors,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
        )


# Singleton instance
_helper_instance: Optional[ProviderFetchHelper] = None


def get_fetch_helper(provider_manager: ProviderManager) -> ProviderFetchHelper:
    """
    Get or create fetch helper singleton
    
    Args:
        provider_manager: ProviderManager instance
        
    Returns:
        ProviderFetchHelper instance
    """
    global _helper_instance
    
    if _helper_instance is None:
        _helper_instance = ProviderFetchHelper(provider_manager)
    
    return _helper_instance


# Example usage
async def example_usage():
    """Example of how to use ProviderFetchHelper"""
    from provider_manager import ProviderManager
    
    # Initialize manager
    manager = ProviderManager()
    await manager.init_session()
    
    # Get helper
    helper = get_fetch_helper(manager)
    
    try:
        # Fetch market data with failover
        result = await helper.fetch_with_failover(
            pool_id="primary_market_data_pool",
            endpoint_key="coins_markets",
            params={"vs_currency": "usd", "per_page": 10}
        )
        
        print(f"✓ Success: {result['provider']}")
        print(f"  Data: {len(result['data'])} items")
        
    except HTTPException as e:
        print(f"✗ Failed: {e.detail}")
    
    finally:
        await manager.close_session()


if __name__ == "__main__":
    asyncio.run(example_usage())

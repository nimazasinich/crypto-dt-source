#!/usr/bin/env python3
"""
Provider Fetch Helper - Integrated with ProviderManager for automatic failover and retry
Provides simple interface for fetching data with circuit breaker and retry logic
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Import from existing modules
try:
    from provider_manager import ProviderManager
except ImportError:
    ProviderManager = None

logger = logging.getLogger(__name__)


class ProviderFetchHelper:
    """
    Helper class for fetching data from providers with automatic failover
    Integrates with ProviderManager for pool-based rotation
    """
    
    def __init__(self, manager: Optional[ProviderManager] = None):
        """
        Initialize the fetch helper
        
        Args:
            manager: ProviderManager instance (optional, will create if not provided)
        """
        self.manager = manager
        if self.manager is None and ProviderManager is not None:
            try:
                self.manager = ProviderManager()
            except Exception as e:
                logger.warning(f"Could not initialize ProviderManager: {e}")
                self.manager = None
    
    async def fetch_with_fallback(
        self,
        pool_id: Optional[str] = None,
        provider_ids: Optional[List[str]] = None,
        url: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Fetch data with automatic fallback to other providers
        
        Args:
            pool_id: Pool ID to fetch from (e.g., "primary_market_data_pool")
            provider_ids: List of provider IDs to try in order (alternative to pool_id)
            url: Direct URL to fetch (if not using pool/provider system)
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        
        Returns:
            Dict with 'success', 'data', 'provider', 'error' keys
        """
        # If using ProviderManager and pool system
        if self.manager and pool_id:
            return await self._fetch_from_pool(pool_id, max_retries, timeout)
        
        # If using ProviderManager with specific provider IDs
        if self.manager and provider_ids:
            return await self._fetch_from_providers(provider_ids, max_retries, timeout)
        
        # Direct URL fetch (no provider management)
        if url:
            return await self._fetch_direct(url, timeout)
        
        return {
            "success": False,
            "data": None,
            "provider": None,
            "error": "No valid fetch configuration provided"
        }
    
    async def _fetch_from_pool(
        self,
        pool_id: str,
        max_retries: int,
        timeout: int
    ) -> Dict[str, Any]:
        """Fetch from a provider pool with automatic rotation"""
        pool = self.manager.get_pool(pool_id)
        if not pool:
            logger.error(f"Pool not found: {pool_id}")
            return {
                "success": False,
                "data": None,
                "provider": None,
                "error": f"Pool '{pool_id}' not found"
            }
        
        attempts = 0
        last_error = None
        
        while attempts < max_retries:
            attempts += 1
            
            # Get next provider from pool
            provider = pool.get_next_provider()
            if not provider:
                logger.warning(f"No available providers in pool: {pool_id}")
                return {
                    "success": False,
                    "data": None,
                    "provider": None,
                    "error": "No available providers in pool"
                }
            
            # Check circuit breaker
            if provider.circuit_breaker_open:
                logger.info(f"Circuit breaker open for {provider.name}, trying next provider")
                continue
            
            # Attempt fetch
            try:
                logger.info(f"Fetching from {provider.name} (attempt {attempts}/{max_retries})")
                
                # Get endpoint URL
                if not provider.endpoints:
                    logger.warning(f"No endpoints configured for {provider.name}")
                    provider.record_failure("No endpoints configured")
                    continue
                
                endpoint = list(provider.endpoints.values())[0]
                url = f"{provider.base_url}{endpoint}"
                
                # Make request
                if not self.manager.session:
                    await self.manager.init_session()
                
                async with self.manager.session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        provider.record_success(response.elapsed.total_seconds() * 1000)
                        
                        logger.info(f"Successfully fetched from {provider.name}")
                        return {
                            "success": True,
                            "data": data,
                            "provider": provider.name,
                            "provider_id": provider.provider_id,
                            "error": None
                        }
                    else:
                        error_msg = f"HTTP {response.status}"
                        logger.warning(f"{provider.name} returned {error_msg}")
                        provider.record_failure(error_msg)
                        last_error = error_msg
            
            except asyncio.TimeoutError:
                error_msg = "Request timeout"
                logger.warning(f"{provider.name}: {error_msg}")
                provider.record_failure(error_msg)
                last_error = error_msg
            
            except Exception as e:
                error_msg = str(e)
                logger.error(f"{provider.name} error: {error_msg}")
                provider.record_failure(error_msg)
                last_error = error_msg
        
        # All retries exhausted
        return {
            "success": False,
            "data": None,
            "provider": None,
            "error": f"All providers failed. Last error: {last_error}"
        }
    
    async def _fetch_from_providers(
        self,
        provider_ids: List[str],
        max_retries: int,
        timeout: int
    ) -> Dict[str, Any]:
        """Fetch from specific providers in order"""
        for provider_id in provider_ids:
            provider = self.manager.get_provider(provider_id)
            if not provider or not provider.is_available:
                continue
            
            try:
                if not provider.endpoints:
                    continue
                
                endpoint = list(provider.endpoints.values())[0]
                url = f"{provider.base_url}{endpoint}"
                
                if not self.manager.session:
                    await self.manager.init_session()
                
                async with self.manager.session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        provider.record_success(response.elapsed.total_seconds() * 1000)
                        return {
                            "success": True,
                            "data": data,
                            "provider": provider.name,
                            "provider_id": provider.provider_id,
                            "error": None
                        }
                    else:
                        provider.record_failure(f"HTTP {response.status}")
            
            except Exception as e:
                logger.error(f"Error fetching from {provider.name}: {e}")
                provider.record_failure(str(e))
                continue
        
        return {
            "success": False,
            "data": None,
            "provider": None,
            "error": "All specified providers failed"
        }
    
    async def _fetch_direct(self, url: str, timeout: int) -> Dict[str, Any]:
        """Direct URL fetch without provider management"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data,
                            "provider": "direct",
                            "error": None
                        }
                    else:
                        return {
                            "success": False,
                            "data": None,
                            "provider": "direct",
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "provider": "direct",
                "error": str(e)
            }


# Singleton instance for easy import
_fetch_helper_instance = None


def get_fetch_helper(manager: Optional[ProviderManager] = None) -> ProviderFetchHelper:
    """Get or create singleton fetch helper instance"""
    global _fetch_helper_instance
    if _fetch_helper_instance is None:
        _fetch_helper_instance = ProviderFetchHelper(manager)
    return _fetch_helper_instance

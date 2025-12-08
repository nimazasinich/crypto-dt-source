"""
Base provider class with common functionality for all REST API providers.

Features:
- Async HTTP requests via httpx
- 10-second timeout control
- Simple 30-second in-memory caching
- Standardized JSON response format
- Error handling and logging
"""

from __future__ import annotations
import time
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

import httpx

# Configure provider logging
logger = logging.getLogger("providers")


@dataclass
class CacheEntry:
    """Cache entry with expiration tracking"""
    data: Any
    timestamp: float
    ttl: float = 30.0  # 30 seconds default
    
    def is_expired(self) -> bool:
        return (time.time() - self.timestamp) > self.ttl


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: float = 30.0):
        self._cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._cache[key]
                return None
            return entry.data
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache with TTL"""
        async with self._lock:
            self._cache[key] = CacheEntry(
                data=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl
            )
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries, return count removed"""
        now = time.time()
        expired_keys = [
            k for k, v in self._cache.items() 
            if (now - v.timestamp) > v.ttl
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)


def create_success_response(source: str, data: Any) -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "success": True,
        "source": source,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def create_error_response(source: str, error: str, details: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        "success": False,
        "source": source,
        "error": error,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if details:
        response["details"] = details
    return response


class BaseProvider(ABC):
    """Base class for all REST API data providers"""
    
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
        cache_ttl: float = 30.0
    ):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.cache = SimpleCache(default_ttl=cache_ttl)
        self.logger = logging.getLogger(f"providers.{name}")
        self._client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers=self._get_default_headers()
            )
        return self._client
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests (override in subclasses)"""
        return {
            "Accept": "application/json",
            "User-Agent": "HF-Crypto-Data-Engine/1.0"
        }
    
    async def close(self) -> None:
        """Close HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        use_cache: bool = True,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with caching, error handling, and timeout control.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body for POST requests
            use_cache: Whether to use caching (GET only)
            cache_key: Custom cache key
        
        Returns:
            Standardized response dict with success/error format
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Generate cache key for GET requests
        if use_cache and method.upper() == "GET":
            _cache_key = cache_key or f"{self.name}:{endpoint}:{str(params)}"
            cached = await self.cache.get(_cache_key)
            if cached is not None:
                self.logger.debug(f"Cache hit for {_cache_key}")
                return cached
        
        try:
            client = await self.get_client()
            
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, params=params, json=json_data)
            else:
                response = await client.request(method, url, params=params, json=json_data)
            
            response.raise_for_status()
            data = response.json()
            
            # Create success response
            result = create_success_response(self.name, data)
            
            # Cache GET requests
            if use_cache and method.upper() == "GET":
                await self.cache.set(_cache_key, result)
            
            return result
            
        except httpx.TimeoutException as e:
            error_msg = f"{self.name} request failed (timeout)"
            self.logger.error(f"{error_msg}: {e}")
            return create_error_response(self.name, error_msg, str(e))
            
        except httpx.HTTPStatusError as e:
            error_msg = f"{self.name} request failed (HTTP {e.response.status_code})"
            self.logger.error(f"{error_msg}: {e}")
            return create_error_response(self.name, error_msg, str(e))
            
        except httpx.RequestError as e:
            error_msg = f"{self.name} request failed (connection error)"
            self.logger.error(f"{error_msg}: {e}")
            return create_error_response(self.name, error_msg, str(e))
            
        except Exception as e:
            error_msg = f"{self.name} request failed (unexpected error)"
            self.logger.error(f"{error_msg}: {e}", exc_info=True)
            return create_error_response(self.name, error_msg, str(e))
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Make GET request"""
        return await self._request("GET", endpoint, params=params, use_cache=use_cache)
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make POST request (not cached)"""
        return await self._request("POST", endpoint, params=params, json_data=json_data, use_cache=False)

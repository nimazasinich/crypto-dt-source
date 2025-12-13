import time
import asyncio
from typing import Any, Dict, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

class TTLCache:
    """
    Async-safe TTL Cache for provider responses.
    Features:
    - Time-To-Live expiration
    - Async get/set
    - Invalidation
    """
    def __init__(self, default_ttl: int = 60):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()
        self.default_ttl = default_ttl

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                else:
                    # Lazy expiration
                    del self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        ttl_val = ttl if ttl is not None else self.default_ttl
        expiry = time.time() + ttl_val
        async with self._lock:
            self._cache[key] = (value, expiry)

    async def delete(self, key: str):
        """Delete specific key"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self):
        """Clear all cache"""
        async with self._lock:
            self._cache.clear()
            
    async def cleanup(self):
        """Remove expired items"""
        now = time.time()
        keys_to_remove = []
        async with self._lock:
            for key, (_, expiry) in self._cache.items():
                if now >= expiry:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._cache[key]
    
    def get_sync(self, key: str) -> Optional[Any]:
        """Synchronous get for non-async contexts (use with caution regarding race conditions)"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                del self._cache[key]
        return None

# Global cache instance
ttl_cache = TTLCache(default_ttl=60)

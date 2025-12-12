import time
import asyncio
from typing import Any, Dict, Optional, Tuple

class CacheManager:
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 60):
        async with self._lock:
            self._cache[key] = (value, time.time() + ttl)

    async def delete(self, key: str):
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self):
        async with self._lock:
            self._cache.clear()

# Global cache instance
cache_manager = CacheManager()

"""Caching layer for HuggingFace Crypto Data Engine"""
from __future__ import annotations
from typing import Optional, Any
from datetime import datetime, timedelta
import time
import json
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Cache entry with TTL"""
    value: Any
    expires_at: float


class MemoryCache:
    """In-memory cache with TTL support"""

    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]

        # Check if expired
        if time.time() > entry.expires_at:
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: int):
        """Set value in cache with TTL in seconds"""
        expires_at = time.time() + ttl
        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total) if total > 0 else 0

        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hitRate": round(hit_rate, 2)
        }

    def cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry.expires_at
        ]

        for key in expired_keys:
            del self._cache[key]


# Global cache instance
cache = MemoryCache()


def cache_key(prefix: str, **kwargs) -> str:
    """Generate cache key from prefix and parameters"""
    params = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return f"{prefix}:{params}" if params else prefix


async def get_or_set(
    key: str,
    ttl: int,
    factory: callable
) -> Any:
    """Get from cache or compute and store"""
    # Try to get from cache
    cached = cache.get(key)
    if cached is not None:
        return cached

    # Compute value
    value = await factory()

    # Store in cache
    cache.set(key, value, ttl)

    return value

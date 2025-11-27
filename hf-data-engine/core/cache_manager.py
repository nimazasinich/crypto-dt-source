"""
Cache Manager with In-Memory and Optional Redis Support
Provides caching layer for API responses
"""

import json
import hashlib
import logging
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CacheBackend(str, Enum):
    """Cache backend types"""

    MEMORY = "memory"
    REDIS = "redis"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""

    key: str
    data: Any
    created_at: datetime
    expires_at: datetime
    hits: int = 0
    source: str = "unknown"


class InMemoryCache:
    """Simple in-memory cache implementation"""

    def __init__(self, max_size: int = 1000):
        self.cache: dict[str, CacheEntry] = {}
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        entry = self.cache.get(key)

        if not entry:
            return None

        # Check expiration
        if datetime.utcnow() > entry.expires_at:
            del self.cache[key]
            return None

        # Update hits
        entry.hits += 1

        return entry.data

    def set(self, key: str, value: Any, ttl: int = 60, source: str = "unknown"):
        """Set cached value"""
        # Check cache size
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        entry = CacheEntry(
            key=key,
            data=value,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl),
            source=source,
        )

        self.cache[key] = entry

    def delete(self, key: str):
        """Delete cached value"""
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """Clear all cache"""
        self.cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        total_hits = sum(entry.hits for entry in self.cache.values())

        # Calculate memory usage (rough estimate)
        memory_bytes = sum(
            len(json.dumps(entry.data).encode("utf-8")) for entry in self.cache.values()
        )

        return {
            "backend": "memory",
            "entries": total_entries,
            "max_size": self.max_size,
            "total_hits": total_hits,
            "memory_bytes": memory_bytes,
            "memory_mb": round(memory_bytes / (1024 * 1024), 2),
        }

    def _evict_oldest(self):
        """Evict oldest entry"""
        if not self.cache:
            return

        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
        del self.cache[oldest_key]


class RedisCache:
    """Redis cache implementation (optional)"""

    def __init__(self, redis_url: str, max_size: int = 10000):
        try:
            import redis

            self.redis = redis.from_url(redis_url)
            self.max_size = max_size
            logger.info(f"Redis cache initialized: {redis_url}")
        except ImportError:
            logger.warning("Redis not installed. Install with: pip install redis")
            self.redis = None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.redis:
            return None

        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 60, source: str = "unknown"):
        """Set cached value"""
        if not self.redis:
            return

        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def delete(self, key: str):
        """Delete cached value"""
        if not self.redis:
            return

        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    def clear(self):
        """Clear all cache"""
        if not self.redis:
            return

        try:
            self.redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis:
            return {"backend": "redis", "status": "unavailable"}

        try:
            info = self.redis.info()
            return {
                "backend": "redis",
                "keys": self.redis.dbsize(),
                "memory_bytes": info.get("used_memory", 0),
                "memory_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {"backend": "redis", "status": "error", "error": str(e)}


class CacheManager:
    """
    Unified cache manager with automatic backend selection
    """

    def __init__(
        self,
        backend: CacheBackend = CacheBackend.MEMORY,
        redis_url: Optional[str] = None,
        max_size: int = 1000,
    ):
        self.backend_type = backend

        if backend == CacheBackend.REDIS and redis_url:
            self.backend = RedisCache(redis_url, max_size)
            # Fallback to memory if Redis fails
            if self.backend.redis is None:
                logger.warning("Falling back to in-memory cache")
                self.backend = InMemoryCache(max_size)
                self.backend_type = CacheBackend.MEMORY
        else:
            self.backend = InMemoryCache(max_size)

        logger.info(f"Cache manager initialized with backend: {self.backend_type}")

    def cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Sort kwargs for consistent keys
        parts = [prefix]
        for k, v in sorted(kwargs.items()):
            parts.append(f"{k}={v}")

        key_str = "|".join(parts)

        # Hash for shorter keys
        key_hash = hashlib.md5(key_str.encode()).hexdigest()

        return f"{prefix}:{key_hash}"

    async def get_or_set(
        self, key: str, ttl: int, fetch_fn: Callable, source: str = "unknown"
    ) -> Any:
        """
        Get from cache or fetch and cache

        Args:
            key: Cache key
            ttl: Time to live in seconds
            fetch_fn: Async function to fetch data if not cached
            source: Data source for metadata

        Returns:
            Cached or fetched data
        """
        # Try cache first
        cached = self.backend.get(key)
        if cached is not None:
            logger.debug(f"Cache hit: {key}")
            return cached

        # Cache miss - fetch data
        logger.debug(f"Cache miss: {key}")
        data = await fetch_fn()

        # Cache the result
        self.backend.set(key, data, ttl, source)

        return data

    def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: int = 60, source: str = "unknown"):
        """Set cache value"""
        self.backend.set(key, value, ttl, source)

    def delete(self, key: str):
        """Delete from cache"""
        self.backend.delete(key)

    def clear(self):
        """Clear all cache"""
        self.backend.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return self.backend.get_stats()


# Global cache instance
_cache: Optional[CacheManager] = None


def get_cache(
    backend: CacheBackend = CacheBackend.MEMORY, redis_url: Optional[str] = None
) -> CacheManager:
    """Get or create global cache manager"""
    global _cache

    if _cache is None:
        _cache = CacheManager(backend=backend, redis_url=redis_url)

    return _cache


def cache_key(prefix: str, **kwargs) -> str:
    """Generate cache key (convenience function)"""
    cache = get_cache()
    return cache.cache_key(prefix, **kwargs)


# Cache TTL presets (seconds)
class CacheTTL:
    """Predefined cache TTL values"""

    VERY_SHORT = 10  # 10 seconds
    SHORT = 30  # 30 seconds
    MEDIUM = 60  # 1 minute
    LONG = 300  # 5 minutes
    VERY_LONG = 600  # 10 minutes
    HOUR = 3600  # 1 hour
    DAY = 86400  # 24 hours

    # Endpoint-specific TTLs
    MARKET_DATA = 30
    MARKET_PAIRS = 300  # Pairs don't change often
    OHLC = 120
    NEWS = 300
    SENTIMENT = 600
    WHALE = 60
    GAS = 30
    BLOCKCHAIN_STATS = 300
    PROVIDERS = 600
    STATUS = 10

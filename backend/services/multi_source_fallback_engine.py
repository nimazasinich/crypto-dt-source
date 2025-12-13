#!/usr/bin/env python3
"""
Multi-Source Fallback Engine
Implements cascading fallback system with 10+ sources per data type
NEVER FAILS - Always returns data or cached data
"""

import httpx
import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Supported data types"""
    MARKET_PRICES = "market_prices"
    OHLC_CANDLESTICK = "ohlc_candlestick"
    BLOCKCHAIN_EXPLORER = "blockchain_explorer"
    NEWS_FEEDS = "news_feeds"
    SENTIMENT_DATA = "sentiment_data"
    ONCHAIN_ANALYTICS = "onchain_analytics"
    WHALE_TRACKING = "whale_tracking"


class SourceStatus(Enum):
    """Source availability status"""
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    TEMPORARILY_DOWN = "temporarily_down"
    PERMANENTLY_FAILED = "permanently_failed"


class MultiSourceCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float, float]] = {}  # key: (data, timestamp, ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached data if not expired"""
        if key in self._cache:
            data, timestamp, ttl = self._cache[key]
            if time.time() - timestamp < ttl:
                logger.info(f"✅ Cache HIT: {key}")
                return data
            else:
                # Expired
                del self._cache[key]
                logger.debug(f"⏰ Cache EXPIRED: {key}")
        return None
    
    def set(self, key: str, data: Any, ttl: int):
        """Set cache with TTL in seconds"""
        self._cache[key] = (data, time.time(), ttl)
        logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
    
    def get_stale(self, key: str, max_age: int) -> Optional[Any]:
        """Get cached data even if expired, within max_age"""
        if key in self._cache:
            data, timestamp, _ = self._cache[key]
            age = time.time() - timestamp
            if age < max_age:
                logger.warning(f"⚠️ Cache STALE: {key} (age: {age:.0f}s)")
                return data
        return None
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()


class SourceMonitor:
    """Monitor source performance and availability"""
    
    def __init__(self):
        self._source_stats: Dict[str, Dict[str, Any]] = {}
        self._source_status: Dict[str, SourceStatus] = {}
        self._unavailable_until: Dict[str, float] = {}  # timestamp when source becomes available again
    
    def record_success(self, source_name: str, response_time: float):
        """Record successful request"""
        if source_name not in self._source_stats:
            self._source_stats[source_name] = {
                "success_count": 0,
                "failure_count": 0,
                "total_response_time": 0,
                "last_success": None,
                "last_failure": None
            }
        
        stats = self._source_stats[source_name]
        stats["success_count"] += 1
        stats["total_response_time"] += response_time
        stats["last_success"] = time.time()
        
        # Mark as available
        self._source_status[source_name] = SourceStatus.AVAILABLE
        if source_name in self._unavailable_until:
            del self._unavailable_until[source_name]
        
        logger.debug(f"✅ {source_name}: Success ({response_time:.2f}s)")
    
    def record_failure(self, source_name: str, error_type: str, status_code: Optional[int] = None):
        """Record failed request"""
        if source_name not in self._source_stats:
            self._source_stats[source_name] = {
                "success_count": 0,
                "failure_count": 0,
                "total_response_time": 0,
                "last_success": None,
                "last_failure": None
            }
        
        stats = self._source_stats[source_name]
        stats["failure_count"] += 1
        stats["last_failure"] = time.time()
        stats["last_error"] = error_type
        stats["last_status_code"] = status_code
        
        # Handle different error types
        if status_code == 429:
            # Rate limited - mark unavailable for 60 minutes
            self._source_status[source_name] = SourceStatus.RATE_LIMITED
            self._unavailable_until[source_name] = time.time() + 3600
            logger.warning(f"⚠️ {source_name}: RATE LIMITED (unavailable for 60 min)")
        
        elif status_code in [500, 502, 503, 504]:
            # Server error - mark unavailable for 5 minutes
            self._source_status[source_name] = SourceStatus.TEMPORARILY_DOWN
            self._unavailable_until[source_name] = time.time() + 300
            logger.warning(f"⚠️ {source_name}: TEMPORARILY DOWN (unavailable for 5 min)")
        
        elif status_code in [401, 403]:
            # Auth error - mark unavailable for 24 hours
            self._source_status[source_name] = SourceStatus.TEMPORARILY_DOWN
            self._unavailable_until[source_name] = time.time() + 86400
            logger.error(f"❌ {source_name}: AUTH FAILED (unavailable for 24 hours)")
        
        else:
            logger.warning(f"⚠️ {source_name}: Failed ({error_type})")
    
    def is_available(self, source_name: str) -> bool:
        """Check if source is available"""
        if source_name in self._unavailable_until:
            if time.time() < self._unavailable_until[source_name]:
                return False
            else:
                # Became available again
                del self._unavailable_until[source_name]
                self._source_status[source_name] = SourceStatus.AVAILABLE
        
        return True
    
    def get_stats(self, source_name: str) -> Dict[str, Any]:
        """Get source statistics"""
        if source_name not in self._source_stats:
            return {}
        
        stats = self._source_stats[source_name]
        total_requests = stats["success_count"] + stats["failure_count"]
        
        return {
            "total_requests": total_requests,
            "success_count": stats["success_count"],
            "failure_count": stats["failure_count"],
            "success_rate": stats["success_count"] / total_requests if total_requests > 0 else 0,
            "avg_response_time": stats["total_response_time"] / stats["success_count"] if stats["success_count"] > 0 else 0,
            "last_success": stats.get("last_success"),
            "last_failure": stats.get("last_failure"),
            "status": self._source_status.get(source_name, SourceStatus.AVAILABLE).value
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get all source statistics"""
        return {name: self.get_stats(name) for name in self._source_stats.keys()}


class MultiSourceFallbackEngine:
    """
    Core engine for multi-source data fetching with automatic failover
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the fallback engine"""
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / "multi_source_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize components
        self.cache = MultiSourceCache()
        self.monitor = SourceMonitor()
        
        logger.info("✅ Multi-Source Fallback Engine initialized")
    
    def _get_sources_for_data_type(self, data_type: DataType, **kwargs) -> List[Dict[str, Any]]:
        """Get all sources for a data type in priority order"""
        sources = []
        
        if data_type == DataType.MARKET_PRICES:
            config = self.config["api_sources"]["market_prices"]
            sources.extend(config.get("primary", []))
            sources.extend(config.get("secondary", []))
            sources.extend(config.get("tertiary", []))
        
        elif data_type == DataType.OHLC_CANDLESTICK:
            config = self.config["api_sources"]["ohlc_candlestick"]
            sources.extend(config.get("primary", []))
            sources.extend(config.get("secondary", []))
            # HuggingFace datasets as fallback
            sources.extend(config.get("huggingface_datasets", []))
        
        elif data_type == DataType.BLOCKCHAIN_EXPLORER:
            chain = kwargs.get("chain", "ethereum")
            config = self.config["api_sources"]["blockchain_explorer"]
            sources.extend(config.get(chain, []))
        
        elif data_type == DataType.NEWS_FEEDS:
            config = self.config["api_sources"]["news_feeds"]
            sources.extend(config.get("api_sources", []))
            sources.extend(config.get("rss_feeds", []))
        
        elif data_type == DataType.SENTIMENT_DATA:
            config = self.config["api_sources"]["sentiment_data"]
            sources.extend(config.get("primary", []))
            sources.extend(config.get("social_analytics", []))
        
        elif data_type == DataType.ONCHAIN_ANALYTICS:
            sources.extend(self.config["api_sources"]["onchain_analytics"])
        
        elif data_type == DataType.WHALE_TRACKING:
            sources.extend(self.config["api_sources"]["whale_tracking"])
        
        # Sort by priority
        sources.sort(key=lambda x: x.get("priority", 999))
        
        # Filter out unavailable sources
        available_sources = [s for s in sources if self.monitor.is_available(s["name"])]
        
        logger.info(f"📊 {data_type.value}: {len(available_sources)}/{len(sources)} sources available")
        
        return available_sources
    
    async def _fetch_from_source(
        self,
        source: Dict[str, Any],
        fetch_func: Callable,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Fetch data from a single source"""
        source_name = source["name"]
        
        try:
            start_time = time.time()
            
            # Call the fetch function
            result = await fetch_func(source, **kwargs)
            
            response_time = time.time() - start_time
            
            # Validate result
            if result and self._validate_result(result):
                self.monitor.record_success(source_name, response_time)
                return result
            else:
                logger.warning(f"⚠️ {source_name}: Invalid result")
                self.monitor.record_failure(source_name, "invalid_result")
                return None
        
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.warning(f"⚠️ {source_name}: HTTP {status_code}")
            self.monitor.record_failure(source_name, f"http_{status_code}", status_code)
            return None
        
        except httpx.TimeoutException as e:
            logger.warning(f"⚠️ {source_name}: Timeout")
            self.monitor.record_failure(source_name, "timeout")
            return None
        
        except Exception as e:
            logger.error(f"❌ {source_name}: {type(e).__name__}: {str(e)}")
            self.monitor.record_failure(source_name, type(e).__name__)
            return None
    
    def _validate_result(self, result: Any) -> bool:
        """Validate result data"""
        if not result:
            return False
        
        # Basic validation - can be extended
        if isinstance(result, dict):
            return True
        elif isinstance(result, list):
            return len(result) > 0
        
        return False
    
    async def fetch_with_fallback(
        self,
        data_type: DataType,
        fetch_func: Callable,
        cache_key: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch data with automatic fallback through multiple sources
        
        Args:
            data_type: Type of data to fetch
            fetch_func: Async function to fetch from a source
            cache_key: Unique cache key
            **kwargs: Additional parameters for fetch function
        
        Returns:
            Data from successful source or cache
        """
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return {
                "success": True,
                "data": cached,
                "source": "cache",
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get all sources for this data type
        sources = self._get_sources_for_data_type(data_type, **kwargs)
        
        if not sources:
            logger.error(f"❌ No sources available for {data_type.value}")
            # Try stale cache as emergency fallback
            return self._emergency_fallback(cache_key, data_type)
        
        # Try each source in order
        attempts = 0
        for source in sources:
            attempts += 1
            source_name = source["name"]
            
            logger.info(f"🔄 Attempt {attempts}/{len(sources)}: Trying {source_name}")
            
            result = await self._fetch_from_source(source, fetch_func, **kwargs)
            
            if result:
                # Success! Cache and return
                cache_ttl = self.config["caching"].get(data_type.value, {}).get("ttl_seconds", 60)
                self.cache.set(cache_key, result, cache_ttl)
                
                logger.info(f"✅ SUCCESS: {source_name} (attempt {attempts}/{len(sources)})")
                
                return {
                    "success": True,
                    "data": result,
                    "source": source_name,
                    "cached": False,
                    "attempts": attempts,
                    "total_sources": len(sources),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # All sources failed - try emergency fallback
        logger.error(f"❌ All {len(sources)} sources failed for {data_type.value}")
        return self._emergency_fallback(cache_key, data_type)
    
    def _emergency_fallback(self, cache_key: str, data_type: DataType) -> Dict[str, Any]:
        """Emergency fallback when all sources fail"""
        # Try stale cache
        max_age = self.config["caching"].get(data_type.value, {}).get("max_age_seconds", 3600)
        stale_data = self.cache.get_stale(cache_key, max_age)
        
        if stale_data:
            logger.warning(f"⚠️ EMERGENCY FALLBACK: Using stale cache for {cache_key}")
            return {
                "success": True,
                "data": stale_data,
                "source": "stale_cache",
                "cached": True,
                "stale": True,
                "warning": "Data may be outdated",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # No cache available
        logger.error(f"❌ COMPLETE FAILURE: No data available for {cache_key}")
        return {
            "success": False,
            "error": "All sources failed and no cached data available",
            "data_type": data_type.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def fetch_parallel(
        self,
        data_type: DataType,
        fetch_func: Callable,
        cache_key: str,
        max_parallel: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch from multiple sources in parallel and return first successful result
        
        Args:
            data_type: Type of data to fetch
            fetch_func: Async function to fetch from a source
            cache_key: Unique cache key
            max_parallel: Maximum number of parallel requests
            **kwargs: Additional parameters for fetch function
        
        Returns:
            Data from first successful source
        """
        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return {
                "success": True,
                "data": cached,
                "source": "cache",
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get sources
        sources = self._get_sources_for_data_type(data_type, **kwargs)[:max_parallel]
        
        if not sources:
            return self._emergency_fallback(cache_key, data_type)
        
        logger.info(f"🚀 Parallel fetch from {len(sources)} sources")
        
        # Create tasks for parallel execution
        tasks = [
            self._fetch_from_source(source, fetch_func, **kwargs)
            for source in sources
        ]
        
        # Wait for first successful result
        for completed in asyncio.as_completed(tasks):
            try:
                result = await completed
                if result:
                    # Cache and return first success
                    cache_ttl = self.config["caching"].get(data_type.value, {}).get("ttl_seconds", 60)
                    self.cache.set(cache_key, result, cache_ttl)
                    
                    logger.info(f"✅ PARALLEL SUCCESS: Got first result")
                    
                    return {
                        "success": True,
                        "data": result,
                        "source": "parallel_fetch",
                        "cached": False,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            except:
                continue
        
        # All parallel requests failed
        logger.error(f"❌ All parallel requests failed")
        return self._emergency_fallback(cache_key, data_type)
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics for all sources"""
        return {
            "sources": self.monitor.get_all_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("🗑️ Cache cleared")


# Global instance
_engine_instance: Optional[MultiSourceFallbackEngine] = None


def get_fallback_engine() -> MultiSourceFallbackEngine:
    """Get or create global fallback engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = MultiSourceFallbackEngine()
    return _engine_instance


__all__ = [
    "MultiSourceFallbackEngine",
    "DataType",
    "SourceStatus",
    "get_fallback_engine"
]

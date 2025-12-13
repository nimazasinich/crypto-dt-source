import asyncio
import logging
import time
import json
import random
import os
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime

from backend.cache.ttl_cache import ttl_cache

# Configure logging
def setup_provider_logger(name, log_file):
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

health_logger = setup_provider_logger("provider_health", "logs/provider_health.log")
failure_logger = setup_provider_logger("provider_failures", "logs/provider_failures.log")
rotation_logger = setup_provider_logger("provider_rotation", "logs/provider_rotation.log")
main_logger = logging.getLogger("ProviderManager")

class ProviderStatus(Enum):
    ACTIVE = "active"
    COOLDOWN = "cooldown"
    FAILED = "failed"
    DISABLED = "disabled"
    RATE_LIMITED = "rate_limited"  # NEW: Specific status for rate limited providers

@dataclass
class ProviderMetrics:
    total_requests: int = 0
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    last_response_time: float = 0.0
    avg_response_time: float = 0.0
    last_success: float = 0.0
    last_failure: float = 0.0
    rate_limit_hits: int = 0

@dataclass
class ProviderConfig:
    name: str
    category: str  # market, news, onchain, sentiment, rpc
    base_url: str
    api_key: Optional[str] = None
    weight: int = 100
    priority: int = 100  # NEW: Priority (higher = better, 1-100 scale)
    rate_limit_per_min: int = 60
    timeout: int = 10
    headers: Dict[str, str] = field(default_factory=dict)
    
    # SMART ROUTING: Priority mapping
    # Priority 1 (90-100): Crypto DT Source (Binance proxy), fast and reliable
    # Priority 2 (80-89): Crypto API Clean (281 resources, 7.8ms avg)
    # Priority 3 (70-79): CryptoCompare (working well)
    # Priority 4 (60-69): CoinGecko (cached only, rate limited, last resort)

class Provider:
    def __init__(self, config: ProviderConfig, fetch_func: Callable[..., Awaitable[Any]]):
        self.config = config
        self.fetch_func = fetch_func
        self.status = ProviderStatus.ACTIVE
        self.metrics = ProviderMetrics()
        self.cooldown_until: float = 0.0
        self.request_timestamps: List[float] = []  # For sliding window rate limiting

    async def is_available(self) -> bool:
        if self.status == ProviderStatus.DISABLED:
            return False
        
        now = time.time()
        
        # Check cooldown
        if self.status == ProviderStatus.COOLDOWN:
            if now >= self.cooldown_until:
                self.recover()
            else:
                return False
        
        # Check rate limits
        self._clean_request_timestamps(now)
        if len(self.request_timestamps) >= self.config.rate_limit_per_min:
            main_logger.warning(f"Provider {self.config.name} hit rate limit ({len(self.request_timestamps)}/{self.config.rate_limit_per_min})")
            return False
            
        return True

    def _clean_request_timestamps(self, now: float):
        """Remove timestamps older than 1 minute"""
        cutoff = now - 60
        self.request_timestamps = [t for t in self.request_timestamps if t > cutoff]

    def record_request(self):
        self.metrics.total_requests += 1
        self.request_timestamps.append(time.time())

    def record_success(self, latency: float):
        self.metrics.success_count += 1
        self.metrics.consecutive_failures = 0
        self.metrics.last_success = time.time()
        self.metrics.last_response_time = latency
        
        # Moving average
        if self.metrics.avg_response_time == 0:
            self.metrics.avg_response_time = latency
        else:
            self.metrics.avg_response_time = (self.metrics.avg_response_time * 0.9) + (latency * 0.1)
            
        health_logger.info(f"SUCCESS: {self.config.name} | Latency: {latency*1000:.2f}ms | Avg: {self.metrics.avg_response_time*1000:.2f}ms")

    def record_failure(self, error: str):
        self.metrics.failure_count += 1
        self.metrics.consecutive_failures += 1
        self.metrics.last_failure = time.time()
        
        failure_logger.error(f"FAILURE: {self.config.name} | Error: {error} | Consecutive: {self.metrics.consecutive_failures}")
        
        # Check if it's a rate limit error
        if "429" in error or "rate limit" in error.lower():
            self.metrics.rate_limit_hits += 1
            self.status = ProviderStatus.RATE_LIMITED
            # Longer cooldown for rate limits (5 minutes for CoinGecko)
            if "coingecko" in self.config.name.lower():
                self.enter_cooldown(reason="Rate limit (429)", duration=300)  # 5 minutes
            else:
                self.enter_cooldown(reason="Rate limit", duration=120)  # 2 minutes
        # Auto-cooldown logic for consecutive failures
        elif self.metrics.consecutive_failures >= 3:
            self.enter_cooldown(reason="Too many consecutive failures")

    def enter_cooldown(self, reason: str, duration: int = 60):
        self.status = ProviderStatus.COOLDOWN
        self.cooldown_until = time.time() + duration
        main_logger.warning(f"Provider {self.config.name} entering COOLDOWN for {duration}s. Reason: {reason}")
        rotation_logger.info(f"COOLDOWN_START: {self.config.name} | Duration: {duration}s | Reason: {reason}")

    def recover(self):
        self.status = ProviderStatus.ACTIVE
        self.cooldown_until = 0.0
        self.metrics.consecutive_failures = 0
        main_logger.info(f"Provider {self.config.name} recovered from cooldown")
        rotation_logger.info(f"RECOVERY: {self.config.name} returned to active pool")

class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, List[Provider]] = {
            "market": [],
            "news": [],
            "onchain": [],
            "sentiment": [],
            "rpc": []
        }
        self._lock = asyncio.Lock()

    def register_provider(self, category: str, config: ProviderConfig, fetch_func: Callable[..., Awaitable[Any]]):
        if category not in self.providers:
            self.providers[category] = []
        
        provider = Provider(config, fetch_func)
        self.providers[category].append(provider)
        main_logger.info(f"Registered provider: {config.name} for category: {category}")

    async def get_next_provider(self, category: str) -> Optional[Provider]:
        """
        Get next provider with SMART PRIORITY-BASED ROUTING
        
        Priority order:
        1. Crypto DT Source (90-100): Binance proxy, fast, reliable
        2. Crypto API Clean (80-89): 281 resources, 7.8ms avg
        3. CryptoCompare (70-79): Working well
        4. CoinGecko (60-69): Cached only, rate limited, last resort
        
        Falls back to round-robin if priorities are equal
        """
        async with self._lock:
            if category not in self.providers or not self.providers[category]:
                return None
            
            queue = self.providers[category]
            
            # Sort providers by priority (highest first) and availability
            sorted_providers = sorted(
                queue,
                key=lambda p: (
                    p.config.priority if hasattr(p.config, 'priority') else p.config.weight,
                    -p.metrics.consecutive_failures,
                    p.metrics.avg_response_time if p.metrics.avg_response_time > 0 else 999
                ),
                reverse=True
            )
            
            # Find first available provider in priority order
            for provider in sorted_providers:
                if await provider.is_available():
                    rotation_logger.info(
                        f"SMART_ROUTING: Selected {provider.config.name} "
                        f"(priority: {getattr(provider.config, 'priority', provider.config.weight)}, "
                        f"avg_latency: {provider.metrics.avg_response_time*1000:.1f}ms) "
                        f"for {category}"
                    )
                    return provider
            
            # No available provider
            main_logger.warning(f"No available providers for {category}")
            return None

    async def fetch_data(self, category: str, params: Dict[str, Any] = None, use_cache: bool = True, ttl: int = 60) -> Dict[str, Any]:
        """
        Main entry point for fetching data.
        Handles caching, rotation, failover, and standardized response.
        """
        if params is None:
            params = {}
            
        # 1. Check Cache
        cache_key = f"{category}:{json.dumps(params, sort_keys=True)}"
        if use_cache:
            cached = await ttl_cache.get(cache_key)
            if cached:
                main_logger.debug(f"Cache hit for {cache_key}")
                return cached

        # 2. Get Provider & Fetch
        attempts = 0
        max_attempts = len(self.providers.get(category, [])) + 1 # Try potentially all providers + retry
        
        errors = []
        
        while attempts < max_attempts:
            provider = await self.get_next_provider(category)
            
            if not provider:
                if attempts == 0:
                    main_logger.error(f"No providers available for {category}")
                    return self._create_error_response("No providers available", category)
                else:
                    # All providers exhausted or busy
                    break

            attempts += 1
            start_time = time.time()
            provider.record_request()
            
            try:
                # Call the fetch function
                # Note: fetch_func should accept **params
                main_logger.info(f"Fetching {category} from {provider.config.name}...")
                
                # Add headers if needed
                request_kwargs = params.copy()
                if provider.config.api_key and "api_key" not in request_kwargs:
                     # Some providers need key in params, some in headers. 
                     # The fetch_func implementation should handle how to use the key from config
                     pass

                result = await provider.fetch_func(provider.config, **params)
                
                # Success
                latency = time.time() - start_time
                provider.record_success(latency)
                
                response = {
                    "success": True,
                    "data": result,
                    "source": provider.config.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "latency_ms": round(latency * 1000, 2)
                }
                
                # Set Cache
                if use_cache:
                    await ttl_cache.set(cache_key, response, ttl=ttl)
                
                return response

            except Exception as e:
                error_msg = str(e)
                latency = time.time() - start_time
                provider.record_failure(error_msg)
                errors.append(f"{provider.config.name}: {error_msg}")
                main_logger.warning(f"Provider {provider.config.name} failed: {error_msg}. Rotating...")
                
                # If it's a critical failure (401, 403, 429), maybe longer cooldown?
                if "429" in error_msg:
                    provider.enter_cooldown("Rate limit hit", duration=300)
                
                continue

        # Fallback if all failed
        failure_logger.critical(f"All providers failed for {category}. Errors: {errors}")
        return self._create_error_response(f"All providers failed: {'; '.join(errors)}", category)

    def _create_error_response(self, message: str, category: str) -> Dict[str, Any]:
        return {
            "success": False,
            "error": message,
            "category": category,
            "timestamp": datetime.utcnow().isoformat(),
            "data": None
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get basic provider statistics"""
        stats = {}
        for category, providers in self.providers.items():
            stats[category] = []
            for p in providers:
                stats[category].append({
                    "name": p.config.name,
                    "status": p.status.value,
                    "success_rate": round((p.metrics.success_count / max(1, p.metrics.total_requests)) * 100, 2),
                    "avg_latency": round(p.metrics.avg_response_time * 1000, 2),
                    "requests": p.metrics.total_requests,
                    "failures": p.metrics.failure_count
                })
        return stats
    
    def get_detailed_stats(self) -> List[Dict[str, Any]]:
        """
        Get detailed provider statistics for status display
        
        Returns list of providers with detailed metrics:
        - name, status, priority
        - response_time_ms, success_rate
        - last_check, error details
        - rate_limit_hits, cooldown status
        """
        detailed_stats = []
        
        for category, providers in self.providers.items():
            for p in providers:
                stat = {
                    "name": p.config.name,
                    "category": category,
                    "status": p.status.value,
                    "priority": getattr(p.config, 'priority', p.config.weight),
                    "response_time_ms": round(p.metrics.avg_response_time * 1000, 2) if p.metrics.avg_response_time > 0 else None,
                    "success_rate": round((p.metrics.success_count / max(1, p.metrics.total_requests)) * 100, 2),
                    "total_requests": p.metrics.total_requests,
                    "failure_count": p.metrics.failure_count,
                    "consecutive_failures": p.metrics.consecutive_failures,
                    "rate_limit_hits": p.metrics.rate_limit_hits,
                    "last_success": datetime.fromtimestamp(p.metrics.last_success).isoformat() if p.metrics.last_success > 0 else None,
                    "last_failure": datetime.fromtimestamp(p.metrics.last_failure).isoformat() if p.metrics.last_failure > 0 else None,
                    "cooldown_until": datetime.fromtimestamp(p.cooldown_until).isoformat() if p.cooldown_until > time.time() else None
                }
                
                detailed_stats.append(stat)
        
        # Sort by priority (highest first)
        detailed_stats.sort(key=lambda x: x["priority"], reverse=True)
        
        return detailed_stats

# Global Orchestrator Instance
provider_manager = ProviderManager()

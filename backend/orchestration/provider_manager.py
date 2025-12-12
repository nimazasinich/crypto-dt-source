import asyncio
import logging
import time
import json
import os
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime

from backend.cache.ttl_cache import ttl_cache

# Configure logging
def setup_provider_logger(name, log_file):
    """
    Create a provider logger.

    HF Spaces safety:
    - Ensure the logs/ directory exists
    - If file logging fails (read-only FS), fall back to a NullHandler
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers on repeated imports/reloads
    if logger.handlers:
        return logger

    try:
        log_dir = os.path.dirname(log_file) or "."
        os.makedirs(log_dir, exist_ok=True)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception:
        # Last-resort: do not break app import/startup
        logger.addHandler(logging.NullHandler())

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
    rate_limit_per_min: int = 60
    timeout: int = 10
    headers: Dict[str, str] = field(default_factory=dict)

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
        
        # Auto-cooldown logic
        if self.metrics.consecutive_failures >= 3:
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
        # Smooth weighted round-robin state per category
        # key: category -> provider_name -> current_weight
        self._swr_state: Dict[str, Dict[str, int]] = {}

    def register_provider(self, category: str, config: ProviderConfig, fetch_func: Callable[..., Awaitable[Any]]):
        if category not in self.providers:
            self.providers[category] = []
        
        provider = Provider(config, fetch_func)
        self.providers[category].append(provider)
        main_logger.info(f"Registered provider: {config.name} for category: {category}")

        # Initialize SWRR state slot
        self._swr_state.setdefault(category, {}).setdefault(config.name, 0)

    def _select_provider_smooth_weighted_rr(self, category: str, available: List[Provider]) -> Optional[Provider]:
        """
        Smooth Weighted Round Robin (SWRR).
        Deterministic and matches configured weights over time.
        """
        if not available:
            return None

        state = self._swr_state.setdefault(category, {})

        total_weight = 0
        best: Optional[Provider] = None
        best_cw: Optional[int] = None

        for p in available:
            w = int(getattr(p.config, "weight", 1) or 1)
            if w < 1:
                w = 1
            total_weight += w

            cw = state.get(p.config.name, 0) + w
            state[p.config.name] = cw

            if best is None or cw > (best_cw if best_cw is not None else -10**18):
                best = p
                best_cw = cw

        if best is not None and total_weight > 0:
            state[best.config.name] = state.get(best.config.name, 0) - total_weight

        return best

    async def get_next_provider(self, category: str) -> Optional[Provider]:
        async with self._lock:
            if category not in self.providers or not self.providers[category]:
                return None
            
            # Simple round-robin with availability check
            # We iterate through the list, finding the first available one
            # Then we move it to the end of the list to rotate
            
            queue = self.providers[category]

            # Resolve availability first (async)
            available: List[Provider] = []
            for p in queue:
                if await p.is_available():
                    available.append(p)

            if not available:
                return None

            # If weights are configured (not all equal), use SWRR; else simple RR.
            weights = [int(getattr(p.config, "weight", 1) or 1) for p in available]
            use_weighted = len(set(weights)) > 1

            selected: Optional[Provider]
            if use_weighted:
                selected = self._select_provider_smooth_weighted_rr(category, available)
            else:
                selected = available[0]

            if selected is None:
                return None

            # Rotate queue order for observability/debug parity with QA expectations
            try:
                idx = queue.index(selected)
                queue.pop(idx)
            except ValueError:
                # Shouldn't happen, but don't fail selection
                pass
            queue.append(selected)
            rotation_logger.info(f"ROTATION: Selected {selected.config.name} for {category}. Queue rotated.")

            return selected

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
                # Geo-blocked providers should be cooled down aggressively to avoid retry storms
                if "451" in error_msg or "Geo-blocked" in error_msg:
                    provider.enter_cooldown("Geo-blocked / restricted", duration=3600)
                
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

# Global Orchestrator Instance
provider_manager = ProviderManager()

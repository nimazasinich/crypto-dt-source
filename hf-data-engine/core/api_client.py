"""
API Client with HF-first + Fallback Logic
Implements the primary data fetching logic with provider fallback
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx
from core.fallback_config import ProviderConfig, get_fallback_config

logger = logging.getLogger(__name__)


class DataSource(str, Enum):
    """Data source types"""

    HF = "hf"
    HF_WS = "hf-ws"
    FALLBACK = "fallback"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for provider health tracking"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time: Optional[datetime] = None

    def record_success(self):
        """Record successful request"""
        self.failures = 0
        self.state = CircuitBreakerState.CLOSED

    def record_failure(self):
        """Record failed request"""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()

        if self.failures >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker OPEN (failures={self.failures})")

    def can_attempt(self) -> bool:
        """Check if request can be attempted"""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed > self.timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit breaker HALF_OPEN (timeout passed)")
                    return True
            return False

        # HALF_OPEN: allow one attempt
        return True

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state"""
        return {
            "state": self.state.value,
            "failures": self.failures,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }


class APIClient:
    """
    Main API client with HF-first + fallback logic

    Priority:
    1. HF HTTP endpoints (primary)
    2. HF WebSocket (exception-only)
    3. Fallback providers (ordered by config)
    """

    def __init__(self, hf_base_url: str = "http://localhost:8000", timeout: int = 10):
        self.hf_base_url = hf_base_url.rstrip("/")
        self.timeout = timeout
        self.config = get_fallback_config()

        # HTTP client
        self.client = httpx.AsyncClient(timeout=timeout)

        # Circuit breakers per provider
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Provider stats
        self.provider_stats: Dict[str, Dict[str, int]] = {}

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def _get_circuit_breaker(self, provider_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for provider"""
        if provider_name not in self.circuit_breakers:
            self.circuit_breakers[provider_name] = CircuitBreaker()
        return self.circuit_breakers[provider_name]

    def _record_provider_stat(self, provider_name: str, success: bool):
        """Record provider statistics"""
        if provider_name not in self.provider_stats:
            self.provider_stats[provider_name] = {"success": 0, "failure": 0}

        if success:
            self.provider_stats[provider_name]["success"] += 1
        else:
            self.provider_stats[provider_name]["failure"] += 1

    async def fetch_with_fallback(
        self,
        endpoint: str,
        category: str,
        params: Optional[Dict[str, Any]] = None,
        normalize_fn: Optional[Callable] = None,
        hf_only: bool = False,
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Main fetch method with HF-first + fallback logic

        Args:
            endpoint: HF endpoint path (e.g., "/api/market")
            category: Category for fallback lookup (e.g., "market_data")
            params: Query parameters
            normalize_fn: Function to normalize provider responses
            hf_only: If True, only try HF (no fallbacks)

        Returns:
            Tuple of (data, meta_info)

        Raises:
            Exception: If all providers fail
        """
        attempted = []
        params = params or {}

        # 1. Try HF HTTP first
        try:
            logger.info(f"Attempting HF endpoint: {endpoint}")
            attempted.append("hf")

            breaker = self._get_circuit_breaker("hf")
            if breaker.can_attempt():
                data = await self._call_hf_http(endpoint, params)
                breaker.record_success()
                self._record_provider_stat("hf", True)

                meta = self._create_meta("hf", cache_ttl=30)
                logger.info(f"✓ HF endpoint succeeded: {endpoint}")
                return data, meta
            else:
                logger.warning("HF circuit breaker is OPEN, skipping")

        except Exception as e:
            logger.warning(f"HF endpoint failed: {e}")
            breaker = self._get_circuit_breaker("hf")
            breaker.record_failure()
            self._record_provider_stat("hf", False)

        # If HF-only mode, fail here
        if hf_only:
            raise Exception(f"HF endpoint required but unavailable: {endpoint}")

        # 2. Try fallback providers
        fallback_providers = self._get_fallback_providers(category)

        for provider in fallback_providers:
            try:
                logger.info(f"Attempting fallback: {provider.name}")
                attempted.append(provider.name)

                breaker = self._get_circuit_breaker(provider.name)
                if not breaker.can_attempt():
                    logger.warning(f"Circuit breaker OPEN for {provider.name}, skipping")
                    continue

                # Call provider
                provider_data = await self._call_provider(provider, endpoint, params)

                # Normalize if function provided
                if normalize_fn:
                    data = normalize_fn(provider_data, provider.name)
                else:
                    data = provider_data

                breaker.record_success()
                self._record_provider_stat(provider.name, True)

                meta = self._create_meta(provider.name, cache_ttl=60)
                logger.info(f"✓ Fallback succeeded: {provider.name}")
                return data, meta

            except Exception as e:
                logger.warning(f"Fallback {provider.name} failed: {e}")
                breaker = self._get_circuit_breaker(provider.name)
                breaker.record_failure()
                self._record_provider_stat(provider.name, False)

        # 3. All failed
        raise Exception(f"All providers failed for {endpoint}. Attempted: {attempted}")

    async def _call_hf_http(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Call HF HTTP endpoint"""
        url = f"{self.hf_base_url}{endpoint}"

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # If response already has data, return it
        if isinstance(data, dict) and "data" in data:
            return data["data"]

        return data

    async def _call_provider(
        self, provider: ProviderConfig, endpoint: str, params: Dict[str, Any]
    ) -> Any:
        """Call external provider API"""
        # Map generic endpoint to provider-specific endpoint
        url = self._map_endpoint_to_provider(provider, endpoint, params)

        # Prepare headers
        headers = {}
        if provider.header_key and provider.key:
            headers[provider.header_key] = provider.key

        # Add API key to params if needed
        request_params = params.copy()
        if provider.key and not provider.header_key:
            request_params["apikey"] = provider.key

        # Make request
        if provider.method == "POST":
            response = await self.client.post(url, json=request_params, headers=headers)
        else:
            response = await self.client.get(url, params=request_params, headers=headers)

        response.raise_for_status()
        return response.json()

    def _map_endpoint_to_provider(
        self, provider: ProviderConfig, endpoint: str, params: Dict[str, Any]
    ) -> str:
        """Map generic endpoint to provider-specific URL"""
        base = provider.base_url

        # Market data mapping
        if "/api/market" in endpoint:
            if provider.name == "coingecko":
                if "pairs" in endpoint:
                    return f"{base}/coins/markets?vs_currency=usd&order=market_cap_desc"
                elif "ohlc" in endpoint:
                    symbol = params.get("symbol", "bitcoin").lower()
                    days = params.get("limit", 1) // 24  # Approximate
                    return f"{base}/coins/{symbol}/market_chart?vs_currency=usd&days={days}"
                else:
                    return f"{base}/coins/markets?vs_currency=usd&order=market_cap_desc"

            elif provider.name == "binance":
                if "ohlc" in endpoint:
                    symbol = params.get("symbol", "BTC") + "USDT"
                    interval = self._map_interval(params.get("interval", "1h"))
                    return f"{base}/klines?symbol={symbol}&interval={interval}"
                else:
                    return f"{base}/ticker/24hr"

            elif provider.name == "coincap":
                return f"{base}/assets"

        # News mapping
        elif "/api/news" in endpoint:
            if provider.name == "cryptopanic":
                return f"{base}/posts/?public=true"
            elif provider.name == "reddit_crypto":
                return f"{base}/hot.json?limit={params.get('limit', 20)}"

        # Sentiment mapping
        elif "/api/sentiment" in endpoint:
            if provider.name == "alternative_me":
                return f"{base}/?limit=1"

        # Whale tracking
        elif "/api/crypto/whales" in endpoint:
            if provider.name == "clankapp":
                return f"{base}/whales/recent"

        # Gas prices
        elif "/api/crypto/blockchain/gas" in endpoint:
            chain = params.get("chain", "ethereum")
            if provider.name.startswith("etherscan"):
                return f"{base}?module=gastracker&action=gasoracle"

        # Default: use base URL
        return base

    def _map_interval(self, interval: int) -> str:
        """Map interval minutes to Binance format"""
        mapping = {1: "1m", 5: "5m", 15: "15m", 60: "1h", 240: "4h", 1440: "1d"}
        return mapping.get(interval, "1h")

    def _get_fallback_providers(self, category: str) -> List[ProviderConfig]:
        """Get ordered list of fallback providers for category"""
        if category == "market_data":
            return self.config.market_data
        elif category == "news":
            return self.config.news
        elif category == "sentiment":
            return self.config.sentiment
        elif category == "whale_tracking":
            return self.config.whale_tracking
        elif category in ["ethereum", "bsc", "tron"]:
            return self.config.explorers.get(category, [])
        else:
            return []

    def _create_meta(self, source: str, cache_ttl: int = 30) -> Dict[str, Any]:
        """Create meta information for response"""
        return {
            "source": source,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "cache_ttl_seconds": cache_ttl,
        }

    def get_provider_health(self) -> Dict[str, Any]:
        """Get health status of all providers"""
        health = {}

        for name, breaker in self.circuit_breakers.items():
            stats = self.provider_stats.get(name, {"success": 0, "failure": 0})
            total = stats["success"] + stats["failure"]
            success_rate = (stats["success"] / total * 100) if total > 0 else 0

            health[name] = {
                "circuit_breaker": breaker.get_state(),
                "stats": stats,
                "success_rate": round(success_rate, 2),
            }

        return health


# Global client instance
_client: Optional[APIClient] = None


async def get_api_client() -> APIClient:
    """Get or create global API client"""
    global _client

    if _client is None:
        _client = APIClient()

    return _client


async def close_api_client():
    """Close global API client"""
    global _client

    if _client:
        await _client.close()
        _client = None

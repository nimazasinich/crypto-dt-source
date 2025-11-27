"""
Provider Fallback Manager
Manages fallback to external providers when HF cannot provide data
Uses /mnt/data/api-config-complete.txt as authoritative source
"""

import asyncio
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

from ..enhanced_logger import logger

# ====================
# CONFIGURATION
# ====================

FALLBACK_CONFIG_PATH = "/mnt/data/api-config-complete.txt"
FALLBACK_CONFIG_URL = os.getenv("FALLBACK_CONFIG_URL", None)
HF_PRIORITY = True  # Always try HF first
MAX_RETRIES = 3
TIMEOUT_SECONDS = 10
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 300  # 5 minutes

# ====================
# ENUMS & MODELS
# ====================


class ProviderStatus(Enum):
    """Provider availability status"""

    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class Provider:
    """Provider configuration"""

    name: str
    base_url: str
    api_key: Optional[str] = None
    priority: int = 100
    endpoints: Dict[str, str] = None
    rate_limit: Optional[int] = None
    status: ProviderStatus = ProviderStatus.AVAILABLE
    failures: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    circuit_open_until: Optional[datetime] = None

    def is_available(self) -> bool:
        """Check if provider is available"""
        if self.status == ProviderStatus.CIRCUIT_OPEN:
            if self.circuit_open_until and datetime.now(timezone.utc) > self.circuit_open_until:
                # Circuit breaker timeout expired, try again
                self.status = ProviderStatus.AVAILABLE
                self.failures = 0
                return True
            return False
        return self.status in [ProviderStatus.AVAILABLE, ProviderStatus.DEGRADED]

    def record_success(self):
        """Record successful request"""
        self.failures = 0
        self.last_success = datetime.now(timezone.utc)
        self.status = ProviderStatus.AVAILABLE

    def record_failure(self):
        """Record failed request"""
        self.failures += 1
        self.last_failure = datetime.now(timezone.utc)

        if self.failures >= CIRCUIT_BREAKER_THRESHOLD:
            # Open circuit breaker
            self.status = ProviderStatus.CIRCUIT_OPEN
            self.circuit_open_until = (
                datetime.now(timezone.utc).timestamp() + CIRCUIT_BREAKER_TIMEOUT
            )
            logger.warning(
                f"Circuit breaker opened for {self.name} until {self.circuit_open_until}"
            )
        elif self.failures >= 2:
            self.status = ProviderStatus.DEGRADED


@dataclass
class FallbackResult:
    """Result from fallback attempt"""

    data: Optional[Any]
    source: str
    attempted: List[str]
    success: bool
    error: Optional[str] = None
    latency_ms: Optional[int] = None


# ====================
# PROVIDER FALLBACK MANAGER
# ====================


class ProviderFallbackManager:
    """Manages fallback to external providers with circuit breaker pattern"""

    def __init__(self):
        self.providers: List[Provider] = []
        self.hf_handler = None
        self._load_providers()
        self._session: Optional[aiohttp.ClientSession] = None

    def _load_providers(self):
        """Load provider configurations from file or URL"""
        config_data = None

        # Try local file first
        if Path(FALLBACK_CONFIG_PATH).exists():
            try:
                with open(FALLBACK_CONFIG_PATH, "r") as f:
                    content = f.read()
                    # Handle both JSON and text format
                    if content.strip().startswith("{"):
                        config_data = json.loads(content)
                    else:
                        # Parse text format
                        config_data = self._parse_text_config(content)
                logger.info(
                    f"Loaded {len(config_data.get('providers', []))} providers from local file"
                )
            except Exception as e:
                logger.error(f"Failed to load local config: {e}")

        # Try URL if configured
        if not config_data and FALLBACK_CONFIG_URL:
            try:
                import requests

                response = requests.get(FALLBACK_CONFIG_URL, timeout=5)
                if response.status_code == 200:
                    config_data = response.json()
                    logger.info(
                        f"Loaded {len(config_data.get('providers', []))} providers from URL"
                    )
            except Exception as e:
                logger.error(f"Failed to load config from URL: {e}")

        # Parse providers
        if config_data and "providers" in config_data:
            for idx, provider_config in enumerate(config_data["providers"]):
                provider = Provider(
                    name=provider_config.get("name", f"provider_{idx}"),
                    base_url=provider_config.get("base_url", ""),
                    api_key=provider_config.get("api_key")
                    or os.getenv(f"{provider_config.get('name', '').upper()}_API_KEY"),
                    priority=provider_config.get("priority", 100),
                    endpoints=provider_config.get("endpoints", {}),
                    rate_limit=provider_config.get("rate_limit"),
                )
                self.providers.append(provider)

        # Sort by priority (lower number = higher priority)
        self.providers.sort(key=lambda p: p.priority)

        # Add default providers if none loaded
        if not self.providers:
            self._add_default_providers()

    def _parse_text_config(self, content: str) -> Dict:
        """Parse text format config into JSON structure"""
        providers = []
        lines = content.strip().split("\n")

        for line in lines:
            if line.strip() and not line.startswith("#"):
                parts = line.split(",")
                if len(parts) >= 2:
                    providers.append(
                        {
                            "name": parts[0].strip(),
                            "base_url": parts[1].strip(),
                            "api_key": parts[2].strip() if len(parts) > 2 else None,
                            "priority": int(parts[3].strip()) if len(parts) > 3 else 100,
                        }
                    )

        return {"providers": providers}

    def _add_default_providers(self):
        """Add default fallback providers"""
        defaults = [
            Provider(
                name="coingecko",
                base_url="https://api.coingecko.com/api/v3",
                priority=10,
                endpoints={
                    "rate": "/simple/price",
                    "market": "/coins/markets",
                    "history": "/coins/{id}/market_chart",
                },
            ),
            Provider(
                name="binance",
                base_url="https://api.binance.com/api/v3",
                priority=20,
                endpoints={"rate": "/ticker/price", "history": "/klines", "depth": "/depth"},
            ),
            Provider(
                name="coinmarketcap",
                base_url="https://pro-api.coinmarketcap.com/v1",
                api_key=os.getenv("CMC_API_KEY"),
                priority=30,
                endpoints={
                    "rate": "/cryptocurrency/quotes/latest",
                    "market": "/cryptocurrency/listings/latest",
                },
            ),
        ]

        self.providers.extend(defaults)
        logger.info(f"Added {len(defaults)} default providers")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if not self._session:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
            )
        return self._session

    async def close(self):
        """Close aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None

    async def _call_hf(
        self, endpoint: str, params: Dict = None
    ) -> Tuple[Optional[Any], Optional[str]]:
        """Try to get data from HF first"""
        if not HF_PRIORITY:
            return None, None

        try:
            # This would call actual HF models/datasets
            # For now, simulate HF response
            logger.debug(f"Attempting HF for {endpoint}")

            # Simulate HF response based on endpoint
            if "/pair" in endpoint:
                # Pair metadata MUST come from HF
                return {
                    "pair": params.get("pair", "BTC/USDT"),
                    "base": "BTC",
                    "quote": "USDT",
                    "tick_size": 0.01,
                    "min_qty": 0.00001,
                }, None

            # For other endpoints, simulate occasional failure to test fallback
            import random

            if random.random() > 0.3:  # 70% success rate for testing
                return None, "HF data not available"

            return {"source": "hf", "data": "sample"}, None

        except Exception as e:
            logger.debug(f"HF call failed: {e}")
            return None, str(e)

    async def _call_provider(
        self, provider: Provider, endpoint: str, params: Dict = None, method: str = "GET"
    ) -> Tuple[Optional[Any], Optional[str]]:
        """Call a specific provider"""

        if not provider.is_available():
            return None, f"Provider {provider.name} unavailable (circuit open)"

        try:
            session = await self._get_session()

            # Build URL
            url = f"{provider.base_url}{endpoint}"

            # Add API key if needed
            headers = {}
            if provider.api_key:
                # Different providers use different auth methods
                if "coinmarketcap" in provider.name.lower():
                    headers["X-CMC_PRO_API_KEY"] = provider.api_key
                elif "alphavantage" in provider.name.lower():
                    if params is None:
                        params = {}
                    params["apikey"] = provider.api_key
                else:
                    headers["Authorization"] = f"Bearer {provider.api_key}"

            # Make request
            start_time = datetime.now(timezone.utc)

            if method == "GET":
                async with session.get(url, params=params, headers=headers) as response:
                    latency_ms = int(
                        (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    )

                    if response.status == 200:
                        data = await response.json()
                        provider.record_success()
                        logger.debug(f"Provider {provider.name} succeeded in {latency_ms}ms")
                        return data, None
                    else:
                        error = f"HTTP {response.status}"
                        provider.record_failure()
                        return None, error

            elif method == "POST":
                async with session.post(url, json=params, headers=headers) as response:
                    latency_ms = int(
                        (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    )

                    if response.status == 200:
                        data = await response.json()
                        provider.record_success()
                        logger.debug(f"Provider {provider.name} succeeded in {latency_ms}ms")
                        return data, None
                    else:
                        error = f"HTTP {response.status}"
                        provider.record_failure()
                        return None, error

        except asyncio.TimeoutError:
            provider.record_failure()
            return None, "Timeout"

        except Exception as e:
            provider.record_failure()
            logger.error(f"Provider {provider.name} error: {e}")
            return None, str(e)

    async def fetch_with_fallback(
        self,
        endpoint: str,
        params: Dict = None,
        method: str = "GET",
        transform_func: callable = None,
    ) -> FallbackResult:
        """
        Fetch data with HF-first then fallback strategy

        Args:
            endpoint: API endpoint path
            params: Query parameters
            method: HTTP method
            transform_func: Function to transform provider response to standard format

        Returns:
            FallbackResult with data, source, and metadata
        """

        attempted = []
        start_time = datetime.now(timezone.utc)

        # 1. Try HF first
        if HF_PRIORITY:
            attempted.append("hf")
            hf_data, hf_error = await self._call_hf(endpoint, params)

            if hf_data:
                latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                return FallbackResult(
                    data=hf_data,
                    source="hf",
                    attempted=attempted,
                    success=True,
                    latency_ms=latency_ms,
                )

        # 2. Try fallback providers in priority order
        for provider in self.providers:
            if not provider.is_available():
                logger.debug(f"Skipping unavailable provider {provider.name}")
                continue

            attempted.append(provider.base_url)

            # Map endpoint to provider-specific endpoint if configured
            provider_endpoint = endpoint
            if provider.endpoints:
                # Find matching endpoint pattern
                for key, value in provider.endpoints.items():
                    if key in endpoint:
                        provider_endpoint = value
                        break

            # Call provider
            data, error = await self._call_provider(provider, provider_endpoint, params, method)

            if data:
                # Transform data if function provided
                if transform_func:
                    try:
                        data = transform_func(data, provider.name)
                    except Exception as e:
                        logger.error(f"Transform failed for {provider.name}: {e}")
                        continue

                latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                return FallbackResult(
                    data=data,
                    source=provider.base_url,
                    attempted=attempted,
                    success=True,
                    latency_ms=latency_ms,
                )

        # All failed
        latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        return FallbackResult(
            data=None,
            source="none",
            attempted=attempted,
            success=False,
            error="All providers failed",
            latency_ms=latency_ms,
        )

    def get_provider_status(self) -> Dict[str, Any]:
        """Get current status of all providers"""

        status = {"timestamp": datetime.now(timezone.utc).isoformat(), "providers": []}

        for provider in self.providers:
            status["providers"].append(
                {
                    "name": provider.name,
                    "base_url": provider.base_url,
                    "priority": provider.priority,
                    "status": provider.status.value,
                    "failures": provider.failures,
                    "is_available": provider.is_available(),
                    "last_success": (
                        provider.last_success.isoformat() if provider.last_success else None
                    ),
                    "last_failure": (
                        provider.last_failure.isoformat() if provider.last_failure else None
                    ),
                    "circuit_open_until": (
                        provider.circuit_open_until if provider.circuit_open_until else None
                    ),
                }
            )

        # Count available providers
        available_count = sum(1 for p in self.providers if p.is_available())
        status["available_providers"] = available_count
        status["total_providers"] = len(self.providers)
        status["hf_priority"] = HF_PRIORITY

        return status

    def reset_provider(self, provider_name: str) -> bool:
        """Reset a specific provider's circuit breaker"""

        for provider in self.providers:
            if provider.name == provider_name:
                provider.status = ProviderStatus.AVAILABLE
                provider.failures = 0
                provider.circuit_open_until = None
                logger.info(f"Reset provider {provider_name}")
                return True

        return False

    def reset_all_providers(self):
        """Reset all providers' circuit breakers"""

        for provider in self.providers:
            provider.status = ProviderStatus.AVAILABLE
            provider.failures = 0
            provider.circuit_open_until = None

        logger.info("Reset all providers")


# ====================
# TRANSFORM FUNCTIONS
# ====================


def transform_coingecko_rate(data: Dict, provider: str) -> Dict:
    """Transform CoinGecko rate response to standard format"""
    # CoinGecko returns: {"bitcoin": {"usd": 50000}}
    if data and isinstance(data, dict):
        for coin, prices in data.items():
            for currency, price in prices.items():
                return {
                    "pair": f"{coin.upper()}/{currency.upper()}",
                    "price": price,
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
    return data


def transform_binance_rate(data: Dict, provider: str) -> Dict:
    """Transform Binance rate response to standard format"""
    # Binance returns: {"symbol": "BTCUSDT", "price": "50000.00"}
    if data and "symbol" in data:
        return {
            "pair": f"{data['symbol'][:-4]}/{data['symbol'][-4:]}",  # Assumes 4-char quote
            "price": float(data["price"]),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
    return data


# ====================
# SINGLETON INSTANCE
# ====================

# Create singleton instance
fallback_manager = ProviderFallbackManager()

# Export for use in routers
__all__ = [
    "ProviderFallbackManager",
    "FallbackResult",
    "Provider",
    "ProviderStatus",
    "fallback_manager",
    "transform_coingecko_rate",
    "transform_binance_rate",
]

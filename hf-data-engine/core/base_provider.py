"""Base provider interface for data sources"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import time
import httpx
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.models import OHLCV, Price, ProviderHealth


class CircuitBreaker:
    """Circuit breaker for provider failures"""

    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.is_open = False

    def record_success(self):
        """Record successful request"""
        self.failures = 0
        self.is_open = False

    def record_failure(self):
        """Record failed request"""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.threshold:
            self.is_open = True

    def can_attempt(self) -> bool:
        """Check if we can attempt a request"""
        if not self.is_open:
            return True

        # Check if timeout has passed
        if self.last_failure_time:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.timeout:
                self.is_open = False
                self.failures = 0
                return True

        return False


class BaseProvider(ABC):
    """Base class for all data providers"""

    def __init__(self, name: str, base_url: str, timeout: int = 10):
        self.name = name
        self.base_url = base_url
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker()
        self.last_latency: Optional[int] = None
        self.last_check: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=self.timeout)
        return self.client

    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def _make_request(self, url: str, params: Optional[dict] = None) -> dict:
        """Make HTTP request with timing and error handling"""
        if not self.circuit_breaker.can_attempt():
            raise Exception(f"Circuit breaker open for {self.name}")

        client = await self.get_client()
        start_time = time.time()

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()

            self.last_latency = int((time.time() - start_time) * 1000)
            self.last_check = datetime.now()
            self.last_error = None
            self.circuit_breaker.record_success()

            return response.json()

        except Exception as e:
            self.last_error = str(e)
            self.circuit_breaker.record_failure()
            raise

    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int) -> List[OHLCV]:
        """Fetch OHLCV data"""
        pass

    @abstractmethod
    async def fetch_prices(self, symbols: List[str]) -> List[Price]:
        """Fetch current prices"""
        pass

    async def get_health(self) -> ProviderHealth:
        """Get provider health status"""
        if self.circuit_breaker.is_open:
            status = "offline"
        elif self.last_error:
            status = "degraded"
        else:
            status = "online"

        return ProviderHealth(
            name=self.name,
            status=status,
            latency=self.last_latency,
            lastCheck=self.last_check.isoformat() if self.last_check else datetime.now().isoformat(),
            errorMessage=self.last_error
        )

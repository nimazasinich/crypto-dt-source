"""
API Fallback Manager
Automatically switches to alternative API providers when primary fails
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider status"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    COOLDOWN = "cooldown"


class APIProvider:
    """Represents an API provider with health tracking"""
    
    def __init__(
        self,
        name: str,
        priority: int,
        fetch_function: Callable,
        cooldown_seconds: int = 300,
        max_failures: int = 3
    ):
        self.name = name
        self.priority = priority
        self.fetch_function = fetch_function
        self.cooldown_seconds = cooldown_seconds
        self.max_failures = max_failures
        
        self.failures = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.status = ProviderStatus.ACTIVE
        self.last_failure_time = None
        self.last_success_time = None
    
    def record_success(self):
        """Record successful request"""
        self.successful_requests += 1
        self.total_requests += 1
        self.failures = 0  # Reset failures on success
        self.status = ProviderStatus.ACTIVE
        self.last_success_time = datetime.now()
        logger.info(f"✅ {self.name}: Success (total: {self.successful_requests}/{self.total_requests})")
    
    def record_failure(self, error: Exception):
        """Record failed request"""
        self.failures += 1
        self.total_requests += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.max_failures:
            self.status = ProviderStatus.COOLDOWN
            logger.warning(
                f"❌ {self.name}: Entering cooldown after {self.failures} failures. "
                f"Last error: {str(error)}"
            )
        else:
            self.status = ProviderStatus.DEGRADED
            logger.warning(f"⚠️  {self.name}: Failure {self.failures}/{self.max_failures} - {str(error)}")
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        if self.status == ProviderStatus.COOLDOWN:
            # Check if cooldown period has passed
            if self.last_failure_time:
                cooldown_end = self.last_failure_time + timedelta(seconds=self.cooldown_seconds)
                if datetime.now() >= cooldown_end:
                    self.status = ProviderStatus.ACTIVE
                    self.failures = 0
                    logger.info(f"🔄 {self.name}: Cooldown ended, provider reactivated")
                    return True
            return False
        
        return self.status in [ProviderStatus.ACTIVE, ProviderStatus.DEGRADED]
    
    def get_health_score(self) -> float:
        """Get health score (0-100)"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100


class APIFallbackManager:
    """
    Manages API fallback across multiple providers
    
    Usage:
        manager = APIFallbackManager("OHLCV")
        manager.add_provider("Binance", 1, fetch_binance_ohlcv)
        manager.add_provider("CoinGecko", 2, fetch_coingecko_ohlcv)
        
        result = await manager.fetch_with_fallback(symbol="BTC", timeframe="1h")
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.providers: List[APIProvider] = []
        logger.info(f"📡 Initialized fallback manager for {service_name}")
    
    def add_provider(
        self,
        name: str,
        priority: int,
        fetch_function: Callable,
        cooldown_seconds: int = 300,
        max_failures: int = 3
    ):
        """Add a provider to the fallback chain"""
        provider = APIProvider(name, priority, fetch_function, cooldown_seconds, max_failures)
        self.providers.append(provider)
        # Sort by priority (lower number = higher priority)
        self.providers.sort(key=lambda p: p.priority)
        logger.info(f"✅ Added provider '{name}' (priority: {priority}) to {self.service_name}")
    
    async def fetch_with_fallback(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch data with automatic fallback
        
        Args:
            **kwargs: Parameters to pass to fetch functions
        
        Returns:
            Dict with:
                - success: bool
                - data: Any (if successful)
                - provider: str (which provider succeeded)
                - attempts: List of attempts
                - error: str (if all failed)
        """
        attempts = []
        last_error = None
        
        for provider in self.providers:
            if not provider.is_available():
                attempts.append({
                    "provider": provider.name,
                    "status": "skipped",
                    "reason": f"Provider in {provider.status.value} state"
                })
                continue
            
            try:
                logger.info(f"🔄 {self.service_name}: Trying {provider.name}...")
                start_time = datetime.now()
                
                # Call the provider's fetch function
                data = await provider.fetch_function(**kwargs)
                
                duration = (datetime.now() - start_time).total_seconds()
                provider.record_success()
                
                attempts.append({
                    "provider": provider.name,
                    "status": "success",
                    "duration": duration
                })
                
                logger.info(
                    f"✅ {self.service_name}: {provider.name} succeeded in {duration:.2f}s"
                )
                
                return {
                    "success": True,
                    "data": data,
                    "provider": provider.name,
                    "attempts": attempts,
                    "health_score": provider.get_health_score()
                }
            
            except Exception as e:
                last_error = e
                provider.record_failure(e)
                
                attempts.append({
                    "provider": provider.name,
                    "status": "failed",
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                
                logger.warning(
                    f"❌ {self.service_name}: {provider.name} failed - {str(e)}"
                )
        
        # All providers failed
        logger.error(
            f"🚨 {self.service_name}: ALL PROVIDERS FAILED! "
            f"Tried {len(attempts)} provider(s)"
        )
        
        return {
            "success": False,
            "data": None,
            "provider": None,
            "attempts": attempts,
            "error": f"All providers failed. Last error: {str(last_error)}"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            "service": self.service_name,
            "providers": [
                {
                    "name": p.name,
                    "priority": p.priority,
                    "status": p.status.value,
                    "health_score": p.get_health_score(),
                    "total_requests": p.total_requests,
                    "successful_requests": p.successful_requests,
                    "failures": p.failures,
                    "available": p.is_available()
                }
                for p in self.providers
            ]
        }


# Example usage patterns:

async def example_ohlcv_binance(symbol: str, timeframe: str, limit: int = 100):
    """Example: Fetch from Binance"""
    from backend.services.binance_client import BinanceClient
    client = BinanceClient()
    return await client.get_ohlcv(symbol, timeframe=timeframe, limit=limit)


async def example_ohlcv_coingecko(symbol: str, timeframe: str, limit: int = 100):
    """Example: Fetch from CoinGecko (would need implementation)"""
    # Implementation would go here
    raise NotImplementedError("CoinGecko OHLCV not implemented yet")


async def example_news_newsapi(q: str, **kwargs):
    """Example: Fetch news from NewsAPI"""
    import httpx
    api_key = "968a5e25552b4cb5ba3280361d8444ab"
    url = f"https://newsapi.org/v2/everything?q={q}&sortBy=publishedAt&apiKey={api_key}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()


async def example_news_cryptocompare(q: str, **kwargs):
    """Example: Fetch news from CryptoCompare"""
    import httpx
    url = f"https://min-api.cryptocompare.com/data/v2/news/?categories={q}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()


# Global managers (singleton pattern)
_managers: Dict[str, APIFallbackManager] = {}


def get_fallback_manager(service_name: str) -> APIFallbackManager:
    """Get or create a fallback manager for a service"""
    if service_name not in _managers:
        _managers[service_name] = APIFallbackManager(service_name)
    return _managers[service_name]


def get_all_managers_status() -> Dict[str, Any]:
    """Get status of all fallback managers"""
    return {
        name: manager.get_status()
        for name, manager in _managers.items()
    }


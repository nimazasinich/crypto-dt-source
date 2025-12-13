#!/usr/bin/env python3
"""
Enhanced Provider Manager - Universal Load Balancing for All Data Types
Extends the existing intelligent provider service to support:
- Market data (prices, charts, OHLCV)
- News (crypto news feeds)
- Sentiment (Fear & Greed, social sentiment)
- AI/Predictions (analysis, sentiment analysis)
- Technical data (indicators, correlations)
- Metadata (exchanges, coin lists)

Integrates:
- Binance DNS connector (multi-endpoint failover)
- Render.com backup service
- CoinGecko, CoinPaprika, CoinCap
- CryptoCompare, Alternative.me
- RSS feeds
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import httpx

from backend.services.binance_dns_connector import get_binance_connector, BinanceDNSConnector
from backend.services.crypto_dt_source_client import get_crypto_dt_source_service

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class DataCategory(Enum):
    """Data category types"""
    MARKET_PRICE = "market_price"           # Real-time prices
    MARKET_OHLCV = "market_ohlcv"           # Candlestick/historical data
    MARKET_VOLUME = "market_volume"         # Trading volume data
    MARKET_ORDERBOOK = "market_orderbook"   # Order book depth
    MARKET_METADATA = "market_metadata"     # Exchanges, coins list
    NEWS = "news"                           # Crypto news
    SENTIMENT = "sentiment"                 # Fear & Greed, sentiment
    AI_PREDICTION = "ai_prediction"         # Price predictions
    TECHNICAL = "technical"                 # Technical indicators
    SOCIAL = "social"                       # Social media data


@dataclass
class Provider:
    """Provider configuration and health tracking"""
    name: str
    category: DataCategory
    priority: int  # 1=highest, 2=backup, 3=fallback, 4=ultimate fallback
    fetch_func: Callable  # Async function to fetch data
    status: ProviderStatus = ProviderStatus.HEALTHY
    last_check: Optional[datetime] = None
    response_time: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    backoff_until: float = 0
    cache_duration: int = 30  # seconds
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 100.0
        return (self.success_count / total) * 100
    
    @property
    def is_available(self) -> bool:
        """Check if provider is available (not in backoff)"""
        return time.time() >= self.backoff_until
    
    @property
    def load_score(self) -> float:
        """Calculate load score (lower is better)"""
        now = time.time()
        score = 100 - self.success_rate
        
        # Penalty for recent failures
        score += self.consecutive_failures * 10
        
        # Penalty for being in backoff
        if not self.is_available:
            score += 1000
        
        return score


class EnhancedProviderManager:
    """
    Universal provider manager with intelligent load balancing
    
    Features:
    - Category-based provider registration
    - Round-robin with health-based selection
    - Circuit breaker pattern
    - Exponential backoff
    - Multi-provider failover
    - Binance DNS failover integration
    - Render.com ultimate fallback
    """
    
    def __init__(self):
        self.providers: Dict[DataCategory, List[Provider]] = {
            category: [] for category in DataCategory
        }
        self.circuit_breaker_threshold = 3
        self.binance_connector = get_binance_connector(use_us=False)
        self.render_service = get_crypto_dt_source_service()
        
        logger.info("🚀 Enhanced Provider Manager initialized")
        
        # Auto-register all providers
        self._register_all_providers()
    
    def _register_all_providers(self):
        """Register all available providers for each category"""
        
        # ===== MARKET PRICE PROVIDERS =====
        self.register_provider(Provider(
            name="Binance",
            category=DataCategory.MARKET_PRICE,
            priority=1,
            fetch_func=self._fetch_binance_price,
            cache_duration=10
        ))
        
        self.register_provider(Provider(
            name="CoinCap",
            category=DataCategory.MARKET_PRICE,
            priority=2,
            fetch_func=self._fetch_coincap_price,
            cache_duration=30
        ))
        
        self.register_provider(Provider(
            name="CoinGecko",
            category=DataCategory.MARKET_PRICE,
            priority=2,
            fetch_func=self._fetch_coingecko_price,
            cache_duration=60
        ))
        
        self.register_provider(Provider(
            name="Render-Backup",
            category=DataCategory.MARKET_PRICE,
            priority=4,
            fetch_func=self._fetch_render_price,
            cache_duration=30
        ))
        
        # ===== MARKET OHLCV PROVIDERS =====
        self.register_provider(Provider(
            name="Binance",
            category=DataCategory.MARKET_OHLCV,
            priority=1,
            fetch_func=self._fetch_binance_ohlcv,
            cache_duration=60
        ))
        
        self.register_provider(Provider(
            name="CryptoCompare",
            category=DataCategory.MARKET_OHLCV,
            priority=2,
            fetch_func=self._fetch_cryptocompare_ohlcv,
            cache_duration=60
        ))
        
        self.register_provider(Provider(
            name="Render-Backup",
            category=DataCategory.MARKET_OHLCV,
            priority=4,
            fetch_func=self._fetch_render_ohlcv,
            cache_duration=60
        ))
        
        # ===== MARKET VOLUME PROVIDERS =====
        self.register_provider(Provider(
            name="Binance",
            category=DataCategory.MARKET_VOLUME,
            priority=1,
            fetch_func=self._fetch_binance_volume,
            cache_duration=30
        ))
        
        # ===== MARKET ORDERBOOK PROVIDERS =====
        self.register_provider(Provider(
            name="Binance",
            category=DataCategory.MARKET_ORDERBOOK,
            priority=1,
            fetch_func=self._fetch_binance_orderbook,
            cache_duration=5
        ))
        
        # ===== MARKET METADATA PROVIDERS =====
        self.register_provider(Provider(
            name="CoinGecko",
            category=DataCategory.MARKET_METADATA,
            priority=1,
            fetch_func=self._fetch_coingecko_metadata,
            cache_duration=3600  # 1 hour
        ))
        
        self.register_provider(Provider(
            name="CoinPaprika",
            category=DataCategory.MARKET_METADATA,
            priority=2,
            fetch_func=self._fetch_coinpaprika_metadata,
            cache_duration=3600
        ))
        
        # ===== NEWS PROVIDERS =====
        self.register_provider(Provider(
            name="CryptoCompare",
            category=DataCategory.NEWS,
            priority=1,
            fetch_func=self._fetch_cryptocompare_news,
            cache_duration=300  # 5 min
        ))
        
        self.register_provider(Provider(
            name="Render-Backup",
            category=DataCategory.NEWS,
            priority=3,
            fetch_func=self._fetch_render_news,
            cache_duration=300
        ))
        
        # ===== SENTIMENT PROVIDERS =====
        self.register_provider(Provider(
            name="Alternative.me",
            category=DataCategory.SENTIMENT,
            priority=1,
            fetch_func=self._fetch_alternative_sentiment,
            cache_duration=3600  # 1 hour
        ))
        
        self.register_provider(Provider(
            name="Render-Backup",
            category=DataCategory.SENTIMENT,
            priority=3,
            fetch_func=self._fetch_render_sentiment,
            cache_duration=3600
        ))
        
        logger.info(f"✅ Registered providers for {len(self.providers)} categories")
    
    def register_provider(self, provider: Provider):
        """Register a provider for a specific category"""
        self.providers[provider.category].append(provider)
        logger.debug(f"📝 Registered {provider.name} for {provider.category.value} (priority {provider.priority})")
    
    async def fetch_data(
        self,
        category: DataCategory,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data with intelligent provider selection and failover
        
        Args:
            category: Data category to fetch
            **kwargs: Parameters to pass to provider fetch function
        
        Returns:
            Data dict with provider info or None if all failed
        """
        providers = self.providers.get(category, [])
        
        if not providers:
            logger.error(f"❌ No providers registered for {category.value}")
            return None
        
        # Sort by priority and load score
        sorted_providers = sorted(
            [p for p in providers if p.is_available],
            key=lambda p: (p.priority, p.load_score)
        )
        
        if not sorted_providers:
            logger.warning(f"⚠️ All providers for {category.value} in backoff!")
            sorted_providers = sorted(providers, key=lambda p: p.backoff_until)
        
        # Try each provider in order
        for provider in sorted_providers:
            start_time = time.time()
            
            try:
                logger.debug(f"🔄 Trying {provider.name} for {category.value}...")
                
                result = await provider.fetch_func(**kwargs)
                
                if result:
                    response_time = time.time() - start_time
                    self._record_success(provider, response_time)
                    
                    return {
                        "success": True,
                        "data": result,
                        "provider": provider.name,
                        "category": category.value,
                        "response_time": response_time,
                        "timestamp": datetime.now().isoformat()
                    }
            
            except Exception as e:
                logger.error(f"❌ {provider.name} failed for {category.value}: {e}")
                self._record_failure(provider, str(e))
        
        logger.error(f"❌ All providers failed for {category.value}")
        return {
            "success": False,
            "data": None,
            "error": "All providers failed",
            "category": category.value,
            "timestamp": datetime.now().isoformat()
        }
    
    def _record_success(self, provider: Provider, response_time: float):
        """Record successful request"""
        provider.consecutive_failures = 0
        provider.success_count += 1
        provider.status = ProviderStatus.HEALTHY
        provider.response_time = response_time
        provider.last_check = datetime.now()
        provider.backoff_until = 0
        
        logger.info(
            f"✅ {provider.name} ({provider.category.value}): "
            f"{response_time*1000:.0f}ms, {provider.success_rate:.1f}% success"
        )
    
    def _record_failure(self, provider: Provider, error: str):
        """Record failed request with exponential backoff"""
        provider.consecutive_failures += 1
        provider.failure_count += 1
        provider.last_check = datetime.now()
        
        # Exponential backoff: 2^failures seconds (max 300s)
        backoff_duration = min(2 ** provider.consecutive_failures, 300)
        provider.backoff_until = time.time() + backoff_duration
        
        if provider.consecutive_failures >= self.circuit_breaker_threshold:
            provider.status = ProviderStatus.DOWN
        else:
            provider.status = ProviderStatus.DEGRADED
        
        logger.warning(
            f"❌ {provider.name} ({provider.category.value}): {error} "
            f"(failures: {provider.consecutive_failures}, backoff: {backoff_duration}s)"
        )
    
    # ===== PROVIDER FETCH FUNCTIONS =====
    
    async def _fetch_binance_price(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """Fetch price from Binance with DNS failover"""
        result = await self.binance_connector.get(
            "/api/v3/ticker/price",
            params={"symbol": symbol}
        )
        return result
    
    async def _fetch_binance_ohlcv(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1h",
        limit: int = 100
    ) -> Optional[Dict]:
        """Fetch OHLCV from Binance"""
        result = await self.binance_connector.get(
            "/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit}
        )
        return result
    
    async def _fetch_binance_volume(self, symbol: Optional[str] = None) -> Optional[Dict]:
        """Fetch volume data from Binance"""
        params = {"symbol": f"{symbol}USDT"} if symbol else {}
        result = await self.binance_connector.get("/api/v3/ticker/24hr", params=params)
        return result
    
    async def _fetch_binance_orderbook(
        self,
        symbol: str = "BTCUSDT",
        limit: int = 100
    ) -> Optional[Dict]:
        """Fetch orderbook from Binance"""
        result = await self.binance_connector.get(
            "/api/v3/depth",
            params={"symbol": symbol, "limit": limit}
        )
        return result
    
    async def _fetch_coincap_price(self, coin_id: str = "bitcoin") -> Optional[Dict]:
        """Fetch price from CoinCap"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://api.coincap.io/v2/assets/{coin_id}")
            response.raise_for_status()
            return response.json()
    
    async def _fetch_coingecko_price(self, coin_id: str = "bitcoin") -> Optional[Dict]:
        """Fetch price from CoinGecko"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.coingecko.com/api/v3/simple/price",
                params={"ids": coin_id, "vs_currencies": "usd"}
            )
            response.raise_for_status()
            return response.json()
    
    async def _fetch_coingecko_metadata(self, data_type: str = "exchanges") -> Optional[Dict]:
        """Fetch metadata from CoinGecko"""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"https://api.coingecko.com/api/v3/{data_type}")
            response.raise_for_status()
            return response.json()
    
    async def _fetch_coinpaprika_metadata(self, data_type: str = "coins") -> Optional[Dict]:
        """Fetch metadata from CoinPaprika"""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"https://api.coinpaprika.com/v1/{data_type}")
            response.raise_for_status()
            return response.json()
    
    async def _fetch_cryptocompare_ohlcv(
        self,
        symbol: str = "BTC",
        interval: str = "hour",
        limit: int = 100
    ) -> Optional[Dict]:
        """Fetch OHLCV from CryptoCompare"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            endpoint = f"histo{interval}" if interval in ["day", "hour", "minute"] else "histohour"
            response = await client.get(
                f"https://min-api.cryptocompare.com/data/v2/{endpoint}",
                params={"fsym": symbol, "tsym": "USD", "limit": limit}
            )
            response.raise_for_status()
            return response.json()
    
    async def _fetch_cryptocompare_news(self, limit: int = 50) -> Optional[Dict]:
        """Fetch news from CryptoCompare"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://min-api.cryptocompare.com/data/v2/news/",
                params={"lang": "EN"}
            )
            response.raise_for_status()
            return response.json()
    
    async def _fetch_alternative_sentiment(self, limit: int = 1) -> Optional[Dict]:
        """Fetch Fear & Greed Index from Alternative.me"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.alternative.me/fng/",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
    
    async def _fetch_render_price(self, coin_id: str = "bitcoin") -> Optional[Dict]:
        """Fetch price from Render backup service"""
        result = await self.render_service.get_coingecko_price(ids=coin_id)
        return result.get("data") if result.get("success") else None
    
    async def _fetch_render_ohlcv(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1h",
        limit: int = 100
    ) -> Optional[Dict]:
        """Fetch OHLCV from Render backup service"""
        result = await self.render_service.get_binance_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )
        return result.get("data") if result.get("success") else None
    
    async def _fetch_render_news(self, feed_name: str = "coindesk", limit: int = 20) -> Optional[Dict]:
        """Fetch news from Render backup service"""
        result = await self.render_service.get_rss_feed(feed_name=feed_name, limit=limit)
        return result.get("data") if result.get("success") else None
    
    async def _fetch_render_sentiment(self, limit: int = 1) -> Optional[Dict]:
        """Fetch sentiment from Render backup service"""
        result = await self.render_service.get_fear_greed_index(limit=limit)
        return result.get("data") if result.get("success") else None
    
    def get_provider_health(self) -> Dict[str, Any]:
        """Get health status of all providers"""
        health_data = {}
        
        for category, providers in self.providers.items():
            health_data[category.value] = [
                {
                    "name": p.name,
                    "priority": p.priority,
                    "status": p.status.value,
                    "available": p.is_available,
                    "success_rate": f"{p.success_rate:.1f}%",
                    "consecutive_failures": p.consecutive_failures,
                    "response_time_ms": f"{p.response_time*1000:.0f}",
                    "last_check": p.last_check.isoformat() if p.last_check else None
                }
                for p in sorted(providers, key=lambda x: x.priority)
            ]
        
        # Add Binance connector health
        binance_health = self.binance_connector.get_health_status()
        health_data["binance_dns"] = binance_health
        
        return health_data


# ===== GLOBAL INSTANCE =====

_enhanced_provider_manager: Optional[EnhancedProviderManager] = None


def get_enhanced_provider_manager() -> EnhancedProviderManager:
    """Get singleton instance of enhanced provider manager"""
    global _enhanced_provider_manager
    if _enhanced_provider_manager is None:
        _enhanced_provider_manager = EnhancedProviderManager()
    return _enhanced_provider_manager


# ===== CONVENIENCE FUNCTIONS =====

async def fetch_market_price(symbol: str = "BTCUSDT") -> Optional[Dict]:
    """Fetch market price with intelligent failover"""
    manager = get_enhanced_provider_manager()
    return await manager.fetch_data(DataCategory.MARKET_PRICE, symbol=symbol)


async def fetch_market_ohlcv(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100) -> Optional[Dict]:
    """Fetch OHLCV data with intelligent failover"""
    manager = get_enhanced_provider_manager()
    return await manager.fetch_data(
        DataCategory.MARKET_OHLCV,
        symbol=symbol,
        interval=interval,
        limit=limit
    )


async def fetch_news(limit: int = 50) -> Optional[Dict]:
    """Fetch news with intelligent failover"""
    manager = get_enhanced_provider_manager()
    return await manager.fetch_data(DataCategory.NEWS, limit=limit)


async def fetch_sentiment(limit: int = 1) -> Optional[Dict]:
    """Fetch sentiment with intelligent failover"""
    manager = get_enhanced_provider_manager()
    return await manager.fetch_data(DataCategory.SENTIMENT, limit=limit)

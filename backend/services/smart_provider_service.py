"""
Smart Provider Service with Rate Limiting, Caching, and Intelligent Fallback
Fixes: CoinGecko 429 errors, smart provider rotation, exponential backoff
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import httpx
import hashlib
import json

logger = logging.getLogger(__name__)


class ProviderPriority(Enum):
    """Provider priority levels (lower number = higher priority)"""
    PRIMARY = 1      # Binance - unlimited, use first
    SECONDARY = 2    # HuggingFace Space, CoinCap
    FALLBACK = 3     # CoinGecko - use only as last resort


@dataclass
class ProviderStats:
    """Track provider statistics and health"""
    name: str
    priority: ProviderPriority
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_hits: int = 0
    last_request_time: float = 0
    last_success_time: float = 0
    last_error_time: float = 0
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    backoff_until: float = 0  # Exponential backoff timestamp
    cache_duration: int = 30  # Default cache duration in seconds
    
    def is_available(self) -> bool:
        """Check if provider is available (not in backoff)"""
        return time.time() >= self.backoff_until
    
    def record_success(self):
        """Record successful request"""
        self.total_requests += 1
        self.successful_requests += 1
        self.last_request_time = time.time()
        self.last_success_time = time.time()
        self.consecutive_failures = 0
        self.backoff_until = 0  # Reset backoff on success
    
    def record_failure(self, error: str, is_rate_limit: bool = False):
        """Record failed request with exponential backoff"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_request_time = time.time()
        self.last_error_time = time.time()
        self.last_error = error
        self.consecutive_failures += 1
        
        if is_rate_limit:
            self.rate_limit_hits += 1
            # Aggressive backoff for rate limits: 60s, 120s, 300s, 600s
            backoff_seconds = min(60 * (2 ** min(self.consecutive_failures - 1, 3)), 600)
            logger.warning(f"{self.name}: Rate limit hit #{self.rate_limit_hits}, backing off {backoff_seconds}s")
        else:
            # Standard exponential backoff: 5s, 10s, 20s, 40s
            backoff_seconds = min(5 * (2 ** min(self.consecutive_failures - 1, 3)), 40)
            logger.warning(f"{self.name}: Failure #{self.consecutive_failures}, backing off {backoff_seconds}s")
        
        self.backoff_until = time.time() + backoff_seconds
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100


@dataclass
class CacheEntry:
    """Cache entry with expiration"""
    data: Any
    timestamp: float
    ttl: int  # Time to live in seconds
    
    def is_valid(self) -> bool:
        """Check if cache entry is still valid"""
        return time.time() < (self.timestamp + self.ttl)


class SmartProviderService:
    """
    Smart provider service with intelligent fallback and caching
    
    Provider Priority (use in order):
    1. Binance (PRIMARY) - unlimited rate, no key required
    2. CoinCap (SECONDARY) - good rate limits
    3. HuggingFace Space (SECONDARY) - when working
    4. CoinGecko (FALLBACK) - ONLY when others fail, with 5min cache
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)
        self.cache: Dict[str, CacheEntry] = {}
        
        # Initialize provider stats with proper priorities
        self.providers: Dict[str, ProviderStats] = {
            'binance': ProviderStats(
                name='Binance',
                priority=ProviderPriority.PRIMARY,
                cache_duration=30  # 30s cache for market data
            ),
            'coincap': ProviderStats(
                name='CoinCap',
                priority=ProviderPriority.SECONDARY,
                cache_duration=30  # 30s cache
            ),
            'huggingface': ProviderStats(
                name='HuggingFace',
                priority=ProviderPriority.SECONDARY,
                cache_duration=60  # 1min cache
            ),
            'coingecko': ProviderStats(
                name='CoinGecko',
                priority=ProviderPriority.FALLBACK,
                cache_duration=300  # 5min cache - prevent 429 errors!
            )
        }
        
        # Symbol mappings
        self.symbol_to_coingecko_id = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "XRP": "ripple", "ADA": "cardano", "DOGE": "dogecoin",
            "SOL": "solana", "TRX": "tron", "DOT": "polkadot",
            "MATIC": "matic-network", "LTC": "litecoin", "SHIB": "shiba-inu",
            "AVAX": "avalanche-2", "UNI": "uniswap", "LINK": "chainlink",
            "ATOM": "cosmos", "XLM": "stellar", "ETC": "ethereum-classic",
            "XMR": "monero", "BCH": "bitcoin-cash"
        }
    
    def _get_cache_key(self, provider: str, endpoint: str, params: Dict = None) -> str:
        """Generate cache key"""
        key_parts = [provider, endpoint]
        if params:
            # Sort params for consistent cache keys
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(sorted_params)
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if entry.is_valid():
                logger.debug(f"Cache HIT: {cache_key[:8]}...")
                return entry.data
            else:
                # Clean expired cache
                del self.cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Any, ttl: int):
        """Set data in cache"""
        self.cache[cache_key] = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl=ttl
        )
        logger.debug(f"Cache SET: {cache_key[:8]}... (TTL: {ttl}s)")
    
    def _get_sorted_providers(self) -> List[Tuple[str, ProviderStats]]:
        """Get providers sorted by priority and availability"""
        available_providers = [
            (name, stats) for name, stats in self.providers.items()
            if stats.is_available()
        ]
        
        # Sort by priority (lower number first), then by success rate
        available_providers.sort(
            key=lambda x: (x[1].priority.value, -x[1].success_rate)
        )
        
        return available_providers
    
    async def get_market_prices(self, symbols: Optional[List[str]] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get market prices with smart provider fallback
        
        Returns:
            Dict with 'data', 'source', 'cached' keys
        """
        cache_key = self._get_cache_key('market_prices', 'all', {'symbols': symbols, 'limit': limit})
        
        # Check cache first
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return {
                'data': cached_data,
                'source': 'cache',
                'cached': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Try providers in priority order
        sorted_providers = self._get_sorted_providers()
        
        if not sorted_providers:
            logger.error("No providers available! All in backoff.")
            return {
                'data': [],
                'source': 'none',
                'cached': False,
                'error': 'All providers unavailable',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        last_error = None
        for provider_name, provider_stats in sorted_providers:
            try:
                logger.info(f"Trying {provider_name} (priority={provider_stats.priority.value})...")
                
                if provider_name == 'binance':
                    data = await self._fetch_binance_prices(symbols, limit)
                elif provider_name == 'coincap':
                    data = await self._fetch_coincap_prices(limit)
                elif provider_name == 'coingecko':
                    data = await self._fetch_coingecko_prices(symbols, limit)
                elif provider_name == 'huggingface':
                    # HuggingFace Space fallback (if available)
                    continue  # Skip for now, implement if needed
                else:
                    continue
                
                if data and len(data) > 0:
                    provider_stats.record_success()
                    # Cache with provider-specific duration
                    self._set_cache(cache_key, data, provider_stats.cache_duration)
                    
                    logger.info(f"✅ {provider_name}: Success! {len(data)} prices fetched")
                    return {
                        'data': data,
                        'source': provider_name,
                        'cached': False,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    provider_stats.record_failure("Empty response")
                    last_error = f"{provider_name}: Empty response"
                    
            except httpx.HTTPStatusError as e:
                is_rate_limit = e.response.status_code == 429
                error_msg = f"HTTP {e.response.status_code}"
                provider_stats.record_failure(error_msg, is_rate_limit=is_rate_limit)
                last_error = f"{provider_name}: {error_msg}"
                logger.error(f"❌ {provider_name}: {error_msg}")
                
            except Exception as e:
                error_msg = str(e)[:100]
                provider_stats.record_failure(error_msg)
                last_error = f"{provider_name}: {error_msg}"
                logger.error(f"❌ {provider_name}: {error_msg}")
        
        # All providers failed
        logger.error(f"All providers failed. Last error: {last_error}")
        return {
            'data': [],
            'source': 'none',
            'cached': False,
            'error': last_error or 'All providers failed',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _fetch_binance_prices(self, symbols: Optional[List[str]], limit: int) -> List[Dict[str, Any]]:
        """Fetch prices from Binance (PRIMARY - unlimited)"""
        url = "https://api.binance.com/api/v3/ticker/24hr"
        
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Transform to standard format
        prices = []
        for ticker in data[:limit]:
            symbol = ticker.get('symbol', '')
            # Filter USDT pairs
            if not symbol.endswith('USDT'):
                continue
            
            base_symbol = symbol.replace('USDT', '')
            
            # Filter by requested symbols if specified
            if symbols and base_symbol not in symbols:
                continue
            
            prices.append({
                'symbol': base_symbol,
                'name': base_symbol,
                'price': float(ticker.get('lastPrice', 0)),
                'change24h': float(ticker.get('priceChange', 0)),
                'changePercent24h': float(ticker.get('priceChangePercent', 0)),
                'volume24h': float(ticker.get('volume', 0)) * float(ticker.get('lastPrice', 0)),
                'high24h': float(ticker.get('highPrice', 0)),
                'low24h': float(ticker.get('lowPrice', 0)),
                'source': 'binance',
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            })
        
        return prices
    
    async def _fetch_coincap_prices(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch prices from CoinCap (SECONDARY)"""
        url = "https://api.coincap.io/v2/assets"
        params = {'limit': min(limit, 100)}
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Transform to standard format
        prices = []
        for asset in data.get('data', []):
            prices.append({
                'symbol': asset.get('symbol', '').upper(),
                'name': asset.get('name', ''),
                'price': float(asset.get('priceUsd', 0)),
                'change24h': float(asset.get('changePercent24Hr', 0)),
                'changePercent24h': float(asset.get('changePercent24Hr', 0)),
                'volume24h': float(asset.get('volumeUsd24Hr', 0) or 0),
                'marketCap': float(asset.get('marketCapUsd', 0) or 0),
                'source': 'coincap',
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            })
        
        return prices
    
    async def _fetch_coingecko_prices(self, symbols: Optional[List[str]], limit: int) -> List[Dict[str, Any]]:
        """Fetch prices from CoinGecko (FALLBACK ONLY - heavy caching)"""
        logger.warning("⚠️ Using CoinGecko as fallback (rate limit risk!)")
        
        if symbols:
            # Specific symbols
            coin_ids = [self.symbol_to_coingecko_id.get(s, s.lower()) for s in symbols]
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
        else:
            # Top coins
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(limit, 250),
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Transform to standard format
        prices = []
        
        if symbols:
            # Simple price format
            for coin_id, coin_data in data.items():
                symbol = next((k for k, v in self.symbol_to_coingecko_id.items() if v == coin_id), coin_id.upper())
                prices.append({
                    'symbol': symbol,
                    'name': symbol,
                    'price': coin_data.get('usd', 0),
                    'change24h': coin_data.get('usd_24h_change', 0),
                    'changePercent24h': coin_data.get('usd_24h_change', 0),
                    'volume24h': coin_data.get('usd_24h_vol', 0) or 0,
                    'marketCap': coin_data.get('usd_market_cap', 0) or 0,
                    'source': 'coingecko',
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                })
        else:
            # Markets format
            for coin in data:
                prices.append({
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name', ''),
                    'price': coin.get('current_price', 0),
                    'change24h': coin.get('price_change_24h', 0),
                    'changePercent24h': coin.get('price_change_percentage_24h', 0),
                    'volume24h': coin.get('total_volume', 0) or 0,
                    'marketCap': coin.get('market_cap', 0) or 0,
                    'source': 'coingecko',
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                })
        
        return prices
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'providers': {}
        }
        
        for name, provider in self.providers.items():
            stats['providers'][name] = {
                'name': provider.name,
                'priority': provider.priority.value,
                'total_requests': provider.total_requests,
                'successful_requests': provider.successful_requests,
                'failed_requests': provider.failed_requests,
                'rate_limit_hits': provider.rate_limit_hits,
                'success_rate': round(provider.success_rate, 2),
                'consecutive_failures': provider.consecutive_failures,
                'is_available': provider.is_available(),
                'backoff_until': provider.backoff_until if provider.backoff_until > time.time() else None,
                'last_success': datetime.fromtimestamp(provider.last_success_time).isoformat() if provider.last_success_time > 0 else None,
                'last_error': provider.last_error,
                'cache_duration': provider.cache_duration
            }
        
        # Add cache stats
        valid_cache_entries = sum(1 for entry in self.cache.values() if entry.is_valid())
        stats['cache'] = {
            'total_entries': len(self.cache),
            'valid_entries': valid_cache_entries,
            'expired_entries': len(self.cache) - valid_cache_entries
        }
        
        return stats
    
    def clear_cache(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def reset_provider(self, provider_name: str):
        """Reset a provider's backoff and stats"""
        if provider_name in self.providers:
            provider = self.providers[provider_name]
            provider.consecutive_failures = 0
            provider.backoff_until = 0
            logger.info(f"Reset provider: {provider_name}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global instance
_smart_provider_service = SmartProviderService()


def get_smart_provider_service() -> SmartProviderService:
    """Get global smart provider service instance"""
    return _smart_provider_service


__all__ = ['SmartProviderService', 'get_smart_provider_service']

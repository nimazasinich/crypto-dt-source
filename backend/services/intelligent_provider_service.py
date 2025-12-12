"""
Intelligent Provider Service with True Load Balancing
Distributes load across ALL providers intelligently, not just priority-based fallback
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from collections import deque
import httpx
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class ProviderHealth:
    """Track provider health and usage"""
    name: str
    base_url: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_hits: int = 0
    last_used: float = 0
    last_success: float = 0
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    backoff_until: float = 0
    cache_duration: int = 30
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def is_available(self) -> bool:
        return time.time() >= self.backoff_until
    
    @property
    def load_score(self) -> float:
        """Calculate load score - lower is better for selection"""
        now = time.time()
        
        # Base score on success rate (0-100, invert so lower is better)
        score = 100 - self.success_rate
        
        # Add penalty for recent usage (prevent hammering same provider)
        time_since_use = now - self.last_used
        if time_since_use < 10:  # Used in last 10 seconds
            score += 50  # Heavy penalty
        elif time_since_use < 60:  # Used in last minute
            score += 20  # Moderate penalty
        
        # Add penalty for failures
        score += self.consecutive_failures * 10
        
        # Add penalty for high request count (load balancing)
        score += (self.total_requests / 100)
        
        return score


@dataclass
class CacheEntry:
    """Cache entry with expiration"""
    data: Any
    timestamp: float
    ttl: int
    provider: str
    
    def is_valid(self) -> bool:
        return time.time() < (self.timestamp + self.ttl)


class IntelligentProviderService:
    """
    Intelligent provider service with TRUE load balancing
    
    Strategy: Round-robin with health-based selection
    - Each provider gets used fairly
    - After use, provider goes to back of queue
    - Failed providers get exponential backoff
    - Load distributed across ALL providers
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)
        self.cache: Dict[str, CacheEntry] = {}
        
        # Initialize providers with health tracking
        self.providers: Dict[str, ProviderHealth] = {
            'binance': ProviderHealth(
                name='Binance',
                base_url='https://api.binance.com/api/v3',
                cache_duration=30
            ),
            'coincap': ProviderHealth(
                name='CoinCap',
                base_url='https://api.coincap.io/v2',
                cache_duration=30
            ),
            'coingecko': ProviderHealth(
                name='CoinGecko',
                base_url='https://api.coingecko.com/api/v3',
                cache_duration=300  # Longer cache to prevent rate limits
            )
        }
        
        # Round-robin queue - fair distribution
        self.provider_queue = deque(['binance', 'coincap', 'coingecko'])
        
        # Symbol mappings for CoinGecko
        self.symbol_to_coingecko_id = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "XRP": "ripple", "ADA": "cardano", "DOGE": "dogecoin",
            "SOL": "solana", "TRX": "tron", "DOT": "polkadot",
            "MATIC": "matic-network", "LTC": "litecoin", "SHIB": "shiba-inu",
            "AVAX": "avalanche-2", "UNI": "uniswap", "LINK": "chainlink"
        }
    
    def _get_next_provider(self) -> Optional[str]:
        """
        Get next provider using intelligent selection
        
        Strategy:
        1. Get available providers (not in backoff)
        2. Score them based on health, recent usage, load
        3. Select provider with BEST score (lowest)
        4. After selection, rotate queue for fairness
        """
        available_providers = [
            name for name in self.provider_queue
            if self.providers[name].is_available
        ]
        
        if not available_providers:
            logger.warning("No providers available! All in backoff.")
            return None
        
        # Score all available providers (lower score = better)
        scored_providers = [
            (name, self.providers[name].load_score)
            for name in available_providers
        ]
        
        # Sort by score (ascending - lower is better)
        scored_providers.sort(key=lambda x: x[1])
        
        # Select best provider
        selected = scored_providers[0][0]
        
        # CRITICAL: Rotate queue to ensure fair distribution
        # Move selected provider to back of queue
        while self.provider_queue[0] != selected:
            self.provider_queue.rotate(-1)
        self.provider_queue.rotate(-1)  # Move selected to back
        
        logger.debug(f"Selected provider: {selected} (score: {scored_providers[0][1]:.2f})")
        logger.debug(f"Queue after selection: {list(self.provider_queue)}")
        
        return selected
    
    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Generate cache key"""
        key_parts = [endpoint]
        if params:
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(sorted_params)
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[Tuple[Any, str]]:
        """Get data from cache if valid, returns (data, provider)"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if entry.is_valid():
                logger.debug(f"Cache HIT from {entry.provider}")
                return entry.data, entry.provider
            else:
                del self.cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Any, provider: str, ttl: int):
        """Set data in cache"""
        self.cache[cache_key] = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl=ttl,
            provider=provider
        )
    
    async def get_market_prices(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get market prices with intelligent load balancing
        
        NO FAKE DATA - All data from real APIs only!
        """
        cache_key = self._get_cache_key('market_prices', {'symbols': symbols, 'limit': limit})
        
        # Check cache first
        cached = self._get_cached(cache_key)
        if cached:
            data, provider = cached
            return {
                'data': data,
                'source': provider,
                'cached': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Try providers with intelligent selection
        max_attempts = len(self.providers)
        last_error = None
        
        for attempt in range(max_attempts):
            provider_name = self._get_next_provider()
            
            if not provider_name:
                # All providers in backoff
                break
            
            provider = self.providers[provider_name]
            
            try:
                logger.info(f"[Attempt {attempt+1}/{max_attempts}] Using {provider_name} (load: {provider.load_score:.1f})")
                
                # Fetch from provider - REAL DATA ONLY
                if provider_name == 'binance':
                    data = await self._fetch_binance(symbols, limit)
                elif provider_name == 'coincap':
                    data = await self._fetch_coincap(limit)
                elif provider_name == 'coingecko':
                    data = await self._fetch_coingecko(symbols, limit)
                else:
                    continue
                
                # Verify data is real (not empty, has required fields)
                if not data or len(data) == 0:
                    raise ValueError("Empty data received")
                
                # Verify first item has required fields
                if not isinstance(data[0], dict) or 'price' not in data[0]:
                    raise ValueError("Invalid data structure")
                
                # Success! Update provider stats
                provider.total_requests += 1
                provider.successful_requests += 1
                provider.last_used = time.time()
                provider.last_success = time.time()
                provider.consecutive_failures = 0
                provider.backoff_until = 0
                
                # Cache the result
                self._set_cache(cache_key, data, provider_name, provider.cache_duration)
                
                logger.info(f"✅ {provider_name}: Success! {len(data)} prices (success_rate: {provider.success_rate:.1f}%)")
                
                return {
                    'data': data,
                    'source': provider_name,
                    'cached': False,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except httpx.HTTPStatusError as e:
                is_rate_limit = e.response.status_code == 429
                self._record_failure(provider, f"HTTP {e.response.status_code}", is_rate_limit)
                last_error = f"{provider_name}: HTTP {e.response.status_code}"
                logger.warning(f"❌ {last_error}")
                
            except Exception as e:
                self._record_failure(provider, str(e)[:100])
                last_error = f"{provider_name}: {str(e)[:100]}"
                logger.warning(f"❌ {last_error}")
        
        # All providers failed - return error (NO FAKE DATA)
        return {
            'data': [],
            'source': 'none',
            'cached': False,
            'error': last_error or 'All providers failed',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _record_failure(self, provider: ProviderHealth, error: str, is_rate_limit: bool = False):
        """Record provider failure with exponential backoff"""
        provider.total_requests += 1
        provider.failed_requests += 1
        provider.last_used = time.time()
        provider.last_error = error
        provider.consecutive_failures += 1
        
        if is_rate_limit:
            provider.rate_limit_hits += 1
            # Aggressive backoff for rate limits
            backoff_seconds = min(60 * (2 ** min(provider.consecutive_failures - 1, 4)), 600)
        else:
            # Standard exponential backoff
            backoff_seconds = min(5 * (2 ** min(provider.consecutive_failures - 1, 3)), 60)
        
        provider.backoff_until = time.time() + backoff_seconds
        logger.warning(f"{provider.name}: Backoff {backoff_seconds}s (failures: {provider.consecutive_failures})")
    
    async def _fetch_binance(self, symbols: Optional[List[str]], limit: int) -> List[Dict[str, Any]]:
        """Fetch REAL data from Binance - NO FAKE DATA"""
        url = f"{self.providers['binance'].base_url}/ticker/24hr"
        
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Transform to standard format
        prices = []
        for ticker in data:
            symbol = ticker.get('symbol', '')
            if not symbol.endswith('USDT'):
                continue
            
            base_symbol = symbol.replace('USDT', '')
            
            if symbols and base_symbol not in symbols:
                continue
            
            # REAL DATA ONLY - verify fields exist
            if 'lastPrice' not in ticker:
                continue
            
            prices.append({
                'symbol': base_symbol,
                'name': base_symbol,
                'price': float(ticker['lastPrice']),
                'change24h': float(ticker.get('priceChange', 0)),
                'changePercent24h': float(ticker.get('priceChangePercent', 0)),
                'volume24h': float(ticker.get('volume', 0)) * float(ticker['lastPrice']),
                'high24h': float(ticker.get('highPrice', 0)),
                'low24h': float(ticker.get('lowPrice', 0)),
                'source': 'binance',
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            })
            
            if len(prices) >= limit:
                break
        
        return prices
    
    async def _fetch_coincap(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch REAL data from CoinCap - NO FAKE DATA"""
        url = f"{self.providers['coincap'].base_url}/assets"
        params = {'limit': min(limit, 100)}
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Transform to standard format - REAL DATA ONLY
        prices = []
        for asset in data.get('data', []):
            # Verify required fields exist
            if 'priceUsd' not in asset or 'symbol' not in asset:
                continue
            
            prices.append({
                'symbol': asset['symbol'].upper(),
                'name': asset.get('name', asset['symbol']),
                'price': float(asset['priceUsd']),
                'change24h': float(asset.get('changePercent24Hr', 0)),
                'changePercent24h': float(asset.get('changePercent24Hr', 0)),
                'volume24h': float(asset.get('volumeUsd24Hr', 0) or 0),
                'marketCap': float(asset.get('marketCapUsd', 0) or 0),
                'source': 'coincap',
                'timestamp': int(datetime.utcnow().timestamp() * 1000)
            })
        
        return prices
    
    async def _fetch_coingecko(self, symbols: Optional[List[str]], limit: int) -> List[Dict[str, Any]]:
        """Fetch REAL data from CoinGecko - NO FAKE DATA"""
        base_url = self.providers['coingecko'].base_url
        
        if symbols:
            coin_ids = [self.symbol_to_coingecko_id.get(s, s.lower()) for s in symbols]
            url = f"{base_url}/simple/price"
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
        else:
            url = f"{base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(limit, 250),
                'page': 1,
                'sparkline': 'false'
            }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Transform to standard format - REAL DATA ONLY
        prices = []
        
        if symbols:
            for coin_id, coin_data in data.items():
                if 'usd' not in coin_data:
                    continue
                    
                symbol = next((k for k, v in self.symbol_to_coingecko_id.items() if v == coin_id), coin_id.upper())
                prices.append({
                    'symbol': symbol,
                    'name': symbol,
                    'price': coin_data['usd'],
                    'change24h': coin_data.get('usd_24h_change', 0),
                    'changePercent24h': coin_data.get('usd_24h_change', 0),
                    'volume24h': coin_data.get('usd_24h_vol', 0) or 0,
                    'marketCap': coin_data.get('usd_market_cap', 0) or 0,
                    'source': 'coingecko',
                    'timestamp': int(datetime.utcnow().timestamp() * 1000)
                })
        else:
            for coin in data:
                if 'current_price' not in coin:
                    continue
                    
                prices.append({
                    'symbol': coin['symbol'].upper(),
                    'name': coin.get('name', ''),
                    'price': coin['current_price'],
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
            'queue_order': list(self.provider_queue),
            'providers': {}
        }
        
        for name, provider in self.providers.items():
            stats['providers'][name] = {
                'name': provider.name,
                'total_requests': provider.total_requests,
                'successful_requests': provider.successful_requests,
                'failed_requests': provider.failed_requests,
                'rate_limit_hits': provider.rate_limit_hits,
                'success_rate': round(provider.success_rate, 2),
                'load_score': round(provider.load_score, 2),
                'consecutive_failures': provider.consecutive_failures,
                'is_available': provider.is_available,
                'backoff_seconds': max(0, int(provider.backoff_until - time.time())),
                'last_used': datetime.fromtimestamp(provider.last_used).isoformat() if provider.last_used > 0 else None,
                'cache_duration': provider.cache_duration
            }
        
        # Add cache stats
        valid_cache = sum(1 for e in self.cache.values() if e.is_valid())
        stats['cache'] = {
            'total_entries': len(self.cache),
            'valid_entries': valid_cache
        }
        
        return stats
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global instance
_intelligent_provider_service = IntelligentProviderService()


def get_intelligent_provider_service() -> IntelligentProviderService:
    """Get global intelligent provider service instance"""
    return _intelligent_provider_service


__all__ = ['IntelligentProviderService', 'get_intelligent_provider_service']

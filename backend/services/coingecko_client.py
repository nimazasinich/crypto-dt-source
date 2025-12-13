#!/usr/bin/env python3
"""
CoinGecko API Client - REAL DATA ONLY with CACHING and RATE LIMIT PROTECTION
Fetches real cryptocurrency market data from CoinGecko
NO MOCK DATA - All data from live CoinGecko API
ENHANCED: 5-minute mandatory cache, exponential backoff, auto-blacklist on 429
"""

import httpx
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Cache and rate limit management
_cache: Dict[str, Dict[str, Any]] = {}
_last_request_time = 0.0
_min_request_interval = 10.0  # Minimum 10 seconds between requests
_blacklist_until = 0.0  # Blacklist timestamp
_consecutive_429s = 0  # Track consecutive 429 errors


def _get_cache_key(method: str, **kwargs) -> str:
    """Generate cache key from method and parameters"""
    params_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return f"{method}:{params_str}"


def _get_from_cache(cache_key: str, ttl: int = 300) -> Optional[Any]:
    """Get data from cache if not expired (default 5 min TTL)"""
    global _cache
    if cache_key in _cache:
        cached_data = _cache[cache_key]
        if time.time() - cached_data["timestamp"] < ttl:
            logger.info(f"✅ CoinGecko: Cache hit for {cache_key}")
            return cached_data["data"]
        else:
            # Expired, remove from cache
            del _cache[cache_key]
    return None


def _set_cache(cache_key: str, data: Any):
    """Set data in cache with current timestamp"""
    global _cache
    _cache[cache_key] = {
        "data": data,
        "timestamp": time.time()
    }


def _check_rate_limit() -> bool:
    """Check if we should rate limit (return True if we should wait)"""
    global _last_request_time, _min_request_interval, _blacklist_until
    
    current_time = time.time()
    
    # Check blacklist
    if current_time < _blacklist_until:
        logger.warning(f"🔴 CoinGecko: Blacklisted until {datetime.fromtimestamp(_blacklist_until).strftime('%H:%M:%S')}")
        return True
    
    # Check minimum interval
    time_since_last = current_time - _last_request_time
    if time_since_last < _min_request_interval:
        wait_time = _min_request_interval - time_since_last
        logger.warning(f"⏳ CoinGecko: Rate limiting - wait {wait_time:.1f}s")
        return True
    
    return False


async def _wait_for_rate_limit():
    """Wait until rate limit allows next request"""
    global _last_request_time, _min_request_interval
    
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    
    if time_since_last < _min_request_interval:
        wait_time = _min_request_interval - time_since_last
        logger.info(f"⏳ CoinGecko: Waiting {wait_time:.1f}s before next request")
        await asyncio.sleep(wait_time)


def _update_last_request_time():
    """Update the last request timestamp"""
    global _last_request_time
    _last_request_time = time.time()


def _handle_429_error():
    """Handle 429 rate limit error with exponential backoff"""
    global _consecutive_429s, _blacklist_until, _min_request_interval
    
    _consecutive_429s += 1
    
    if _consecutive_429s >= 3:
        # Blacklist for 10 minutes after 3 consecutive 429s
        _blacklist_until = time.time() + 600  # 10 minutes
        logger.error(f"🔴 CoinGecko: {_consecutive_429s} consecutive 429s - BLACKLISTED for 10 minutes")
    else:
        # Exponential backoff
        backoff_time = min(60 * (2 ** _consecutive_429s), 300)  # Max 5 minutes
        _blacklist_until = time.time() + backoff_time
        logger.warning(f"⚠️ CoinGecko: 429 rate limit - backing off for {backoff_time}s")


def _reset_429_counter():
    """Reset 429 counter on successful request"""
    global _consecutive_429s
    if _consecutive_429s > 0:
        logger.info(f"✅ CoinGecko: Successful request - resetting 429 counter (was {_consecutive_429s})")
        _consecutive_429s = 0


class CoinGeckoClient:
    """
    Real CoinGecko API Client with CACHING and RATE LIMIT PROTECTION
    Primary source for real-time cryptocurrency market prices
    ENHANCED: 5-minute mandatory cache, exponential backoff, auto-blacklist on 429
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.timeout = 15.0
        
        # Symbol to CoinGecko ID mapping
        self.symbol_to_id = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "SOL": "solana",
            "TRX": "tron",
            "DOT": "polkadot",
            "MATIC": "matic-network",
            "LTC": "litecoin",
            "SHIB": "shiba-inu",
            "AVAX": "avalanche-2",
            "UNI": "uniswap",
            "LINK": "chainlink",
            "ATOM": "cosmos",
            "XLM": "stellar",
            "ETC": "ethereum-classic",
            "XMR": "monero",
            "BCH": "bitcoin-cash"
        }
        
        # Reverse mapping
        self.id_to_symbol = {v: k for k, v in self.symbol_to_id.items()}
    
    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """Convert crypto symbol to CoinGecko coin ID"""
        symbol = symbol.upper().replace("USDT", "").replace("USD", "")
        return self.symbol_to_id.get(symbol, symbol.lower())
    
    def _coingecko_id_to_symbol(self, coin_id: str) -> str:
        """Convert CoinGecko coin ID to symbol"""
        return self.id_to_symbol.get(coin_id, coin_id.upper())
    
    async def get_market_prices(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch REAL market prices from CoinGecko with CACHING and RATE LIMITING
        
        Args:
            symbols: List of crypto symbols (e.g., ["BTC", "ETH"])
            limit: Maximum number of results
        
        Returns:
            List of real market data
        
        ENHANCED: 5-minute mandatory cache, rate limiting, exponential backoff
        """
        # Generate cache key
        cache_key = _get_cache_key("market_prices", symbols=str(symbols), limit=limit)
        
        # Check cache first (5-minute TTL)
        cached_data = _get_from_cache(cache_key, ttl=300)
        if cached_data is not None:
            return cached_data
        
        # Check if blacklisted
        if _check_rate_limit():
            # Return cached data even if expired, or raise error
            if cache_key in _cache:
                logger.warning("🔴 CoinGecko: Rate limited - returning stale cache")
                return _cache[cache_key]["data"]
            else:
                raise HTTPException(
                    status_code=429,
                    detail="CoinGecko rate limited - no cached data available"
                )
        
        try:
            # Wait for rate limit if needed
            await _wait_for_rate_limit()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if symbols:
                    # Get specific symbols using /simple/price endpoint
                    coin_ids = [self._symbol_to_coingecko_id(s) for s in symbols]
                    
                    response = await client.get(
                        f"{self.base_url}/simple/price",
                        params={
                            "ids": ",".join(coin_ids),
                            "vs_currencies": "usd",
                            "include_24hr_change": "true",
                            "include_24hr_vol": "true",
                            "include_market_cap": "true"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Transform to standard format
                    prices = []
                    for coin_id, coin_data in data.items():
                        symbol = self._coingecko_id_to_symbol(coin_id)
                        prices.append({
                            "symbol": symbol,
                            "name": symbol,  # CoinGecko simple/price doesn't include name
                            "price": coin_data.get("usd", 0),
                            "change24h": coin_data.get("usd_24h_change", 0),
                            "changePercent24h": coin_data.get("usd_24h_change", 0),
                            "volume24h": coin_data.get("usd_24h_vol", 0),
                            "marketCap": coin_data.get("usd_market_cap", 0),
                            "source": "coingecko",
                            "timestamp": int(datetime.utcnow().timestamp() * 1000)
                        })
                    
                    logger.info(f"✅ CoinGecko: Fetched {len(prices)} real prices for specific symbols")
                    
                    # Update rate limit tracking
                    _update_last_request_time()
                    _reset_429_counter()
                    
                    # Cache the result
                    _set_cache(cache_key, prices)
                    
                    return prices
                
                else:
                    # Get top coins by market cap using /coins/markets endpoint
                    response = await client.get(
                        f"{self.base_url}/coins/markets",
                        params={
                            "vs_currency": "usd",
                            "order": "market_cap_desc",
                            "per_page": min(limit, 250),
                            "page": 1,
                            "sparkline": "false",
                            "price_change_percentage": "24h"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Transform to standard format
                    prices = []
                    for coin in data:
                        prices.append({
                            "id": coin.get("id", ""),
                            "symbol": coin.get("symbol", "").upper(),
                            "name": coin.get("name", ""),
                            "image": coin.get("image", ""),  # CoinGecko provides real image URLs
                            "price": coin.get("current_price", 0),
                            "change24h": coin.get("price_change_24h", 0),
                            "changePercent24h": coin.get("price_change_percentage_24h", 0),
                            "volume24h": coin.get("total_volume", 0),
                            "marketCap": coin.get("market_cap", 0),
                            "market_cap_rank": coin.get("market_cap_rank", 0),
                            "circulating_supply": coin.get("circulating_supply", 0),
                            "total_supply": coin.get("total_supply", 0),
                            "max_supply": coin.get("max_supply", 0),
                            "ath": coin.get("ath", 0),
                            "atl": coin.get("atl", 0),
                            "source": "coingecko",
                            "timestamp": int(datetime.utcnow().timestamp() * 1000)
                        })
                    
                    logger.info(f"✅ CoinGecko: Fetched {len(prices)} real market prices")
                    
                    # Update rate limit tracking
                    _update_last_request_time()
                    _reset_429_counter()
                    
                    # Cache the result
                    _set_cache(cache_key, prices)
                    
                    return prices
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Handle 429 specifically
                _handle_429_error()
                
                # Try to return cached data even if expired
                if cache_key in _cache:
                    logger.warning("🔴 CoinGecko: 429 rate limit - returning stale cache")
                    return _cache[cache_key]["data"]
                
                raise HTTPException(
                    status_code=429,
                    detail="CoinGecko rate limited - please try again later"
                )
            
            logger.error(f"❌ CoinGecko API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"CoinGecko API error: HTTP {e.response.status_code}"
            )
        
        except httpx.HTTPError as e:
            logger.error(f"❌ CoinGecko API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"CoinGecko API temporarily unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ CoinGecko API failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch real market data from CoinGecko: {str(e)}"
            )
    
    async def get_ohlcv(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Fetch REAL OHLCV (price history) data from CoinGecko with CACHING
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
            days: Number of days of historical data (1, 7, 14, 30, 90, 180, 365, max)
        
        Returns:
            Dict with OHLCV data
        
        ENHANCED: 5-minute cache, rate limiting
        """
        # Generate cache key
        cache_key = _get_cache_key("ohlcv", symbol=symbol, days=days)
        
        # Check cache first
        cached_data = _get_from_cache(cache_key, ttl=300)
        if cached_data is not None:
            return cached_data
        
        # Check if blacklisted
        if _check_rate_limit():
            if cache_key in _cache:
                logger.warning("🔴 CoinGecko OHLCV: Rate limited - returning stale cache")
                return _cache[cache_key]["data"]
            else:
                raise HTTPException(
                    status_code=429,
                    detail="CoinGecko rate limited - no cached data available"
                )
        
        try:
            await _wait_for_rate_limit()
            
            coin_id = self._symbol_to_coingecko_id(symbol)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get market chart (OHLC) data
                response = await client.get(
                    f"{self.base_url}/coins/{coin_id}/market_chart",
                    params={
                        "vs_currency": "usd",
                        "days": str(days),
                        "interval": "daily" if days > 1 else "hourly"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ CoinGecko: Fetched {days} days of OHLCV data for {symbol}")
                
                # Update rate limit tracking
                _update_last_request_time()
                _reset_429_counter()
                
                # Cache the result
                _set_cache(cache_key, data)
                
                return data
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                _handle_429_error()
                if cache_key in _cache:
                    logger.warning("🔴 CoinGecko OHLCV: 429 - returning stale cache")
                    return _cache[cache_key]["data"]
                raise HTTPException(status_code=429, detail="CoinGecko rate limited")
            
            logger.error(f"❌ CoinGecko OHLCV API HTTP error: {e}")
            raise HTTPException(status_code=503, detail=f"CoinGecko OHLCV API error: HTTP {e.response.status_code}")
        
        except httpx.HTTPError as e:
            logger.error(f"❌ CoinGecko OHLCV API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"CoinGecko OHLCV API unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ CoinGecko OHLCV API failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch OHLCV data from CoinGecko: {str(e)}"
            )
    
    async def get_trending_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch REAL trending coins from CoinGecko with CACHING
        
        Returns:
            List of real trending coins
        
        ENHANCED: 5-minute cache, rate limiting
        """
        # Generate cache key
        cache_key = _get_cache_key("trending", limit=limit)
        
        # Check cache first
        cached_data = _get_from_cache(cache_key, ttl=300)
        if cached_data is not None:
            return cached_data
        
        # Check if blacklisted
        if _check_rate_limit():
            if cache_key in _cache:
                logger.warning("🔴 CoinGecko trending: Rate limited - returning stale cache")
                return _cache[cache_key]["data"]
            else:
                raise HTTPException(status_code=429, detail="CoinGecko rate limited")
        
        try:
            await _wait_for_rate_limit()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get trending coins
                response = await client.get(f"{self.base_url}/search/trending")
                response.raise_for_status()
                data = response.json()
                
                trending = []
                coins = data.get("coins", [])[:limit]
                
                # Get price data for trending coins
                if coins:
                    coin_ids = [coin["item"]["id"] for coin in coins]
                    
                    # Fetch current prices
                    price_response = await client.get(
                        f"{self.base_url}/simple/price",
                        params={
                            "ids": ",".join(coin_ids),
                            "vs_currencies": "usd",
                            "include_24hr_change": "true"
                        }
                    )
                    price_response.raise_for_status()
                    price_data = price_response.json()
                    
                    for idx, coin_obj in enumerate(coins):
                        coin = coin_obj["item"]
                        coin_id = coin["id"]
                        prices = price_data.get(coin_id, {})
                        
                        trending.append({
                            "symbol": coin.get("symbol", "").upper(),
                            "name": coin.get("name", ""),
                            "rank": idx + 1,
                            "price": prices.get("usd", 0),
                            "change24h": prices.get("usd_24h_change", 0),
                            "marketCapRank": coin.get("market_cap_rank", 0),
                            "source": "coingecko",
                            "timestamp": int(datetime.utcnow().timestamp() * 1000)
                        })
                
                logger.info(f"✅ CoinGecko: Fetched {len(trending)} real trending coins")
                
                # Update rate limit tracking
                _update_last_request_time()
                _reset_429_counter()
                
                # Cache the result
                _set_cache(cache_key, trending)
                
                return trending
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                _handle_429_error()
                if cache_key in _cache:
                    logger.warning("🔴 CoinGecko trending: 429 - returning stale cache")
                    return _cache[cache_key]["data"]
                raise HTTPException(status_code=429, detail="CoinGecko rate limited")
            
            logger.error(f"❌ CoinGecko trending API HTTP error: {e}")
            raise HTTPException(status_code=503, detail=f"CoinGecko trending API error: HTTP {e.response.status_code}")
        
        except httpx.HTTPError as e:
            logger.error(f"❌ CoinGecko trending API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"CoinGecko trending API unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ CoinGecko trending API failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch trending coins: {str(e)}"
            )


# Global instance
coingecko_client = CoinGeckoClient()


__all__ = ["CoinGeckoClient", "coingecko_client"]

"""
Market Data Background Worker - REAL DATA FROM FREE APIs ONLY

CRITICAL RULES:
- MUST fetch REAL data from CoinGecko API (FREE tier)
- MUST store actual prices, not fake data
- MUST use actual timestamps from API responses
- NEVER generate or fake any data
- If API fails, log error and retry (don't fake it)
"""

import asyncio
import time
import logging
from datetime import datetime
from typing import List, Dict, Any
import httpx

from database.cache_queries import get_cache_queries
from database.db_manager import db_manager
from utils.logger import setup_logger

logger = setup_logger("market_worker")

# Get cache queries instance
cache = get_cache_queries(db_manager)

# CoinGecko API (FREE tier - no API key required)
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Top cryptocurrencies to track
TOP_SYMBOLS = [
    "bitcoin", "ethereum", "binancecoin", "ripple", "cardano",
    "solana", "polkadot", "dogecoin", "polygon", "avalanche",
    "chainlink", "litecoin", "uniswap", "algorand", "stellar",
    "cosmos", "tron", "monero", "ethereum-classic", "tezos"
]

# Symbol mapping (CoinGecko ID -> Symbol)
SYMBOL_MAP = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "binancecoin": "BNB",
    "ripple": "XRP",
    "cardano": "ADA",
    "solana": "SOL",
    "polkadot": "DOT",
    "dogecoin": "DOGE",
    "polygon": "MATIC",
    "avalanche": "AVAX",
    "chainlink": "LINK",
    "litecoin": "LTC",
    "uniswap": "UNI",
    "algorand": "ALGO",
    "stellar": "XLM",
    "cosmos": "ATOM",
    "tron": "TRX",
    "monero": "XMR",
    "ethereum-classic": "ETC",
    "tezos": "XTZ"
}


async def fetch_coingecko_prices() -> List[Dict[str, Any]]:
    """
    Fetch REAL market prices from CoinGecko API (FREE tier)
    
    CRITICAL RULES:
    1. MUST call actual CoinGecko API
    2. MUST return actual data from API response
    3. NEVER generate fake prices
    4. If API fails, return empty list (not fake data)
    
    Returns:
        List of dictionaries with REAL market data
    """
    try:
        # Build API request - REAL API call
        ids = ",".join(TOP_SYMBOLS)
        url = f"{COINGECKO_BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": ids,
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h"
        }
        
        logger.info(f"Fetching REAL data from CoinGecko API: {url}")
        
        # Make REAL HTTP request to CoinGecko
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            # Parse REAL response data
            coins = response.json()
            
            if not coins or not isinstance(coins, list):
                logger.error(f"Invalid response from CoinGecko: {coins}")
                return []
            
            logger.info(f"Successfully fetched {len(coins)} coins from CoinGecko")
            
            # Extract REAL data from API response
            market_data = []
            for coin in coins:
                try:
                    coin_id = coin.get("id", "")
                    symbol = SYMBOL_MAP.get(coin_id, coin.get("symbol", "").upper())
                    
                    # REAL data from API - NOT fake
                    data = {
                        "symbol": symbol,
                        "price": float(coin.get("current_price", 0)),  # REAL price
                        "market_cap": float(coin.get("market_cap", 0)) if coin.get("market_cap") else None,
                        "volume_24h": float(coin.get("total_volume", 0)) if coin.get("total_volume") else None,
                        "change_24h": float(coin.get("price_change_percentage_24h", 0)) if coin.get("price_change_percentage_24h") else None,
                        "high_24h": float(coin.get("high_24h", 0)) if coin.get("high_24h") else None,
                        "low_24h": float(coin.get("low_24h", 0)) if coin.get("low_24h") else None,
                        "provider": "coingecko"
                    }
                    
                    market_data.append(data)
                    
                except Exception as e:
                    logger.error(f"Error parsing coin data for {coin.get('id')}: {e}")
                    continue
            
            return market_data
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching from CoinGecko: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching from CoinGecko: {e}", exc_info=True)
        return []


async def save_market_data_to_cache(market_data: List[Dict[str, Any]]) -> int:
    """
    Save REAL market data to database cache
    
    Args:
        market_data: List of REAL market data dictionaries
        
    Returns:
        int: Number of records saved
    """
    saved_count = 0
    
    for data in market_data:
        try:
            success = cache.save_market_data(
                symbol=data["symbol"],
                price=data["price"],
                market_cap=data.get("market_cap"),
                volume_24h=data.get("volume_24h"),
                change_24h=data.get("change_24h"),
                high_24h=data.get("high_24h"),
                low_24h=data.get("low_24h"),
                provider=data["provider"]
            )
            
            if success:
                saved_count += 1
                logger.debug(f"Saved market data for {data['symbol']}: ${data['price']:.2f}")
            
        except Exception as e:
            logger.error(f"Error saving market data for {data.get('symbol')}: {e}")
            continue
    
    return saved_count


async def market_data_worker_loop():
    """
    Background worker loop - Fetch REAL market data periodically
    
    CRITICAL RULES:
    1. Run continuously in background
    2. Fetch REAL data from CoinGecko every 60 seconds
    3. Store REAL data in database
    4. NEVER generate fake data as fallback
    5. If API fails, log error and retry on next iteration
    """
    
    logger.info("Starting market data background worker")
    iteration = 0
    
    while True:
        try:
            iteration += 1
            start_time = time.time()
            
            logger.info(f"[Iteration {iteration}] Fetching REAL market data from CoinGecko...")
            
            # Fetch REAL data from CoinGecko API
            market_data = await fetch_coingecko_prices()
            
            if not market_data or len(market_data) == 0:
                logger.warning(f"[Iteration {iteration}] No data received from CoinGecko API")
                # Wait and retry - DON'T generate fake data
                await asyncio.sleep(60)
                continue
            
            # Save REAL data to database
            saved_count = await save_market_data_to_cache(market_data)
            
            elapsed = time.time() - start_time
            logger.info(
                f"[Iteration {iteration}] Successfully saved {saved_count}/{len(market_data)} "
                f"REAL market records from CoinGecko in {elapsed:.2f}s"
            )
            
            # CoinGecko free tier: 10-50 calls/minute limit
            # Sleep for 60 seconds to stay within limits
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"[Iteration {iteration}] Worker error: {e}", exc_info=True)
            # Wait and retry - DON'T generate fake data
            await asyncio.sleep(60)


async def start_market_data_worker():
    """
    Start market data background worker
    
    This should be called during application startup
    """
    try:
        logger.info("Initializing market data worker...")
        
        # Run initial fetch immediately
        logger.info("Running initial market data fetch...")
        market_data = await fetch_coingecko_prices()
        
        if market_data and len(market_data) > 0:
            saved_count = await save_market_data_to_cache(market_data)
            logger.info(f"Initial fetch: Saved {saved_count} REAL market records")
        else:
            logger.warning("Initial fetch returned no data")
        
        # Start background loop
        asyncio.create_task(market_data_worker_loop())
        logger.info("Market data worker started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start market data worker: {e}", exc_info=True)


# For testing
if __name__ == "__main__":
    import sys
    sys.path.append("/workspace")
    
    async def test():
        """Test the worker"""
        logger.info("Testing market data worker...")
        
        # Test API fetch
        data = await fetch_coingecko_prices()
        logger.info(f"Fetched {len(data)} coins from CoinGecko")
        
        if data:
            # Print sample data
            for coin in data[:5]:
                logger.info(f"  {coin['symbol']}: ${coin['price']:.2f}")
            
            # Test save to database
            saved = await save_market_data_to_cache(data)
            logger.info(f"Saved {saved} records to database")
    
    asyncio.run(test())

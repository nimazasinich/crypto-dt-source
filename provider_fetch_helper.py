#!/usr/bin/env python3
"""
Provider Fetch Helper - Real data fetching functions for HuggingFace deployment
Fetches REAL data from free APIs (CoinGecko, Alternative.me, etc.)
NO MOCKS - Production ready
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from db_helper import get_database

# Setup logging
logger = logging.getLogger(__name__)

# HTTP Client Configuration
TIMEOUT = 10.0
MAX_RETRIES = 2


async def fetch_coingecko_market_data() -> Dict[str, Any]:
    """
    Fetch REAL market data from CoinGecko (free, no API key required)
    
    Returns:
        Dict with cryptocurrencies list and global market data
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Fetch market data for top cryptocurrencies
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h"
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            coins_data = response.json()
            
            # Fetch global market data
            global_url = "https://api.coingecko.com/api/v3/global"
            global_response = await client.get(global_url)
            global_response.raise_for_status()
            global_data = global_response.json()
            
            # Format response
            cryptocurrencies = []
            for coin in coins_data:
                cryptocurrencies.append({
                    "rank": coin.get("market_cap_rank", 0),
                    "name": coin.get("name", ""),
                    "symbol": coin.get("symbol", "").upper(),
                    "price": coin.get("current_price", 0),
                    "change_24h": coin.get("price_change_percentage_24h", 0),
                    "market_cap": coin.get("market_cap", 0),
                    "volume_24h": coin.get("total_volume", 0),
                    "image": coin.get("image", "")
                })
            
            # Save to database
            db = get_database()
            for crypto in cryptocurrencies:
                db.save_price({
                    "symbol": crypto["symbol"],
                    "name": crypto["name"],
                    "price_usd": crypto["price"],
                    "volume_24h": crypto["volume_24h"],
                    "market_cap": crypto["market_cap"],
                    "percent_change_24h": crypto["change_24h"],
                    "rank": crypto["rank"]
                })
            
            # Extract global data
            global_market = global_data.get("data", {})
            btc_dominance = global_market.get("market_cap_percentage", {}).get("btc", 0)
            eth_dominance = global_market.get("market_cap_percentage", {}).get("eth", 0)
            
            return {
                "cryptocurrencies": cryptocurrencies,
                "global": {
                    "btc_dominance": round(btc_dominance, 2),
                    "eth_dominance": round(eth_dominance, 2)
                }
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching market data: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise


async def fetch_fear_greed_index() -> Dict[str, Any]:
    """
    Fetch REAL Fear & Greed Index from Alternative.me (free, no API key)
    
    Returns:
        Dict with fear_greed_index containing value and classification
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            url = "https://api.alternative.me/fng/"
            
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract data
            fng_data = data.get("data", [{}])[0]
            value = int(fng_data.get("value", 50))
            classification = fng_data.get("value_classification", "Neutral")
            
            return {
                "fear_greed_index": {
                    "value": value,
                    "classification": classification
                }
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching fear & greed index: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching fear & greed index: {e}")
        raise


async def fetch_trending_coins() -> Dict[str, Any]:
    """
    Fetch REAL trending coins from CoinGecko (free, no API key)
    
    Returns:
        Dict with trending coins list
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            url = "https://api.coingecko.com/api/v3/search/trending"
            
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract trending coins
            trending_list = []
            for item in data.get("coins", [])[:10]:
                coin = item.get("item", {})
                trending_list.append({
                    "name": coin.get("name", ""),
                    "symbol": coin.get("symbol", "").upper(),
                    "thumb": coin.get("thumb", "")
                })
            
            return {
                "trending": trending_list
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching trending coins: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching trending coins: {e}")
        raise


def get_market_history(symbol: str = "BTC", hours: int = 24) -> Dict[str, Any]:
    """
    Get REAL market history from SQLite database
    
    Args:
        symbol: Cryptocurrency symbol (default: BTC)
        hours: Number of hours to look back (default: 24)
    
    Returns:
        Dict with history data
    """
    try:
        db = get_database()
        history = db.get_price_history(symbol, hours=hours)
        
        # Format for API response
        formatted_history = []
        for record in history:
            formatted_history.append({
                "timestamp": record.get("timestamp"),
                "price": record.get("price_usd"),
                "volume": record.get("volume_24h"),
                "change_24h": record.get("percent_change_24h")
            })
        
        return {
            "symbol": symbol,
            "hours": hours,
            "history": formatted_history,
            "count": len(formatted_history)
        }
        
    except Exception as e:
        logger.error(f"Error fetching market history: {e}")
        raise


async def fetch_market_stats() -> Dict[str, Any]:
    """
    Fetch REAL market statistics from CoinGecko
    
    Returns:
        Dict with market statistics
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            url = "https://api.coingecko.com/api/v3/global"
            
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract global data
            global_data = data.get("data", {})
            
            return {
                "market": {
                    "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
                    "total_volume": global_data.get("total_volume", {}).get("usd", 0),
                    "btc_dominance": round(global_data.get("market_cap_percentage", {}).get("btc", 0), 2)
                }
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching market stats: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching market stats: {e}")
        raise


# Initialize database on module load
def init_database():
    """Initialize database tables"""
    try:
        db = get_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# Call init on import
init_database()

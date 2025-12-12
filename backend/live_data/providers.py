import logging
import aiohttp
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.orchestration.provider_manager import provider_manager, ProviderConfig

logger = logging.getLogger(__name__)

# ==============================================================================
# FETCH IMPLEMENTATIONS
# ==============================================================================

async def fetch_coingecko_market(config: ProviderConfig, **kwargs) -> Any:
    ids = kwargs.get("ids", "bitcoin,ethereum")
    vs_currency = kwargs.get("vs_currency", "usd")
    
    url = f"{config.base_url}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "ids": ids,
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h"
    }
    
    # Pro API key support
    if config.api_key:
        params["x_cg_pro_api_key"] = config.api_key
        
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            if response.status == 429:
                raise Exception("Rate limit exceeded (429)")
            response.raise_for_status()
            return await response.json()

async def fetch_coingecko_price(config: ProviderConfig, **kwargs) -> Any:
    coin_id = kwargs.get("coin_id", "bitcoin")
    vs_currencies = kwargs.get("vs_currencies", "usd")
    
    url = f"{config.base_url}/simple/price"
    params = {"ids": coin_id, "vs_currencies": vs_currencies}
    
    if config.api_key:
        params["x_cg_pro_api_key"] = config.api_key

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            response.raise_for_status()
            return await response.json()

async def fetch_binance_ticker(config: ProviderConfig, **kwargs) -> Any:
    symbol = kwargs.get("symbol", "BTCUSDT").upper()
    url = f"{config.base_url}/ticker/price"
    params = {"symbol": symbol}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            if response.status == 451:
                raise Exception("Geo-blocked (451)")
            response.raise_for_status()
            data = await response.json()
            # Normalize to look somewhat like CoinGecko for generic usage if needed
            return {"price": float(data.get("price", 0)), "symbol": data.get("symbol")}

async def fetch_binance_klines(config: ProviderConfig, **kwargs) -> Any:
    symbol = kwargs.get("symbol", "BTCUSDT").upper()
    interval = kwargs.get("interval", "1h")
    limit = kwargs.get("limit", 100)
    
    url = f"{config.base_url}/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            if response.status == 451:
                raise Exception("Geo-blocked (451)")
            response.raise_for_status()
            return await response.json()

async def fetch_cryptopanic_news(config: ProviderConfig, **kwargs) -> Any:
    filter_type = kwargs.get("filter", "hot")
    url = f"{config.base_url}/posts/"
    
    params = {
        "auth_token": config.api_key,
        "filter": filter_type,
        "public": "true"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            response.raise_for_status()
            return await response.json()

async def fetch_newsapi(config: ProviderConfig, **kwargs) -> Any:
    query = kwargs.get("query", "crypto")
    url = f"{config.base_url}/everything"
    
    params = {
        "q": query,
        "apiKey": config.api_key,
        "sortBy": "publishedAt",
        "language": "en"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            response.raise_for_status()
            return await response.json()

async def fetch_alternative_me_fng(config: ProviderConfig, **kwargs) -> Any:
    limit = kwargs.get("limit", 1)
    url = f"{config.base_url}/fng/"
    params = {"limit": limit}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            response.raise_for_status()
            return await response.json()

async def fetch_etherscan_gas(config: ProviderConfig, **kwargs) -> Any:
    url = config.base_url
    params = {
        "module": "gastracker",
        "action": "gasoracle",
        "apikey": config.api_key
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            response.raise_for_status()
            return await response.json()

# ==============================================================================
# REGISTRATION
# ==============================================================================

def initialize_providers():
    # Market Data Providers
    provider_manager.register_provider(
        "market",
        ProviderConfig(
            name="coingecko_free",
            category="market",
            base_url="https://api.coingecko.com/api/v3",
            rate_limit_per_min=30,  # Conservative for free tier
            weight=100
        ),
        fetch_coingecko_market
    )
    
    provider_manager.register_provider(
        "market_pro",
        ProviderConfig(
            name="coingecko_pro",
            category="market",
            base_url="https://pro-api.coingecko.com/api/v3", # Assuming Pro URL
            api_key=os.getenv("COINGECKO_PRO_API_KEY", "04cf4b5b-9868-465c-8ba0-9f2e78c92eb1"),
            rate_limit_per_min=500,
            weight=200
        ),
        fetch_coingecko_market
    )

    provider_manager.register_provider(
        "market",
        ProviderConfig(
            name="binance",
            category="market",
            base_url="https://api.binance.com/api/v3",
            rate_limit_per_min=1200,
            weight=90
        ),
        fetch_binance_ticker  # Note: This fetch function behaves differently (ticker vs market list), router needs to handle
    )

    # OHLC Providers
    provider_manager.register_provider(
        "ohlc",
        ProviderConfig(
            name="binance_ohlc",
            category="ohlc",
            base_url="https://api.binance.com/api/v3",
            rate_limit_per_min=1200,
            weight=100
        ),
        fetch_binance_klines
    )

    # News Providers
    provider_manager.register_provider(
        "news",
        ProviderConfig(
            name="cryptopanic",
            category="news",
            base_url="https://cryptopanic.com/api/v1",
            api_key=os.getenv("CRYPTOPANIC_API_KEY", "7832690f05026639556837583758"), # Placeholder if env not set
            rate_limit_per_min=60,
            weight=100
        ),
        fetch_cryptopanic_news
    )
    
    provider_manager.register_provider(
        "news",
        ProviderConfig(
            name="newsapi",
            category="news",
            base_url="https://newsapi.org/v2",
            api_key=os.getenv("NEWS_API_KEY", "968a5e25552b4cb5ba3280361d8444ab"),
            rate_limit_per_min=100,
            weight=90
        ),
        fetch_newsapi
    )

    # Sentiment
    provider_manager.register_provider(
        "sentiment",
        ProviderConfig(
            name="alternative_me",
            category="sentiment",
            base_url="https://api.alternative.me",
            rate_limit_per_min=60,
            weight=100
        ),
        fetch_alternative_me_fng
    )

    # OnChain / RPC
    provider_manager.register_provider(
        "onchain",
        ProviderConfig(
            name="etherscan",
            category="onchain",
            base_url="https://api.etherscan.io/api",
            api_key=os.getenv("ETHERSCAN_API_KEY", "SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2"),
            rate_limit_per_min=5, # Free tier limit
            weight=100
        ),
        fetch_etherscan_gas
    )
    
    provider_manager.register_provider(
        "onchain",
        ProviderConfig(
            name="etherscan_backup",
            category="onchain",
            base_url="https://api.etherscan.io/api",
            api_key=os.getenv("ETHERSCAN_API_KEY_2", "T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45"),
            rate_limit_per_min=5,
            weight=90
        ),
        fetch_etherscan_gas
    )

# Auto-initialize
initialize_providers()

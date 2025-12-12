import logging
import aiohttp
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.orchestration.provider_manager import provider_manager, ProviderConfig

logger = logging.getLogger(__name__)

# Minimal mapping for common coins used by HF endpoints
_COINGECKO_ID_TO_BINANCE_SYMBOL: Dict[str, str] = {
    "bitcoin": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "tron": "TRXUSDT",
    "solana": "SOLUSDT",
    "binancecoin": "BNBUSDT",
    "ripple": "XRPUSDT",
}

_BINANCE_SYMBOL_TO_COINGECKO_ID: Dict[str, str] = {v.replace("USDT", "").lower(): k for k, v in _COINGECKO_ID_TO_BINANCE_SYMBOL.items()}

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

async def fetch_binance_market(config: ProviderConfig, **kwargs) -> Any:
    """
    Build a CoinGecko-like market list from Binance 24hr ticker endpoints.

    This exists to allow provider rotation/failover for `/api/market` without returning fake data.
    """
    ids_raw = kwargs.get("ids", "bitcoin,ethereum")
    ids = [i.strip().lower() for i in str(ids_raw).split(",") if i.strip()]
    vs_currency = str(kwargs.get("vs_currency", "usd")).lower()

    # Binance market is typically quoted in USDT; if caller asks for non-usd, we still return the USDT quote.
    if vs_currency not in {"usd", "usdt"}:
        logger.warning("Binance market provider only supports USD/USDT quoting. Requested: %s", vs_currency)

    symbols: List[str] = []
    for coin_id in ids:
        sym = _COINGECKO_ID_TO_BINANCE_SYMBOL.get(coin_id)
        if sym:
            symbols.append(sym)

    if not symbols:
        return []

    url = f"{config.base_url}/ticker/24hr"
    results: List[Dict[str, Any]] = []

    async with aiohttp.ClientSession() as session:
        for sym in symbols:
            params = {"symbol": sym}
            async with session.get(url, params=params, timeout=config.timeout) as response:
                if response.status == 451:
                    raise Exception("Geo-blocked (451)")
                response.raise_for_status()
                data = await response.json()

                base_symbol = str(data.get("symbol", "")).replace("USDT", "")
                try:
                    results.append(
                        {
                            "id": _BINANCE_SYMBOL_TO_COINGECKO_ID.get(base_symbol.lower(), base_symbol.lower()),
                            "symbol": base_symbol.lower(),
                            "name": base_symbol.upper(),
                            "current_price": float(data.get("lastPrice", 0)),
                            "price_change_percentage_24h": float(data.get("priceChangePercent", 0)),
                            "total_volume": float(data.get("quoteVolume", 0)),
                        }
                    )
                except Exception:
                    # Skip malformed entry rather than inventing values
                    continue

    return results

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

async def fetch_coingecko_ohlc(config: ProviderConfig, **kwargs) -> Any:
    """
    Fetch OHLC candles from CoinGecko.

    CoinGecko endpoint: /coins/{id}/ohlc?vs_currency=usd&days=1|7|14|30|90|180|365|max
    Returns: [[timestamp, open, high, low, close], ...]
    """
    symbol = str(kwargs.get("symbol", "BTC")).strip().lower()
    interval = str(kwargs.get("interval", "1h")).strip().lower()
    limit = int(kwargs.get("limit", 100))

    # Best-effort mapping; if unknown, treat symbol as a coin id.
    coin_id = _BINANCE_SYMBOL_TO_COINGECKO_ID.get(symbol.lower(), symbol.lower())

    # Determine days bucket based on interval*limit
    minutes_per_candle = 60
    if interval.endswith("m"):
        try:
            minutes_per_candle = int(interval[:-1])
        except Exception:
            minutes_per_candle = 60
    elif interval.endswith("h"):
        try:
            minutes_per_candle = int(interval[:-1]) * 60
        except Exception:
            minutes_per_candle = 60
    elif interval.endswith("d"):
        try:
            minutes_per_candle = int(interval[:-1]) * 1440
        except Exception:
            minutes_per_candle = 1440

    total_days = max(1, int((minutes_per_candle * max(1, limit)) / 1440))
    # Coingecko allowed buckets
    if total_days <= 1:
        days = 1
    elif total_days <= 7:
        days = 7
    elif total_days <= 14:
        days = 14
    elif total_days <= 30:
        days = 30
    elif total_days <= 90:
        days = 90
    elif total_days <= 180:
        days = 180
    else:
        days = 365

    url = f"{config.base_url}/coins/{coin_id}/ohlc"
    params = {"vs_currency": "usd", "days": days}

    # Pro API key support (only if provided)
    if config.api_key:
        params["x_cg_pro_api_key"] = config.api_key

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=config.timeout) as response:
            if response.status == 429:
                raise Exception("Rate limit exceeded (429)")
            response.raise_for_status()
            data = await response.json()
            # Respect requested limit if possible
            if isinstance(data, list) and limit > 0:
                return data[-limit:]
            return data

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
        "market",
        ProviderConfig(
            name="binance",
            category="market",
            base_url="https://api.binance.com/api/v3",
            rate_limit_per_min=1200,
            weight=90
        ),
        fetch_binance_market
    )

    # Optional CoinGecko Pro provider (only if key present)
    cg_pro_key = os.getenv("COINGECKO_PRO_API_KEY", "").strip()
    if cg_pro_key:
        provider_manager.register_provider(
            "market",
            ProviderConfig(
                name="coingecko_pro",
                category="market",
                base_url="https://pro-api.coingecko.com/api/v3",
                api_key=cg_pro_key,
                rate_limit_per_min=500,
                weight=200,
            ),
            fetch_coingecko_market,
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
    provider_manager.register_provider(
        "ohlc",
        ProviderConfig(
            name="coingecko_ohlc",
            category="ohlc",
            base_url="https://api.coingecko.com/api/v3",
            rate_limit_per_min=30,
            weight=70,
        ),
        fetch_coingecko_ohlc,
    )

    # News Providers
    cryptopanic_key = os.getenv("CRYPTOPANIC_API_KEY", "").strip()
    if cryptopanic_key:
        provider_manager.register_provider(
            "news",
            ProviderConfig(
                name="cryptopanic",
                category="news",
                base_url="https://cryptopanic.com/api/v1",
                api_key=cryptopanic_key,
                rate_limit_per_min=60,
                weight=100,
            ),
            fetch_cryptopanic_news,
        )
    else:
        logger.info("CryptoPanic API key not set; skipping cryptopanic provider registration")

    newsapi_key = os.getenv("NEWS_API_KEY", "").strip()
    if newsapi_key:
        provider_manager.register_provider(
            "news",
            ProviderConfig(
                name="newsapi",
                category="news",
                base_url="https://newsapi.org/v2",
                api_key=newsapi_key,
                rate_limit_per_min=100,
                weight=90,
            ),
            fetch_newsapi,
        )
    else:
        logger.info("NewsAPI key not set; skipping newsapi provider registration")

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
    etherscan_key = os.getenv("ETHERSCAN_API_KEY", "").strip()
    if etherscan_key:
        provider_manager.register_provider(
            "onchain",
            ProviderConfig(
                name="etherscan",
                category="onchain",
                base_url="https://api.etherscan.io/api",
                api_key=etherscan_key,
                rate_limit_per_min=5,  # Free tier limit
                weight=100,
            ),
            fetch_etherscan_gas,
        )
    else:
        logger.info("Etherscan API key not set; skipping etherscan provider registration")

    etherscan_key_2 = os.getenv("ETHERSCAN_API_KEY_2", "").strip()
    if etherscan_key_2:
        provider_manager.register_provider(
            "onchain",
            ProviderConfig(
                name="etherscan_backup",
                category="onchain",
                base_url="https://api.etherscan.io/api",
                api_key=etherscan_key_2,
                rate_limit_per_min=5,
                weight=90,
            ),
            fetch_etherscan_gas,
        )
    else:
        logger.info("Etherscan backup key not set; skipping etherscan_backup provider registration")

# Auto-initialize
initialize_providers()

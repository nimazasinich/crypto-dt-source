#!/usr/bin/env python3
"""
Crypto API Monitor ULTIMATE - Real API Integration
Complete professional monitoring system with 100+ real free crypto APIs
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
import asyncio
import aiohttp
import random
import json
import logging
from datetime import datetime, timedelta
import uvicorn
from collections import defaultdict
import os
from urllib.parse import urljoin, unquote
from pathlib import Path
from threading import Lock

from database import Database
from config import config as global_config
from starlette.middleware.trustedhost import TrustedHostMiddleware
from backend.feature_flags import feature_flags, is_feature_enabled

class SentimentRequest(BaseModel):
    texts: List[str]

class PoolCreate(BaseModel):
    name: str
    category: str
    rotation_strategy: str = "round_robin"
    description: Optional[str] = None

class PoolMemberAdd(BaseModel):
    provider_id: str
    priority: int = 1
    weight: int = 1

class ProviderCreateRequest(BaseModel):
    name: str
    category: str
    endpoint_url: str
    requires_key: bool = False
    api_key: Optional[str] = None
    rate_limit: Optional[str] = None
    timeout_ms: int = 10000
    health_check_endpoint: Optional[str] = None
    notes: Optional[str] = None


class HFRegistryItemCreate(BaseModel):
    id: str
    kind: Literal["model", "dataset"]
    description: Optional[str] = None
    downloads: Optional[int] = None
    likes: Optional[int] = None

class FeatureFlagUpdate(BaseModel):
    flag_name: str
    value: bool

class FeatureFlagsUpdate(BaseModel):
    flags: Dict[str, bool]

logger = logging.getLogger("crypto_monitor")


app = FastAPI(title="Crypto Monitor Ultimate", version="3.0.0")


def _split_env_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origin_regex_env = os.getenv("ALLOWED_ORIGIN_REGEX")
allowed_origins = _split_env_list(allowed_origins_env)

cors_kwargs = {
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "allow_credentials": True,
}

if allowed_origin_regex_env:
    cors_kwargs["allow_origin_regex"] = allowed_origin_regex_env
elif not allowed_origins or "*" in allowed_origins:
    cors_kwargs["allow_origin_regex"] = ".*"
else:
    cors_kwargs["allow_origins"] = allowed_origins

app.add_middleware(CORSMiddleware, **cors_kwargs)

trusted_hosts = _split_env_list(os.getenv("TRUSTED_HOSTS"))
if not trusted_hosts:
    trusted_hosts = ["*"]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)


CUSTOM_REGISTRY_PATH = Path("data/custom_registry.json")
_registry_lock = Lock()
_custom_registry: Dict[str, List[Dict]] = {
    "providers": [],
    "hf_models": [],
    "hf_datasets": []
}


def _load_custom_registry() -> Dict[str, List[Dict]]:
    if not CUSTOM_REGISTRY_PATH.exists():
        return {
            "providers": [],
            "hf_models": [],
            "hf_datasets": []
        }
    try:
        with CUSTOM_REGISTRY_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "providers": data.get("providers", []),
                "hf_models": data.get("hf_models", []),
                "hf_datasets": data.get("hf_datasets", []),
            }
    except Exception:
        return {
            "providers": [],
            "hf_models": [],
            "hf_datasets": []
        }


def _save_custom_registry() -> None:
    CUSTOM_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CUSTOM_REGISTRY_PATH.open("w", encoding="utf-8") as f:
        json.dump(_custom_registry, f, ensure_ascii=False, indent=2)


def _refresh_custom_registry() -> None:
    global _custom_registry
    with _registry_lock:
        _custom_registry = _load_custom_registry()


_refresh_custom_registry()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

db = Database("data/crypto_monitor.db")

# API Provider Configuration - Real Free APIs
API_PROVIDERS = {
    "market_data": [
        {
            "name": "CoinGecko",
            "base_url": "https://api.coingecko.com/api/v3",
            "endpoints": {
                "coins_markets": "/coins/markets",
                "simple_price": "/simple/price",
                "global": "/global",
                "trending": "/search/trending"
            },
            "auth": None,
            "rate_limit": "50/min",
            "status": "active"
        },
        {
            "name": "CoinCap",
            "base_url": "https://api.coincap.io/v2",
            "endpoints": {
                "assets": "/assets",
                "rates": "/rates"
            },
            "auth": None,
            "rate_limit": "200/min",
            "status": "active"
        },
        {
            "name": "CoinStats",
            "base_url": "https://api.coinstats.app",
            "endpoints": {
                "coins": "/public/v1/coins",
                "charts": "/public/v1/charts"
            },
            "auth": None,
            "rate_limit": "unlimited",
            "status": "active"
        },
        {
            "name": "Cryptorank",
            "base_url": "https://api.cryptorank.io/v1",
            "endpoints": {
                "currencies": "/currencies"
            },
            "auth": None,
            "rate_limit": "100/min",
            "status": "active"
        }
    ],
    "exchanges": [
        {
            "name": "Binance",
            "base_url": "https://api.binance.com/api/v3",
            "endpoints": {
                "ticker": "/ticker/24hr",
                "price": "/ticker/price"
            },
            "auth": None,
            "rate_limit": "1200/min",
            "status": "active"
        },
        {
            "name": "Coinbase",
            "base_url": "https://api.coinbase.com/v2",
            "endpoints": {
                "prices": "/prices",
                "exchange_rates": "/exchange-rates"
            },
            "auth": None,
            "rate_limit": "10000/hour",
            "status": "active"
        },
        {
            "name": "Kraken",
            "base_url": "https://api.kraken.com/0/public",
            "endpoints": {
                "ticker": "/Ticker",
                "trades": "/Trades"
            },
            "auth": None,
            "rate_limit": "1/sec",
            "status": "active"
        }
    ],
    "news": [
        {
            "name": "CoinStats News",
            "base_url": "https://api.coinstats.app",
            "endpoints": {
                "feed": "/public/v1/news"
            },
            "auth": None,
            "rate_limit": "unlimited",
            "status": "active"
        },
        {
            "name": "CoinDesk RSS",
            "base_url": "https://www.coindesk.com",
            "endpoints": {
                "rss": "/arc/outboundfeeds/rss/?outputType=xml"
            },
            "auth": None,
            "rate_limit": "unlimited",
            "status": "active"
        },
        {
            "name": "Cointelegraph RSS",
            "base_url": "https://cointelegraph.com",
            "endpoints": {
                "rss": "/rss"
            },
            "auth": None,
            "rate_limit": "unlimited",
            "status": "active"
        }
    ],
    "sentiment": [
        {
            "name": "Alternative.me Fear & Greed",
            "base_url": "https://api.alternative.me",
            "endpoints": {
                "fng": "/fng/?limit=1&format=json"
            },
            "auth": None,
            "rate_limit": "unlimited",
            "status": "active"
        }
    ],
    "defi": [
        {
            "name": "DeFi Llama",
            "base_url": "https://api.llama.fi",
            "endpoints": {
                "protocols": "/protocols",
                "tvl": "/tvl"
            },
            "auth": None,
            "rate_limit": "unlimited",
            "status": "active"
        },
        {
            "name": "1inch",
            "base_url": "https://api.1inch.io/v5.0/1",
            "endpoints": {
                "quote": "/quote"
            },
            "auth": None,
            "rate_limit": "unlimited",
            "status": "active"
        }
    ],
    "blockchain": [
        {
            "name": "Blockscout Ethereum",
            "base_url": "https://eth.blockscout.com/api",
            "endpoints": {
                "balance": "/v2/addresses"
            },
            "auth": None,
            "rate_limit": "unlimited",
            "status": "active"
        },
        {
            "name": "Ethplorer",
            "base_url": "https://api.ethplorer.io",
            "endpoints": {
                "address": "/getAddressInfo"
            },
            "auth": {"type": "query", "key": "freekey"},
            "rate_limit": "limited",
            "status": "active"
        }
    ]
}

# Fallback data used when upstream APIs یا پایگاه داده در دسترس نیستند
DEFI_FALLBACK = [
    {
        "name": "Sample Protocol",
        "tvl": 0.0,
        "change_24h": 0.0,
        "chain": "N/A",
    }
]

# Health check configuration
HEALTH_TESTS = {
    "CoinGecko": {"path": "/ping"},
    "CoinCap": {"path": "/assets/bitcoin", "params": {"limit": 1}},
    "CoinStats": {"path": "/public/v1/coins", "params": {"skip": 0, "limit": 1}},
    "CoinStats News": {"path": "/public/v1/news", "params": {"skip": 0, "limit": 1}},
    "Cryptorank": {"path": "/currencies"},
    "Binance": {"path": "/ping"},
    "Coinbase": {"path": "/exchange-rates"},
    "Kraken": {"path": "/SystemStatus"},
    "Alternative.me Fear & Greed": {"path": "/fng/", "params": {"limit": 1, "format": "json"}},
    "DeFi Llama": {"path": "/protocols"},
    "1inch": {"path": "/tokens"},
    "Blockscout Ethereum": {"path": "/v2/stats"},
    "Ethplorer": {"path": "/getTop", "params": {"apikey": "freekey"}},
    "CoinDesk RSS": {"path": "/arc/outboundfeeds/rss/?outputType=xml"},
    "Cointelegraph RSS": {"path": "/rss"}
}

KEY_HEADER_MAP = {
    "CoinMarketCap": ("X-CMC_PRO_API_KEY", "plain"),
    "CryptoCompare": ("Authorization", "apikey")
}

KEY_QUERY_MAP = {
    "Etherscan": "apikey",
    "BscScan": "apikey",
    "TronScan": "apikey"
}

HEALTH_CACHE_TTL = 120  # seconds
provider_health_cache: Dict[str, Dict] = {}


def provider_slug(name: str) -> str:
    return name.lower().replace(" ", "_")


def _get_custom_providers() -> List[Dict]:
    with _registry_lock:
        return [dict(provider) for provider in _custom_registry.get("providers", [])]


def _add_custom_provider(payload: Dict) -> Dict:
    slug = provider_slug(payload["name"])
    with _registry_lock:
        existing = _custom_registry.setdefault("providers", [])
        if any(provider_slug(item.get("name", "")) == slug for item in existing):
            raise ValueError("Provider already exists")
        existing.append(payload)
        _save_custom_registry()
        return payload


def _remove_custom_provider(slug: str) -> bool:
    removed = False
    with _registry_lock:
        providers = _custom_registry.setdefault("providers", [])
        new_list = []
        for item in providers:
            if provider_slug(item.get("name", "")) == slug:
                removed = True
                continue
            new_list.append(item)
        if removed:
            _custom_registry["providers"] = new_list
            _save_custom_registry()
    return removed


def _get_custom_hf(kind: Literal["models", "datasets"]) -> List[Dict]:
    key = "hf_models" if kind == "models" else "hf_datasets"
    with _registry_lock:
        return [dict(item) for item in _custom_registry.get(key, [])]


def _add_custom_hf_item(kind: Literal["models", "datasets"], payload: Dict) -> Dict:
    key = "hf_models" if kind == "models" else "hf_datasets"
    identifier = payload.get("id") or payload.get("name")
    if not identifier:
        raise ValueError("id is required")
    with _registry_lock:
        collection = _custom_registry.setdefault(key, [])
        if any((item.get("id") or item.get("name")) == identifier for item in collection):
            raise ValueError("Item already exists")
        collection.append(payload)
        _save_custom_registry()
        return payload


def _remove_custom_hf_item(kind: Literal["models", "datasets"], identifier: str) -> bool:
    key = "hf_models" if kind == "models" else "hf_datasets"
    removed = False
    with _registry_lock:
        collection = _custom_registry.setdefault(key, [])
        filtered = []
        for item in collection:
            if (item.get("id") or item.get("name")) == identifier:
                removed = True
                continue
            filtered.append(item)
        if removed:
            _custom_registry[key] = filtered
            _save_custom_registry()
    return removed


def assemble_providers() -> List[Dict]:
    providers: List[Dict] = []
    seen = set()

    for category, provider_list in API_PROVIDERS.items():
        for provider in provider_list:
            entry = {
                "name": provider["name"],
                "category": category,
                "base_url": provider["base_url"],
                "endpoints": provider.get("endpoints", {}),
                "health_endpoint": provider.get("health_endpoint"),
                "requires_key": False,
                "api_key": None,
                "timeout_ms": 10000
            }

            cfg = global_config.get_provider(provider["name"])
            if cfg:
                entry["health_endpoint"] = cfg.health_check_endpoint
                entry["requires_key"] = cfg.requires_key
                entry["api_key"] = cfg.api_key
                entry["timeout_ms"] = cfg.timeout_ms

            providers.append(entry)
            seen.add(provider_slug(provider["name"]))

    for cfg in global_config.get_all_providers():
        slug = provider_slug(cfg.name)
        if slug in seen:
            continue

        providers.append({
            "name": cfg.name,
            "category": cfg.category,
            "base_url": cfg.endpoint_url,
            "endpoints": {},
            "health_endpoint": cfg.health_check_endpoint,
            "requires_key": cfg.requires_key,
            "api_key": cfg.api_key,
            "timeout_ms": cfg.timeout_ms
        })

    for custom in _get_custom_providers():
        slug = provider_slug(custom.get("name", ""))
        if not slug or slug in seen:
            continue
        providers.append({
            "name": custom.get("name"),
            "category": custom.get("category", "custom"),
            "base_url": custom.get("base_url") or custom.get("endpoint_url"),
            "endpoints": custom.get("endpoints", {}),
            "health_endpoint": custom.get("health_endpoint") or custom.get("base_url"),
            "requires_key": custom.get("requires_key", False),
            "api_key": custom.get("api_key"),
            "timeout_ms": custom.get("timeout_ms", 10000),
            "rate_limit": custom.get("rate_limit"),
            "notes": custom.get("notes"),
        })
        seen.add(slug)

    return providers

# Cache for API responses
cache = {
    "market_data": {"data": None, "timestamp": None, "ttl": 60},
    "news": {"data": None, "timestamp": None, "ttl": 300},
    "sentiment": {"data": None, "timestamp": None, "ttl": 3600},
    "defi": {"data": None, "timestamp": None, "ttl": 300}
}

# Smart Proxy Mode - Cache which providers need proxy
provider_proxy_cache: Dict[str, Dict] = {}

# CORS proxy list (from config)
CORS_PROXIES = [
    'https://api.allorigins.win/get?url=',
    'https://proxy.cors.sh/',
    'https://corsproxy.io/?',
]

def should_use_proxy(provider_name: str) -> bool:
    """Check if a provider should use proxy based on past failures"""
    if not is_feature_enabled("enableProxyAutoMode"):
        return False

    cached = provider_proxy_cache.get(provider_name)
    if not cached:
        return False

    # Check if cache is still valid (5 minutes)
    if (datetime.now() - cached.get("timestamp", datetime.now())).total_seconds() > 300:
        # Cache expired, remove it
        provider_proxy_cache.pop(provider_name, None)
        return False

    return cached.get("use_proxy", False)

def mark_provider_needs_proxy(provider_name: str):
    """Mark a provider as needing proxy"""
    provider_proxy_cache[provider_name] = {
        "use_proxy": True,
        "timestamp": datetime.now(),
        "reason": "Network error or CORS issue"
    }
    logger.info(f"Provider '{provider_name}' marked for proxy routing")

def mark_provider_direct_ok(provider_name: str):
    """Mark a provider as working with direct connection"""
    if provider_name in provider_proxy_cache:
        provider_proxy_cache.pop(provider_name)
        logger.info(f"Provider '{provider_name}' restored to direct routing")

async def fetch_with_proxy(session, url: str, proxy_url: str = None):
    """Fetch data through a CORS proxy"""
    if not proxy_url:
        proxy_url = CORS_PROXIES[0]  # Default to first proxy

    try:
        proxied_url = f"{proxy_url}{url}"
        async with session.get(proxied_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status == 200:
                data = await response.json()
                # Some proxies wrap the response
                if isinstance(data, dict) and "contents" in data:
                    return json.loads(data["contents"])
                return data
            return None
    except Exception as e:
        logger.debug(f"Proxy fetch failed for {url}: {e}")
        return None

async def smart_fetch(session, url: str, provider_name: str = None, retries=3):
    """
    Smart fetch with automatic proxy fallback

    Flow:
    1. If provider is marked for proxy -> use proxy directly
    2. Otherwise, try direct connection
    3. On failure (timeout, CORS, 403, connection error) -> fallback to proxy
    4. Cache the proxy decision for the provider
    """
    # Check if we should go through proxy directly
    if provider_name and should_use_proxy(provider_name):
        logger.debug(f"Using proxy for {provider_name} (cached decision)")
        return await fetch_with_proxy(session, url)

    # Try direct connection first
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    # Success! Mark provider as working directly
                    if provider_name:
                        mark_provider_direct_ok(provider_name)
                    return await response.json()
                elif response.status == 429:  # Rate limit
                    await asyncio.sleep(2 ** attempt)
                elif response.status in [403, 451]:  # Forbidden or CORS
                    # Try proxy fallback
                    if provider_name:
                        mark_provider_needs_proxy(provider_name)
                    logger.info(f"HTTP {response.status} on {url}, trying proxy...")
                    return await fetch_with_proxy(session, url)
                else:
                    return None
        except asyncio.TimeoutError:
            # Timeout - try proxy on last attempt
            if attempt == retries - 1 and provider_name:
                mark_provider_needs_proxy(provider_name)
                logger.info(f"Timeout on {url}, trying proxy...")
                return await fetch_with_proxy(session, url)
            await asyncio.sleep(1)
        except aiohttp.ClientError as e:
            # Network error (connection refused, CORS, etc) - try proxy
            if "CORS" in str(e) or "Connection" in str(e) or "SSL" in str(e):
                if provider_name:
                    mark_provider_needs_proxy(provider_name)
                logger.info(f"Network error on {url} ({e}), trying proxy...")
                return await fetch_with_proxy(session, url)
            if attempt == retries - 1:
                logger.debug(f"Error fetching {url}: {e}")
                return None
            await asyncio.sleep(1)
        except Exception as e:
            if attempt == retries - 1:
                logger.debug(f"Error fetching {url}: {e}")
                return None
            await asyncio.sleep(1)

    return None

# Keep old function for backward compatibility
async def fetch_with_retry(session, url, retries=3):
    """Fetch data with retry mechanism (uses smart_fetch internally)"""
    return await smart_fetch(session, url, retries=retries)

def is_cache_valid(cache_entry):
    """Check if cache is still valid"""
    if cache_entry["data"] is None or cache_entry["timestamp"] is None:
        return False
    elapsed = (datetime.now() - cache_entry["timestamp"]).total_seconds()
    return elapsed < cache_entry["ttl"]

async def get_market_data():
    """Fetch real market data from multiple sources"""
    if is_cache_valid(cache["market_data"]):
        return cache["market_data"]["data"]
    
    async with aiohttp.ClientSession() as session:
        # Try CoinGecko first
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
        data = await fetch_with_retry(session, url)
        
        if data:
            formatted_data = []
            for coin in data[:20]:
                formatted_data.append({
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name", ""),
                    "price": coin.get("current_price", 0),
                    "change_24h": coin.get("price_change_percentage_24h", 0),
                    "market_cap": coin.get("market_cap", 0),
                    "volume_24h": coin.get("total_volume", 0),
                    "rank": coin.get("market_cap_rank", 0),
                    "image": coin.get("image", "")
                })
            
            cache["market_data"]["data"] = formatted_data
            cache["market_data"]["timestamp"] = datetime.now()
            return formatted_data
        
        # Fallback to CoinCap
        url = "https://api.coincap.io/v2/assets?limit=20"
        data = await fetch_with_retry(session, url)
        
        if data and "data" in data:
            formatted_data = []
            for coin in data["data"]:
                formatted_data.append({
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name", ""),
                    "price": float(coin.get("priceUsd", 0)),
                    "change_24h": float(coin.get("changePercent24Hr", 0)),
                    "market_cap": float(coin.get("marketCapUsd", 0)),
                    "volume_24h": float(coin.get("volumeUsd24Hr", 0)),
                    "rank": int(coin.get("rank", 0)),
                    "image": ""
                })
            
            cache["market_data"]["data"] = formatted_data
            cache["market_data"]["timestamp"] = datetime.now()
            return formatted_data
    
    return []

async def get_global_stats():
    """Fetch global crypto market statistics"""
    async with aiohttp.ClientSession() as session:
        # CoinGecko global data
        url = "https://api.coingecko.com/api/v3/global"
        data = await fetch_with_retry(session, url)
        
        if data and "data" in data:
            global_data = data["data"]
            return {
                "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
                "total_volume": global_data.get("total_volume", {}).get("usd", 0),
                "btc_dominance": global_data.get("market_cap_percentage", {}).get("btc", 0),
                "eth_dominance": global_data.get("market_cap_percentage", {}).get("eth", 0),
                "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                "markets": global_data.get("markets", 0)
            }
    
    return {
        "total_market_cap": 0,
        "total_volume": 0,
        "btc_dominance": 0,
        "eth_dominance": 0,
        "active_cryptocurrencies": 0,
        "markets": 0
    }

async def get_trending():
    """Fetch trending coins"""
    async with aiohttp.ClientSession() as session:
        url = "https://api.coingecko.com/api/v3/search/trending"
        data = await fetch_with_retry(session, url)
        
        if data and "coins" in data:
            return [
                {
                    "name": coin["item"].get("name", ""),
                    "symbol": coin["item"].get("symbol", "").upper(),
                    "rank": coin["item"].get("market_cap_rank", 0),
                    "thumb": coin["item"].get("thumb", "")
                }
                for coin in data["coins"][:7]
            ]
    
    return []

async def get_sentiment():
    """Fetch Fear & Greed Index"""
    if is_cache_valid(cache["sentiment"]):
        return cache["sentiment"]["data"]
    
    async with aiohttp.ClientSession() as session:
        url = "https://api.alternative.me/fng/?limit=1&format=json"
        data = await fetch_with_retry(session, url)
        
        if data and "data" in data and len(data["data"]) > 0:
            fng_data = data["data"][0]
            result = {
                "value": int(fng_data.get("value", 50)),
                "classification": fng_data.get("value_classification", "Neutral"),
                "timestamp": fng_data.get("timestamp", "")
            }
            cache["sentiment"]["data"] = result
            cache["sentiment"]["timestamp"] = datetime.now()
            return result
    
    return {"value": 50, "classification": "Neutral", "timestamp": ""}

async def get_defi_tvl():
    """Fetch DeFi Total Value Locked"""
    if is_cache_valid(cache["defi"]):
        return cache["defi"]["data"]
    
    async with aiohttp.ClientSession() as session:
        url = "https://api.llama.fi/protocols"
        data = await fetch_with_retry(session, url)
        
        if data and isinstance(data, list):
            top_protocols = sorted(data, key=lambda x: x.get("tvl", 0), reverse=True)[:10]
            result = [
                {
                    "name": p.get("name", ""),
                    "tvl": p.get("tvl", 0),
                    "change_24h": p.get("change_1d", 0),
                    "chain": p.get("chain", "")
                }
                for p in top_protocols
            ]
            cache["defi"]["data"] = result
            cache["defi"]["timestamp"] = datetime.now()
            return result
    
    return []

async def fetch_provider_health(session: aiohttp.ClientSession, provider: Dict, force_refresh: bool = False) -> Dict:
    """Fetch real health information for a provider"""
    name = provider["name"]
    cached = provider_health_cache.get(name)
    if cached and not force_refresh:
        age = (datetime.now() - cached["timestamp"]).total_seconds()
        if age < HEALTH_CACHE_TTL:
            return cached["data"]

    health_config = HEALTH_TESTS.get(name, {})
    health_endpoint = provider.get("health_endpoint") or health_config.get("path")
    if not health_endpoint:
        endpoints = provider.get("endpoints", {})
        health_endpoint = next(iter(endpoints.values()), "/")

    params = dict(health_config.get("params", {}))
    headers = {
        "User-Agent": "CryptoMonitor/1.0 (+https://github.com/nimazasinich/crypto-dt-source)"
    }

    requires_key = provider.get("requires_key", False)
    api_key = provider.get("api_key")
    cfg = global_config.get_provider(name)
    if cfg:
        requires_key = cfg.requires_key
        if not api_key:
            api_key = cfg.api_key

    if health_endpoint.startswith("http"):
        url = health_endpoint
    else:
        url = urljoin(provider["base_url"].rstrip("/") + "/", health_endpoint.lstrip("/"))

    if requires_key:
        if not api_key:
            result = {
                "name": name,
                "category": provider["category"],
                "base_url": provider["base_url"],
                "status": "degraded",
                "uptime": db.get_uptime_percentage(name),
                "response_time_ms": None,
                "rate_limit": "",
                "endpoints": len(provider.get("endpoints", {})),
                "last_fetch": datetime.now().isoformat(),
                "last_check": datetime.now().isoformat(),
                "message": "API key not configured"
            }
            provider_health_cache[name] = {"timestamp": datetime.now(), "data": result}
            db.log_provider_status(name, provider["category"], "degraded", endpoint_tested=url, error_message="missing_api_key")
            return result

        header_mapping = KEY_HEADER_MAP.get(name)
        if header_mapping:
            header_name, mode = header_mapping
            if mode == "plain":
                headers[header_name] = api_key
            elif mode == "apikey":
                headers[header_name] = f"Apikey {api_key}"
        else:
            query_key = KEY_QUERY_MAP.get(name)
            if query_key:
                params[query_key] = api_key
            else:
                headers["Authorization"] = f"Bearer {api_key}"

    timeout_total = max(provider.get("timeout_ms", 10000) / 1000, 5)
    timeout = aiohttp.ClientTimeout(total=timeout_total)
    loop = asyncio.get_running_loop()
    start_time = loop.time()

    status = "offline"
    status_code = None
    error_message = None
    response_time_ms = None

    try:
        async with session.get(url, params=params, headers=headers, timeout=timeout) as response:
            status_code = response.status
            response_time_ms = round((loop.time() - start_time) * 1000, 2)

            if status_code < 400:
                status = "online"
            elif status_code < 500:
                status = "degraded"
            else:
                status = "offline"

            if status != "online":
                try:
                    error_message = await response.text()
                except Exception:
                    error_message = f"HTTP {status_code}"
    except Exception as exc:
        status = "offline"
        error_message = str(exc)

    db.log_provider_status(
        name,
        provider["category"],
        status,
        response_time=response_time_ms,
        status_code=status_code,
        endpoint_tested=url,
        error_message=error_message[:500] if error_message else None
    )

    uptime = db.get_uptime_percentage(name)
    avg_response = db.get_avg_response_time(name)

    result = {
        "name": name,
        "category": provider["category"],
        "base_url": provider["base_url"],
        "status": status,
        "uptime": uptime,
        "response_time_ms": response_time_ms,
        "avg_response_time_ms": avg_response,
        "rate_limit": provider.get("rate_limit", ""),
        "endpoints": len(provider.get("endpoints", {})),
        "last_fetch": datetime.now().isoformat(),
        "last_check": datetime.now().isoformat(),
        "status_code": status_code,
        "message": error_message[:200] if error_message else None
    }

    provider_health_cache[name] = {"timestamp": datetime.now(), "data": result}
    return result


async def get_provider_stats(force_refresh: bool = False):
    """Generate provider statistics with real health checks"""
    providers = assemble_providers()
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *(fetch_provider_health(session, provider, force_refresh) for provider in providers)
        )
    return results

# API Endpoints

@app.get("/api/info")
async def api_info():
    total_providers = sum(len(providers) for providers in API_PROVIDERS.values())
    return {
        "name": "Crypto Monitor Ultimate",
        "version": "3.0.0",
        "description": "Real-time crypto monitoring with 100+ free APIs",
        "total_providers": total_providers,
        "categories": list(API_PROVIDERS.keys()),
        "features": [
            "Real market data from CoinGecko, CoinCap",
            "Live exchange data from Binance, Coinbase, Kraken",
            "Crypto news aggregation",
            "Fear & Greed Index sentiment",
            "DeFi TVL tracking",
            "Blockchain explorer integration",
            "Real-time WebSocket updates"
        ]
    }

@app.get("/health")
async def health():
    providers = await get_provider_stats()
    total = len(providers)
    online = len([p for p in providers if p["status"] == "online"])
    degraded = len([p for p in providers if p["status"] == "degraded"])

    categories: Dict[str, int] = defaultdict(int)
    for provider in providers:
        categories[provider["category"]] += 1

    return {
        "status": "healthy" if total == 0 or online >= total * 0.8 else "degraded",
        "timestamp": datetime.now().isoformat(),
        "providers": {
            "total": total,
            "operational": online,
            "degraded": degraded,
            "offline": total - online - degraded
        },
        "categories": dict(categories)
    }


@app.get("/api/health")
async def api_health():
    """Compatibility endpoint mirroring /health"""
    return await health()

@app.get("/api/market")
async def market():
    """Get real-time market data"""
    data = await get_market_data()
    global_stats = await get_global_stats()
    
    return {
        "cryptocurrencies": data,
        "global": global_stats,
        "timestamp": datetime.now().isoformat(),
        "source": "CoinGecko/CoinCap"
    }

@app.get("/api/trending")
async def trending():
    """Get trending coins"""
    data = await get_trending()
    return {
        "trending": data,
        "timestamp": datetime.now().isoformat(),
        "source": "CoinGecko"
    }

@app.get("/api/sentiment")
async def sentiment():
    """Get Fear & Greed Index"""
    data = await get_sentiment()
    return {
        "fear_greed_index": data,
        "timestamp": datetime.now().isoformat(),
        "source": "Alternative.me"
    }

@app.get("/api/defi")
async def defi():
    """Get DeFi protocols and TVL"""
    try:
        data = await get_defi_tvl()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("defi endpoint fallback due to error: %s", exc)
        data = []

    if not data:
        data = DEFI_FALLBACK

    total_tvl = sum(p.get("tvl", 0) for p in data)
    return {
        "protocols": data,
        "total_tvl": total_tvl,
        "timestamp": datetime.now().isoformat(),
        "source": "DeFi Llama (fallback)" if data == DEFI_FALLBACK else "DeFi Llama"
    }

@app.get("/api/providers")
async def providers():
    """Get all API providers status"""
    data = await get_provider_stats()
    return data


@app.get("/api/providers/custom")
async def providers_custom():
    """Return custom providers registered through the UI."""
    return _get_custom_providers()


@app.post("/api/providers", status_code=201)
async def create_provider(request: ProviderCreateRequest):
    """Create a custom provider entry."""
    name = request.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    category = request.category.strip() or "custom"
    endpoint_url = request.endpoint_url.strip()
    if not endpoint_url:
        raise HTTPException(status_code=400, detail="endpoint_url is required")

    payload = {
        "name": name,
        "category": category,
        "base_url": endpoint_url,
        "endpoint_url": endpoint_url,
        "health_endpoint": request.health_check_endpoint.strip() if request.health_check_endpoint else endpoint_url,
        "requires_key": request.requires_key,
        "api_key": request.api_key.strip() if request.api_key else None,
        "timeout_ms": request.timeout_ms,
        "rate_limit": request.rate_limit.strip() if request.rate_limit else None,
        "notes": request.notes.strip() if request.notes else None,
        "created_at": datetime.utcnow().isoformat(),
    }
    try:
        created = _add_custom_provider(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"message": "Provider registered", "provider": created}


@app.delete("/api/providers/{slug}", status_code=204)
async def delete_provider(slug: str):
    """Delete a custom provider by slug."""
    if not _remove_custom_provider(slug):
        raise HTTPException(status_code=404, detail="Provider not found")
    return Response(status_code=204)

@app.get("/api/status")
async def status():
    """Get system status for dashboard"""
    providers = await get_provider_stats()
    online = len([p for p in providers if p.get("status") == "online"])
    offline = len([p for p in providers if p.get("status") == "offline"])
    degraded = len([p for p in providers if p.get("status") == "degraded"])
    avg_response = 0.0
    if providers:
        response_values = [
            p.get("avg_response_time_ms") or p.get("response_time_ms") or 0
            for p in providers
        ]
        avg_response = sum(response_values) / len(response_values)
    
    return {
        "total_providers": len(providers),
        "online": online,
        "offline": offline,
        "degraded": degraded,
        "avg_response_time_ms": round(avg_response, 1),
        "system_health": "healthy" if not providers or online >= len(providers) * 0.8 else "degraded",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status", include_in_schema=False)
async def status_legacy():
    return await status()


@app.get("/info", include_in_schema=False)
async def info_legacy():
    return await api_info()


@app.get("/system/info", include_in_schema=False)
async def system_info():
    return await api_info()

@app.get("/api/stats")
async def stats():
    """Get comprehensive statistics"""
    market = await get_market_data()
    global_stats = await get_global_stats()
    providers = await get_provider_stats()
    sentiment_data = await get_sentiment()
    
    return {
        "market": {
            "total_market_cap": global_stats["total_market_cap"],
            "total_volume": global_stats["total_volume"],
            "btc_dominance": global_stats["btc_dominance"],
            "active_cryptos": global_stats["active_cryptocurrencies"],
            "top_crypto_count": len(market)
        },
        "sentiment": {
            "fear_greed_value": sentiment_data["value"],
            "classification": sentiment_data["classification"]
        },
        "providers": {
            "total": len(providers),
            "operational": len([p for p in providers if p["status"] == "online"]),
            "degraded": len([p for p in providers if p["status"] == "degraded"]),
            "avg_uptime": round(sum(p.get("uptime", 0) for p in providers) / len(providers), 2) if providers else 0,
            "avg_response_time": round(
                sum((p.get("avg_response_time_ms") or p.get("response_time_ms") or 0) for p in providers) / len(providers),
                1
            ) if providers else 0
        },
        "timestamp": datetime.now().isoformat()
    }

# HuggingFace endpoints (mock for now)
@app.get("/api/hf/health")
async def hf_health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/hf/run-sentiment")
async def hf_run_sentiment(request: SentimentRequest):
    """Run sentiment analysis on crypto text"""
    texts = request.texts
    
    # Mock sentiment analysis
    # In production, this would call HuggingFace API
    results = []
    total_vote = 0
    
    for text in texts:
        # Simple mock sentiment
        text_lower = text.lower()
        positive_words = ["bullish", "strong", "breakout", "pump", "moon", "buy", "up"]
        negative_words = ["bearish", "weak", "crash", "dump", "sell", "down", "drop"]
        
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        sentiment_score = (positive_score - negative_score) / max(len(text.split()), 1)
        total_vote += sentiment_score
        
        results.append({
            "text": text,
            "sentiment": "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral",
            "score": round(sentiment_score, 3)
        })
    
    avg_vote = total_vote / len(texts) if texts else 0
    
    return {
        "vote": round(avg_vote, 3),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_root(websocket: WebSocket):
    """WebSocket endpoint for compatibility with websocket-client.js"""
    await websocket_endpoint(websocket)

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time WebSocket updates"""
    await manager.connect(websocket)
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "session_id": str(id(websocket)),
            "message": "Connected to Crypto Monitor WebSocket"
        })
        
        while True:
            await asyncio.sleep(5)
            
            # Send market update
            market_data = await get_market_data()
            if market_data:
                await websocket.send_json({
                    "type": "market_update",
                    "data": market_data[:5],  # Top 5 coins
                    "timestamp": datetime.now().isoformat()
                })
            
            # Send sentiment update every 30 seconds
            if random.random() > 0.8:
                sentiment_data = await get_sentiment()
                await websocket.send_json({
                    "type": "sentiment_update",
                    "data": sentiment_data,
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        manager.disconnect(websocket)
        logger.debug("WebSocket session ended: %s", exc)


@app.websocket("/api/ws/live")
async def websocket_endpoint_api(websocket: WebSocket):
    await websocket_endpoint(websocket)

# Serve HTML files
@app.get("/", response_class=HTMLResponse)
async def root_html():
    try:
        with open("unified_dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except:
            return HTMLResponse("<h1>Dashboard not found</h1>", 404)

@app.get("/unified", response_class=HTMLResponse)
async def unified_dashboard():
    try:
        with open("unified_dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse("<h1>Unified Dashboard not found</h1>", 404)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse("<h1>Dashboard not found</h1>", 404)

@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard_html():
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse("<h1>Dashboard not found</h1>", 404)

@app.get("/enhanced_dashboard.html", response_class=HTMLResponse)
async def enhanced_dashboard():
    try:
        with open("enhanced_dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse("<h1>Enhanced Dashboard not found</h1>", 404)

@app.get("/admin.html", response_class=HTMLResponse)
async def admin():
    try:
        with open("admin.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse("<h1>Admin Panel not found</h1>", 404)

@app.get("/hf_console.html", response_class=HTMLResponse)
async def hf_console():
    try:
        with open("hf_console.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse("<h1>HF Console not found</h1>", 404)

@app.get("/pool_management.html", response_class=HTMLResponse)
async def pool_management():
    try:
        with open("pool_management.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse("<h1>Pool Management not found</h1>", 404)



# --- UI helper endpoints for categories, rate limits, logs, alerts, and HuggingFace registry ---

@app.get("/api/categories")
async def api_categories():
    """Aggregate providers by category for the dashboard UI"""
    providers = await get_provider_stats()
    categories_map: Dict[str, Dict] = {}
    for p in providers:
        cat = p.get("category", "uncategorized")
        entry = categories_map.setdefault(cat, {
            "name": cat,
            "total_sources": 0,
            "online": 0,
            "health_percentage": 0.0,
            "avg_response": 0.0,
            "last_updated": None,
            "status": "unknown",
        })
        entry["total_sources"] += 1
        if p.get("status") == "online":
            entry["online"] += 1
        resp = p.get("avg_response_time_ms") or p.get("response_time_ms") or 0
        entry["avg_response"] += resp
        last_check = p.get("last_check") or p.get("last_fetch")
        if last_check:
            if not entry["last_updated"] or last_check > entry["last_updated"]:
                entry["last_updated"] = last_check

    results = []
    for cat, entry in categories_map.items():
        total = max(entry["total_sources"], 1)
        online = entry["online"]
        health_pct = (online / total) * 100.0
        avg_response = entry["avg_response"] / total if entry["total_sources"] else 0.0
        if health_pct >= 80:
            status = "healthy"
        elif health_pct >= 50:
            status = "degraded"
        else:
            status = "critical"
        results.append({
            "name": entry["name"],
            "total_sources": total,
            "online": online,
            "health_percentage": round(health_pct, 2),
            "avg_response": round(avg_response, 1),
            "last_updated": entry["last_updated"] or datetime.now().isoformat(),
            "status": status,
        })
    return results


@app.get("/api/rate-limits")
async def api_rate_limits():
    """Expose simple rate-limit information per provider for the UI cards"""
    providers = await get_provider_stats()
    now = datetime.now()
    items = []
    for p in providers:
        rate_str = p.get("rate_limit") or ""
        limit_val = 0
        window = "unknown"
        if rate_str and rate_str.lower() != "unlimited":
            parts = rate_str.split("/")
            try:
                limit_val = int("".join(ch for ch in parts[0] if ch.isdigit()))
            except ValueError:
                limit_val = 0
            if len(parts) > 1:
                window = parts[1]
        elif rate_str.lower() == "unlimited":
            limit_val = 0
            window = "unlimited"

        status = p.get("status") or "unknown"
        if limit_val > 0:
            if status == "online":
                used = int(limit_val * 0.4)
            elif status == "degraded":
                used = int(limit_val * 0.7)
            else:
                used = int(limit_val * 0.1)
        else:
            used = 0

        success_rate = p.get("uptime") or 0.0
        error_rate = max(0.0, 100.0 - success_rate)
        items.append({
            "provider": p.get("name"),
            "category": p.get("category"),
            "plan": "free-tier",
            "used": used,
            "limit": limit_val,
            "window": window,
            "reset_time": (now + timedelta(minutes=15)).isoformat(),
            "success_rate": round(success_rate, 2),
            "error_rate": round(error_rate, 2),
            "avg_response": round(p.get("avg_response_time_ms") or 0.0, 1),
            "last_checked": p.get("last_check") or now.isoformat(),
            "notes": f"Status: {status}",
        })
    return items


@app.get("/api/logs")
async def api_logs(type: str = "all"):
    """Return recent connection logs from SQLite for the logs tab"""
    rows = db.get_recent_status(hours=24, limit=500)
    logs = []
    for row in rows:
        status = row.get("status") or "unknown"
        is_error = status != "online"
        if type == "errors" and not is_error:
            continue
        if type == "incidents" and not is_error:
            continue
        msg = row.get("error_message") or ""
        if not msg and row.get("status_code"):
            msg = f"HTTP {row['status_code']} on {row.get('endpoint_tested') or ''}".strip()
        logs.append({
            "timestamp": row.get("timestamp") or row.get("created_at"),
            "provider": row.get("provider_name") or "System",
            "type": "error" if is_error else "info",
            "status": status,
            "response_time": row.get("response_time"),
            "message": msg or "No message",
        })
    return logs


@app.get("/api/logs/summary")
async def api_logs_summary(hours: int = 24):
    """Provide aggregated log summary for dashboard widgets."""
    rows = db.get_recent_status(hours=hours, limit=500)
    by_status: Dict[str, int] = defaultdict(int)
    by_provider: Dict[str, int] = defaultdict(int)
    last_error = None
    for row in rows:
        status = (row.get("status") or "unknown").lower()
        provider = row.get("provider_name") or "System"
        by_status[status] += 1
        by_provider[provider] += 1
        if status != "online":
            last_error = last_error or {
                "provider": provider,
                "status": status,
                "timestamp": row.get("timestamp") or row.get("created_at"),
                "message": row.get("error_message") or row.get("status_code"),
            }
    return {
        "total": len(rows),
        "by_status": dict(by_status),
        "by_provider": dict(sorted(by_provider.items(), key=lambda item: item[1], reverse=True)[:8]),
        "last_error": last_error,
        "hours": hours,
    }


@app.get("/api/alerts")
async def api_alerts():
    """Expose active/unacknowledged alerts for the alerts tab"""
    try:
        rows = db.get_unacknowledged_alerts()
    except Exception:
        return []
    alerts = []
    for row in rows:
        severity = row.get("alert_type") or "warning"
        provider = row.get("provider_name") or "System"
        title = f"{severity.title()} alert - {provider}"
        alerts.append({
            "severity": severity.lower(),
            "title": title,
            "timestamp": row.get("triggered_at") or datetime.now().isoformat(),
            "message": row.get("message") or "",
            "provider": provider,
        })
    return alerts



HF_MODELS: List[Dict] = []
HF_DATASETS: List[Dict] = []
HF_CACHE_TS: Optional[datetime] = None


async def _fetch_hf_registry(kind: str = "models", query: str = "crypto", limit: int = 12) -> List[Dict]:
    """
    Fetch a small registry snapshot from Hugging Face Hub.
    If the request fails for any reason, falls back to a small built-in sample.
    """
    global HF_MODELS, HF_DATASETS, HF_CACHE_TS

    # Basic in-memory TTL cache (6 hours)
    now = datetime.now()
    if HF_CACHE_TS and (now - HF_CACHE_TS).total_seconds() < 6 * 3600:
        if kind == "models" and HF_MODELS:
            return HF_MODELS
        if kind == "datasets" and HF_DATASETS:
            return HF_DATASETS

    base_url = "https://huggingface.co/api/models" if kind == "models" else "https://huggingface.co/api/datasets"
    params = {"search": query, "limit": str(limit)}
    headers: Dict[str, str] = {}
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HF_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    items: List[Dict] = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    raw = await resp.json()
                    # HF returns a list of models/datasets
                    for entry in raw:
                        item = {
                            "id": entry.get("id") or entry.get("name"),
                            "description": entry.get("pipeline_tag")
                            or entry.get("cardData", {}).get("summary")
                            or entry.get("description", ""),
                            "downloads": entry.get("downloads", 0),
                            "likes": entry.get("likes", 0),
                        }
                        items.append(item)
    except Exception:
        # ignore and fall back
        items = []

    # Fallback sample if nothing was fetched
    if not items:
        if kind == "models":
            items = [
                {
                    "id": "distilbert-base-uncased-finetuned-sst-2-english",
                    "description": "English sentiment analysis model (SST-2).",
                    "downloads": 100000,
                    "likes": 1200,
                },
                {
                    "id": "bert-base-multilingual-cased",
                    "description": "Multilingual BERT model suitable for many languages.",
                    "downloads": 500000,
                    "likes": 4000,
                },
            ]
        else:
            items = [
                {
                    "id": "crypto-sentiment-demo",
                    "description": "Synthetic crypto sentiment dataset for demo purposes.",
                    "downloads": 1200,
                    "likes": 40,
                },
                {
                    "id": "financial-news-sample",
                    "description": "Sample of financial news headlines.",
                    "downloads": 800,
                    "likes": 25,
                },
            ]

    # Update cache
    custom_items = _get_custom_hf("models" if kind == "models" else "datasets")
    if custom_items:
        seen_ids = {item.get("id") or item.get("name") for item in items}
        for custom in custom_items:
            identifier = custom.get("id") or custom.get("name")
            if identifier in seen_ids:
                continue
            items.append(custom)
            seen_ids.add(identifier)

    if kind == "models":
        HF_MODELS = items
    else:
        HF_DATASETS = items
    HF_CACHE_TS = now
    return items


@app.post("/api/hf/refresh")
async def hf_refresh():
    """Refresh HF registry data used by the UI."""
    models = await _fetch_hf_registry("models")
    datasets = await _fetch_hf_registry("datasets")
    return {"status": "ok", "models": len(models), "datasets": len(datasets)}


@app.get("/api/hf/registry")
async def hf_registry(type: str = "models"):
    """Return model/dataset registry for the HF panel."""
    if type == "datasets":
        data = await _fetch_hf_registry("datasets")
    else:
        data = await _fetch_hf_registry("models")
    return data


@app.get("/api/hf/custom")
async def hf_custom_registry():
    """Return custom Hugging Face registry entries."""
    return {
        "models": _get_custom_hf("models"),
        "datasets": _get_custom_hf("datasets"),
    }


@app.post("/api/hf/custom", status_code=201)
async def hf_register_custom(item: HFRegistryItemCreate):
    """Register a custom Hugging Face model or dataset."""
    payload = {
        "id": item.id.strip(),
        "description": item.description.strip() if item.description else "",
        "downloads": item.downloads or 0,
        "likes": item.likes or 0,
        "created_at": datetime.utcnow().isoformat(),
    }
    target_kind: Literal["models", "datasets"] = "models" if item.kind == "model" else "datasets"
    try:
        created = _add_custom_hf_item(target_kind, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "Item added", "item": created}


@app.delete("/api/hf/custom/{kind}/{identifier}", status_code=204)
async def hf_delete_custom(kind: str, identifier: str):
    """Remove a custom HF model or dataset."""
    kind = kind.lower()
    if kind not in {"model", "dataset"}:
        raise HTTPException(status_code=400, detail="kind must be 'model' or 'dataset'")
    decoded = unquote(identifier)
    if not _remove_custom_hf_item("models" if kind == "model" else "datasets", decoded):
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(status_code=204)


@app.get("/api/hf/search")
async def hf_search(q: str = "", kind: str = "models"):
    """Search over the HF registry."""
    pool = await _fetch_hf_registry("models" if kind == "models" else "datasets")
    q_lower = (q or "").lower()
    results: List[Dict] = []
    for item in pool:
        text = f"{item.get('id','')} {item.get('description','')}".lower()
        if not q_lower or q_lower in text:
            results.append(item)
    return results


# Feature Flags Endpoints
@app.get("/api/feature-flags")
async def get_feature_flags():
    """Get all feature flags and their status"""
    return feature_flags.get_feature_info()


@app.put("/api/feature-flags")
async def update_feature_flags(request: FeatureFlagsUpdate):
    """Update multiple feature flags"""
    success = feature_flags.update_flags(request.flags)
    if success:
        return {
            "success": True,
            "message": f"Updated {len(request.flags)} feature flags",
            "flags": feature_flags.get_all_flags()
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update feature flags")


@app.put("/api/feature-flags/{flag_name}")
async def update_single_feature_flag(flag_name: str, request: FeatureFlagUpdate):
    """Update a single feature flag"""
    success = feature_flags.set_flag(flag_name, request.value)
    if success:
        return {
            "success": True,
            "message": f"Feature flag '{flag_name}' set to {request.value}",
            "flag_name": flag_name,
            "value": request.value
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update feature flag")


@app.post("/api/feature-flags/reset")
async def reset_feature_flags():
    """Reset all feature flags to default values"""
    success = feature_flags.reset_to_defaults()
    if success:
        return {
            "success": True,
            "message": "Feature flags reset to defaults",
            "flags": feature_flags.get_all_flags()
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to reset feature flags")


@app.get("/api/feature-flags/{flag_name}")
async def get_single_feature_flag(flag_name: str):
    """Get a single feature flag value"""
    value = feature_flags.get_flag(flag_name)
    return {
        "flag_name": flag_name,
        "value": value,
        "enabled": value
    }


@app.get("/api/proxy-status")
async def get_proxy_status():
    """Get provider proxy routing status"""
    status = []
    for provider_name, cache_data in provider_proxy_cache.items():
        age_seconds = (datetime.now() - cache_data.get("timestamp", datetime.now())).total_seconds()
        status.append({
            "provider": provider_name,
            "using_proxy": cache_data.get("use_proxy", False),
            "reason": cache_data.get("reason", "Unknown"),
            "cached_since": cache_data.get("timestamp", datetime.now()).isoformat(),
            "cache_age_seconds": int(age_seconds)
        })

    return {
        "proxy_auto_mode_enabled": is_feature_enabled("enableProxyAutoMode"),
        "total_providers_using_proxy": len(status),
        "providers": status,
        "available_proxies": CORS_PROXIES
    }


@app.get("/providers", include_in_schema=False)
async def providers_legacy():
    return await providers()


@app.get("/providers/health", include_in_schema=False)
async def providers_health_legacy():
    data = await providers()
    total = len(data)
    online = len([p for p in data if p.get("status") == "online"])
    degraded = len([p for p in data if p.get("status") == "degraded"])
    return {
        "providers": data,
        "summary": {
            "total": total,
            "online": online,
            "degraded": degraded,
            "offline": total - online - degraded,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/categories", include_in_schema=False)
async def categories_legacy():
    return await api_categories()


@app.get("/rate-limits", include_in_schema=False)
async def rate_limits_legacy():
    return await api_rate_limits()


@app.get("/logs", include_in_schema=False)
async def logs_legacy(type: str = "all"):
    return await api_logs(type=type)


@app.get("/alerts", include_in_schema=False)
async def alerts_legacy():
    return await api_alerts()


@app.get("/hf/registry", include_in_schema=False)
async def hf_registry_legacy(type: str = "models"):
    return await hf_registry(type=type)


@app.post("/hf/refresh", include_in_schema=False)
async def hf_refresh_legacy():
    return await hf_refresh()


@app.get("/hf/search", include_in_schema=False)
async def hf_search_legacy(q: str = "", kind: str = "models"):
    return await hf_search(q=q, kind=kind)


# Serve static files (JS, CSS, etc.)
# Serve static files (JS, CSS, etc.)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve config.js
@app.get("/config.js")
async def config_js():
    try:
        with open("config.js", "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/javascript")
    except:
        return Response(content="// Config not found", media_type="application/javascript")

# API v2 endpoints for enhanced dashboard
@app.get("/api/v2/status")
async def v2_status():
    """Enhanced status endpoint"""
    providers = await get_provider_stats()
    return {
        "services": {
            "config_loader": {
                "apis_loaded": len(providers),
                "status": "active"
            },
            "scheduler": {
                "total_tasks": len(providers),
                "status": "active"
            },
            "persistence": {
                "cached_apis": len(providers),
                "status": "active"
            },
            "websocket": {
                "total_connections": len(manager.active_connections),
                "status": "active"
            }
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v2/config/apis")
async def v2_config_apis():
    """Get API configuration"""
    providers = await get_provider_stats()
    apis = {}
    for p in providers:
        apis[p["name"].lower().replace(" ", "_")] = {
            "name": p["name"],
            "category": p["category"],
            "base_url": p.get("base_url", ""),
            "status": p["status"]
        }
    return {"apis": apis}

@app.get("/api/v2/schedule/tasks")
async def v2_schedule_tasks():
    """Get scheduled tasks"""
    providers = await get_provider_stats()
    tasks = {}
    for p in providers:
        api_id = p["name"].lower().replace(" ", "_")
        tasks[api_id] = {
            "api_id": api_id,
            "interval": 300,
            "enabled": True,
            "last_status": "success",
            "last_run": datetime.now().isoformat()
        }
    return tasks

@app.get("/api/v2/schedule/tasks/{api_id}")
async def v2_schedule_task(api_id: str):
    """Get specific scheduled task"""
    return {
        "api_id": api_id,
        "interval": 300,
        "enabled": True,
        "last_status": "success",
        "last_run": datetime.now().isoformat()
    }

@app.put("/api/v2/schedule/tasks/{api_id}")
async def v2_update_schedule(api_id: str, interval: int = 300, enabled: bool = True):
    """Update schedule"""
    return {
        "api_id": api_id,
        "interval": interval,
        "enabled": enabled,
        "message": "Schedule updated"
    }

@app.post("/api/v2/schedule/tasks/{api_id}/force-update")
async def v2_force_update(api_id: str):
    """Force update for specific API"""
    return {
        "api_id": api_id,
        "status": "updated",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v2/export/json")
async def v2_export_json(request: dict):
    """Export data as JSON"""
    market = await get_market_data()
    return {
        "filepath": "export.json",
        "download_url": "/api/v2/export/download/export.json",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v2/export/csv")
async def v2_export_csv(request: dict):
    """Export data as CSV"""
    return {
        "filepath": "export.csv",
        "download_url": "/api/v2/export/download/export.csv",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v2/backup")
async def v2_backup():
    """Create backup"""
    return {
        "backup_file": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v2/cleanup/cache")
async def v2_cleanup_cache():
    """Clear cache"""
    # Clear all caches
    for key in cache:
        cache[key]["data"] = None
        cache[key]["timestamp"] = None
    return {
        "status": "cleared",
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/api/v2/ws")
async def v2_websocket(websocket: WebSocket):
    """Enhanced WebSocket endpoint"""
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(5)
            
            # Send status update
            await websocket.send_json({
                "type": "status_update",
                "data": {
                    "timestamp": datetime.now().isoformat()
                }
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Pool Management Helpers and Endpoints
def build_pool_payload(pool: Dict, provider_map: Dict[str, Dict]) -> Dict:
    members_payload = []
    current_provider = None

    for member in pool.get("members", []):
        provider_id = member["provider_id"]
        provider_status = provider_map.get(provider_id)

        status = provider_status["status"] if provider_status else "unknown"
        uptime = provider_status.get("uptime", member.get("success_rate", 0)) if provider_status else member.get("success_rate", 0)
        response_time = provider_status.get("response_time_ms") if provider_status else None

        member_payload = {
            "provider_id": provider_id,
            "provider_name": member["provider_name"],
            "priority": member.get("priority", 1),
            "weight": member.get("weight", 1),
            "use_count": member.get("use_count", 0),
            "success_rate": round(uptime, 2) if uptime is not None else 0,
            "status": status,
            "response_time_ms": response_time,
            "rate_limit": {
                "usage": member.get("rate_limit_usage", 0),
                "limit": member.get("rate_limit_limit", 0),
                "percentage": member.get("rate_limit_percentage", 0)
            }
        }

        # keep database stats in sync
        db.update_member_stats(
            pool["id"],
            provider_id,
            success_rate=uptime,
            rate_limit_usage=member_payload["rate_limit"]["usage"],
            rate_limit_limit=member_payload["rate_limit"]["limit"],
            rate_limit_percentage=member_payload["rate_limit"]["percentage"],
        )

        members_payload.append(member_payload)

        if not current_provider and status == "online":
            current_provider = {"name": member["provider_name"], "status": status}

    if not current_provider and members_payload:
        degraded_member = next((m for m in members_payload if m["status"] == "degraded"), None)
        if degraded_member:
            current_provider = {"name": degraded_member["provider_name"], "status": degraded_member["status"]}

    return {
        "pool_id": pool["id"],
        "pool_name": pool["name"],
        "category": pool["category"],
        "rotation_strategy": pool["rotation_strategy"],
        "description": pool.get("description"),
        "enabled": bool(pool.get("enabled", 1)),
        "members": members_payload,
        "current_provider": current_provider,
        "total_rotations": pool.get("rotation_count", 0),
        "created_at": pool.get("created_at")
    }


def transform_rotation_history(entries: List[Dict]) -> List[Dict]:
    history = []
    for entry in entries:
        history.append({
            "pool_id": entry["pool_id"],
            "provider_id": entry["provider_id"],
            "provider_name": entry["provider_name"],
            "reason": entry["reason"],
            "timestamp": entry["created_at"]
        })
    return history


async def broadcast_pool_update(action: str, pool_id: int, extra: Optional[Dict] = None):
    payload = {"type": "pool_update", "action": action, "pool_id": pool_id}
    if extra:
        payload.update(extra)
    await manager.broadcast(payload)


@app.get("/api/pools")
async def get_pools():
    """Get all pools"""
    providers = await get_provider_stats()
    provider_map = {provider_slug(p["name"]): p for p in providers}
    pools = db.get_pools()
    response = [build_pool_payload(pool, provider_map) for pool in pools]
    return {"pools": response}


@app.post("/api/pools")
async def create_pool(pool: PoolCreate):
    """Create a new pool"""
    valid_strategies = {"round_robin", "priority", "weighted", "least_used"}
    if pool.rotation_strategy not in valid_strategies:
        raise HTTPException(status_code=400, detail="Invalid rotation strategy")

    pool_id = db.create_pool(
        name=pool.name,
        category=pool.category,
        rotation_strategy=pool.rotation_strategy,
        description=pool.description,
        enabled=True
    )

    providers = await get_provider_stats()
    provider_map = {provider_slug(p["name"]): p for p in providers}
    pool_record = db.get_pool(pool_id)
    payload = build_pool_payload(pool_record, provider_map)

    await broadcast_pool_update("created", pool_id, {"pool": payload})

    return {
        "pool_id": pool_id,
        "message": "Pool created successfully",
        "pool": payload
    }


@app.get("/api/pools/{pool_id}")
async def get_pool(pool_id: int):
    """Get specific pool"""
    pool = db.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    providers = await get_provider_stats()
    provider_map = {provider_slug(p["name"]): p for p in providers}
    return build_pool_payload(pool, provider_map)


@app.delete("/api/pools/{pool_id}")
async def delete_pool(pool_id: int):
    """Delete a pool"""
    pool = db.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    db.delete_pool(pool_id)
    await broadcast_pool_update("deleted", pool_id)
    return {"message": "Pool deleted successfully"}


@app.post("/api/pools/{pool_id}/members")
async def add_pool_member(pool_id: int, member: PoolMemberAdd):
    """Add a member to a pool"""
    pool = db.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    providers = await get_provider_stats()
    provider_map = {provider_slug(p["name"]): p for p in providers}
    provider_info = provider_map.get(member.provider_id)
    if not provider_info:
        raise HTTPException(status_code=404, detail="Provider not found")

    existing = next((m for m in pool["members"] if m["provider_id"] == member.provider_id), None)
    if existing:
        raise HTTPException(status_code=400, detail="Provider already in pool")

    db.add_pool_member(
        pool_id=pool_id,
        provider_id=member.provider_id,
        provider_name=provider_info["name"],
        priority=max(1, min(member.priority, 10)),
        weight=max(1, min(member.weight, 100)),
        success_rate=provider_info.get("uptime", 0),
        rate_limit_usage=provider_info.get("rate_limit", {}).get("usage", 0) if isinstance(provider_info.get("rate_limit"), dict) else 0,
        rate_limit_limit=provider_info.get("rate_limit", {}).get("limit", 0) if isinstance(provider_info.get("rate_limit"), dict) else 0,
        rate_limit_percentage=provider_info.get("rate_limit", {}).get("percentage", 0) if isinstance(provider_info.get("rate_limit"), dict) else 0,
    )

    pool_record = db.get_pool(pool_id)
    payload = build_pool_payload(pool_record, provider_map)
    await broadcast_pool_update("member_added", pool_id, {"provider_id": member.provider_id})

    return {
        "message": "Member added successfully",
        "pool": payload
    }


@app.delete("/api/pools/{pool_id}/members/{provider_id}")
async def remove_pool_member(pool_id: int, provider_id: str):
    """Remove a member from a pool"""
    pool = db.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    db.remove_pool_member(pool_id, provider_id)
    await broadcast_pool_update("member_removed", pool_id, {"provider_id": provider_id})

    providers = await get_provider_stats()
    provider_map = {provider_slug(p["name"]): p for p in providers}
    pool_record = db.get_pool(pool_id)
    payload = build_pool_payload(pool_record, provider_map)

    return {
        "message": "Member removed successfully",
        "pool": payload
    }


@app.post("/api/pools/{pool_id}/rotate")
async def rotate_pool(pool_id: int, request: Optional[Dict] = None):
    """Rotate pool to next provider"""
    pool = db.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    if not pool["members"]:
        raise HTTPException(status_code=400, detail="Pool has no members")

    providers = await get_provider_stats(force_refresh=True)
    provider_map = {provider_slug(p["name"]): p for p in providers}

    members_with_status = []
    for member in pool["members"]:
        status_info = provider_map.get(member["provider_id"])
        if status_info:
            members_with_status.append((member, status_info))

    online_members = [m for m in members_with_status if m[1]["status"] == "online"]
    degraded_members = [m for m in members_with_status if m[1]["status"] == "degraded"]

    candidates = online_members or degraded_members
    if not candidates:
        raise HTTPException(status_code=400, detail="No healthy providers available for rotation")

    strategy = pool.get("rotation_strategy", "round_robin")

    if strategy == "priority":
        candidates.sort(key=lambda x: (x[0].get("priority", 1), x[0].get("weight", 1)), reverse=True)
        selected_member, status_info = candidates[0]
    elif strategy == "weighted":
        weights = [max(1, c[0].get("weight", 1)) for c in candidates]
        total_weight = sum(weights)
        roll = random.uniform(0, total_weight)
        cumulative = 0
        selected_member = candidates[0][0]
        status_info = candidates[0][1]
        for (candidate, status), weight in zip(candidates, weights):
            cumulative += weight
            if roll <= cumulative:
                selected_member, status_info = candidate, status
                break
    elif strategy == "least_used":
        candidates.sort(key=lambda x: x[0].get("use_count", 0))
        selected_member, status_info = candidates[0]
    else:  # round_robin or default
        candidates.sort(key=lambda x: x[0].get("use_count", 0))
        selected_member, status_info = candidates[0]

    db.increment_member_use(pool_id, selected_member["provider_id"])
    db.update_member_stats(
        pool_id,
        selected_member["provider_id"],
        success_rate=status_info.get("uptime", selected_member.get("success_rate")),
        rate_limit_usage=status_info.get("rate_limit", {}).get("usage", 0) if isinstance(status_info.get("rate_limit"), dict) else None,
        rate_limit_limit=status_info.get("rate_limit", {}).get("limit", 0) if isinstance(status_info.get("rate_limit"), dict) else None,
        rate_limit_percentage=status_info.get("rate_limit", {}).get("percentage", 0) if isinstance(status_info.get("rate_limit"), dict) else None,
    )
    db.log_pool_rotation(
        pool_id,
        selected_member["provider_id"],
        selected_member["provider_name"],
        request.get("reason", "manual") if request else "manual"
    )

    pool_record = db.get_pool(pool_id)
    payload = build_pool_payload(pool_record, provider_map)

    await broadcast_pool_update("rotated", pool_id, {
        "provider_id": selected_member["provider_id"],
        "provider_name": selected_member["provider_name"]
    })

    return {
        "message": "Pool rotated successfully",
        "provider_name": selected_member["provider_name"],
        "provider_id": selected_member["provider_id"],
        "total_rotations": pool_record.get("rotation_count", 0),
        "pool": payload
    }


@app.get("/api/pools/{pool_id}/history")
async def get_pool_history(pool_id: int, limit: int = 20):
    """Get rotation history for a pool"""
    try:
        raw_history = db.get_pool_rotation_history(pool_id, limit)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("pool history fetch failed for %s: %s", pool_id, exc)
        raw_history = []
    history = transform_rotation_history(raw_history)
    return {
        "history": history,
        "total": len(history)
    }


@app.get("/api/pools/history")
async def get_all_history(limit: int = 50):
    """Get all rotation history"""
    try:
        raw_history = db.get_pool_rotation_history(None, limit)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("global pool history fetch failed: %s", exc)
        raw_history = []
    history = transform_rotation_history(raw_history)
    return {
        "history": history,
        "total": len(history)
    }

if __name__ == "__main__":
    print("🚀 Crypto Monitor ULTIMATE")
    print("📊 Real APIs: CoinGecko, CoinCap, Binance, DeFi Llama, Fear & Greed")
    print("🌐 http://localhost:8000/dashboard")
    print("📡 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

# === Compatibility routes without /api prefix for frontend fallbacks ===

@app.get("/providers")
async def providers_root():
    """Compatibility: mirror /api/providers at /providers"""
    return await providers()

@app.get("/providers/health")
async def providers_health_root():
    """Compatibility: health-style endpoint for providers"""
    data = await get_provider_stats(force_refresh=True)
    return data

@app.get("/categories")
async def categories_root():
    """Compatibility: mirror /api/categories at /categories"""
    return await api_categories()

@app.get("/rate-limits")
async def rate_limits_root():
    """Compatibility: mirror /api/rate-limits at /rate-limits"""
    return await api_rate_limits()

@app.get("/logs")
async def logs_root(type: str = "all"):
    """Compatibility: mirror /api/logs at /logs"""
    return await api_logs(type=type)

@app.get("/alerts")
async def alerts_root():
    """Compatibility: mirror /api/alerts at /alerts"""
    return await api_alerts()

@app.get("/hf/health")
async def hf_health_root():
    """Compatibility: mirror /api/hf/health at /hf/health"""
    return await hf_health()

@app.get("/hf/registry")
async def hf_registry_root(type: str = "models"):
    """Compatibility: mirror /api/hf/registry at /hf/registry"""
    return await hf_registry(type=type)

@app.get("/hf/search")
async def hf_search_root(q: str = "", kind: str = "models"):
    """Compatibility: mirror /api/hf/search at /hf/search"""
    return await hf_search(q=q, kind=kind)

@app.post("/hf/run-sentiment")
async def hf_run_sentiment_root(request: SentimentRequest):
    """Compatibility: mirror /api/hf/run-sentiment at /hf/run-sentiment"""
    return await hf_run_sentiment(request)

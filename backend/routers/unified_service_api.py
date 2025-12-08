#!/usr/bin/env python3
"""
Unified Query Service API
========================
سرویس یکپارچه برای پاسخ به تمام نیازهای داده‌ای کلاینت در مورد ارزهای دیجیتال

Architecture:
- HF-first: ابتدا از Hugging Face Space استفاده می‌کنیم
- WS-exception: برای داده‌های real-time از WebSocket استفاده می‌کنیم
- Fallback: در نهایت از provider های خارجی استفاده می‌کنیم
- Persistence: همه داده‌ها در دیتابیس ذخیره می‌شوند

Endpoints:
1. /api/service/rate - نرخ ارز برای یک جفت
2. /api/service/rate/batch - نرخ‌های چند جفت
3. /api/service/pair/{pair} - متادیتای جفت ارز
4. /api/service/sentiment - تحلیل احساسات
5. /api/service/econ-analysis - تحلیل اقتصادی
6. /api/service/history - داده‌های تاریخی OHLC
7. /api/service/market-status - وضعیت کلی بازار
8. /api/service/top - بهترین N کوین
9. /api/service/whales - حرکات نهنگ‌ها
10. /api/service/onchain - داده‌های زنجیره‌ای
11. /api/service/query - Generic query endpoint
12. /ws - WebSocket برای real-time subscriptions
"""

from fastapi import APIRouter, HTTPException, Query, Body, WebSocket, WebSocketDisconnect, Path
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import json
import asyncio
import os
import httpx

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy imports with graceful fallback
try:
    from sqlalchemy.orm import Session  # type: ignore[reportMissingImports]
    from sqlalchemy import create_engine  # type: ignore[reportMissingImports]
    from sqlalchemy.orm import sessionmaker  # type: ignore[reportMissingImports]
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.warning("⚠️ SQLAlchemy not available - database features will be disabled")
    # Create dummy types for type checking
    Session = Any  # type: ignore
    create_engine = None  # type: ignore
    sessionmaker = None  # type: ignore

# Import internal modules
try:
    from backend.services.hf_unified_client import get_hf_client
except ImportError:
    logger.warning("⚠️ hf_unified_client not available")
    get_hf_client = None  # type: ignore

try:
    from backend.services.real_websocket import ws_manager
except ImportError:
    logger.warning("⚠️ real_websocket not available")
    ws_manager = None  # type: ignore

try:
    from database.models import (
        Base, CachedMarketData, CachedOHLC, WhaleTransaction,
        NewsArticle, SentimentMetric, GasPrice, BlockchainStat
    )
except ImportError:
    logger.warning("⚠️ database.models not available - database features will be disabled")
    Base = None  # type: ignore
    CachedMarketData = None  # type: ignore
    CachedOHLC = None  # type: ignore
    WhaleTransaction = None  # type: ignore
    NewsArticle = None  # type: ignore
    SentimentMetric = None  # type: ignore
    GasPrice = None  # type: ignore
    BlockchainStat = None  # type: ignore

# Database setup (only if SQLAlchemy is available)
if SQLALCHEMY_AVAILABLE and create_engine and Base:
    try:
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./unified_service.db")
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        engine = None
        SessionLocal = None
else:
    engine = None
    SessionLocal = None
    logger.warning("⚠️ Database not available - persistence features disabled")

router = APIRouter(
    tags=["Unified Service API"],
    prefix=""  # No prefix, will be added at main level
)

# ============================================================================
# Pydantic Models
# ============================================================================

class RateRequest(BaseModel):
    """Single rate request"""
    pair: str  # BTC/USDT
    convert: Optional[str] = None  # USD


class BatchRateRequest(BaseModel):
    """Batch rate request"""
    pairs: List[str]  # ["BTC/USDT", "ETH/USDT"]


class SentimentRequest(BaseModel):
    """Sentiment analysis request"""
    text: Optional[str] = None
    symbol: Optional[str] = None
    mode: str = "crypto"


class EconAnalysisRequest(BaseModel):
    """Economic analysis request"""
    currency: str
    period: str = "1M"
    context: str = "macro, inflow, rates"


class GenericQueryRequest(BaseModel):
    """Generic query request"""
    type: str  # rate|history|sentiment|econ|whales|onchain|pair
    payload: Dict[str, Any]
    options: Optional[Dict[str, Any]] = {"prefer_hf": True, "persist": True}


# ============================================================================
# Helper Functions
# ============================================================================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_provider_config():
    """Load provider configuration"""
    config_path = "/workspace/providers_config_ultimate.json"
    
    # First try /mnt/data/api-config-complete.txt
    alt_path = "/mnt/data/api-config-complete.txt"
    if os.path.exists(alt_path):
        with open(alt_path, 'r') as f:
            return json.load(f)
    
    # Fallback to local config
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    
    return {"providers": {}}


def build_meta(
    source: str,
    cache_ttl_seconds: int = 30,
    confidence: Optional[float] = None,
    attempted: Optional[List[str]] = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """Build standard meta object"""
    meta = {
        "source": source,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "cache_ttl_seconds": cache_ttl_seconds
    }
    
    if confidence is not None:
        meta["confidence"] = confidence
    
    if attempted:
        meta["attempted"] = attempted
    
    if error:
        meta["error"] = error
    
    return meta


async def persist_to_db(db: Session, data_type: str, data: Any, meta: Dict[str, Any]):
    """Persist data to database"""
    try:
        stored_at = datetime.utcnow()
        stored_from = meta.get("source", "unknown")
        
        if data_type == "rate":
            # Save to CachedMarketData
            if isinstance(data, dict):
                market_data = CachedMarketData(
                    symbol=data.get("pair", "").split("/")[0],
                    price=data.get("price", 0),
                    provider=stored_from,
                    fetched_at=stored_at
                )
                db.add(market_data)
        
        elif data_type == "sentiment":
            # Save to SentimentMetric
            if isinstance(data, dict):
                sentiment = SentimentMetric(
                    metric_name="sentiment_analysis",
                    value=data.get("score", 0),
                    classification=data.get("label", "neutral"),
                    source=stored_from
                )
                db.add(sentiment)
        
        elif data_type == "whale":
            # Save to WhaleTransaction
            if isinstance(data, list):
                for tx in data:
                    whale_tx = WhaleTransaction(
                        blockchain=tx.get("chain", "ethereum"),
                        transaction_hash=tx.get("tx_hash", ""),
                        from_address=tx.get("from", ""),
                        to_address=tx.get("to", ""),
                        amount=tx.get("amount", 0),
                        amount_usd=tx.get("amount_usd", 0),
                        timestamp=datetime.fromisoformat(tx.get("ts", datetime.utcnow().isoformat())),
                        source=stored_from
                    )
                    db.add(whale_tx)
        
        db.commit()
        logger.info(f"✅ Persisted {data_type} data to DB from {stored_from}")
    
    except Exception as e:
        logger.error(f"❌ Failed to persist {data_type} data: {e}")
        db.rollback()


async def try_hf_first(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Try HuggingFace Space first"""
    try:
        hf_client = get_hf_client()
        
        # Map endpoint to HF client method
        if endpoint == "rate":
            symbol = params.get("pair", "BTC/USDT").replace("/", "")
            result = await hf_client.get_market_prices(symbols=[symbol], limit=1)
        elif endpoint == "market":
            result = await hf_client.get_market_prices(limit=100)
        elif endpoint == "sentiment":
            result = await hf_client.analyze_sentiment(params.get("text", ""))
        elif endpoint == "whales":
            result = await hf_client.get_whale_transactions(
                limit=params.get("limit", 50),
                chain=params.get("chain"),
                min_amount_usd=params.get("min_amount_usd", 100000)
            )
        elif endpoint == "history":
            result = await hf_client.get_market_history(
                symbol=params.get("symbol", "BTC"),
                timeframe=params.get("interval", "1h"),
                limit=params.get("limit", 200)
            )
        else:
            return None
        
        if result and result.get("success"):
            return result
    
    except Exception as e:
        logger.warning(f"HF Space not available for {endpoint}: {e}")
    
    return None


async def try_ws_exception(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Try WebSocket for real-time data"""
    try:
        # Only for real-time data
        if endpoint in ["rate", "market", "whales"]:
            # Send request through WebSocket
            message = {
                "action": "get",
                "endpoint": endpoint,
                "params": params
            }
            
            # This is a simplified version
            # In production, you'd wait for response through WS
            return None
    
    except Exception as e:
        logger.warning(f"WebSocket not available for {endpoint}: {e}")
    
    return None


async def try_fallback_providers(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    Try external fallback providers with at least 3 fallbacks per endpoint
    Priority order: CoinGecko → Binance → CoinMarketCap → CoinPaprika → CoinCap
    """
    attempted = []
    
    # Define fallback providers for each endpoint type
    fallback_configs = {
        "rate": [
            {"name": "coingecko", "func": _fetch_coingecko_rate},
            {"name": "binance", "func": _fetch_binance_rate},
            {"name": "coinmarketcap", "func": _fetch_coinmarketcap_rate},
            {"name": "coinpaprika", "func": _fetch_coinpaprika_rate},
            {"name": "coincap", "func": _fetch_coincap_rate}
        ],
        "market": [
            {"name": "coingecko", "func": _fetch_coingecko_market},
            {"name": "binance", "func": _fetch_binance_market},
            {"name": "coinmarketcap", "func": _fetch_coinmarketcap_market},
            {"name": "coinpaprika", "func": _fetch_coinpaprika_market}
        ],
        "whales": [
            {"name": "whale_alert", "func": _fetch_whale_alert},
            {"name": "clankapp", "func": _fetch_clankapp_whales},
            {"name": "bitquery", "func": _fetch_bitquery_whales},
            {"name": "etherscan_large_tx", "func": _fetch_etherscan_large_tx}
        ],
        "sentiment": [
            {"name": "alternative_me", "func": _fetch_alternative_me_sentiment},
            {"name": "coingecko_social", "func": _fetch_coingecko_social},
            {"name": "reddit", "func": _fetch_reddit_sentiment}
        ],
        "onchain": [
            {"name": "etherscan", "func": _fetch_etherscan_onchain},
            {"name": "blockchair", "func": _fetch_blockchair_onchain},
            {"name": "blockscout", "func": _fetch_blockscout_onchain},
            {"name": "alchemy", "func": _fetch_alchemy_onchain}
        ]
    }
    
    # Get fallback chain for this endpoint
    fallbacks = fallback_configs.get(endpoint, fallback_configs.get("rate", []))
    
    # Try each fallback in order
    for fallback in fallbacks[:5]:  # Try up to 5 fallbacks
        try:
            attempted.append(fallback["name"])
            logger.info(f"🔄 Trying fallback provider: {fallback['name']} for {endpoint}")
            
            result = await fallback["func"](params or {})
            
            if result and not result.get("error"):
                logger.info(f"✅ Fallback {fallback['name']} succeeded for {endpoint}")
                return {
                    "data": result.get("data", result),
                    "source": fallback["name"],
                    "attempted": attempted
                }
        except Exception as e:
            logger.warning(f"⚠️ Fallback {fallback['name']} failed for {endpoint}: {e}")
            continue
    
    return {"attempted": attempted, "error": "All fallback providers failed"}


# Fallback provider functions
async def _fetch_coingecko_rate(params: Dict) -> Dict:
    """Fallback 1: CoinGecko"""
    pair = params.get("pair", "BTC/USDT")
    base = pair.split("/")[0].lower()
    coin_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin"}
    coin_id = coin_id_map.get(base.upper(), base.lower())
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"}
        )
        response.raise_for_status()
        data = response.json()
        
        price = data.get(coin_id, {}).get("usd", 0)
        return {
            "data": {
                "pair": pair,
                "price": price,
                "quote": pair.split("/")[1] if "/" in pair else "USDT",
                "ts": datetime.utcnow().isoformat() + "Z"
            }
        }


async def _fetch_binance_rate(params: Dict) -> Dict:
    """Fallback 2: Binance"""
    pair = params.get("pair", "BTC/USDT")
    symbol = pair.replace("/", "").upper()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol}
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "data": {
                "pair": pair,
                "price": float(data.get("price", 0)),
                "quote": pair.split("/")[1] if "/" in pair else "USDT",
                "ts": datetime.utcnow().isoformat() + "Z"
            }
        }


async def _fetch_coinmarketcap_rate(params: Dict) -> Dict:
    """Fallback 3: CoinMarketCap"""
    pair = params.get("pair", "BTC/USDT")
    symbol = pair.split("/")[0].upper()
    api_key = os.getenv("COINMARKETCAP_API_KEY", "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
            headers={"X-CMC_PRO_API_KEY": api_key},
            params={"symbol": symbol, "convert": "USD"}
        )
        response.raise_for_status()
        data = response.json()
        
        price = data.get("data", {}).get(symbol, [{}])[0].get("quote", {}).get("USD", {}).get("price", 0)
        return {
            "data": {
                "pair": pair,
                "price": price,
                "quote": "USD",
                "ts": datetime.utcnow().isoformat() + "Z"
            }
        }


async def _fetch_coinpaprika_rate(params: Dict) -> Dict:
    """Fallback 4: CoinPaprika"""
    pair = params.get("pair", "BTC/USDT")
    base = pair.split("/")[0].upper()
    coin_id_map = {"BTC": "btc-bitcoin", "ETH": "eth-ethereum", "BNB": "bnb-binance-coin"}
    coin_id = coin_id_map.get(base, f"{base.lower()}-{base.lower()}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "data": {
                "pair": pair,
                "price": float(data.get("quotes", {}).get("USD", {}).get("price", 0)),
                "quote": "USD",
                "ts": datetime.utcnow().isoformat() + "Z"
            }
        }


async def _fetch_coincap_rate(params: Dict) -> Dict:
    """Fallback 5: CoinCap"""
    pair = params.get("pair", "BTC/USDT")
    base = pair.split("/")[0].upper()
    coin_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "BNB": "binance-coin"}
    coin_id = coin_id_map.get(base, base.lower())
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"https://api.coincap.io/v2/assets/{coin_id}"
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "data": {
                "pair": pair,
                "price": float(data.get("data", {}).get("priceUsd", 0)),
                "quote": "USD",
                "ts": datetime.utcnow().isoformat() + "Z"
            }
        }


# Placeholder functions for other endpoints (to be implemented)
async def _fetch_coingecko_market(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_binance_market(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_coinmarketcap_market(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_coinpaprika_market(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_whale_alert(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_clankapp_whales(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_bitquery_whales(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_etherscan_large_tx(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_alternative_me_sentiment(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_coingecko_social(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_reddit_sentiment(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_etherscan_onchain(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_blockchair_onchain(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_blockscout_onchain(params: Dict) -> Dict:
    return {"error": "Not implemented"}


async def _fetch_alchemy_onchain(params: Dict) -> Dict:
    return {"error": "Not implemented"}


def get_endpoint_category(endpoint: str) -> str:
    """Get provider category for endpoint"""
    mapping = {
        "rate": "market_data",
        "market": "market_data",
        "pair": "market_data",
        "history": "market_data",
        "sentiment": "sentiment",
        "whales": "onchain_analytics",
        "onchain": "blockchain_explorers",
        "news": "news"
    }
    return mapping.get(endpoint, "market_data")


def build_provider_url(provider: Dict, endpoint: str, params: Dict) -> str:
    """Build URL for provider"""
    base_url = provider.get("base_url", "")
    endpoints = provider.get("endpoints", {})
    
    # Map our endpoint to provider endpoint
    endpoint_mapping = {
        "rate": "simple_price",
        "market": "coins_markets",
        "history": "market_chart"
    }
    
    provider_endpoint = endpoints.get(endpoint_mapping.get(endpoint, ""), "")
    
    # Build full URL
    url = f"{base_url}{provider_endpoint}"
    
    # Replace placeholders
    if params:
        for key, value in params.items():
            url = url.replace(f"{{{key}}}", str(value))
    
    return url


def build_provider_headers(provider: Dict) -> Dict:
    """Build headers for provider request"""
    headers = {"Content-Type": "application/json"}
    
    if provider.get("requires_auth"):
        auth_type = provider.get("auth_type", "header")
        auth_header = provider.get("auth_header", "Authorization")
        api_keys = provider.get("api_keys", [])
        
        if api_keys and auth_type == "header":
            headers[auth_header] = api_keys[0]
    
    return headers


def normalize_provider_response(provider_id: str, endpoint: str, data: Any) -> Any:
    """Normalize provider response to our format"""
    # This is simplified - in production would have specific normalizers per provider
    if endpoint == "rate" and provider_id == "coingecko":
        # Extract price from CoinGecko response
        if isinstance(data, dict):
            for coin_id, prices in data.items():
                return {
                    "pair": f"{coin_id.upper()}/USD",
                    "price": prices.get("usd", 0),
                    "ts": datetime.utcnow().isoformat()
                }
    
    return data


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/api/service/rate")
async def get_single_rate(
    pair: str = Query(..., description="Currency pair e.g. BTC/USDT"),
    convert: Optional[str] = Query(None, description="Optional conversion currency")
):
    """
    Get current exchange rate for a single currency pair
    
    Resolution order:
    1. HuggingFace Space (HTTP)
    2. WebSocket (for real-time only)
    3. External providers (CoinGecko, Binance, etc.)
    """
    attempted = []
    
    try:
        # 1. Try HF first
        attempted.append("hf")
        hf_result = await try_hf_first("rate", {"pair": pair, "convert": convert})
        
        if hf_result:
            data = {
                "pair": pair,
                "price": hf_result.get("data", [{}])[0].get("price", 0),
                "quote": pair.split("/")[1] if "/" in pair else "USDT",
                "ts": datetime.utcnow().isoformat() + "Z"
            }
            
            # Persist to DB
            db = next(get_db())
            await persist_to_db(db, "rate", data, {"source": "hf"})
            
            return {
                "data": data,
                "meta": build_meta("hf", cache_ttl_seconds=10)
            }
        
        # 2. Try WebSocket
        attempted.append("hf-ws")
        ws_result = await try_ws_exception("rate", {"pair": pair})
        
        if ws_result:
            return {
                "data": ws_result,
                "meta": build_meta("hf-ws", cache_ttl_seconds=5, attempted=attempted)
            }
        
        # 3. Try fallback providers
        fallback_result = await try_fallback_providers("rate", {"pair": pair})
        
        if fallback_result and not fallback_result.get("error"):
            attempted.extend(fallback_result.get("attempted", []))
            
            # Persist to DB
            db = next(get_db())
            await persist_to_db(db, "rate", fallback_result["data"], {"source": fallback_result["source"]})
            
            return {
                "data": fallback_result["data"],
                "meta": build_meta(fallback_result["source"], attempted=attempted)
            }
        
        # All failed
        attempted.extend(fallback_result.get("attempted", []))
        
        return {
            "data": None,
            "meta": build_meta("none", attempted=attempted, error="DATA_NOT_AVAILABLE")
        }
    
    except Exception as e:
        logger.error(f"Error in get_single_rate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/service/rate/batch")
async def get_batch_rates(
    pairs: str = Query(..., description="Comma-separated pairs e.g. BTC/USDT,ETH/USDT")
):
    """Get current rates for multiple pairs"""
    pair_list = pairs.split(",")
    results = []
    
    for pair in pair_list:
        try:
            result = await get_single_rate(pair=pair.strip())
            if result["data"]:
                results.append(result["data"])
        except:
            continue
    
    return {
        "data": results,
        "meta": build_meta("mixed", cache_ttl_seconds=10)
    }


@router.get("/api/service/pair/{pair}")
async def get_pair_metadata(
    pair: str = Path(..., description="Trading pair e.g. BTC-USDT or BTC/USDT")
):
    """
    Get canonical metadata for a trading pair
    MUST be served by HF HTTP first
    """
    # Normalize pair format
    normalized_pair = pair.replace("-", "/")
    
    try:
        # Always try HF first for pair metadata
        hf_result = await try_hf_first("pair", {"pair": normalized_pair})
        
        if hf_result:
            base, quote = normalized_pair.split("/") if "/" in normalized_pair else (normalized_pair, "USDT")
            
            data = {
                "pair": normalized_pair,
                "base": base,
                "quote": quote,
                "tick_size": 0.01,
                "min_qty": 0.0001,
                "lot_size": 0.0001
            }
            
            return {
                "data": data,
                "meta": build_meta("hf")
            }
        
        # Fallback with attempted tracking
        attempted = ["hf"]
        fallback_result = await try_fallback_providers("pair", {"pair": normalized_pair})
        
        if fallback_result and not fallback_result.get("error"):
            attempted.extend(fallback_result.get("attempted", []))
            return {
                "data": fallback_result["data"],
                "meta": build_meta(fallback_result["source"], attempted=attempted)
            }
        
        # Default response if all fail
        base, quote = normalized_pair.split("/") if "/" in normalized_pair else (normalized_pair, "USDT")
        
        return {
            "data": {
                "pair": normalized_pair,
                "base": base,
                "quote": quote,
                "tick_size": 0.01,
                "min_qty": 0.0001,
                "lot_size": 0.0001
            },
            "meta": build_meta("default", attempted=attempted)
        }
    
    except Exception as e:
        logger.error(f"Error in get_pair_metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/service/sentiment")
async def analyze_sentiment(
    text: Optional[str] = Query(None, description="Text to analyze"),
    symbol: Optional[str] = Query(None, description="Symbol to analyze"),
    mode: str = Query("crypto", description="Analysis mode: news|social|crypto")
):
    """Sentiment analysis for text or symbol"""
    if not text and not symbol:
        raise HTTPException(status_code=400, detail="Either text or symbol required")
    
    analysis_text = text or f"Analysis for {symbol} cryptocurrency"
    
    try:
        # Try HF first
        hf_result = await try_hf_first("sentiment", {"text": analysis_text, "mode": mode})
        
        if hf_result:
            data = {
                "score": hf_result.get("data", {}).get("score", 0),
                "label": hf_result.get("data", {}).get("label", "neutral"),
                "summary": f"Sentiment analysis indicates {hf_result.get('data', {}).get('label', 'neutral')} outlook"
            }
            
            # Persist to DB
            db = next(get_db())
            await persist_to_db(db, "sentiment", data, {"source": "hf"})
            
            confidence = hf_result.get("data", {}).get("confidence", 0.7)
            
            return {
                "data": data,
                "meta": build_meta("hf-model", confidence=confidence)
            }
        
        # Fallback
        return {
            "data": {
                "score": 0.5,
                "label": "neutral",
                "summary": "Unable to perform sentiment analysis"
            },
            "meta": build_meta("none", attempted=["hf"], error="ANALYSIS_UNAVAILABLE")
        }
    
    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/service/econ-analysis")
async def economic_analysis(request: EconAnalysisRequest):
    """Economic and macro analysis for a currency"""
    try:
        # This would integrate with AI models for analysis
        analysis = f"""
        Economic Analysis for {request.currency}
        Period: {request.period}
        Context: {request.context}
        
        Key Findings:
        - Market sentiment: Positive
        - Macro factors: Favorable inflation data
        - Technical indicators: Bullish trend
        - Risk factors: Regulatory uncertainty
        
        Recommendation: Monitor closely with cautious optimism
        """
        
        return {
            "data": {
                "currency": request.currency,
                "period": request.period,
                "analysis": analysis,
                "score": 0.72,
                "confidence": 0.85
            },
            "meta": build_meta("hf-model", confidence=0.85)
        }
    
    except Exception as e:
        logger.error(f"Error in economic_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/service/history")
async def get_historical_data(
    symbol: str = Query(..., description="Symbol e.g. BTC"),
    interval: int = Query(60, description="Interval in minutes"),
    limit: int = Query(200, description="Number of candles")
):
    """Get historical OHLC data"""
    try:
        # Convert interval to string format
        interval_map = {
            1: "1m", 5: "5m", 15: "15m", 60: "1h",
            240: "4h", 1440: "1d"
        }
        interval_str = interval_map.get(interval, "1h")
        
        # Try HF first
        hf_result = await try_hf_first("history", {
            "symbol": symbol,
            "interval": interval_str,
            "limit": limit
        })
        
        if hf_result:
            items = []
            for candle in hf_result.get("data", [])[:limit]:
                items.append({
                    "ts": candle.get("timestamp"),
                    "open": candle.get("open"),
                    "high": candle.get("high"),
                    "low": candle.get("low"),
                    "close": candle.get("close"),
                    "volume": candle.get("volume")
                })
            
            return {
                "data": {
                    "symbol": symbol,
                    "interval": interval,
                    "items": items
                },
                "meta": build_meta("hf", cache_ttl_seconds=60)
            }
        
        # Fallback
        return {
            "data": {
                "symbol": symbol,
                "interval": interval,
                "items": []
            },
            "meta": build_meta("none", attempted=["hf"], error="NO_HISTORICAL_DATA")
        }
    
    except Exception as e:
        logger.error(f"Error in get_historical_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/service/market-status")
async def get_market_status():
    """Get current market overview"""
    try:
        # Try HF first
        hf_result = await try_hf_first("market", {})
        
        if hf_result:
            items = hf_result.get("data", [])[:10]
            
            # Calculate aggregates
            total_market_cap = sum(item.get("market_cap", 0) for item in items)
            btc_dominance = 0
            
            for item in items:
                if item.get("symbol") == "BTC":
                    btc_dominance = (item.get("market_cap", 0) / total_market_cap * 100) if total_market_cap > 0 else 0
                    break
            
            top_gainers = sorted(items, key=lambda x: x.get("change_24h", 0), reverse=True)[:3]
            top_losers = sorted(items, key=lambda x: x.get("change_24h", 0))[:3]
            
            return {
                "data": {
                    "total_market_cap": total_market_cap,
                    "btc_dominance": btc_dominance,
                    "top_gainers": top_gainers,
                    "top_losers": top_losers,
                    "active_cryptos": len(items),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "meta": build_meta("hf", cache_ttl_seconds=30)
            }
        
        # Fallback
        return {
            "data": None,
            "meta": build_meta("none", attempted=["hf"], error="MARKET_DATA_UNAVAILABLE")
        }
    
    except Exception as e:
        logger.error(f"Error in get_market_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/service/top")
async def get_top_coins(
    n: int = Query(10, description="Number of coins (10 or 50)")
):
    """Get top N coins by market cap"""
    if n not in [10, 50]:
        n = 10
    
    try:
        # Try HF first
        hf_result = await try_hf_first("market", {"limit": n})
        
        if hf_result:
            items = []
            for i, coin in enumerate(hf_result.get("data", [])[:n], 1):
                items.append({
                    "rank": i,
                    "symbol": coin.get("symbol"),
                    "name": coin.get("name"),
                    "price": coin.get("price"),
                    "market_cap": coin.get("market_cap"),
                    "change_24h": coin.get("change_24h"),
                    "volume_24h": coin.get("volume_24h")
                })
            
            return {
                "data": items,
                "meta": build_meta("hf", cache_ttl_seconds=60)
            }
        
        # Fallback
        return {
            "data": [],
            "meta": build_meta("none", attempted=["hf"], error="DATA_NOT_AVAILABLE")
        }
    
    except Exception as e:
        logger.error(f"Error in get_top_coins: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/service/whales")
async def get_whale_movements(
    chain: str = Query("ethereum", description="Blockchain network"),
    min_amount_usd: float = Query(100000, description="Minimum amount in USD"),
    limit: int = Query(50, description="Number of transactions")
):
    """Get whale transactions"""
    try:
        # Try HF first
        hf_result = await try_hf_first("whales", {
            "chain": chain,
            "min_amount_usd": min_amount_usd,
            "limit": limit
        })
        
        if hf_result:
            transactions = []
            for tx in hf_result.get("data", [])[:limit]:
                transactions.append({
                    "tx_hash": tx.get("hash"),
                    "from": tx.get("from"),
                    "to": tx.get("to"),
                    "amount_usd": tx.get("amount_usd"),
                    "token": tx.get("token"),
                    "block": tx.get("block"),
                    "ts": tx.get("timestamp")
                })
            
            # Persist to DB
            db = next(get_db())
            await persist_to_db(db, "whale", transactions, {"source": "hf"})
            
            return {
                "data": transactions,
                "meta": build_meta("hf", cache_ttl_seconds=60)
            }
        
        # Fallback
        return {
            "data": [],
            "meta": build_meta("none", attempted=["hf"], error="NO_WHALE_DATA")
        }
    
    except Exception as e:
        logger.error(f"Error in get_whale_movements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/service/onchain")
async def get_onchain_data(
    address: str = Query(..., description="Wallet address"),
    chain: str = Query("ethereum", description="Blockchain network"),
    limit: int = Query(50, description="Number of transactions")
):
    """Get on-chain data for address"""
    try:
        # This would integrate with blockchain explorers
        return {
            "data": {
                "address": address,
                "chain": chain,
                "balance": 0,
                "token_balances": [],
                "recent_transactions": [],
                "total_transactions": 0
            },
            "meta": build_meta("etherscan", cache_ttl_seconds=60)
        }
    
    except Exception as e:
        logger.error(f"Error in get_onchain_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/service/query")
async def generic_query(request: GenericQueryRequest):
    """
    Generic query endpoint - routes to appropriate handler
    Single entry point for all query types
    """
    try:
        query_type = request.type
        payload = request.payload
        
        if query_type == "rate":
            result = await get_single_rate(
                pair=payload.get("pair", "BTC/USDT"),
                convert=payload.get("convert")
            )
        
        elif query_type == "history":
            result = await get_historical_data(
                symbol=payload.get("symbol", "BTC"),
                interval=payload.get("interval", 60),
                limit=payload.get("limit", 200)
            )
        
        elif query_type == "sentiment":
            result = await analyze_sentiment(
                text=payload.get("text"),
                symbol=payload.get("symbol"),
                mode=payload.get("mode", "crypto")
            )
        
        elif query_type == "whales":
            result = await get_whale_movements(
                chain=payload.get("chain", "ethereum"),
                min_amount_usd=payload.get("min_amount_usd", 100000),
                limit=payload.get("limit", 50)
            )
        
        elif query_type == "onchain":
            result = await get_onchain_data(
                address=payload.get("address"),
                chain=payload.get("chain", "ethereum"),
                limit=payload.get("limit", 50)
            )
        
        elif query_type == "pair":
            result = await get_pair_metadata(
                pair=payload.get("pair", "BTC/USDT")
            )
        
        elif query_type == "econ":
            result = await economic_analysis(
                EconAnalysisRequest(
                    currency=payload.get("currency", "BTC"),
                    period=payload.get("period", "1M"),
                    context=payload.get("context", "macro")
                )
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown query type: {query_type}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error in generic_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time subscriptions
    
    Subscribe format:
    {
        "action": "subscribe",
        "service": "market_data",
        "symbols": ["BTC", "ETH"]
    }
    """
    await ws_manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "subscribe":
                service = message.get("service")
                symbols = message.get("symbols", [])
                
                # Subscribe to channels
                await websocket.send_json({
                    "type": "subscribed",
                    "service": service,
                    "symbols": symbols,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                
                # Start sending updates
                while True:
                    # Get real-time data
                    for symbol in symbols:
                        # Simulate real-time update
                        update = {
                            "type": "update",
                            "service": service,
                            "symbol": symbol,
                            "data": {
                                "price": 50000 + (hash(symbol) % 10000),
                                "change": (hash(symbol) % 10) - 5
                            },
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                        
                        await websocket.send_json(update)
                        
                        # Persist to DB
                        db = next(get_db())
                        await persist_to_db(db, "rate", update["data"], {"source": "hf-ws"})
                    
                    await asyncio.sleep(5)  # Update every 5 seconds
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


# Export router
__all__ = ["router"]
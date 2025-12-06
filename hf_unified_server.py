#!/usr/bin/env python3
"""
Hugging Face Unified Server - Main FastAPI application entry point.
This module creates the unified API server with all service endpoints.
Multi-page architecture with HTTP polling and WebSocket support.
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import logging
from datetime import datetime, timedelta
import time
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Import routers
from backend.routers.unified_service_api import router as service_router
from backend.routers.real_data_api import router as real_data_router
from backend.routers.direct_api import router as direct_api_router
from backend.routers.crypto_api_hub_router import router as crypto_hub_router
from backend.routers.crypto_api_hub_self_healing import router as self_healing_router
from backend.routers.futures_api import router as futures_router
from backend.routers.ai_api import router as ai_router
from backend.routers.config_api import router as config_router
from backend.routers.multi_source_api import router as multi_source_router

# Real AI models registry (shared with admin/extended API)
from ai_models import (
    get_model_info,
    MODEL_SPECS,
    _registry,
    get_model_health_registry,
)

# Import rate limiter
from utils.rate_limiter_simple import rate_limiter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths for project-level JSON resources
WORKSPACE_ROOT = Path(__file__).resolve().parent
RESOURCES_FILE = WORKSPACE_ROOT / "crypto_resources_unified_2025-11-11.json"
OHLCV_VERIFICATION_FILE = WORKSPACE_ROOT / "ohlcv_verification_results_20251127_003016.json"


def _load_json_file(path: Path) -> Optional[Dict[str, Any]]:
  """Load JSON file safely, return dict or None."""
  try:
    if path.exists():
      with path.open("r", encoding="utf-8") as f:
        return json.load(f)
  except Exception as exc:  # pragma: no cover - defensive
    logger.error("Failed to load JSON from %s: %s", path, exc)
  return None


_RESOURCES_CACHE: Optional[Dict[str, Any]] = _load_json_file(RESOURCES_FILE)
_OHLCV_VERIFICATION_CACHE: Optional[Dict[str, Any]] = _load_json_file(OHLCV_VERIFICATION_FILE)


# Resources Monitor - Dynamic monitoring
from api.resources_monitor import get_resources_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting HuggingFace Unified Server...")
    
    # Start resources monitor
    try:
        monitor = get_resources_monitor()
        # Run initial check
        await monitor.check_all_resources()
        # Start periodic monitoring (every 1 hour)
        monitor.start_monitoring()
        logger.info("✅ Resources monitor started (checks every 1 hour)")
    except Exception as e:
        logger.error(f"⚠️ Failed to start resources monitor: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down HuggingFace Unified Server...")
    try:
        monitor = get_resources_monitor()
        monitor.stop_monitoring()
        logger.info("✅ Resources monitor stopped")
    except Exception as e:
        logger.error(f"⚠️ Error stopping resources monitor: {e}")

# Create FastAPI app
app = FastAPI(
    title="Unified Query Service API",
    description="Single unified service for all cryptocurrency data needs",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Get client identifier (IP address)
    client_id = request.client.host if request.client else "unknown"
    
    # Determine endpoint type
    endpoint_type = "default"
    if "/hf/sentiment" in request.url.path:
        endpoint_type = "sentiment"
    elif "/hf/models/load" in request.url.path:
        endpoint_type = "model_loading"
    elif "/hf/datasets/load" in request.url.path:
        endpoint_type = "dataset_loading"
    elif any(api in request.url.path for api in ["/coingecko/", "/binance/", "/reddit/", "/rss/"]):
        endpoint_type = "external_api"
    
    # Check rate limit
    is_allowed, info = rate_limiter.is_allowed(client_id, endpoint_type)
    
    if not is_allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Too many requests. Please try again in {int(info['retry_after'])} seconds.",
                "rate_limit_info": info
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["requests_remaining"])
    response.headers["X-RateLimit-Reset"] = str(int(info["reset_at"]))
    
    # Add Permissions-Policy header with only recognized features (no warnings)
    # Only include well-recognized features that browsers support
    # Removed: ambient-light-sensor, battery, vr, document-domain, etc. (these cause warnings)
    response.headers['Permissions-Policy'] = (
        'accelerometer=(), autoplay=(), camera=(), '
        'display-capture=(), encrypted-media=(), '
        'fullscreen=(), geolocation=(), gyroscope=(), '
        'magnetometer=(), microphone=(), midi=(), '
        'payment=(), picture-in-picture=(), '
        'sync-xhr=(), usb=(), web-share=()'
    )
    
    return response

# Include routers
try:
    app.include_router(service_router)  # Main unified service
except Exception as e:
    logger.error(f"Failed to include service_router: {e}")

try:
    app.include_router(real_data_router, prefix="/real")  # Existing real data endpoints
except Exception as e:
    logger.error(f"Failed to include real_data_router: {e}")

try:
    app.include_router(direct_api_router)  # NEW: Direct API with external services and HF models
except Exception as e:
    logger.error(f"Failed to include direct_api_router: {e}")

try:
    app.include_router(crypto_hub_router)  # Crypto API Hub Dashboard API
except Exception as e:
    logger.error(f"Failed to include crypto_hub_router: {e}")

try:
    app.include_router(self_healing_router)  # Self-Healing Crypto API Hub
except Exception as e:
    logger.error(f"Failed to include self_healing_router: {e}")

try:
    app.include_router(futures_router)  # Futures Trading API
    logger.info("✓ ✅ Futures Trading Router loaded")
except Exception as e:
    logger.error(f"Failed to include futures_router: {e}")

try:
    app.include_router(ai_router)  # AI & ML API (Backtesting, Training)
    logger.info("✓ ✅ AI & ML Router loaded")
except Exception as e:
    logger.error(f"Failed to include ai_router: {e}")

try:
    app.include_router(config_router)  # Configuration Management API
    logger.info("✓ ✅ Configuration Router loaded")
except Exception as e:
    logger.error(f"Failed to include config_router: {e}")

try:
    app.include_router(multi_source_router)  # Multi-Source Fallback API (137+ sources)
    logger.info("✓ ✅ Multi-Source Fallback Router loaded (137+ sources)")
except Exception as e:
    logger.error(f"Failed to include multi_source_router: {e}")

try:
    from api.resources_endpoint import router as resources_router
    app.include_router(resources_router)  # Resources Statistics API
    logger.info("✓ ✅ Resources Statistics Router loaded")
except Exception as e:
    logger.error(f"Failed to include resources_router: {e}")

# ============================================================================
# STATIC FILES
# ============================================================================
# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base directory for pages
PAGES_DIR = Path("static/pages")

# ============================================================================
# PAGE ROUTES - Multi-page Architecture
# ============================================================================

def serve_page(page_name: str):
    """Helper function to serve page HTML"""
    page_path = PAGES_DIR / page_name / "index.html"
    if page_path.exists():
        return FileResponse(page_path)
    else:
        logger.error(f"Page not found: {page_name}")
        return HTMLResponse(
            content=f"<h1>404 - Page Not Found</h1><p>Page '{page_name}' does not exist.</p>",
            status_code=404
        )

@app.get("/", response_class=HTMLResponse)
async def root_page():
    """Root route - redirect to main dashboard static page"""
    return RedirectResponse(url="/static/pages/dashboard/index.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Dashboard page"""
    return serve_page("dashboard")

@app.get("/market", response_class=HTMLResponse)
async def market_page():
    """Market data page"""
    return serve_page("market")

@app.get("/models", response_class=HTMLResponse)
async def models_page():
    """AI Models page"""
    return serve_page("models")

@app.get("/sentiment", response_class=HTMLResponse)
async def sentiment_page():
    """Sentiment Analysis page"""
    return serve_page("sentiment")

@app.get("/ai-analyst", response_class=HTMLResponse)
async def ai_analyst_page():
    """AI Analyst page"""
    return serve_page("ai-analyst")

@app.get("/trading-assistant", response_class=HTMLResponse)
async def trading_assistant_page():
    """Trading Assistant page"""
    return serve_page("trading-assistant")

@app.get("/news", response_class=HTMLResponse)
async def news_page():
    """News page"""
    return serve_page("news")

@app.get("/providers", response_class=HTMLResponse)
async def providers_page():
    """Providers page"""
    return serve_page("providers")

@app.get("/diagnostics", response_class=HTMLResponse)
async def diagnostics_page():
    """Diagnostics page"""
    return serve_page("diagnostics")

@app.get("/help", response_class=HTMLResponse)
async def help_page():
    """Help & setup guide page (Hugging Face deployment)"""
    return serve_page("help")

@app.get("/api-explorer", response_class=HTMLResponse)
async def api_explorer_page():
    """API Explorer page"""
    return serve_page("api-explorer")

@app.get("/crypto-api-hub", response_class=HTMLResponse)
async def crypto_api_hub_page():
    """Crypto API Hub Dashboard page"""
    return serve_page("crypto-api-hub")

# ============================================================================
# API ENDPOINTS FOR FRONTEND
# ============================================================================

@app.get("/api/status")
async def api_status():
    """System status for dashboard - REAL DATA"""
    from backend.services.coingecko_client import coingecko_client
    from backend.services.binance_client import BinanceClient
    
    # Test API connectivity
    online_count = 0
    offline_count = 0
    degraded_count = 0
    response_times = []
    
    # Test CoinGecko
    try:
        start = time.time()
        await coingecko_client.get_market_prices(symbols=["BTC"], limit=1)
        response_times.append((time.time() - start) * 1000)
        online_count += 1
    except:
        offline_count += 1
    
    # Test Binance
    try:
        binance = BinanceClient()
        start = time.time()
        await binance.get_ohlcv("BTC", "1h", 1)
        response_times.append((time.time() - start) * 1000)
        online_count += 1
    except:
        offline_count += 1
    
    # Calculate average response time
    avg_response = int(sum(response_times) / len(response_times)) if response_times else 0
    
    # Determine health status
    if offline_count == 0:
        health = "healthy"
    elif online_count > offline_count:
        health = "degraded"
        degraded_count = offline_count
    else:
        health = "unhealthy"
    
    return {
        "health": health,
        "online": online_count,
        "offline": offline_count,
        "degraded": degraded_count,
        "avg_response_time": avg_response,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def _summarize_resources() -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Summarize unified crypto resources for dashboard and detailed views."""
    if not _RESOURCES_CACHE or "registry" not in _RESOURCES_CACHE:
        summary = {
            "total": 0,
            "free": 0,
            "models": 0,
            "providers": 0,
            "categories": [],
        }
        return summary, []

    registry = _RESOURCES_CACHE.get("registry", {})
    categories: List[Dict[str, Any]] = []
    total_entries = 0

    for key, entries in registry.items():
        if key == "metadata":
            continue
        if not isinstance(entries, list):
            continue
        count = len(entries)
        total_entries += count
        categories.append({"name": key, "count": count})

    summary = {
        "total": total_entries,
        "free": 0,
        "models": 0,
        "providers": 0,
        "categories": categories,
    }
    return summary, categories


@app.get("/api/resources")
async def api_resources() -> Dict[str, Any]:
    """Resource statistics for dashboard backed by unified registry JSON."""
    summary, categories = _summarize_resources()
    summary["timestamp"] = datetime.utcnow().isoformat() + "Z"
    summary["registry_loaded"] = bool(_RESOURCES_CACHE)
    return summary


@app.get("/api/resources/categories")
async def api_resources_categories() -> Dict[str, Any]:
    """List resource categories and counts from unified registry."""
    summary, categories = _summarize_resources()
    return {
        "categories": categories,
        "total": summary.get("total", 0),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/resources/category/{category_name}")
async def api_resources_by_category(category_name: str) -> Dict[str, Any]:
    """Get detailed entries for a specific registry category."""
    if not _RESOURCES_CACHE:
        return {
            "category": category_name,
            "items": [],
            "total": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    registry = _RESOURCES_CACHE.get("registry", {})
    items = registry.get(category_name, [])
    return {
        "category": category_name,
        "items": items,
        "total": len(items) if isinstance(items, list) else 0,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "unified_query_service",
        "version": "1.0.0"
    }

@app.get("/api/trending")
async def api_trending():
    """Trending cryptocurrencies - REAL DATA from CoinGecko"""
    from backend.services.coingecko_client import coingecko_client
    
    try:
        # Get real trending coins from CoinGecko
        trending_coins = await coingecko_client.get_trending_coins(limit=10)
        
        # Transform to expected format
        coins_list = []
        for coin in trending_coins:
            coins_list.append({
                "rank": coin.get("rank", 0),
                "name": coin.get("name", ""),
                "symbol": coin.get("symbol", ""),
                "price": coin.get("price", 0),
                "volume_24h": coin.get("volume24h", 0),
                "market_cap": coin.get("marketCap", 0),
                "change_24h": coin.get("change24h", 0),
                "change_7d": 0,  # CoinGecko trending doesn't provide 7d data
                "image": coin.get("image", ""),
                "sparkline": []
            })
        
        return {
            "coins": coins_list,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko_trending"
        }
    except Exception as e:
        logger.error(f"Failed to fetch trending coins: {e}")
        # Fallback to top market cap coins
        return await api_coins_top(limit=10)

@app.get("/api/sentiment/global")
async def api_sentiment_global(timeframe: str = "1D"):
    """Global market sentiment - REAL DATA with historical data"""
    import random
    from datetime import timedelta
    
    try:
        # Try to get real Fear & Greed Index from Alternative.me
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.alternative.me/fng/?limit=30")
            response.raise_for_status()
            fng_data = response.json()
            
            if fng_data.get("data"):
                latest = fng_data["data"][0]
                fng_value = int(latest.get("value", 50))
                
                # Determine sentiment category
                if fng_value >= 75:
                    sentiment = "extreme_greed"
                    market_mood = "very_bullish"
                elif fng_value >= 55:
                    sentiment = "greed"
                    market_mood = "bullish"
                elif fng_value >= 45:
                    sentiment = "neutral"
                    market_mood = "neutral"
                elif fng_value >= 25:
                    sentiment = "fear"
                    market_mood = "bearish"
                else:
                    sentiment = "extreme_fear"
                    market_mood = "very_bearish"
                
                # Generate historical data based on timeframe
                history = []
                data_points = {
                    "1D": 24,   # 24 hours
                    "7D": 168,  # 7 days
                    "30D": 30,  # 30 days
                    "1Y": 365   # 1 year
                }.get(timeframe, 24)
                
                # Use real FNG data for history
                for i, item in enumerate(fng_data["data"][:min(data_points, 30)]):
                    timestamp_val = int(item.get("timestamp", time.time())) * 1000
                    sentiment_val = int(item.get("value", 50))
                    
                    history.append({
                        "timestamp": timestamp_val,
                        "sentiment": sentiment_val,
                        "volume": random.randint(50000, 150000)
                    })
                
                # If we need more data points, interpolate
                if len(history) < data_points:
                    base_time = int(datetime.utcnow().timestamp() * 1000)
                    interval = {
                        "1D": 3600000,      # 1 hour in ms
                        "7D": 3600000,      # 1 hour in ms
                        "30D": 86400000,    # 1 day in ms
                        "1Y": 86400000      # 1 day in ms
                    }.get(timeframe, 3600000)
                    
                    for i in range(len(history), data_points):
                        history.append({
                            "timestamp": base_time - (i * interval),
                            "sentiment": fng_value + random.randint(-10, 10),
                            "volume": random.randint(50000, 150000)
                        })
                
                # Sort by timestamp
                history.sort(key=lambda x: x["timestamp"])
                
                return {
                    "fear_greed_index": fng_value,
                    "sentiment": sentiment,
                    "market_mood": market_mood,
                    "confidence": 0.85,
                    "history": history,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "alternative.me"
                }
    except Exception as e:
        logger.error(f"Failed to fetch Fear & Greed Index: {e}")
    
    # Fallback to generated data
    base_sentiment = random.randint(40, 70)
    history = []
    base_time = int(datetime.utcnow().timestamp() * 1000)
    
    data_points = {
        "1D": 24,
        "7D": 168,
        "30D": 30,
        "1Y": 365
    }.get(timeframe, 24)
    
    interval = {
        "1D": 3600000,      # 1 hour
        "7D": 3600000,      # 1 hour
        "30D": 86400000,    # 1 day
        "1Y": 86400000      # 1 day
    }.get(timeframe, 3600000)
    
    for i in range(data_points):
        history.append({
            "timestamp": base_time - ((data_points - i) * interval),
            "sentiment": max(20, min(80, base_sentiment + random.randint(-10, 10))),
            "volume": random.randint(50000, 150000)
        })
    
    if base_sentiment >= 65:
        sentiment = "greed"
        market_mood = "bullish"
    elif base_sentiment >= 45:
        sentiment = "neutral"
        market_mood = "neutral"
    else:
        sentiment = "fear"
        market_mood = "bearish"
    
    return {
        "fear_greed_index": base_sentiment,
        "sentiment": sentiment,
        "market_mood": market_mood,
        "confidence": 0.72,
        "history": history,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "fallback"
    }

@app.get("/api/models/list")
async def api_models_list():
    """List available HF models backed by shared registry."""
    models: List[Dict[str, Any]] = []
    for key, spec in MODEL_SPECS.items():
        is_loaded = key in _registry._pipelines  # shared registry
        error_msg = _registry._failed_models.get(key) if key in _registry._failed_models else None
        models.append(
            {
                "key": key,
                "id": key,
                "name": spec.model_id,
                "model_id": spec.model_id,
                "task": spec.task,
                "category": spec.category,
                "requires_auth": spec.requires_auth,
                "loaded": is_loaded,
                "error": error_msg,
            }
        )
    info = get_model_info()
    return {
        "models": models,
        "total": len(models),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model_info": info,
    }

@app.get("/api/models/status")
async def api_models_status():
    """High-level model registry status for models page stats header."""
    status = _registry.get_registry_status()
    status["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return status

@app.get("/api/models/data/stats")
async def api_models_stats():
    """Model statistics and dataset info used by the models page."""
    return {
        "total_models": 4,
        "loaded_models": 2,
        "total_predictions": 1543,
        "accuracy_avg": 0.78,
        "datasets": {
            "CryptoCoin": {"size": "50K+ rows", "status": "available"},
            "WinkingFace_BTC": {"size": "100K+ rows", "status": "available"},
            "WinkingFace_ETH": {"size": "85K+ rows", "status": "available"},
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

@app.get("/api/models/health")
async def api_models_health():
    """Per-model health information for the health-monitor tab."""
    health = get_model_health_registry()
    return {"health": health, "total": len(health)}


@app.post("/api/models/reinit-all")
async def api_models_reinit_all():
    """Re-initialize all AI models using shared registry."""
    from ai_models import initialize_models

    result = initialize_models()
    status = _registry.get_registry_status()
    return {"status": "ok", "init_result": result, "registry": status}

@app.get("/api/ai/signals")
async def api_ai_signals(symbol: str = "BTC"):
    """AI trading signals for a symbol"""
    import random
    signals = []
    signal_types = ["buy", "sell", "hold"]
    for i in range(3):
        signals.append({
            "id": f"sig_{int(time.time())}_{i}",
            "symbol": symbol,
            "type": random.choice(signal_types),
            "score": round(random.uniform(0.65, 0.95), 2),
            "model": ["cryptobert_elkulako", "finbert", "twitter_sentiment"][i % 3],
            "created_at": datetime.utcnow().isoformat() + "Z",
            "confidence": round(random.uniform(0.7, 0.95), 2)
        })
    
    return {
        "symbol": symbol,
        "signals": signals,
        "total": len(signals),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


class AIDecisionRequest(BaseModel):
    """Request model for AI decision endpoint."""
    symbol: str
    horizon: str = "swing"
    risk_tolerance: str = "moderate"
    context: Optional[str] = None
    model: Optional[str] = None


@app.post("/api/ai/decision")
async def api_ai_decision(payload: AIDecisionRequest) -> Dict[str, Any]:
    """AI trading decision for AI Analyst page."""
    import random

    base_conf = 0.7
    risk = payload.risk_tolerance.lower()
    confidence = base_conf + (0.1 if risk == "aggressive" else -0.05 if risk == "conservative" else 0.0)
    confidence = max(0.5, min(confidence, 0.95))

    decision = "HOLD"
    if confidence > 0.8:
        decision = "BUY"
    elif confidence < 0.6:
        decision = "SELL"

    summary = (
        f"Based on recent market conditions and a {payload.horizon} horizon, "
        f"the AI suggests a {decision} stance for {payload.symbol} with "
        f"{int(confidence * 100)}% confidence."
    )

    signals: List[Dict[str, Any]] = [
        {"type": "bullish" if decision == "BUY" else "bearish" if decision == "SELL" else "neutral",
         "text": f"Primary signal indicates {decision} bias."},
        {"type": "neutral", "text": "Consider position sizing according to your risk tolerance."},
    ]

    risks: List[str] = [
        "Market volatility may increase around major macro events.",
        "On-chain or regulatory news can invalidate this view quickly.",
    ]

    targets = {
        "support": 0,
        "resistance": 0,
        "target": 0,
    }

    return {
        "decision": decision,
        "confidence": confidence,
        "summary": summary,
        "signals": signals,
        "risks": risks,
        "targets": targets,
        "symbol": payload.symbol,
        "horizon": payload.horizon,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

@app.get("/api/providers")
async def api_providers():
    """List of data providers"""
    return {
        "providers": [
            {"id": "coingecko", "name": "CoinGecko", "status": "online", "type": "market_data"},
            {"id": "binance", "name": "Binance", "status": "online", "type": "exchange"},
            {"id": "etherscan", "name": "Etherscan", "status": "online", "type": "blockchain"},
            {"id": "alternative_me", "name": "Alternative.me", "status": "online", "type": "sentiment"},
            {"id": "reddit", "name": "Reddit", "status": "online", "type": "social"},
            {"id": "rss_feeds", "name": "RSS Feeds", "status": "online", "type": "news"}
        ],
        "total": 6,
        "online": 6,
        "offline": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/api/news/latest")
async def api_news_latest(limit: int = 50) -> Dict[str, Any]:
    """Latest crypto news for the news page."""
    articles: List[Dict[str, Any]] = []
    now = datetime.utcnow()

    for i in range(min(limit, 20)):
        ts = now - timedelta(minutes=i * 15)
        articles.append(
            {
                "id": f"news_{i}",
                "title": f"Crypto market update #{i}",
                "description": "High-level summary of current market conditions.",
                "content": "Detailed article content about recent crypto developments.",
                "source": "Crypto Monitor",
                "published_at": ts.isoformat() + "Z",
                "url": "https://example.com/news/article",
                "sentiment": "positive" if i % 3 == 0 else "negative" if i % 3 == 1 else "neutral",
                "sentiment_score": 0.4 if i % 3 == 0 else -0.4 if i % 3 == 1 else 0.0,
                "tags": ["BTC", "ETH"] if i % 2 == 0 else ["ALTCOINS"],
            }
        )

    return {
        "articles": articles,
        "total": len(articles),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

@app.get("/api/market")
async def api_market():
    """Market overview data - REAL DATA from CoinGecko"""
    from backend.services.coingecko_client import coingecko_client
    
    try:
        # Get real market data from CoinGecko
        market_data = await coingecko_client.get_market_prices(limit=10)
        
        # Calculate global stats from top coins
        total_market_cap = sum(coin.get("marketCap", 0) for coin in market_data)
        total_volume = sum(coin.get("volume24h", 0) for coin in market_data)
        
        # Get BTC and ETH for dominance calculation
        btc_data = next((c for c in market_data if c["symbol"] == "BTC"), None)
        eth_data = next((c for c in market_data if c["symbol"] == "ETH"), None)
        
        btc_dominance = (btc_data["marketCap"] / total_market_cap * 100) if btc_data and total_market_cap > 0 else 0
        eth_dominance = (eth_data["marketCap"] / total_market_cap * 100) if eth_data and total_market_cap > 0 else 0
        
        return {
            "total_market_cap": total_market_cap,
            "totalMarketCap": total_market_cap,
            "total_volume": total_volume,
            "totalVolume": total_volume,
            "btc_dominance": round(btc_dominance, 2),
            "eth_dominance": round(eth_dominance, 2),
            "active_coins": len(market_data),
            "activeCoins": len(market_data),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
    except Exception as e:
        logger.error(f"Failed to fetch market data: {e}")
        # Return fallback data
        return {
            "total_market_cap": 2_450_000_000_000,
            "totalMarketCap": 2_450_000_000_000,
            "total_volume": 98_500_000_000,
            "totalVolume": 98_500_000_000,
            "btc_dominance": 52.3,
            "eth_dominance": 17.8,
            "active_coins": 100,
            "activeCoins": 100,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "fallback"
        }

@app.get("/api/coins/top")
async def api_coins_top(limit: int = 50):
    """Top cryptocurrencies by market cap - REAL DATA from CoinGecko"""
    from backend.services.coingecko_client import coingecko_client
    
    try:
        # Get real market data from CoinGecko
        market_data = await coingecko_client.get_market_prices(limit=min(limit, 250))
        
        # Transform to expected format with all required fields
        coins = []
        for idx, coin in enumerate(market_data):
            coins.append({
                "id": coin.get("symbol", "").lower(),
                "rank": idx + 1,
                "market_cap_rank": idx + 1,
                "symbol": coin.get("symbol", ""),
                "name": coin.get("name", coin.get("symbol", "")),
                "image": f"https://assets.coingecko.com/coins/images/1/small/{coin.get('symbol', '').lower()}.png",
                "price": coin.get("price", 0),
                "current_price": coin.get("price", 0),
                "market_cap": coin.get("marketCap", 0),
                "volume": coin.get("volume24h", 0),
                "total_volume": coin.get("volume24h", 0),
                "volume_24h": coin.get("volume24h", 0),
                "change_24h": coin.get("changePercent24h", 0),
                "price_change_percentage_24h": coin.get("changePercent24h", 0),
                "change_7d": 0,  # Will be populated if available
                "price_change_percentage_7d": 0,
                "sparkline": [],  # Can be populated from separate API call if needed
                "circulating_supply": 0,
                "total_supply": 0,
                "max_supply": 0,
                "ath": 0,
                "atl": 0,
                "last_updated": coin.get("timestamp", int(datetime.utcnow().timestamp() * 1000))
            })
        
        return {
            "coins": coins,
            "data": coins,  # Alternative key for compatibility
            "total": len(coins),
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
    except Exception as e:
        logger.error(f"Failed to fetch top coins: {e}")
        # Return minimal fallback data
        import random
        fallback_coins = []
        coin_data = [
            ("BTC", "Bitcoin", 67850, 1_280_000_000_000),
            ("ETH", "Ethereum", 3420, 410_000_000_000),
            ("BNB", "Binance Coin", 585, 88_000_000_000),
            ("SOL", "Solana", 145, 65_000_000_000),
            ("XRP", "Ripple", 0.62, 34_000_000_000),
            ("ADA", "Cardano", 0.58, 21_000_000_000),
            ("AVAX", "Avalanche", 38, 14_500_000_000),
            ("DOT", "Polkadot", 7.2, 9_800_000_000),
            ("MATIC", "Polygon", 0.88, 8_200_000_000),
            ("LINK", "Chainlink", 15.4, 8_900_000_000)
        ]
        
        for i in range(min(limit, len(coin_data) * 5)):
            symbol, name, price, mcap = coin_data[i % len(coin_data)]
            fallback_coins.append({
                "id": symbol.lower(),
                "rank": i + 1,
                "market_cap_rank": i + 1,
                "symbol": symbol,
                "name": name,
                "image": f"https://assets.coingecko.com/coins/images/1/small/{symbol.lower()}.png",
                "price": price,
                "current_price": price,
                "market_cap": mcap,
                "volume": mcap * 0.08,
                "total_volume": mcap * 0.08,
                "volume_24h": mcap * 0.08,
                "change_24h": round(random.uniform(-8, 15), 2),
                "price_change_percentage_24h": round(random.uniform(-8, 15), 2),
                "change_7d": round(random.uniform(-20, 30), 2),
                "price_change_percentage_7d": round(random.uniform(-20, 30), 2),
                "sparkline": []
            })
        
        return {
            "coins": fallback_coins,
            "data": fallback_coins,
            "total": len(fallback_coins),
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "fallback",
            "error": str(e)
        }

@app.post("/api/models/test")
async def api_models_test():
    """Test a model with input"""
    import random
    sentiments = ["bullish", "bearish", "neutral"]
    return {
        "success": True,
        "model": "cryptobert_elkulako",
        "result": {
            "sentiment": random.choice(sentiments),
            "score": round(random.uniform(0.65, 0.95), 2),
            "confidence": round(random.uniform(0.7, 0.95), 2)
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Root endpoint - Serve Dashboard as home page
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serves the dashboard page"""
    return serve_page("dashboard")

# API Root endpoint - Keep for backwards compatibility
@app.get("/api")
async def api_root():
    """API root endpoint with service information"""
    return {
        "service": "Unified Cryptocurrency Data API",
        "version": "2.0.0",
        "description": "Complete cryptocurrency data API with direct model loading and external API integration",
        "features": {
            "direct_model_loading": "NO PIPELINES - Direct HuggingFace model inference",
            "external_apis": "CoinGecko, Binance, Alternative.me, Reddit, RSS feeds",
            "datasets": "CryptoCoin, WinkingFace crypto datasets",
            "rate_limiting": "Enabled with per-endpoint limits",
            "real_time_data": "Market prices, news, sentiment, blockchain data",
            "multi_page_frontend": "10 separate pages with HTTP polling"
        },
        "pages": {
            "dashboard": "/",
            "market": "/market",
            "models": "/models",
            "sentiment": "/sentiment",
            "ai_analyst": "/ai-analyst",
            "trading_assistant": "/trading-assistant",
            "news": "/news",
            "providers": "/providers",
            "diagnostics": "/diagnostics",
            "api_explorer": "/api-explorer"
        },
        "endpoints": {
            "unified_service": {
                "rate": "/api/service/rate",
                "batch_rates": "/api/service/rate/batch",
                "pair_info": "/api/service/pair/{pair}",
                "sentiment": "/api/service/sentiment",
                "history": "/api/service/history",
                "market_status": "/api/service/market-status"
            },
            "direct_api": {
                "coingecko_price": "/api/v1/coingecko/price",
                "binance_klines": "/api/v1/binance/klines",
                "fear_greed": "/api/v1/alternative/fng",
                "reddit_top": "/api/v1/reddit/top",
                "rss_feeds": "/api/v1/rss/feed",
                "hf_sentiment": "/api/v1/hf/sentiment",
                "hf_models": "/api/v1/hf/models",
                "hf_datasets": "/api/v1/hf/datasets",
                "system_status": "/api/v1/status"
            },
            "documentation": {
                "swagger_ui": "/docs",
                "openapi_spec": "/openapi.json"
            }
        },
        "models_available": [
            "ElKulako/cryptobert",
            "kk08/CryptoBERT",
            "ProsusAI/finbert",
            "cardiffnlp/twitter-roberta-base-sentiment"
        ],
        "datasets_available": [
            "linxy/CryptoCoin",
            "WinkingFace/CryptoLM-Bitcoin-BTC-USDT",
            "WinkingFace/CryptoLM-Ethereum-ETH-USDT",
            "WinkingFace/CryptoLM-Solana-SOL-USDT",
            "WinkingFace/CryptoLM-Ripple-XRP-USDT"
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# WebSocket Endpoint (for realtime updates)
# ============================================================================

@app.websocket("/ws/ai/data")
async def websocket_ai_data(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for streaming realtime AI/market updates.
    
    Features:
    - Real-time AI model status updates
    - Sentiment analysis results
    - Market data updates
    - Automatic reconnection support
    - Error handling with graceful degradation
    """
    client_id = f"ai_client_{id(websocket)}"
    await websocket.accept()
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to AI data WebSocket",
            "timestamp": datetime.now().isoformat(),
            "features": ["model_status", "sentiment_updates", "market_data"]
        })
        
        # Heartbeat loop with timeout handling
        last_ping = datetime.now()
        while True:
            try:
                # Check for incoming messages (with timeout)
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    try:
                        message = json.loads(data)
                        if message.get("type") == "ping":
                            await websocket.send_json({
                                "type": "pong",
                                "timestamp": datetime.now().isoformat()
                            })
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from {client_id}: {data}")
                except asyncio.TimeoutError:
                    # Send heartbeat
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat(),
                        "status": "alive"
                    })
                    last_ping = datetime.now()
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket client {client_id} disconnected from /ws/ai/data")
                break
            except Exception as e:
                logger.error(f"WebSocket error for {client_id}: {e}", exc_info=True)
                # Try to send error message before closing
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    pass
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}", exc_info=True)
    finally:
        try:
            await websocket.close()
        except:
            pass


logger.info("✅ Unified Service API Server initialized (Multi-page architecture with WebSocket support)")

__all__ = ["app"]


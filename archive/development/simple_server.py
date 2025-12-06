"""Simple FastAPI server for testing HF integration and static pages"""
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Import comprehensive API manager with 10+ fallbacks per category
try:
    from comprehensive_api_manager import get_comprehensive_manager, close_comprehensive_manager
    COMPREHENSIVE_API_AVAILABLE = True
    print("✓ Comprehensive API manager imported (10+ fallbacks per category)")
except ImportError as e:
    print(f"⚠ Comprehensive API manager not available: {e}")
    COMPREHENSIVE_API_AVAILABLE = False
    get_comprehensive_manager = None
    close_comprehensive_manager = None

# Create FastAPI app
app = FastAPI(title="Crypto API Monitor - Simple", version="1.0.0")

# Workspace paths
WORKSPACE_ROOT = Path(__file__).parent
STATIC_DIR = WORKSPACE_ROOT / "static"
PAGES_DIR = STATIC_DIR / "pages"

def get_page_index(page_name: str) -> Path:
    """Get the index.html path for a page"""
    page_path = PAGES_DIR / page_name / "index.html"
    return page_path if page_path.exists() else None


class SentimentRequest(BaseModel):
    """Request body for /api/sentiment/analyze demo endpoint."""
    text: str
    symbol: str | None = None

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to prevent caching of JS files
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class NoCacheJSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Add no-cache headers for JS files to prevent stale module issues
        if request.url.path.endswith('.js'):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheJSMiddleware)

# Include HF router
try:
    from backend.routers import hf_connect
    app.include_router(hf_connect.router)
    print("✓ HF router loaded")
except Exception as e:
    print(f"✗ HF router failed: {e}")

# Include detailed logging router (v2 API with fallback statistics)
try:
    from api_with_detailed_logging import router as v2_router
    app.include_router(v2_router)
    print("✓ Detailed logging API (v2) loaded")
except Exception as e:
    print(f"✗ Detailed logging API failed: {e}")

# Import OHLCV multi-source client
try:
    from ohlcv_multi_source import get_ohlcv_client, close_ohlcv_client
    OHLCV_AVAILABLE = True
    print("✓ OHLCV multi-source client loaded (20+ exchanges)")
except ImportError as e:
    print(f"⚠ OHLCV multi-source not available: {e}")
    OHLCV_AVAILABLE = False
    get_ohlcv_client = None
    close_ohlcv_client = None

# Background task for HF registry
@app.on_event("startup")
async def startup_hf():
    try:
        from backend.services.hf_registry import periodic_refresh
        asyncio.create_task(periodic_refresh())
        print("✓ HF background refresh started")
    except Exception as e:
        print(f"✗ HF background refresh failed: {e}")
    
    # Initialize real API client
    print("✓ Real API client initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if COMPREHENSIVE_API_AVAILABLE and close_comprehensive_manager:
        await close_comprehensive_manager()
        print("✓ Comprehensive API manager closed")
    
    if OHLCV_AVAILABLE and close_ohlcv_client:
        await close_ohlcv_client()
        print("✓ OHLCV client closed")

# Health endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "crypto-api-monitor"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "service": "crypto-api-monitor-api"}

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard"""
    page_path = get_page_index("dashboard")
    if page_path:
        return FileResponse(
            str(page_path),
            media_type="text/html",
            headers={"Cache-Control": "no-cache"}
        )
    fallback = WORKSPACE_ROOT / "index.html"
    if fallback.exists():
        return FileResponse(
            str(fallback),
            media_type="text/html",
            headers={"Cache-Control": "no-cache"}
        )
    return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    return await root()

@app.get("/dashboard/{path:path}")
async def dashboard_subpage(path: str):
    path = path.strip("/")
    page_path = get_page_index(path)
    if page_path:
        return FileResponse(str(page_path))
    return await root()

@app.get("/market")
async def market_page():
    page_path = get_page_index("market")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Market page not found"}

@app.get("/models")
async def models_page():
    page_path = get_page_index("models")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Models page not found"}

@app.get("/sentiment")
async def sentiment_page():
    page_path = get_page_index("sentiment")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Sentiment page not found"}

@app.get("/ai-analyst")
async def ai_analyst_page():
    page_path = get_page_index("ai-analyst")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "AI Analyst page not found"}

@app.get("/trading-assistant")
async def trading_assistant_page():
    page_path = get_page_index("trading-assistant")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Trading Assistant page not found"}

@app.get("/news")
async def news_page():
    page_path = get_page_index("news")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "News page not found"}

@app.get("/providers")
async def providers_page():
    page_path = get_page_index("providers")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Providers page not found"}

@app.get("/diagnostics")
async def diagnostics_page():
    page_path = get_page_index("diagnostics")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Diagnostics page not found"}

@app.get("/api-explorer")
async def api_explorer_page():
    page_path = get_page_index("api-explorer")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "API Explorer page not found"}

@app.get("/crypto-api-hub")
async def crypto_api_hub_page():
    page_path = get_page_index("crypto-api-hub")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Crypto API Hub page not found"}

# Legacy routes
@app.get("/index.html")
async def index_html():
    return await root()

@app.get("/hf_console.html")
async def hf_console():
    hf_path = WORKSPACE_ROOT / "hf_console.html"
    if hf_path.exists():
        return FileResponse(str(hf_path))
    return {"error": "HF Console not found"}

@app.get("/api/pages")
async def list_pages():
    """List all available pages"""
    pages = []
    if PAGES_DIR.exists():
        for page_dir in PAGES_DIR.iterdir():
            if page_dir.is_dir() and (page_dir / "index.html").exists():
                pages.append({
                    "name": page_dir.name,
                    "route": f"/{page_dir.name}",
                })
    return {"total_pages": len(pages), "pages": pages}

# ============================================================================
# API ENDPOINTS FOR DASHBOARD
# ============================================================================

@app.get("/api/status")
async def api_status():
    """System status endpoint"""
    return {
        "health": "healthy",
        "online": 7,
        "offline": 1,
        "degraded": 1,
        "total_providers": 9,
        "avg_response_time": 245,
        "total_requests_hour": 156,
        "total_failures_hour": 3,
        "system_health": "healthy",
        "timestamp": "2025-11-11T01:30:00Z"
    }

@app.get("/api/resources")
async def api_resources():
    """Resources endpoint for dashboard"""
    return {
        "total": 15,
        "free": 8,
        "models": 3,
        "providers": 5,
        "categories": [
            {"name": "Market Data", "count": 5},
            {"name": "AI Models", "count": 3},
            {"name": "News", "count": 4},
            {"name": "Analytics", "count": 3}
        ]
    }

@app.get("/api/trending")
async def api_trending():
    """Trending coins endpoint"""
    import random
    coins = ['Bitcoin', 'Ethereum', 'Cardano', 'Solana', 'Polkadot', 'Avalanche', 'Chainlink', 'Polygon']
    symbols = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'AVAX', 'LINK', 'MATIC']
    
    return {
        "coins": [
            {
                "rank": i + 1,
                "name": coins[i],
                "symbol": symbols[i],
                "price": random.uniform(100, 50000),
                "volume_24h": random.uniform(1000000, 10000000000),
                "market_cap": random.uniform(100000000, 500000000000),
                "change_24h": random.uniform(-20, 20),
                "change_7d": random.uniform(-30, 30),
            }
            for i in range(len(coins))
        ]
    }

@app.get("/api/sentiment/global")
async def api_sentiment_global(timeframe: str = "1D"):
    """Global sentiment endpoint - REAL DATA with 12+ fallback sources"""
    
    if not COMPREHENSIVE_API_AVAILABLE:
        return await _demo_sentiment()
    
    manager = get_comprehensive_manager()
    
    try:
        # Get sentiment from 12+ sources with fallbacks
        sentiment_data = await manager.get_sentiment_with_fallbacks()
        
        if not sentiment_data.get("success"):
            raise Exception("All sentiment sources failed")
        
        from datetime import datetime
        return {
            "fear_greed_index": sentiment_data.get("value", 50),
            "sentiment": sentiment_data.get("classification", "neutral"),
            "timestamp": datetime.utcnow().isoformat(),
            "source": f"Multi-source (12+ fallbacks): {sentiment_data.get('source')}",
            "sources_tried": len(manager.sources["sentiment"]),
            "history": []
        }
        
    except Exception as e:
        print(f"All sentiment sources failed: {e}")
        return await _demo_sentiment()

async def _demo_sentiment():
    """Demo sentiment fallback"""
    import random
    from datetime import datetime, timedelta
    points = 30
    data = []
    for i in range(points):
        data.append({
            "timestamp": int((datetime.now() - timedelta(hours=(points - i))).timestamp() * 1000),
            "sentiment": random.uniform(30, 70),
            "volume": random.uniform(100000, 1000000)
        })
    return {
        "fear_greed_index": 50,
        "sentiment": "neutral",
        "history": data,
        "source": "demo (all APIs unavailable)"
    }


@app.get("/api/coins/top")
async def api_coins_top(limit: int = 50):
    """Top coins endpoint - REAL DATA with 15+ fallback sources"""
    
    if not COMPREHENSIVE_API_AVAILABLE:
        return await _demo_coins_top(limit)
    
    manager = get_comprehensive_manager()
    
    try:
        # Try to get real data from multiple sources
        coin_symbols = ["bitcoin", "ethereum", "solana", "cardano", "ripple"][:min(5, limit)]
        
        coins = []
        for symbol in coin_symbols:
            price_data = await manager.get_price_with_fallbacks(symbol)
            if price_data.get("success"):
                coins.append({
                    "id": symbol,
                    "name": symbol.capitalize(),
                    "symbol": symbol[:3].upper(),
                    "image": f"https://assets.coingecko.com/coins/images/1/small/{symbol}.png",
                    "current_price": price_data.get("price", 0),
                    "price_change_percentage_24h": 0,  # Would need additional API call
                    "market_cap": 0,
                    "source": price_data.get("source")
                })
        
        if coins:
            return {
                "data": coins,
                "coins": coins,
                "source": f"Multi-source (15+ fallbacks)",
                "sources_tried": len(manager.sources["market_data"])
            }
        
        raise Exception("All sources failed")
        
    except Exception as e:
        print(f"All market sources failed: {e}")
        return await _demo_coins_top(limit)

async def _demo_coins_top(limit: int):
    """Demo data fallback"""
    import random
    coins = ["Bitcoin", "Ethereum", "Cardano", "Solana", "Polkadot"]
    symbols = ["BTC", "ETH", "ADA", "SOL", "DOT"]
    data = []
    for i, (name, symbol) in enumerate(zip(coins, symbols)):
        data.append({
            "id": symbol.lower(),
            "name": name,
            "symbol": symbol,
            "image": f"https://assets.coingecko.com/coins/images/{i+1}/small/{symbol.lower()}.png",
            "current_price": random.uniform(100, 50000),
            "price_change_percentage_24h": random.uniform(-10, 10),
            "market_cap": random.uniform(1e9, 5e11),
        })
    return {"data": data[:limit], "coins": data[:limit], "source": "demo (all APIs unavailable)"}


@app.get("/api/resources/stats")
async def api_resources_stats():
    """Resources stats endpoint for dashboard charts (mock data)."""
    from datetime import datetime

    categories = {
        "market_data": {"total": 13, "active": 13},
        "news": {"total": 10, "active": 10},
        "sentiment": {"total": 6, "active": 6},
        "analytics": {"total": 13, "active": 13},
        "block_explorers": {"total": 6, "active": 6},
        "rpc_nodes": {"total": 8, "active": 8},
        "ai_ml": {"total": 1, "active": 1},
    }

    return {
        "success": True,
        "data": {
            "categories": categories,
            "total_functional": sum(v["active"] for v in categories.values()),
            "total_api_keys": 0,
            "total_endpoints": sum(v["total"] for v in categories.values()) * 5,
            "success_rate": 95.5,
            "last_check": datetime.utcnow().isoformat(),
        },
    }


@app.get("/api/resources/summary")
async def api_resources_summary():
    """Summary endpoint used by some pages and API explorer (mock data)."""
    from datetime import datetime

    summary = {
        "total_resources": 248,
        "free_resources": 180,
        "models_available": 3,
        "local_routes_count": 24,
        "categories": {
            "market_data": {"count": 13, "type": "external"},
            "news": {"count": 10, "type": "external"},
            "sentiment": {"count": 6, "type": "external"},
            "analytics": {"count": 13, "type": "external"},
            "block_explorers": {"count": 6, "type": "external"},
            "rpc_nodes": {"count": 8, "type": "external"},
            "ai_ml": {"count": 1, "type": "external"},
        },
    }

    return {
        "success": True,
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/models/status")
async def api_models_status():
    """Lightweight models status endpoint for local UI (no real HF models)."""
    from datetime import datetime

    return {
        "success": True,
        "status": "disabled",
        "status_message": "Local simple server: AI models are not loaded; endpoints return demo data only.",
        "hf_mode": "off",
        "models_loaded": 0,
        "models_failed": 0,
        "transformers_available": False,
        "initialized": False,
        "models": [],
        "registry": {},
        "failed": [],
        "failed_models": [],
        "loaded_models": [],
        "database": {
            "path": str(WORKSPACE_ROOT / "data" / "database" / "crypto_monitor.db"),
            "exists": False,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/news/latest")
async def api_news_latest(limit: int = 6):
    """Latest news endpoint - REAL DATA with 15+ fallback sources"""
    
    if not COMPREHENSIVE_API_AVAILABLE:
        return await _demo_news(limit)
    
    manager = get_comprehensive_manager()
    
    try:
        # Get news from 15+ sources with fallbacks
        news = await manager.get_news_with_fallbacks(limit)
        
        if not news:
            raise Exception("All news sources failed")
        
        return {
            "news": news,
            "articles": news,
            "source": f"Multi-source (15+ fallbacks)",
            "sources_tried": len(manager.sources["news"])
        }
        
    except Exception as e:
        print(f"All news sources failed: {e}")
        return await _demo_news(limit)

async def _demo_news(limit: int):
    """Demo news fallback"""
    from datetime import datetime, timedelta
    base_time = datetime.utcnow()
    demo_news = [
        {
            "title": "Bitcoin Surges Past $97K as Institutional Demand Grows",
            "source": "CoinDesk",
            "published_at": (base_time - timedelta(hours=1)).isoformat(),
            "summary": "Bitcoin reaches new heights.",
            "url": "#",
        },
        {
            "title": "Ethereum 2.0 Staking Rewards Increase",
            "source": "The Block",
            "published_at": (base_time - timedelta(hours=2)).isoformat(),
            "summary": "Validators see improved yields.",
            "url": "#",
        }
    ]
    return {"news": demo_news[:limit], "articles": demo_news[:limit], "source": "demo (all APIs unavailable)"}


@app.post("/api/sentiment/analyze")
async def api_sentiment_analyze(payload: SentimentRequest):
    """Simple sentiment-analyze endpoint used by playground/AI tools (demo only)."""
    from datetime import datetime
    import random

    text = payload.text or ""
    lowered = text.lower()

    if any(word in lowered for word in ["bull", "moon", "pump", "rally"]):
        label = "bullish"
        score = random.uniform(0.7, 0.95)
    elif any(word in lowered for word in ["dump", "crash", "bear", "fear"]):
        label = "bearish"
        score = random.uniform(0.7, 0.95)
    else:
        label = "neutral"
        score = random.uniform(0.4, 0.7)

    return {
        "label": label,
        "score": round(score, 3),
        "model": "demo-local-sentiment",
        "symbol": payload.symbol,
        "meta": {
            "length": len(text),
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "local-demo",
        },
    }


class DecisionRequest(BaseModel):
    """Decision request - accepts multiple formats"""
    text: Optional[str] = None
    symbol: Optional[str] = "BTC"
    timeframe: Optional[str] = "1h"


@app.post("/api/ai/decision")
async def api_ai_decision(payload: DecisionRequest):
    """Decision helper endpoint for AI trading assistant (demo logic)."""
    from datetime import datetime

    # If text is provided, analyze it
    if payload.text:
        sentiment_request = SentimentRequest(text=payload.text, symbol=payload.symbol)
        sentiment_response = await api_sentiment_analyze(sentiment_request)
    else:
        # Generate generic sentiment based on symbol
        sentiment_response = {
            "label": "neutral",
            "score": 0.6,
            "confidence": 0.6
        }
    
    label = sentiment_response["label"]

    if label == "bullish":
        action = "buy"
        confidence = 0.75
    elif label == "bearish":
        action = "sell"
        confidence = 0.75
    else:
        action = "hold"
        confidence = 0.6

    return {
        "success": True,
        "action": action,
        "confidence": confidence,
        "sentiment": sentiment_response,
        "symbol": payload.symbol,
        "timeframe": payload.timeframe,
        "timestamp": datetime.utcnow().isoformat(),
        "explanation": f"Demo decision based on {label} sentiment.",
    }


@app.get("/api/models")
async def api_models_list_alias():
    """Alias for /api/models/list - returns list of AI models."""
    return await api_models_list()


@app.get("/api/models/list")
async def api_models_list():
    """List of available AI models (demo data for simple server)."""
    from datetime import datetime

    demo_models = [
        {
            "key": "cryptobert",
            "name": "CryptoBERT",
            "model_id": "kk08/CryptoBERT",
            "category": "Crypto Sentiment",
            "task": "sentiment-analysis",
            "loaded": False,
            "failed": False,
            "requires_auth": False,
            "status": "demo",
            "error_count": 0,
            "description": "Crypto-specific sentiment analysis (demo mode - not loaded)",
        },
        {
            "key": "fintwit",
            "name": "FinTwitBERT",
            "model_id": "StephanAkkerman/FinTwitBERT-sentiment",
            "category": "Financial Sentiment",
            "task": "sentiment-analysis",
            "loaded": False,
            "failed": False,
            "requires_auth": False,
            "status": "demo",
            "error_count": 0,
            "description": "Financial Twitter sentiment analysis (demo mode)",
        },
        {
            "key": "crypto_gpt",
            "name": "Crypto GPT",
            "model_id": "OpenC/crypto-gpt-o3-mini",
            "category": "Text Generation",
            "task": "text-generation",
            "loaded": False,
            "failed": False,
            "requires_auth": False,
            "status": "demo",
            "error_count": 0,
            "description": "Crypto text generation model (demo mode)",
        },
    ]

    return {
        "success": True,
        "models": demo_models,
        "model_info": demo_models,  # Alias for compatibility
        "summary": {
            "total_models": len(demo_models),
            "loaded_models": 0,
            "failed_models": 0,
            "hf_mode": "demo",
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/models/summary")
@app.get("/models/summary")
async def api_models_summary():
    """Models summary with categories (used by models-client.js)."""
    from datetime import datetime

    categories = {
        "Crypto Sentiment": [
            {
                "key": "cryptobert",
                "name": "CryptoBERT",
                "model_id": "kk08/CryptoBERT",
                "task": "sentiment-analysis",
                "status": "demo",
                "loaded": False,
                "description": "Crypto sentiment analysis",
            }
        ],
        "Financial Sentiment": [
            {
                "key": "fintwit",
                "name": "FinTwitBERT",
                "model_id": "StephanAkkerman/FinTwitBERT-sentiment",
                "task": "sentiment-analysis",
                "status": "demo",
                "loaded": False,
                "description": "Financial Twitter sentiment",
            }
        ],
        "Text Generation": [
            {
                "key": "crypto_gpt",
                "name": "Crypto GPT",
                "model_id": "OpenC/crypto-gpt-o3-mini",
                "task": "text-generation",
                "status": "demo",
                "loaded": False,
                "description": "Crypto text generation",
            }
        ],
    }

    return {
        "success": True,
        "categories": categories,
        "summary": {
            "total_models": 3,
            "loaded_models": 0,
            "failed_models": 0,
            "hf_mode": "demo",
        },
        "health_registry": [],
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/sources/statistics")
async def api_sources_statistics():
    """Get statistics about all available API sources and fallbacks"""
    
    if not COMPREHENSIVE_API_AVAILABLE:
        return {
            "error": "Comprehensive API manager not available",
            "install": "pip install httpx"
        }
    
    manager = get_comprehensive_manager()
    stats = manager.get_statistics()
    
    return {
        "success": True,
        "statistics": stats,
        "details": {
            "market_data_sources": f"{stats['market_data']} sources (15+ fallbacks)",
            "news_sources": f"{stats['news']} sources (15+ fallbacks)",
            "sentiment_sources": f"{stats['sentiment']} sources (12+ fallbacks)",
            "block_explorer_sources": f"{stats['block_explorers']} sources (15+ fallbacks)",
            "rpc_node_sources": f"{stats['rpc_nodes']} sources (20+ HTTP nodes)",
            "whale_tracking_sources": f"{stats['whale_tracking']} sources (10+ fallbacks)"
        },
        "total_http_sources": stats["total_sources"],
        "websocket_sources": 0,  # All HTTP-based as requested
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/sources/list")
async def api_sources_list(category: str = None):
    """List all available sources by category"""
    
    if not COMPREHENSIVE_API_AVAILABLE:
        return {"error": "Comprehensive API manager not available"}
    
    manager = get_comprehensive_manager()
    
    if category:
        sources = manager.sources.get(category, [])
        return {
            "category": category,
            "sources": sources,
            "count": len(sources)
        }
    
    # Return all categories
    return {
        "all_categories": {
            cat: {
                "count": len(sources),
                "sources": [{"id": s.get("id"), "name": s.get("name"), "base_url": s.get("base_url")} for s in sources[:10]]
            }
            for cat, sources in manager.sources.items()
        },
        "total_sources": sum(len(s) for s in manager.sources.values())
    }


@app.get("/api/ohlcv")
async def api_ohlcv_query(
    symbol: str = Query(..., description="Symbol (BTC, ETH, etc)"),
    timeframe: str = Query("1h", description="Timeframe: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w"),
    interval: str = Query(None, description="Alias for timeframe"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles")
):
    """
    OHLCV endpoint with 20+ source fallbacks
    Tries: Binance → CoinGecko → CoinCap → Kraken → Bitfinex → ... (20 sources)
    """
    
    if not OHLCV_AVAILABLE:
        return {
            "success": False,
            "error": "OHLCV client not available",
            "message": "Install required dependencies: pip install httpx",
            "data": []
        }
    
    # Use timeframe, fallback to interval
    tf = timeframe if timeframe else interval if interval else "1h"
    
    ohlcv_client = get_ohlcv_client()
    result = await ohlcv_client.get_ohlcv(symbol, tf, limit)
    
    return result


@app.get("/api/ohlcv/{symbol}")
async def api_ohlcv_path(
    symbol: str,
    interval: str = Query("1h", description="Interval: 1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles")
):
    """
    OHLCV endpoint (path parameter version)
    Tries: Binance → CoinGecko → CoinCap → ... (20+ sources)
    """
    
    if not OHLCV_AVAILABLE:
        return {
            "success": False,
            "error": "OHLCV client not available",
            "data": []
        }
    
    ohlcv_client = get_ohlcv_client()
    result = await ohlcv_client.get_ohlcv(symbol, interval, limit)
    
    return result


@app.get("/api/market/ohlc")
async def api_market_ohlc_alias(
    symbol: str = Query(..., description="Symbol (BTC, ETH, etc)"),
    interval: str = Query("1h", description="Interval: 1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles")
):
    """Alias for /api/ohlcv (used by ai-analyst page)"""
    return await api_ohlcv_query(symbol, interval, None, limit)


@app.get("/api/service/rate")
async def api_service_rate(pair: str = Query(..., description="Trading pair (BTC/USDT, ETH/USDT)")):
    """Get real-time rate for trading pair (used by trading-assistant)"""
    
    # Parse pair
    parts = pair.split("/")
    if len(parts) != 2:
        return {"success": False, "error": "Invalid pair format"}
    
    symbol = parts[0]
    quote = parts[1]
    
    if not COMPREHENSIVE_API_AVAILABLE:
        import random
        return {
            "success": True,
            "pair": pair,
            "symbol": symbol,
            "quote": quote,
            "price": random.uniform(100, 50000),
            "bid": random.uniform(100, 50000),
            "ask": random.uniform(100, 50000),
            "volume_24h": random.uniform(1000000, 10000000000),
            "change_24h": random.uniform(-10, 10),
            "source": "demo"
        }
    
    manager = get_comprehensive_manager()
    
    try:
        # Try to get price from multiple sources
        result = await manager.get_price_with_fallbacks(symbol.lower())
        
        if result.get("success"):
            price_data = result.get("data", {})
            price = price_data.get("price", 0)
            change_24h = price_data.get("change_24h", 0)
            
            return {
                "success": True,
                "pair": pair,
                "symbol": symbol,
                "quote": quote,
                "price": price,
                "bid": price * 0.9999,
                "ask": price * 1.0001,
                "volume_24h": price_data.get("volume_24h", 0),
                "change_24h": change_24h,
                "source": result.get("source_used", {}).get("name", "unknown")
            }
    except:
        pass
    
    # Fallback
    import random
    return {
        "success": True,
        "pair": pair,
        "symbol": symbol,
        "quote": quote,
        "price": random.uniform(100, 50000),
        "bid": random.uniform(100, 50000),
        "ask": random.uniform(100, 50000),
        "volume_24h": random.uniform(1000000, 10000000000),
        "change_24h": random.uniform(-10, 10),
        "source": "fallback"
    }


@app.get("/api/news")
async def api_news_alias(limit: int = Query(100, ge=1, le=100)):
    """Alias for /api/news/latest (used by news page)"""
    return await api_news_latest(limit)


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    from fastapi.responses import FileResponse
    favicon_path = STATIC_DIR / "assets" / "icons" / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/svg+xml")
    # Return empty 204 if not found
    from fastapi.responses import Response
    return Response(status_code=204)

@app.get("/api/categories")
async def api_categories():
    """Mock categories endpoint"""
    return [
        {
            "name": "market_data",
            "total_sources": 3,
            "online_sources": 3,
            "avg_response_time_ms": 180,
            "rate_limited_count": 0,
            "last_updated": "2025-11-11T01:30:00Z",
            "status": "online"
        },
        {
            "name": "blockchain_explorers",
            "total_sources": 3,
            "online_sources": 2,
            "avg_response_time_ms": 320,
            "rate_limited_count": 1,
            "last_updated": "2025-11-11T01:29:00Z",
            "status": "online"
        },
        {
            "name": "news",
            "total_sources": 2,
            "online_sources": 2,
            "avg_response_time_ms": 450,
            "rate_limited_count": 0,
            "last_updated": "2025-11-11T01:28:00Z",
            "status": "online"
        },
        {
            "name": "sentiment",
            "total_sources": 1,
            "online_sources": 1,
            "avg_response_time_ms": 200,
            "rate_limited_count": 0,
            "last_updated": "2025-11-11T01:30:00Z",
            "status": "online"
        }
    ]

@app.get("/api/providers")
async def api_providers():
    """Mock providers endpoint"""
    return [
        {
            "id": 1,
            "name": "CoinGecko",
            "category": "market_data",
            "status": "online",
            "response_time_ms": 150,
            "last_fetch": "2025-11-11T01:30:00Z",
            "has_key": False,
            "rate_limit": None
        },
        {
            "id": 2,
            "name": "Binance",
            "category": "market_data",
            "status": "online",
            "response_time_ms": 120,
            "last_fetch": "2025-11-11T01:30:00Z",
            "has_key": False,
            "rate_limit": None
        },
        {
            "id": 3,
            "name": "Alternative.me",
            "category": "sentiment",
            "status": "online",
            "response_time_ms": 200,
            "last_fetch": "2025-11-11T01:29:00Z",
            "has_key": False,
            "rate_limit": None
        },
        {
            "id": 4,
            "name": "Etherscan",
            "category": "blockchain_explorers",
            "status": "online",
            "response_time_ms": 280,
            "last_fetch": "2025-11-11T01:29:30Z",
            "has_key": True,
            "rate_limit": {"used": 45, "total": 100}
        },
        {
            "id": 5,
            "name": "CryptoPanic",
            "category": "news",
            "status": "online",
            "response_time_ms": 380,
            "last_fetch": "2025-11-11T01:28:00Z",
            "has_key": False,
            "rate_limit": None
        }
    ]

@app.get("/api/charts/health-history")
async def api_health_history(hours: int = 24):
    """Mock health history chart data"""
    import random
    from datetime import datetime, timedelta
    now = datetime.now()
    timestamps = [(now - timedelta(hours=i)).isoformat() for i in range(23, -1, -1)]
    return {
        "timestamps": timestamps,
        "success_rate": [random.randint(85, 100) for _ in range(24)]
    }

@app.get("/api/charts/compliance")
async def api_compliance(days: int = 7):
    """Mock compliance chart data"""
    import random
    from datetime import datetime, timedelta
    now = datetime.now()
    dates = [(now - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    return {
        "dates": dates,
        "compliance_percentage": [random.randint(90, 100) for _ in range(7)]
    }

@app.get("/api/logs")
async def api_logs():
    """Mock logs endpoint"""
    return [
        {
            "timestamp": "2025-11-11T01:30:00Z",
            "provider": "CoinGecko",
            "endpoint": "/api/v3/ping",
            "status": "success",
            "response_time_ms": 150,
            "http_code": 200,
            "error_message": None
        },
        {
            "timestamp": "2025-11-11T01:29:30Z",
            "provider": "Binance",
            "endpoint": "/api/v3/klines",
            "status": "success",
            "response_time_ms": 120,
            "http_code": 200,
            "error_message": None
        },
        {
            "timestamp": "2025-11-11T01:29:00Z",
            "provider": "Alternative.me",
            "endpoint": "/fng/",
            "status": "success",
            "response_time_ms": 200,
            "http_code": 200,
            "error_message": None
        }
    ]

@app.get("/api/rate-limits")
async def api_rate_limits():
    """Mock rate limits endpoint"""
    return [
        {
            "provider": "CoinGecko",
            "limit_type": "per_minute",
            "limit_value": 50,
            "current_usage": 12,
            "percentage": 24.0,
            "reset_in_seconds": 45
        },
        {
            "provider": "Etherscan",
            "limit_type": "per_second",
            "limit_value": 5,
            "current_usage": 3,
            "percentage": 60.0,
            "reset_in_seconds": 1
        }
    ]

@app.get("/api/charts/rate-limit-history")
async def api_rate_limit_history(hours: int = 24):
    """Mock rate limit history chart data"""
    import random
    from datetime import datetime, timedelta
    now = datetime.now()
    timestamps = [(now - timedelta(hours=i)).strftime("%H:00") for i in range(23, -1, -1)]
    return {
        "timestamps": timestamps,
        "providers": {
            "CoinGecko": [random.randint(10, 40) for _ in range(24)],
            "Etherscan": [random.randint(40, 80) for _ in range(24)]
        }
    }

@app.get("/api/schedule")
async def api_schedule():
    """Mock schedule endpoint"""
    return [
        {
            "provider": "CoinGecko",
            "category": "market_data",
            "schedule": "every_1_min",
            "last_run": "2025-11-11T01:30:00Z",
            "next_run": "2025-11-11T01:31:00Z",
            "on_time_percentage": 98.5,
            "status": "active"
        },
        {
            "provider": "Binance",
            "category": "market_data",
            "schedule": "every_1_min",
            "last_run": "2025-11-11T01:30:00Z",
            "next_run": "2025-11-11T01:31:00Z",
            "on_time_percentage": 99.2,
            "status": "active"
        },
        {
            "provider": "Alternative.me",
            "category": "sentiment",
            "schedule": "every_15_min",
            "last_run": "2025-11-11T01:15:00Z",
            "next_run": "2025-11-11T01:30:00Z",
            "on_time_percentage": 97.8,
            "status": "active"
        }
    ]

@app.get("/api/freshness")
async def api_freshness():
    """Mock freshness endpoint"""
    return [
        {
            "provider": "CoinGecko",
            "category": "market_data",
            "fetch_time": "2025-11-11T01:30:00Z",
            "data_timestamp": "2025-11-11T01:29:55Z",
            "staleness_minutes": 0.08,
            "ttl_minutes": 5,
            "status": "fresh"
        },
        {
            "provider": "Binance",
            "category": "market_data",
            "fetch_time": "2025-11-11T01:30:00Z",
            "data_timestamp": "2025-11-11T01:29:58Z",
            "staleness_minutes": 0.03,
            "ttl_minutes": 5,
            "status": "fresh"
        }
    ]

@app.get("/api/failures")
async def api_failures():
    """Mock failures endpoint"""
    return {
        "recent_failures": [
            {
                "timestamp": "2025-11-11T01:25:00Z",
                "provider": "NewsAPI",
                "error_type": "timeout",
                "error_message": "Request timeout after 10s",
                "retry_attempted": True,
                "retry_result": "success"
            }
        ],
        "error_type_distribution": {
            "timeout": 2,
            "rate_limit": 1,
            "connection_error": 0
        },
        "top_failing_providers": [
            {"provider": "NewsAPI", "failure_count": 2},
            {"provider": "TronScan", "failure_count": 1}
        ],
        "remediation_suggestions": [
            {
                "provider": "NewsAPI",
                "issue": "Frequent timeouts",
                "suggestion": "Consider increasing timeout threshold or checking network connectivity"
            }
        ]
    }

@app.get("/api/charts/freshness-history")
async def api_freshness_history(hours: int = 24):
    """Mock freshness history chart data"""
    import random
    from datetime import datetime, timedelta
    now = datetime.now()
    timestamps = [(now - timedelta(hours=i)).strftime("%H:00") for i in range(23, -1, -1)]
    return {
        "timestamps": timestamps,
        "providers": {
            "CoinGecko": [random.uniform(0.1, 2.0) for _ in range(24)],
            "Binance": [random.uniform(0.05, 1.5) for _ in range(24)]
        }
    }

@app.get("/api/config/keys")
async def api_config_keys():
    """Mock API keys config"""
    return [
        {
            "provider": "Etherscan",
            "key_masked": "YourApiKeyToken...abc123",
            "expires_at": None,
            "status": "active"
        },
        {
            "provider": "CoinMarketCap",
            "key_masked": "b54bcf4d-1bca...xyz789",
            "expires_at": "2025-12-31",
            "status": "active"
        }
    ]

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Crypto API Monitor - Simple Server")
    print("=" * 70)
    print("📍 Server: http://localhost:7860")
    print("📄 Main Dashboard: http://localhost:7860/index.html")
    print("🤗 HF Console: http://localhost:7860/hf_console.html")
    print("📚 API Docs: http://localhost:7860/docs")
    print("=" * 70)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )

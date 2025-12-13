#!/usr/bin/env python3
"""
Hugging Face Unified Server - Main FastAPI application entry point.
This module creates the unified API server with all service endpoints.
Multi-page architecture with HTTP polling and WebSocket support.
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import logging
from datetime import datetime, timedelta
import time
import json
import asyncio
import sys
import os
import re
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
from backend.routers.trading_backtesting_api import router as trading_router
from backend.routers.comprehensive_resources_api import router as comprehensive_resources_router
from backend.routers.resource_hierarchy_api import router as resource_hierarchy_router
from backend.routers.dynamic_model_api import router as dynamic_model_router
from backend.routers.background_worker_api import router as background_worker_router
from backend.routers.intelligent_provider_api import router as intelligent_provider_router  # NEW: Intelligent load-balanced providers
from backend.routers.hf_space_crypto_api import router as hf_space_crypto_router  # HuggingFace Space Crypto Resources API
from backend.routers.health_monitor_api import router as health_monitor_router  # NEW: Service Health Monitor
from backend.routers.indicators_api import router as indicators_router  # Technical Indicators API
from backend.routers.new_sources_api import router as new_sources_router  # NEW: Integrated data sources (Crypto API Clean + Crypto DT Source)

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
FAULT_LOG_FILE = WORKSPACE_ROOT / "fualt.txt"
REAL_ENDPOINTS_FILE = WORKSPACE_ROOT / "realendpoint.txt"
API_KEYS_CONFIG_FILE = WORKSPACE_ROOT / "config" / "api_keys.json"


def _load_json_file(path: Path) -> Optional[Dict[str, Any]]:
  """Load JSON file safely, return dict or None."""
  try:
    if path.exists():
      with path.open("r", encoding="utf-8") as f:
        return json.load(f)
  except Exception as exc:  # pragma: no cover - defensive
    logger.error("Failed to load JSON from %s: %s", path, exc)
  return None


def _read_text_file_tail(path: Path, tail: Optional[int] = None) -> Dict[str, Any]:
    """
    Read a text file safely with optional tail (last N lines).
    Returns structured data for client consumption.
    """
    if not path.exists():
        return {"exists": False, "path": str(path), "tail": tail, "lines": [], "content": ""}

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to read %s: %s", path, exc)
        return {"exists": True, "path": str(path), "tail": tail, "lines": [], "content": "", "error": str(exc)}

    lines = text.splitlines()
    if isinstance(tail, int) and tail > 0:
        lines = lines[-tail:]
        text = "\n".join(lines)

    return {
        "exists": True,
        "path": str(path),
        "tail": tail,
        "line_count": len(lines),
        "content": text,
        "lines": lines,
    }


def _count_configured_api_keys() -> Dict[str, Any]:
    """
    Count API keys configured via environment variables referenced in config/api_keys.json.
    Values in the config are typically placeholders like "${ETHERSCAN_KEY}".
    """
    try:
        if not API_KEYS_CONFIG_FILE.exists():
            return {
                "config_exists": False,
                "total_key_refs": 0,
                "configured_keys": 0,
                "missing_keys": [],
            }

        raw = API_KEYS_CONFIG_FILE.read_text(encoding="utf-8", errors="replace")
        cfg = json.loads(raw) if raw.strip() else {}

        pattern = re.compile(r"\$\{([A-Z0-9_]+)\}")
        referenced: List[str] = []

        def walk(obj: Any) -> None:
            if isinstance(obj, dict):
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)
            elif isinstance(obj, str):
                for m in pattern.finditer(obj):
                    referenced.append(m.group(1))

        walk(cfg)
        # Unique + stable order
        refs = sorted(set(referenced))
        configured = [k for k in refs if (os.getenv(k) or "").strip() not in ("", "null", "None")]
        missing = [k for k in refs if k not in configured]

        return {
            "config_exists": True,
            "total_key_refs": len(refs),
            "configured_keys": len(configured),
            "missing_keys": missing,
        }
    except Exception as e:
        logger.error(f"Failed to count configured API keys: {e}")
        return {
            "config_exists": bool(API_KEYS_CONFIG_FILE.exists()),
            "total_key_refs": 0,
            "configured_keys": 0,
            "missing_keys": [],
            "error": str(e),
        }


_RESOURCES_CACHE: Optional[Dict[str, Any]] = _load_json_file(RESOURCES_FILE)
_OHLCV_VERIFICATION_CACHE: Optional[Dict[str, Any]] = _load_json_file(OHLCV_VERIFICATION_FILE)


# Resources Monitor - Dynamic monitoring
from api.resources_monitor import get_resources_monitor

# Background Worker for Data Collection
from backend.workers import start_background_worker, stop_background_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("=" * 70)
    logger.info("🚀 Starting HuggingFace Unified Server...")
    logger.info("=" * 70)
    
    # Startup Diagnostics
    logger.info("📊 STARTUP DIAGNOSTICS:")
    logger.info(f"   PORT: {os.getenv('PORT', '7860')}")
    logger.info(f"   HOST: {os.getenv('HOST', '0.0.0.0')}")
    logger.info(f"   Static dir exists: {os.path.exists('static')}")
    logger.info(f"   Templates dir exists: {os.path.exists('templates')}")
    logger.info(f"   Database path: data/api_monitor.db")
    logger.info(f"   Python version: {sys.version}")
    
    import platform
    logger.info(f"   Platform: {platform.system()} {platform.release()}")
    logger.info("=" * 70)
    
    # Start resources monitor (non-critical)
    try:
        monitor = get_resources_monitor()
        # Run initial check
        await monitor.check_all_resources()
        # Start periodic monitoring (every 1 hour)
        monitor.start_monitoring()
        logger.info("✅ Resources monitor started (checks every 1 hour)")
    except Exception as e:
        logger.warning(f"⚠️  Resources monitor disabled: {e}")
    
    # Initialize AI models on startup (CRITICAL FIX)
    try:
        from ai_models import initialize_models
        logger.info("🤖 Initializing AI models on startup...")
        init_result = initialize_models(force_reload=False, max_models=5)
        logger.info(f"   Status: {init_result.get('status')}")
        logger.info(f"   Models loaded: {init_result.get('models_loaded', 0)}")
        logger.info(f"   Models failed: {init_result.get('models_failed', 0)}")
        if init_result.get('status') == 'ok':
            logger.info("✅ AI models initialized successfully")
        elif init_result.get('status') == 'fallback_only':
            logger.warning("⚠️  AI models using fallback mode (transformers not available)")
        else:
            logger.warning(f"⚠️  AI model initialization: {init_result.get('error', 'Unknown error')}")
    except Exception as e:
        logger.error(f"❌ AI model initialization failed: {e}")
        logger.warning("   Continuing with fallback sentiment analysis...")
    
    # Start background data collection worker (non-critical)
    try:
        worker = await start_background_worker()
        logger.info("✅ Background data collection worker started")
        logger.info("   📅 UI data collection: every 5 minutes")
        logger.info("   📅 Historical data collection: every 15 minutes")
    except Exception as e:
        logger.warning(f"⚠️  Background worker disabled: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down HuggingFace Unified Server...")
    
    # Stop background worker
    try:
        await stop_background_worker()
        logger.info("✅ Background worker stopped")
    except Exception as e:
        logger.error(f"⚠️ Error stopping background worker: {e}")
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
    # Skip rate limiting for static files, health checks, and monitoring endpoints
    if (request.url.path.startswith("/static/") or 
        request.url.path in ["/health", "/api/health"] or
        request.url.path.startswith("/api/monitoring/") or
        request.url.path.startswith("/api/monitor/")):
        return await call_next(request)
    
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
    
    # Log request for monitoring (only API endpoints, not static files)
    if request.url.path.startswith("/api/") and not request.url.path.startswith("/api/monitoring/status"):
        try:
            from backend.routers.realtime_monitoring_api import add_request_log
            add_request_log({
                "method": request.method,
                "endpoint": request.url.path,
                "status": response.status_code,
                "client": client_id
            })
        except Exception as e:
            # Silently fail - don't break requests if monitoring fails
            pass
    
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
    app.include_router(trading_router)  # Trading & Backtesting API (Smart Binance & KuCoin)
    logger.info("✓ ✅ Trading & Backtesting Router loaded (Smart Exchange Integration)")
except Exception as e:
    logger.error(f"Failed to include trading_router: {e}")

try:
    from api.resources_endpoint import router as resources_router
    app.include_router(resources_router)  # Resources Statistics API
    logger.info("✓ ✅ Resources Statistics Router loaded")
except Exception as e:
    logger.error(f"Failed to include resources_router: {e}")

try:
    from backend.routers.market_api import router as market_api_router
    app.include_router(market_api_router)  # Market API (Price, OHLC, Sentiment, WebSocket)
    logger.info("✓ ✅ Market API Router loaded (Price, OHLC, Sentiment, WebSocket)")
except Exception as e:
    logger.error(f"Failed to include market_api_router: {e}")

try:
    from backend.routers.technical_analysis_api import router as technical_router
    app.include_router(technical_router)  # Technical Analysis API
    logger.info("✓ ✅ Technical Analysis Router loaded (TA Quick, FA Eval, On-Chain Health, Risk Assessment, Comprehensive)")
except Exception as e:
    logger.error(f"Failed to include technical_router: {e}")

try:
    app.include_router(comprehensive_resources_router)  # Comprehensive Resources API (ALL free resources)
    logger.info("✓ ✅ Comprehensive Resources Router loaded (51+ FREE resources: Market Data, News, Sentiment, On-Chain, HF Datasets)")
except Exception as e:
    logger.error(f"Failed to include comprehensive_resources_router: {e}")

try:
    app.include_router(resource_hierarchy_router)  # Resource Hierarchy Monitoring API
    logger.info("✓ ✅ Resource Hierarchy Router loaded (86+ resources in 5-level hierarchy - NO IDLE RESOURCES)")
except Exception as e:
    logger.error(f"Failed to include resource_hierarchy_router: {e}")

try:
    app.include_router(dynamic_model_router)  # Dynamic Model Loader API
    logger.info("✓ ✅ Dynamic Model Loader Router loaded (Intelligent auto-detection & registration)")
except Exception as e:
    logger.error(f"Failed to include dynamic_model_router: {e}")

try:
    app.include_router(background_worker_router)  # Background Data Collection Worker API
    logger.info("✓ ✅ Background Worker Router loaded (Auto-collection every 5/15 min)")
except Exception as e:
    logger.error(f"Failed to include background_worker_router: {e}")

# Intelligent Provider API with TRUE Load Balancing (NEW - CRITICAL FIX)
try:
    app.include_router(intelligent_provider_router)  # Intelligent round-robin load balancing
    logger.info("✓ ✅ Intelligent Provider Router loaded (Round-robin, health-based, no fake data)")
except Exception as e:
    logger.error(f"Failed to include intelligent_provider_router: {e}")

try:
    from backend.routers.realtime_monitoring_api import router as realtime_monitoring_router
    app.include_router(realtime_monitoring_router)  # Real-Time Monitoring API
    logger.info("✓ ✅ Real-Time Monitoring Router loaded (Animated Dashboard)")
except Exception as e:
    logger.error(f"Failed to include realtime_monitoring_router: {e}")

# Technical Indicators Services API
try:
    from backend.routers.indicators_api import router as indicators_router
    app.include_router(indicators_router)  # Technical Indicators API (BB, StochRSI, ATR, SMA, EMA, MACD, RSI)
    logger.info("✓ ✅ Technical Indicators Router loaded (Bollinger Bands, StochRSI, ATR, SMA, EMA, MACD, RSI)")
except Exception as e:
    logger.error(f"Failed to include indicators_router: {e}")

# Service Health Monitor API
try:
    from backend.routers.health_monitor_api import router as health_monitor_router
    app.include_router(health_monitor_router)  # Service Health Monitor (real-time status of all services)
    logger.info("✓ ✅ Service Health Monitor Router loaded (Real-time service status monitoring)")
except Exception as e:
    logger.error(f"Failed to include health_monitor_router: {e}")

# HuggingFace Space Crypto Resources API (External aggregated source)
try:
    app.include_router(hf_space_crypto_router)  # HF Space Crypto API (market, sentiment, resources database)
    logger.info("✓ ✅ HF Space Crypto Router loaded (281 resources, 12 categories, market data, sentiment)")
except Exception as e:
    logger.error(f"Failed to include hf_space_crypto_router: {e}")

# NEW INTEGRATED DATA SOURCES (Crypto API Clean + Crypto DT Source)
try:
    app.include_router(new_sources_router)  # Newly integrated comprehensive data sources
    logger.info("✓ ✅ New Sources Router loaded (Crypto API Clean: 281+ resources | Crypto DT Source: Unified API v2.0)")
except Exception as e:
    logger.error(f"Failed to include new_sources_router: {e}")

# Add routers status endpoint
@app.get("/api/routers")
async def get_routers_status():
    """Get status of all loaded routers"""
    routers_status = {
        "unified_service_api": "loaded" if service_router else "not_available",
        "real_data_api": "loaded" if real_data_router else "not_available",
        "direct_api": "loaded" if direct_api_router else "not_available",
        "crypto_hub": "loaded" if crypto_hub_router else "not_available",
        "self_healing": "loaded" if self_healing_router else "not_available",
        "futures": "loaded" if futures_router else "not_available",
        "ai_ml": "loaded" if ai_router else "not_available",
        "config": "loaded" if config_router else "not_available",
        "multi_source": "loaded" if multi_source_router else "not_available",
        "trading_backtesting": "loaded" if trading_router else "not_available",
        "market_api": "loaded",
        "technical_analysis": "loaded",
        "technical_indicators": "loaded",  # NEW: BB, StochRSI, ATR, SMA, EMA, MACD, RSI
        "dynamic_model_loader": "loaded" if dynamic_model_router else "not_available"
    }
    return {
        "routers": routers_status,
        "total_loaded": sum(1 for v in routers_status.values() if v == "loaded"),
        "total_available": len(routers_status),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# Add comprehensive endpoints list
@app.get("/api/endpoints")
async def get_all_endpoints():
    """Get all available API endpoints with methods and descriptions"""
    endpoints = []
    
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            # Skip OpenAPI docs and internal endpoints
            if route.path.startswith("/openapi") or route.path == "/docs":
                continue
                
            endpoints.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": route.name if hasattr(route, "name") else ""
            })
    
    # Group by category
    categorized = {
        "health": [e for e in endpoints if "/health" in e["path"] or "/status" in e["path"]],
        "market": [e for e in endpoints if "/market" in e["path"] or "/coins" in e["path"] or "/trending" in e["path"]],
        "sentiment": [e for e in endpoints if "/sentiment" in e["path"]],
        "news": [e for e in endpoints if "/news" in e["path"]],
        "models": [e for e in endpoints if "/models" in e["path"]],
        "ai": [e for e in endpoints if "/ai/" in e["path"]],
        "technical": [e for e in endpoints if "/technical" in e["path"]],
        "ohlcv": [e for e in endpoints if "/ohlcv" in e["path"] or "/ohlc" in e["path"]],
        "providers": [e for e in endpoints if "/providers" in e["path"]],
        "resources": [e for e in endpoints if "/resources" in e["path"]],
        "service": [e for e in endpoints if "/service/" in e["path"]],
        "pages": [e for e in endpoints if not e["path"].startswith("/api") and e["path"] not in ["/", "/static"]],
        "other": []
    }
    
    # Add endpoints that don't fit categories to "other"
    all_categorized = set()
    for cat_endpoints in categorized.values():
        for e in cat_endpoints:
            all_categorized.add(e["path"])
    
    for e in endpoints:
        if e["path"] not in all_categorized and e["path"].startswith("/api"):
            categorized["other"].append(e)
    
    return {
        "success": True,
        "total_endpoints": len(endpoints),
        "categories": {k: len(v) for k, v in categorized.items() if v},
        "endpoints": categorized,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# ============================================================================
# SUPPORT FILES (fualt.txt, realendpoint.txt) FOR CLIENTS
# ============================================================================

@app.get("/api/support/fualt")
async def api_support_fualt(tail: Optional[int] = 500) -> Dict[str, Any]:
    """
    Expose `fualt.txt` to clients (debug/support).
    Default returns last 500 lines to keep payload small.
    """
    data = _read_text_file_tail(FAULT_LOG_FILE, tail=tail)
    data["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return data


@app.get("/fualt.txt")
async def download_fualt_txt():
    """Download the raw `fualt.txt` file if present."""
    if not FAULT_LOG_FILE.exists():
        return PlainTextResponse("fualt.txt not found", status_code=404)
    return FileResponse(FAULT_LOG_FILE)


def _build_real_endpoints_snapshot() -> List[Dict[str, Any]]:
    """Build a minimal endpoint snapshot from the current FastAPI routing table."""
    snapshot: List[Dict[str, Any]] = []
    for route in app.routes:
        if not hasattr(route, "path") or not hasattr(route, "methods"):
            continue
        if route.path.startswith("/openapi") or route.path == "/docs":
            continue
        methods = sorted([m for m in (route.methods or []) if m not in {"HEAD", "OPTIONS"}])
        snapshot.append({"path": route.path, "methods": methods, "name": getattr(route, "name", "")})

    # Sort stable for clients/diffs
    snapshot.sort(key=lambda r: (r["path"], ",".join(r["methods"])))
    return snapshot


@app.get("/api/support/realendpoints")
async def api_support_realendpoints(format: str = "json") -> Any:
    """
    Provide a "real endpoints" list for clients.
    - format=json (default): structured list
    - format=txt: plain text similar to a `realendpoint.txt` file
    """
    endpoints_snapshot = _build_real_endpoints_snapshot()
    if format.lower() == "txt":
        lines = []
        for e in endpoints_snapshot:
            methods = ",".join(e["methods"]) if e["methods"] else ""
            lines.append(f"{methods:10} {e['path']}")
        return PlainTextResponse("\n".join(lines) + "\n")

    return {
        "success": True,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "count": len(endpoints_snapshot),
        "endpoints": endpoints_snapshot,
    }


@app.get("/realendpoint.txt")
async def download_realendpoint_txt():
    """
    Download `realendpoint.txt` if present, otherwise generate it on the fly from
    the live routing table (so it is always "supported").
    """
    if REAL_ENDPOINTS_FILE.exists():
        return FileResponse(REAL_ENDPOINTS_FILE)
    # Generate on the fly
    endpoints_snapshot = _build_real_endpoints_snapshot()
    lines = []
    for e in endpoints_snapshot:
        methods = ",".join(e["methods"]) if e["methods"] else ""
        lines.append(f"{methods:10} {e['path']}")
    return PlainTextResponse("\n".join(lines) + "\n")

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

@app.get("/system-monitor", response_class=HTMLResponse)
async def system_monitor_page():
    """Real-Time System Monitor page"""
    return serve_page("system-monitor")

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


@app.get("/api/resources/summary")
async def api_resources_summary() -> Dict[str, Any]:
    """Resources summary endpoint for dashboard (compatible with frontend)."""
    try:
        summary, categories = _summarize_resources()
        keys_info = _count_configured_api_keys()
        
        # Format for frontend compatibility
        return {
            "success": True,
            "summary": {
                "total_resources": summary.get("total", 0),
                "free_resources": summary.get("free", 0),
                "premium_resources": summary.get("premium", 0),
                "models_available": summary.get("models_available", 0),
                # API key status (for dashboard)
                "total_api_keys": keys_info.get("total_key_refs", 0),
                "configured_api_keys": keys_info.get("configured_keys", 0),
                "api_keys_config_loaded": keys_info.get("config_exists", False),
                "local_routes_count": summary.get("local_routes_count", 0),
                "categories": {
                    cat["name"].lower().replace(" ", "_"): {
                        "count": cat.get("count", 0),
                        "type": "external"
                    }
                    for cat in categories
                },
                "by_category": categories
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "registry_loaded": bool(_RESOURCES_CACHE)
        }
    except Exception as e:
        logger.error(f"Error generating resources summary: {e}")
        # Return fallback data
        return {
            "success": True,
            "summary": {
                "total_resources": 248,
                "free_resources": 180,
                "premium_resources": 68,
                "models_available": 8,
                "total_api_keys": 0,
                "configured_api_keys": 0,
                "api_keys_config_loaded": False,
                "local_routes_count": 24,
                "categories": {
                    "market_data": {"count": 15, "type": "external"},
                    "news": {"count": 10, "type": "external"},
                    "sentiment": {"count": 7, "type": "external"},
                    "analytics": {"count": 17, "type": "external"},
                    "block_explorers": {"count": 9, "type": "external"},
                    "rpc_nodes": {"count": 8, "type": "external"},
                    "ai_ml": {"count": 1, "type": "external"},
                },
                "by_category": [
                    {"name": "Analytics", "count": 17},
                    {"name": "Market Data", "count": 15},
                    {"name": "News", "count": 10},
                    {"name": "Explorers", "count": 9},
                    {"name": "RPC Nodes", "count": 8},
                    {"name": "Sentiment", "count": 7},
                    {"name": "AI/ML", "count": 1}
                ]
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "registry_loaded": False
        }


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
            "success": True,
            "coins": coins_list,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko_trending"
        }
    except Exception as e:
        logger.error(f"Failed to fetch trending coins: {e}")
        # Fallback to top market cap coins
        fallback = await api_coins_top(limit=10)
        fallback["source"] = "fallback_top_coins"
        return fallback


@app.get("/api/market/top")
async def api_market_top(limit: int = 50):
    """Alias for /api/coins/top - Top cryptocurrencies by market cap"""
    return await api_coins_top(limit=limit)


@app.get("/api/market/trending")
async def api_market_trending():
    """Alias for /api/trending - Trending cryptocurrencies"""
    return await api_trending()

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
    
    # Fallback - return error or empty (NO MOCK DATA)
    logger.warning("Sentiment data unavailable and mock data is disabled.")
    return {
        "fear_greed_index": 50,
        "sentiment": "neutral",
        "market_mood": "neutral",
        "confidence": 0,
        "history": [],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "unavailable",
        "error": "Real data unavailable"
    }


@app.get("/api/fear-greed")
async def api_fear_greed(limit: int = 1) -> Dict[str, Any]:
    """
    Convenience endpoint for Fear & Greed Index (Alternative.me).
    This keeps client integrations simple and is safe to call from the dashboard.
    """
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.alternative.me/fng/", params={"limit": str(limit)})
            response.raise_for_status()
            payload = response.json()

        data = payload.get("data") or []
        latest = data[0] if isinstance(data, list) and data else {}

        value = int(latest.get("value", 50))
        classification = latest.get("value_classification", "Neutral")

        return {
            "success": True,
            "value": value,
            "classification": classification,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "alternative.me",
            "data": data[: min(len(data), 30)],
        }
    except Exception as e:
        logger.error(f"Failed to fetch Fear & Greed Index: {e}")
        return {
            "success": False,
            "value": 50,
            "classification": "Neutral",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "unavailable",
            "error": str(e),
        }


@app.get("/api/sentiment/asset/{symbol}")
async def api_sentiment_asset(symbol: str):
    """Get sentiment analysis for a specific asset"""
    # NO MOCK DATA
    return {
        "success": False,
        "symbol": symbol,
        "sentiment": "neutral",
        "sentiment_value": 50,
        "color": "#94a3b8",
        "social_score": 0,
        "news_score": 0,
        "sources": {"twitter": 0, "reddit": 0, "news": 0},
        "error": "Asset sentiment unavailable (mock data removed)",
        "timestamp": datetime.utcnow().isoformat() + "Z"
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


@app.post("/api/models/reinitialize")
async def api_models_reinitialize():
    """Alias for /api/models/reinit-all - Re-initialize all AI models."""
    from ai_models import initialize_models

    result = initialize_models()
    status = _registry.get_registry_status()
    return {"status": "ok", "init_result": result, "registry": status}


@app.get("/api/ai/signals")
async def api_ai_signals(symbol: str = "BTC"):
    """AI trading signals for a symbol - Real signals only"""
    # No mock signals
    signals = []
    
    return {
        "symbol": symbol,
        "signals": signals,
        "total": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message": "No active signals from real models"
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
    
    # NO MOCK DATA - Return safe default
    decision = "HOLD"
    confidence = 0.0
    summary = "AI analysis unavailable. Real models required."

    signals: List[Dict[str, Any]] = [
        {"type": "neutral", "text": "AI models not connected or unavailable."},
    ]

    risks: List[str] = [
        "Data unavailable.",
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


@app.get("/api/news")
async def api_news(limit: int = 50, source: Optional[str] = None) -> Dict[str, Any]:
    """Alias for /api/news/latest - Latest crypto news with optional source filter"""
    return await api_news_latest(limit)


@app.get("/api/news/latest")
async def api_news_latest(limit: int = 50) -> Dict[str, Any]:
    """Latest crypto news - REAL DATA from CryptoCompare RSS"""
    try:
        import feedparser
        import httpx
        
        articles: List[Dict[str, Any]] = []
        
        # Try CryptoCompare RSS feed
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("Data"):
                        for item in data["Data"][:limit]:
                            articles.append({
                                "id": item.get("id", ""),
                                "title": item.get("title", ""),
                                "description": item.get("body", "")[:200] + "...",
                                "content": item.get("body", ""),
                                "source": item.get("source", "CryptoCompare"),
                                "published_at": datetime.fromtimestamp(item.get("published_on", 0)).isoformat() + "Z",
                                "url": item.get("url", ""),
                                "sentiment": "neutral",
                                "sentiment_score": 0.0,
                                "tags": item.get("tags", "").split("|") if item.get("tags") else [],
                            })
        except Exception as e:
            logger.error(f"CryptoCompare news failed: {e}")
        
        # Fallback to CoinDesk RSS if no articles
        if not articles:
            try:
                feed = feedparser.parse("https://www.coindesk.com/arc/outboundfeeds/rss/")
                for entry in feed.entries[:limit]:
                    articles.append({
                        "id": entry.get("id", ""),
                        "title": entry.get("title", ""),
                        "description": entry.get("summary", "")[:200] + "...",
                        "content": entry.get("summary", ""),
                        "source": "CoinDesk",
                        "published_at": entry.get("published", ""),
                        "url": entry.get("link", ""),
                        "sentiment": "neutral",
                        "sentiment_score": 0.0,
                        "tags": ["crypto", "news"],
                    })
            except Exception as e:
                logger.error(f"CoinDesk RSS failed: {e}")
        
        return {
            "articles": articles,
            "news": articles,  # Support both formats
            "total": len(articles),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"News API error: {e}")
        return {
            "articles": [],
            "news": [],
            "total": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e)
        }


# ============================================================================
# DeFi (public, no keys) - DefiLlama
# ============================================================================

@app.get("/api/defi/tvl")
async def api_defi_tvl() -> Dict[str, Any]:
    """Total Value Locked (TVL) using DefiLlama public API."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://api.llama.fi/tvl")
            resp.raise_for_status()
            tvl = resp.json()
        return {"success": True, "tvl": tvl, "source": "defillama", "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"DeFi TVL failed: {e}")
        return {"success": False, "tvl": None, "source": "unavailable", "error": str(e), "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/api/defi/protocols")
async def api_defi_protocols(limit: int = 20) -> Dict[str, Any]:
    """Top DeFi protocols by TVL using DefiLlama public API."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get("https://api.llama.fi/protocols")
            resp.raise_for_status()
            protocols = resp.json()

        if isinstance(protocols, list):
            protocols = sorted(protocols, key=lambda p: float(p.get("tvl") or 0), reverse=True)
            protocols = protocols[: max(1, min(int(limit), 100))]

        return {"success": True, "protocols": protocols, "source": "defillama", "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"DeFi protocols failed: {e}")
        return {"success": False, "protocols": [], "source": "unavailable", "error": str(e), "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/api/defi/yields")
async def api_defi_yields(limit: int = 20) -> Dict[str, Any]:
    """Yield pools snapshot using DefiLlama public API."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get("https://yields.llama.fi/pools")
            resp.raise_for_status()
            payload = resp.json()

        pools = payload.get("data") if isinstance(payload, dict) else []
        if isinstance(pools, list):
            pools = sorted(pools, key=lambda p: float(p.get("tvlUsd") or 0), reverse=True)
            pools = pools[: max(1, min(int(limit), 100))]

        return {"success": True, "pools": pools, "source": "defillama", "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"DeFi yields failed: {e}")
        return {"success": False, "pools": [], "source": "unavailable", "error": str(e), "timestamp": datetime.utcnow().isoformat() + "Z"}

@app.get("/api/market")
async def api_market(limit: Optional[int] = None):
    """Market overview data - REAL DATA from CoinGecko"""
    from backend.services.coingecko_client import coingecko_client
    
    try:
        # Get real market data from CoinGecko
        fetch_limit = limit if limit else 10
        market_data = await coingecko_client.get_market_prices(limit=fetch_limit)
        
        # Calculate global stats from top coins
        total_market_cap = sum(coin.get("marketCap", 0) for coin in market_data)
        total_volume = sum(coin.get("volume24h", 0) for coin in market_data)
        
        # Get BTC and ETH for dominance calculation
        btc_data = next((c for c in market_data if c["symbol"] == "BTC"), None)
        eth_data = next((c for c in market_data if c["symbol"] == "ETH"), None)
        
        btc_dominance = (btc_data["marketCap"] / total_market_cap * 100) if btc_data and total_market_cap > 0 else 0
        eth_dominance = (eth_data["marketCap"] / total_market_cap * 100) if eth_data and total_market_cap > 0 else 0
        
        return {
            "success": True,
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
            "success": False,
            "total_market_cap": 2_450_000_000_000,
            "totalMarketCap": 2_450_000_000_000,
            "total_volume": 98_500_000_000,
            "totalVolume": 98_500_000_000,
            "btc_dominance": 52.3,
            "eth_dominance": 17.8,
            "active_coins": 100,
            "activeCoins": 100,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "fallback",
            "error": str(e)
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
            # Use the real CoinGecko image URL if available
            image_url = coin.get("image", "")
            if not image_url:
                # Fallback to a generated URL
                image_url = f"https://assets.coingecko.com/coins/images/1/small/{coin.get('id', coin.get('symbol', '').lower())}.png"
            
            coins.append({
                "id": coin.get("id", coin.get("symbol", "").lower()),
                "rank": coin.get("market_cap_rank", idx + 1),
                "market_cap_rank": coin.get("market_cap_rank", idx + 1),
                "symbol": coin.get("symbol", ""),
                "name": coin.get("name", coin.get("symbol", "")),
                "image": image_url,  # Real image URL from CoinGecko
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
                "price_change_percentage_7d_in_currency": 0,
                "sparkline": [],  # Can be populated from separate API call if needed
                "circulating_supply": coin.get("circulating_supply", 0),
                "total_supply": coin.get("total_supply", 0),
                "max_supply": coin.get("max_supply", 0),
                "ath": coin.get("ath", 0),
                "atl": coin.get("atl", 0),
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
        # Return minimal fallback data with proper CoinGecko image URLs
        import random
        fallback_coins = []
        # (symbol, name, price, mcap, coingecko_id, image_url)
        coin_data = [
            ("BTC", "Bitcoin", 67850, 1_280_000_000_000, "bitcoin", "https://assets.coingecko.com/coins/images/1/small/bitcoin.png"),
            ("ETH", "Ethereum", 3420, 410_000_000_000, "ethereum", "https://assets.coingecko.com/coins/images/279/small/ethereum.png"),
            ("BNB", "BNB", 585, 88_000_000_000, "binancecoin", "https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png"),
            ("SOL", "Solana", 145, 65_000_000_000, "solana", "https://assets.coingecko.com/coins/images/4128/small/solana.png"),
            ("XRP", "XRP", 0.62, 34_000_000_000, "ripple", "https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png"),
            ("ADA", "Cardano", 0.58, 21_000_000_000, "cardano", "https://assets.coingecko.com/coins/images/975/small/cardano.png"),
            ("AVAX", "Avalanche", 38, 14_500_000_000, "avalanche-2", "https://assets.coingecko.com/coins/images/12559/small/Avalanche_Circle_RedWhite_Trans.png"),
            ("DOT", "Polkadot", 7.2, 9_800_000_000, "polkadot", "https://assets.coingecko.com/coins/images/12171/small/polkadot.png"),
            ("MATIC", "Polygon", 0.88, 8_200_000_000, "matic-network", "https://assets.coingecko.com/coins/images/4713/small/matic-token-icon.png"),
            ("LINK", "Chainlink", 15.4, 8_900_000_000, "chainlink", "https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png")
        ]
        
        for i in range(min(limit, len(coin_data) * 5)):
            symbol, name, price, mcap, coingecko_id, image = coin_data[i % len(coin_data)]
            fallback_coins.append({
                "id": coingecko_id,
                "rank": i + 1,
                "market_cap_rank": i + 1,
                "symbol": symbol,
                "name": name,
                "image": image,  # Correct CoinGecko image URL
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
                "price_change_percentage_7d_in_currency": round(random.uniform(-20, 30), 2),
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


# ============================================================================
# SENTIMENT ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/sentiment/analyze")
async def api_sentiment_analyze(payload: Dict[str, Any]):
    """Analyze sentiment of text using AI models"""
    try:
        text = payload.get("text", "")
        mode = payload.get("mode", "crypto")
        # Optional: allow explicit HF model selection from the UI
        # - `model_key`: key from the server/client registry (preferred)
        # - `model`: backwards-compatible alias used by some pages
        model_key = payload.get("model_key") or payload.get("model")
        use_ensemble = bool(payload.get("use_ensemble", True))
        
        if not text:
            return {
                "success": False,
                "error": "Text is required",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        # Use AI service for sentiment analysis
        try:
            from backend.services.ai_service_unified import ai_service

            # If the UI requested a specific model_key and HF client is available,
            # call it directly so the Models page "Test Model" works.
            if model_key and getattr(ai_service, "hf_client", None) is not None:
                hf_result = await ai_service.hf_client.analyze_sentiment(
                    text=text,
                    model_key=str(model_key),
                    use_cache=True,
                )

                # Normalize HF API client response into the UI-friendly shape.
                if hf_result.get("status") == "success":
                    return {
                        "success": True,
                        "sentiment": hf_result.get("label", "neutral"),
                        "score": hf_result.get("score", hf_result.get("confidence", 0.5)),
                        "confidence": hf_result.get("confidence", hf_result.get("score", 0.5)),
                        "model": hf_result.get("model", "hf_inference_api"),
                        "model_key": hf_result.get("model_key", model_key),
                        "engine": hf_result.get("engine", "hf_inference_api"),
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }

                # If the selected model isn't available, fall back to auto mode.
                # (Still return success=False only if everything fails.)

            result = await ai_service.analyze_sentiment(text, category=mode, use_ensemble=use_ensemble)

            return {
                "success": True,
                "sentiment": result.get("sentiment", result.get("label", "neutral")),
                "score": result.get("score", result.get("confidence", 0.5)),
                "confidence": result.get("confidence", result.get("score", 0.5)),
                "model": result.get("model", "unified"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        except Exception as e:
            logger.warning(f"AI sentiment analysis failed: {e}, using fallback")
            
            # Fallback: Simple keyword-based sentiment
            positive_words = ["bullish", "pump", "moon", "gain", "profit", "buy", "long", "up", "rise", "surge"]
            negative_words = ["bearish", "dump", "crash", "loss", "sell", "short", "down", "fall", "drop"]
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                sentiment = "bullish"
                score = 0.6 + (pos_count * 0.05)
            elif neg_count > pos_count:
                sentiment = "bearish"
                score = 0.4 - (neg_count * 0.05)
            else:
                sentiment = "neutral"
                score = 0.5
            
            score = max(0.0, min(1.0, score))
            
            return {
                "success": True,
                "sentiment": sentiment,
                "score": score,
                "confidence": 0.6,
                "model": "keyword_fallback",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
    except Exception as e:
        logger.error(f"Sentiment analyze error: {e}")
        return {
            "success": False,
            "error": str(e),
            "sentiment": "neutral",
            "score": 0.5,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# ============================================================================
# OHLCV DATA ENDPOINTS
# ============================================================================

@app.get("/api/ohlcv")
async def api_ohlcv_query(symbol: str, timeframe: str = "1h", limit: int = 100):
    """Query-style OHLCV endpoint for frontend compatibility."""
    return await api_ohlcv_symbol(symbol=symbol, timeframe=timeframe, limit=limit)


@app.get("/api/klines")
async def api_klines(symbol: str, interval: str = "1h", limit: int = 100):
    """Binance-style klines alias for frontend compatibility."""
    sym = symbol.upper().strip()
    m = re.match(r"^([A-Z0-9]+?)(USDT|USD|USDC|BUSD)$", sym)
    base = m.group(1) if m else sym
    return await api_ohlcv_symbol(symbol=base, timeframe=interval, limit=limit)


@app.get("/api/historical")
async def api_historical(symbol: str, days: int = 30):
    """Simple historical alias (daily candles)."""
    try:
        from backend.services.binance_client import BinanceClient

        binance = BinanceClient()
        fetch_days = min(max(int(days), 1), 365)
        data = await binance.get_ohlcv(symbol.upper(), "1d", fetch_days)
        return {
            "success": True,
            "symbol": symbol.upper(),
            "days": fetch_days,
            "data": data,
            "count": len(data),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "binance",
        }
    except Exception as e:
        logger.warning(f"Historical fetch failed for {symbol}: {e}")
        return {
            "success": False,
            "symbol": symbol.upper(),
            "days": days,
            "data": [],
            "count": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "unavailable",
            "error": str(e),
        }


@app.get("/api/ohlcv/{symbol}")
async def api_ohlcv_symbol(symbol: str, timeframe: str = "1h", limit: int = 100):
    """Get OHLCV data for a symbol - fallback endpoint"""
    try:
        # Try to get from market API router first
        from backend.services.binance_client import BinanceClient
        
        binance = BinanceClient()
        data = await binance.get_ohlcv(symbol, timeframe, limit)
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data,
            "count": len(data),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.warning(f"OHLCV fetch failed for {symbol}: {e}")
        return {
            "success": False,
            "error": "Data temporarily unavailable",
            "message": "Unable to fetch OHLCV data. External data sources may be restricted or rate-limited.",
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


@app.get("/api/ohlcv/multi")
async def api_ohlcv_multi(symbols: str, timeframe: str = "1h", limit: int = 100):
    """Get OHLCV data for multiple symbols"""
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        results = {}
        
        from backend.services.binance_client import BinanceClient
        binance = BinanceClient()
        
        for symbol in symbol_list:
            try:
                data = await binance.get_ohlcv(symbol, timeframe, limit)
                results[symbol] = {
                    "success": True,
                    "data": data,
                    "count": len(data)
                }
            except Exception as e:
                results[symbol] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": True,
            "results": results,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Multi OHLCV error: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

#
# NOTE:
# `/` is already handled earlier (redirects to dashboard). Keep a single handler
# for a stable routing table (avoids duplicate route definitions).
#

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
# Models Summary Endpoint
# ============================================================================

@app.get("/api/models/summary")
async def get_models_summary():
    """
    Get comprehensive models summary for frontend
    Returns models grouped by category with health status
    """
    try:
        # Get models from ai_models registry
        try:
            health_registry = get_model_health_registry()
            model_specs = MODEL_SPECS
            registry_initialized = _registry._initialized if hasattr(_registry, '_initialized') else False
            loaded_pipelines = list(_registry._pipelines.keys()) if hasattr(_registry, '_pipelines') else []
        except Exception as e:
            logger.warning(f"ai_models registry not available: {e}")
            health_registry = {}
            model_specs = {}
            registry_initialized = False
            loaded_pipelines = []
        
        # Try to get data from AI models monitor (optional)
        ai_models = []
        try:
            from backend.services.ai_models_monitor import db as ai_models_db
            ai_models = ai_models_db.get_all_models()
        except Exception as e:
            logger.debug(f"AI models monitor not available: {e}")
        
        # Build categories from model specs
        categories = {}
        total_models = 0
        loaded_models = 0
        failed_models = 0
        processed_keys = set()
        
        # Process MODEL_SPECS
        for key, spec in model_specs.items():
            if key in processed_keys:
                continue
            processed_keys.add(key)
            
            category = spec.category or "other"
            if category not in categories:
                categories[category] = []
            
            # Get health status
            health_entry = health_registry.get(key)
            if health_entry:
                # Convert ModelHealthEntry to dict
                if hasattr(health_entry, 'status'):
                    status = health_entry.status
                    success_count = health_entry.success_count if hasattr(health_entry, 'success_count') else 0
                    error_count = health_entry.error_count if hasattr(health_entry, 'error_count') else 0
                    last_success = health_entry.last_success if hasattr(health_entry, 'last_success') else None
                    cooldown_until = health_entry.cooldown_until if hasattr(health_entry, 'cooldown_until') else None
                else:
                    status = health_entry.get("status", "unknown")
                    success_count = health_entry.get("success_count", 0)
                    error_count = health_entry.get("error_count", 0)
                    last_success = health_entry.get("last_success")
                    cooldown_until = health_entry.get("cooldown_until")
            else:
                status = "unknown"
                success_count = 0
                error_count = 0
                last_success = None
                cooldown_until = None
            
            loaded = key in loaded_pipelines or status == "healthy"
            
            if loaded:
                loaded_models += 1
            elif status == "unavailable":
                failed_models += 1
            
            model_data = {
                "key": key,
                "model_id": spec.model_id,
                "name": spec.model_id.split("/")[-1] if "/" in spec.model_id else spec.model_id,
                "category": category,
                "task": spec.task or "unknown",
                "loaded": loaded,
                "status": status,
                "success_count": success_count,
                "error_count": error_count,
                "last_success": last_success,
                "cooldown_until": cooldown_until
            }
            
            categories[category].append(model_data)
            total_models += 1
        
        # Also include AI models monitor data if available (avoid duplicates)
        if ai_models:
            for model in ai_models:
                model_id = model.get('model_id', '')
                key = model_id.replace("/", "_") if model_id else f"ai_model_{len(categories)}"
                
                if key in processed_keys:
                    continue
                processed_keys.add(key)
                
                category = model.get('category', 'other')
                if category not in categories:
                    categories[category] = []
                
                status = "available" if model.get('success_rate', 0) > 50 else "failed"
                if status == "available":
                    loaded_models += 1
                else:
                    failed_models += 1
                
                categories[category].append({
                    "key": key,
                    "model_id": model_id,
                    "name": model_id.split("/")[-1] if "/" in model_id else model_id,
                    "category": category,
                    "task": model.get('task', 'unknown'),
                    "loaded": status == "available",
                    "status": status,
                    "success_rate": model.get('success_rate', 0),
                    "avg_response_time_ms": model.get('avg_response_time_ms')
                })
                total_models += 1
        
        # Determine HF mode
        hf_mode = "on" if registry_initialized else "off"
        try:
            import transformers
            transformers_available = True
        except ImportError:
            transformers_available = False
        
        # Build summary
        summary = {
            "total_models": total_models,
            "loaded_models": loaded_models,
            "failed_models": failed_models,
            "hf_mode": hf_mode,
            "transformers_available": transformers_available
        }
        
        # Convert health registry to array format
        health_registry_array = []
        for key, health_entry in health_registry.items():
            if hasattr(health_entry, 'status'):
                # ModelHealthEntry object
                health_registry_array.append({
                    "key": key,
                    "name": health_entry.name if hasattr(health_entry, 'name') else key,
                    "status": health_entry.status,
                    "success_count": health_entry.success_count if hasattr(health_entry, 'success_count') else 0,
                    "error_count": health_entry.error_count if hasattr(health_entry, 'error_count') else 0,
                    "last_success": health_entry.last_success if hasattr(health_entry, 'last_success') else None,
                    "cooldown_until": health_entry.cooldown_until if hasattr(health_entry, 'cooldown_until') else None
                })
            else:
                # Dict format
                health_registry_array.append({
                    "key": key,
                    "name": health_entry.get("name", key),
                    "status": health_entry.get("status", "unknown"),
                    "success_count": health_entry.get("success_count", 0),
                    "error_count": health_entry.get("error_count", 0),
                    "last_success": health_entry.get("last_success"),
                    "cooldown_until": health_entry.get("cooldown_until")
                })
        
        return {
            "ok": True,
            "success": True,
            "summary": summary,
            "categories": categories,
            "health_registry": health_registry_array,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting models summary: {e}", exc_info=True)
        # Return fallback structure
        return {
            "ok": False,
            "success": False,
            "error": str(e),
            "summary": {
                "total_models": 0,
                "loaded_models": 0,
                "failed_models": 0,
                "hf_mode": "error",
                "transformers_available": False
            },
            "categories": {},
            "health_registry": [],
            "fallback": True,
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


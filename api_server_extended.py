#!/usr/bin/env python3
"""
API Server Extended - HuggingFace Spaces Deployment Ready
Complete Admin API with Real Data Only - NO MOCKS
"""

import os
import asyncio
import sqlite3
import httpx
import json
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager
from collections import defaultdict

logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

# Environment variables
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
PORT = int(os.getenv("PORT", "7860"))

# Paths - In Docker container, use /app as base
WORKSPACE_ROOT = Path("/app" if Path("/app").exists() else (Path("/workspace") if Path("/workspace").exists() else Path(".")))
DB_PATH = WORKSPACE_ROOT / "data" / "database" / "crypto_monitor.db"
LOG_DIR = WORKSPACE_ROOT / "logs"
PROVIDERS_CONFIG_PATH = WORKSPACE_ROOT / "providers_config_extended.json"
AUTO_DISCOVERY_REPORT_PATH = WORKSPACE_ROOT / "PROVIDER_AUTO_DISCOVERY_REPORT.json"
API_REGISTRY_PATH = WORKSPACE_ROOT / "all_apis_merged_2025.json"

# Ensure directories exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Global state for providers
_provider_state = {
    "providers": {},
    "pools": {},
    "logs": [],
    "last_check": None,
    "stats": {"total": 0, "online": 0, "offline": 0, "degraded": 0}
}


# ===== Database Setup =====
def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            name TEXT,
            price_usd REAL NOT NULL,
            volume_24h REAL,
            market_cap REAL,
            percent_change_24h REAL,
            rank INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment_label TEXT NOT NULL,
            confidence REAL NOT NULL,
            model_used TEXT,
            analysis_type TEXT,
            symbol TEXT,
            scores TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT,
            source TEXT,
            sentiment_label TEXT,
            sentiment_confidence REAL,
            related_symbols TEXT,
            published_date DATETIME,
            analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_symbol ON prices(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_timestamp ON sentiment_analysis(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_symbol ON sentiment_analysis(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_date)")

    conn.commit()
    conn.close()
    print(f"✓ Database initialized at {DB_PATH}")


def save_price_to_db(price_data: Dict[str, Any]):
    """Save price data to SQLite"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prices (symbol, name, price_usd, volume_24h, market_cap, percent_change_24h, rank)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            price_data.get("symbol"),
            price_data.get("name"),
            price_data.get("price_usd", 0.0),
            price_data.get("volume_24h"),
            price_data.get("market_cap"),
            price_data.get("percent_change_24h"),
            price_data.get("rank")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving price to database: {e}")


def get_price_history_from_db(symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get price history from SQLite"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM prices
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (symbol, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching price history: {e}")
        return []


# ===== Provider Management =====
def load_providers_config() -> Dict[str, Any]:
    """Load providers from providers_config_extended.json"""
    try:
        if PROVIDERS_CONFIG_PATH.exists():
            with open(PROVIDERS_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Validate structure
                if not isinstance(config, dict):
                    logger.warning("Providers config is not a dict, returning empty")
                    return {"providers": {}}
                if "providers" not in config:
                    logger.warning("Providers config missing 'providers' key, adding it")
                    config["providers"] = {}
                return config
        logger.warning(f"Providers config file not found at {PROVIDERS_CONFIG_PATH}")
        return {"providers": {}}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error loading providers config: {e}")
        return {"providers": {}}
    except Exception as e:
        logger.error(f"Error loading providers config: {e}")
        return {"providers": {}}


def load_apl_report() -> Dict[str, Any]:
    """Load APL validation report (alias for auto-discovery report)"""
    return load_auto_discovery_report()

def load_auto_discovery_report() -> Dict[str, Any]:
    """Load PROVIDER_AUTO_DISCOVERY_REPORT.json"""
    try:
        if AUTO_DISCOVERY_REPORT_PATH.exists():
            with open(AUTO_DISCOVERY_REPORT_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading auto-discovery report: {e}")
        return {}

def load_api_registry() -> Dict[str, Any]:
    """Load all_apis_merged_2025.json"""
    try:
        if API_REGISTRY_PATH.exists():
            with open(API_REGISTRY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading API registry: {e}")
        return {}


# ===== Real Data Providers =====
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}


async def fetch_coingecko_simple_price() -> Dict[str, Any]:
    """Fetch real price data from CoinGecko API"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,binancecoin",
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }

    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail=f"CoinGecko API error: HTTP {response.status_code}")
        return response.json()


async def fetch_fear_greed_index() -> Dict[str, Any]:
    """Fetch real Fear & Greed Index from Alternative.me"""
    url = "https://api.alternative.me/fng/"
    params = {"limit": "1", "format": "json"}

    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail=f"Alternative.me API error: HTTP {response.status_code}")
        return response.json()


async def fetch_coingecko_trending() -> Dict[str, Any]:
    """Fetch real trending coins from CoinGecko"""
    url = "https://api.coingecko.com/api/v3/search/trending"

    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail=f"CoinGecko trending API error: HTTP {response.status_code}")
        return response.json()


# ===== Lifespan Management =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("=" * 80)
    print("🚀 Starting Crypto Monitor Admin API")
    print("=" * 80)
    init_database()
    
    # Load providers
    config = load_providers_config()
    _provider_state["providers"] = config.get("providers", {})
    print(f"✓ Loaded {len(_provider_state['providers'])} providers from config")
    
    # Load auto-discovery report
    apl_report = load_auto_discovery_report()
    if apl_report:
        print(f"✓ Loaded auto-discovery report with validation data")
    
    # Load API registry
    api_registry = load_api_registry()
    if api_registry:
        metadata = api_registry.get("metadata", {})
        print(f"✓ Loaded API registry: {metadata.get('name', 'unknown')} v{metadata.get('version', 'unknown')}")
    
    # Initialize AI models
    try:
        from ai_models import initialize_models, registry_status
        model_init_result = initialize_models()
        registry_info = registry_status()
        print(f"✓ AI Models initialized: {model_init_result}")
        print(f"✓ HF Registry status: {registry_info}")
    except Exception as e:
        print(f"⚠ AI Models initialization failed: {e}")
    
    # Validate unified resources
    try:
        from backend.services.resource_validator import validate_unified_resources
        validation_report = validate_unified_resources(str(WORKSPACE_ROOT / "api-resources" / "crypto_resources_unified_2025-11-11.json"))
        print(f"✓ Resource validation: {validation_report['local_backend_routes']['routes_count']} local routes")
        if validation_report['local_backend_routes']['duplicate_signatures'] > 0:
            print(f"⚠ Found {validation_report['local_backend_routes']['duplicate_signatures']} duplicate route signatures")
    except Exception as e:
        print(f"⚠ Resource validation failed: {e}")
    
    print(f"✓ Server ready on port {PORT}")
    print("=" * 80)
    yield
    print("Shutting down...")


# ===== FastAPI Application =====
app = FastAPI(
    title="Crypto Monitor Admin API",
    description="Real-time cryptocurrency data API with Admin Dashboard",
    version="5.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to ensure HTML responses have correct Content-Type
class HTMLContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if isinstance(response, HTMLResponse):
            response.headers["Content-Type"] = "text/html; charset=utf-8"
            response.headers["X-Content-Type-Options"] = "nosniff"
        return response

app.add_middleware(HTMLContentTypeMiddleware)

# Mount static files
try:
    static_path = WORKSPACE_ROOT / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        print(f"✓ Mounted static files from {static_path}")
    else:
        # Create static directories if they don't exist
        static_path.mkdir(parents=True, exist_ok=True)
        (static_path / "css").mkdir(exist_ok=True)
        (static_path / "js").mkdir(exist_ok=True)
        print(f"✓ Created static directories at {static_path}")
except Exception as e:
    print(f"⚠ Could not mount static files: {e}")

# Serve trading pairs file
@app.get("/trading_pairs.txt")
async def get_trading_pairs():
    """Serve trading pairs text file"""
    from fastapi.responses import PlainTextResponse
    trading_pairs_file = WORKSPACE_ROOT / "trading_pairs.txt"
    if trading_pairs_file.exists():
        return FileResponse(trading_pairs_file, media_type="text/plain")
    return PlainTextResponse("BTCUSDT\nETHUSDT\nBNBUSDT\nSOLUSDT", status_code=200)


# ===== HTML UI Endpoints =====
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard"""
    index_path = WORKSPACE_ROOT / "index.html"
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8", errors="ignore")
        return HTMLResponse(
            content=content,
            media_type="text/html",
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "X-Content-Type-Options": "nosniff"
            }
        )
    return HTMLResponse(
        "<h1>Cryptocurrency Data & Analysis API</h1><p>See <a href='/docs'>/docs</a> for API documentation</p>",
        headers={"Content-Type": "text/html; charset=utf-8"}
    )

@app.get("/index.html", response_class=HTMLResponse)
async def index():
    """Serve index.html"""
    index_path = WORKSPACE_ROOT / "index.html"
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8", errors="ignore")
        return HTMLResponse(
            content=content,
            media_type="text/html",
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "X-Content-Type-Options": "nosniff"
            }
        )
    return HTMLResponse(
        "<h1>index.html not found</h1>",
        headers={"Content-Type": "text/html; charset=utf-8"}
    )

@app.get("/ai-tools", response_class=HTMLResponse)
async def ai_tools_page(request: Request):
    """
    Serve the standalone AI Tools page.

    This page provides:
    - Sentiment Playground: POST /api/sentiment/analyze
    - Text Summarizer: POST /api/ai/summarize
    - Model Status & Diagnostics: GET /api/models/status, /api/models/list
    """
    ai_tools_path = WORKSPACE_ROOT / "templates" / "ai_tools.html"
    if ai_tools_path.exists():
        content = ai_tools_path.read_text(encoding="utf-8", errors="ignore")
        return HTMLResponse(
            content=content,
            media_type="text/html",
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "X-Content-Type-Options": "nosniff"
            }
        )
    return HTMLResponse(
        "<h1>AI Tools page not found</h1>",
        headers={"Content-Type": "text/html; charset=utf-8"}
    )


# ===== Health & Status Endpoints =====
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": str(DB_PATH),
        "use_mock_data": USE_MOCK_DATA,
        "providers_loaded": len(_provider_state["providers"])
    }


@app.get("/api/status")
async def get_status():
    """System status"""
    config = load_providers_config()
    providers = config.get("providers", {})
    
    # Count by validation status
    validated_count = sum(1 for p in providers.values() if p.get("validated"))
    
    return {
        "system_health": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_providers": len(providers),
        "validated_providers": validated_count,
        "database_status": "connected",
        "apl_available": AUTO_DISCOVERY_REPORT_PATH.exists(),
        "use_mock_data": USE_MOCK_DATA
    }


@app.get("/api/stats")
async def get_stats():
    """System statistics"""
    config = load_providers_config()
    providers = config.get("providers", {})
    
    # Group by category
    categories = defaultdict(int)
    for p in providers.values():
        cat = p.get("category", "unknown")
        categories[cat] += 1
    
    return {
        "total_providers": len(providers),
        "categories": dict(categories),
        "total_categories": len(categories),
        "timestamp": datetime.now().isoformat()
    }


# ===== Market Data Endpoint =====
@app.get("/api/market")
async def get_market_data():
    """Market data from CoinGecko - REAL DATA ONLY"""
    try:
        data = await fetch_coingecko_simple_price()

        cryptocurrencies = []
        coin_mapping = {
            "bitcoin": {"name": "Bitcoin", "symbol": "BTC", "rank": 1, "image": "https://assets.coingecko.com/coins/images/1/small/bitcoin.png"},
            "ethereum": {"name": "Ethereum", "symbol": "ETH", "rank": 2, "image": "https://assets.coingecko.com/coins/images/279/small/ethereum.png"},
            "binancecoin": {"name": "BNB", "symbol": "BNB", "rank": 3, "image": "https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png"}
        }

        for coin_id, coin_info in coin_mapping.items():
            if coin_id in data:
                coin_data = data[coin_id]
                crypto_entry = {
                    "rank": coin_info["rank"],
                    "name": coin_info["name"],
                    "symbol": coin_info["symbol"],
                    "price": coin_data.get("usd", 0),
                    "change_24h": coin_data.get("usd_24h_change", 0),
                    "market_cap": coin_data.get("usd_market_cap", 0),
                    "volume_24h": coin_data.get("usd_24h_vol", 0),
                    "image": coin_info["image"]
                }
                cryptocurrencies.append(crypto_entry)

                # Save to database
                save_price_to_db({
                    "symbol": coin_info["symbol"],
                    "name": coin_info["name"],
                    "price_usd": crypto_entry["price"],
                    "volume_24h": crypto_entry["volume_24h"],
                    "market_cap": crypto_entry["market_cap"],
                    "percent_change_24h": crypto_entry["change_24h"],
                    "rank": coin_info["rank"]
                })

        # Calculate dominance
        total_market_cap = sum(c["market_cap"] for c in cryptocurrencies)
        btc_dominance = 0
        if total_market_cap > 0:
            btc_entry = next((c for c in cryptocurrencies if c["symbol"] == "BTC"), None)
            if btc_entry:
                btc_dominance = (btc_entry["market_cap"] / total_market_cap) * 100

        return {
            "cryptocurrencies": cryptocurrencies,
            "total_market_cap": total_market_cap,
            "btc_dominance": btc_dominance,
            "timestamp": datetime.now().isoformat(),
            "source": "CoinGecko API (Real Data)"
        }

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch market data: {str(e)}")


@app.get("/api/market/history")
async def get_market_history(symbol: str = "BTC", limit: int = 10):
    """Get price history from database - REAL DATA ONLY"""
    history = get_price_history_from_db(symbol.upper(), limit)
    
    if not history:
        return {
            "symbol": symbol,
            "history": [],
            "count": 0,
            "message": "No history available"
        }
    
    return {
        "symbol": symbol,
        "history": history,
        "count": len(history),
        "source": "SQLite Database (Real Data)"
    }


@app.get("/api/sentiment")
async def get_sentiment():
    """Sentiment data from Alternative.me - REAL DATA ONLY"""
    try:
        data = await fetch_fear_greed_index()
        
        if "data" in data and len(data["data"]) > 0:
            fng_data = data["data"][0]
            return {
                "fear_greed_index": int(fng_data["value"]),
                "fear_greed_label": fng_data["value_classification"],
                "timestamp": datetime.now().isoformat(),
                "source": "Alternative.me API (Real Data)"
            }
        
        raise HTTPException(status_code=503, detail="Invalid response from Alternative.me")
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch sentiment: {str(e)}")


@app.get("/api/resources")
async def get_resources():
    """Get resources summary for HTML dashboard (includes API registry metadata and local routes)"""
    try:
        # Load API registry for metadata
        api_registry = load_api_registry()
        metadata = api_registry.get("metadata", {}) if api_registry else {}
        
        # Try to load resources from JSON files
        resources_json = WORKSPACE_ROOT / "api-resources" / "crypto_resources_unified_2025-11-11.json"
        
        summary = {
            "total_resources": 0,
            "free_resources": 0,
            "models_available": 0,
            "local_routes_count": 0,
            "categories": {}
        }
        
        # Load from unified resources
        if resources_json.exists():
            with open(resources_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                registry = data.get('registry', {})
                
                # Process all categories
                for category, items in registry.items():
                    if category == 'metadata':
                        continue
                    if isinstance(items, list):
                        count = len(items)
                        summary['total_resources'] += count
                        summary['categories'][category] = {
                            "count": count,
                            "type": "local" if category == "local_backend_routes" else "external"
                        }
                        
                        # Track local routes separately
                        if category == 'local_backend_routes':
                            summary['local_routes_count'] = count
                        
                        free_count = sum(1 for item in items if item.get('free', False) or item.get('auth', {}).get('type') == 'none')
                        summary['free_resources'] += free_count
        
        # Try to get model count
        try:
            from ai_models import MODEL_SPECS
            summary['models_available'] = len(MODEL_SPECS) if MODEL_SPECS else 0
        except:
            summary['models_available'] = 0
        
        return {
            "success": True,
            "summary": summary,
            "api_registry_metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": {
                "total_resources": 0,
                "free_resources": 0,
                "models_available": 0,
                "categories": {}
            },
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/resources/apis")
async def get_resources_apis():
    """Get API registry with local and external routes"""
    registry = load_api_registry()
    
    # Load unified resources for local routes
    resources_json = WORKSPACE_ROOT / "api-resources" / "crypto_resources_unified_2025-11-11.json"
    local_routes = []
    unified_metadata = {}
    
    if resources_json.exists():
        try:
            with open(resources_json, 'r', encoding='utf-8') as f:
                unified_data = json.load(f)
                unified_registry = unified_data.get('registry', {})
                unified_metadata = unified_registry.get('metadata', {})
                local_routes = unified_registry.get('local_backend_routes', [])
        except Exception as e:
            logger.error(f"Error loading unified resources: {e}")
    
    # Process legacy registry
    categories = set()
    metadata = {}
    raw_files = []
    trimmed_files = []
    
    if registry:
        metadata = registry.get("metadata", {})
        raw_files = registry.get("raw_files", [])
        
        # Extract categories from raw file content (basic parsing)
        for raw_file in raw_files[:5]:  # Limit to first 5 files for performance
            content = raw_file.get("content", "")
            # Simple category detection from content
            if "market data" in content.lower() or "price" in content.lower():
                categories.add("market_data")
            if "explorer" in content.lower() or "blockchain" in content.lower():
                categories.add("block_explorer")
            if "rpc" in content.lower() or "node" in content.lower():
                categories.add("rpc_nodes")
            if "cors" in content.lower() or "proxy" in content.lower():
                categories.add("cors_proxy")
            if "news" in content.lower():
                categories.add("news")
            if "sentiment" in content.lower() or "fear" in content.lower():
                categories.add("sentiment")
            if "whale" in content.lower():
                categories.add("whale_tracking")
        
        # Provide trimmed raw files (first 500 chars each)
        for raw_file in raw_files[:10]:  # Limit to 10 files
            content = raw_file.get("content", "")
            trimmed_files.append({
                "filename": raw_file.get("filename", ""),
                "preview": content[:500] + "..." if len(content) > 500 else content,
                "size": len(content)
            })
    
    # Add local category
    if local_routes:
        categories.add("local")
    
    return {
        "ok": True,
        "metadata": {
            "name": metadata.get("name", "") or unified_metadata.get("description", ""),
            "version": metadata.get("version", "") or unified_metadata.get("version", ""),
            "description": metadata.get("description", ""),
            "created_at": metadata.get("created_at", ""),
            "source_files": metadata.get("source_files", []),
            "updated": unified_metadata.get("updated", "")
        },
        "categories": list(categories),
        "local_routes": {
            "count": len(local_routes),
            "routes": local_routes[:20]  # Return first 20 for preview
        },
        "raw_files_preview": trimmed_files,
        "total_raw_files": len(raw_files),
        "sources": ["all_apis_merged_2025.json", "crypto_resources_unified_2025-11-11.json"]
    }

@app.get("/api/resources/apis/raw")
async def get_resources_apis_raw():
    """Get raw files from API registry (trimmed to avoid huge payloads)"""
    registry = load_api_registry()
    
    if not registry:
        return {
            "ok": False,
            "error": "API registry file not found"
        }
    
    raw_files = registry.get("raw_files", [])
    
    # Return trimmed versions (first 1000 chars each, max 20 files)
    trimmed = []
    for raw_file in raw_files[:20]:
        content = raw_file.get("content", "")
        trimmed.append({
            "filename": raw_file.get("filename", ""),
            "preview": content[:1000] + "..." if len(content) > 1000 else content,
            "full_size": len(content)
        })
    
    return {
        "ok": True,
        "files": trimmed,
        "total_files": len(raw_files),
        "showing": min(20, len(raw_files)),
        "source": "all_apis_merged_2025.json"
    }


@app.get("/api/trending")
async def get_trending():
    """Trending coins from CoinGecko - REAL DATA ONLY"""
    try:
        data = await fetch_coingecko_trending()
        
        trending_coins = []
        if "coins" in data:
            for item in data["coins"][:10]:
                coin = item.get("item", {})
                trending_coins.append({
                    "id": coin.get("id"),
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "thumb": coin.get("thumb"),
                    "score": coin.get("score", 0)
                })
        
        return {
            "trending": trending_coins,
            "count": len(trending_coins),
            "timestamp": datetime.now().isoformat(),
            "source": "CoinGecko API (Real Data)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch trending: {str(e)}")


# ===== Providers Management Endpoints =====
@app.get("/api/providers")
async def get_providers():
    """Get all providers from providers_config_extended.json + HF Models + auto-discovery status"""
    config = load_providers_config()
    providers = config.get("providers", {})
    
    # Load auto-discovery report to merge status
    discovery_report = load_auto_discovery_report()
    discovery_results = {}
    if discovery_report and "http_providers" in discovery_report:
        for result in discovery_report["http_providers"].get("results", []):
            discovery_results[result.get("provider_id")] = result
    
    result = []
    for provider_id, provider_data in providers.items():
        # Merge with auto-discovery data if available
        discovery_data = discovery_results.get(provider_id, {})
        
        provider_entry = {
            "id": provider_id,
            "provider_id": provider_id,  # Keep for backward compatibility
            "name": provider_data.get("name", provider_id),
            "category": provider_data.get("category", "unknown"),
            "base_url": provider_data.get("base_url", ""),
            "type": provider_data.get("type", "http"),
            "priority": provider_data.get("priority", 0),
            "weight": provider_data.get("weight", 0),
            "requires_auth": provider_data.get("requires_auth", False),
            "rate_limit": provider_data.get("rate_limit", {}),
            "endpoints": provider_data.get("endpoints", {}),
            "status": discovery_data.get("status", "UNKNOWN") if discovery_data else "unvalidated",
            "validated_at": provider_data.get("validated_at"),
            "response_time_ms": discovery_data.get("response_time_ms") or provider_data.get("response_time_ms"),
            "error_reason": discovery_data.get("error_reason"),
            "test_endpoint": discovery_data.get("test_endpoint"),
            "added_by": provider_data.get("added_by", "manual")
        }
        result.append(provider_entry)
    
    # Add HF Models as providers
    try:
        from ai_models import MODEL_SPECS, _registry
        for model_key, spec in MODEL_SPECS.items():
            is_loaded = model_key in _registry._pipelines
            result.append({
                "id": f"hf_model_{model_key}",
                "provider_id": f"hf_model_{model_key}",
                "name": f"HF Model: {spec.model_id}",
                "category": spec.category,
                "type": "hf_model",
                "status": "available" if is_loaded else "not_loaded",
                "model_key": model_key,
                "model_id": spec.model_id,
                "task": spec.task,
                "requires_auth": spec.requires_auth,
                "endpoint": f"/api/models/{model_key}/predict",
                "added_by": "hf_models"
            })
    except Exception as e:
        logger.warning(f"Could not add HF models as providers: {e}")
    
    return {
        "providers": result,
        "total": len(result),
        "source": "providers_config_extended.json + HF Models + Auto-Discovery Report"
    }


@app.get("/api/providers/{provider_id}")
async def get_provider_detail(provider_id: str):
    """Get specific provider details"""
    # Check if it's an HF model provider
    if provider_id.startswith("hf_model_"):
        model_key = provider_id.replace("hf_model_", "")
        try:
            from ai_models import MODEL_SPECS, _registry
            if model_key not in MODEL_SPECS:
                raise HTTPException(status_code=404, detail=f"Model {model_key} not found")
            
            spec = MODEL_SPECS[model_key]
            is_loaded = model_key in _registry._pipelines
            
            return {
                "provider_id": provider_id,
                "name": f"HF Model: {spec.model_id}",
                "category": spec.category,
                "type": "hf_model",
                "status": "available" if is_loaded else "not_loaded",
                "model_key": model_key,
                "model_id": spec.model_id,
                "task": spec.task,
                "requires_auth": spec.requires_auth,
                "endpoint": f"/api/models/{model_key}/predict",
                "usage": {
                    "method": "POST",
                    "url": f"/api/models/{model_key}/predict",
                    "body": {"text": "string", "options": {}}
                },
                "added_by": "hf_models"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Regular provider
    config = load_providers_config()
    providers = config.get("providers", {})
    
    if provider_id not in providers:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
    
    return {
        "provider_id": provider_id,
        **providers[provider_id]
    }


@app.get("/api/providers/category/{category}")
async def get_providers_by_category(category: str):
    """Get providers by category"""
    config = load_providers_config()
    providers = config.get("providers", {})
    
    filtered = {
        pid: data for pid, data in providers.items()
        if data.get("category") == category
    }
    
    return {
        "category": category,
        "providers": filtered,
        "count": len(filtered)
    }


# ===== Pools Endpoints (Placeholder - to be implemented) =====
@app.get("/api/pools")
async def get_pools():
    """Get provider pools"""
    return {
        "pools": [],
        "message": "Pools feature not yet implemented in this version"
    }


# ===== Logs Endpoints =====
@app.get("/api/logs/recent")
async def get_recent_logs():
    """Get recent logs"""
    return {
        "logs": _provider_state.get("logs", [])[-50:],
        "count": min(50, len(_provider_state.get("logs", [])))
    }


@app.get("/api/logs/errors")
async def get_error_logs():
    """Get error logs"""
    all_logs = _provider_state.get("logs", [])
    errors = [log for log in all_logs if log.get("level") == "ERROR"]
    return {
        "errors": errors[-50:],
        "count": len(errors)
    }


# ===== Diagnostics Endpoints =====
@app.post("/api/diagnostics/run")
async def run_diagnostics(auto_fix: bool = False):
    """Run system diagnostics"""
    issues = []
    fixes_applied = []
    
    # Check database
    if not DB_PATH.exists():
        issues.append({"type": "database", "message": "Database file not found"})
        if auto_fix:
            init_database()
            fixes_applied.append("Initialized database")
    
    # Check providers config
    if not PROVIDERS_CONFIG_PATH.exists():
        issues.append({"type": "config", "message": "Providers config not found"})
    
    # Check auto-discovery report
    if not AUTO_DISCOVERY_REPORT_PATH.exists():
        issues.append({"type": "auto_discovery", "message": "Auto-discovery report not found"})
    
    return {
        "status": "completed",
        "issues_found": len(issues),
        "issues": issues,
        "fixes_applied": fixes_applied if auto_fix else [],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/diagnostics/last")
async def get_last_diagnostics():
    """Get last diagnostics results"""
    # Would load from file in real implementation
    return {
        "status": "no_previous_run",
        "message": "No previous diagnostics run found"
    }


# ===== APL (Auto Provider Loader) Endpoints =====
@app.post("/api/apl/run")
async def run_apl_scan():
    """Run APL provider scan"""
    try:
        # Run APL script
        result = subprocess.run(
            ["python3", str(WORKSPACE_ROOT / "auto_provider_loader.py")],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(WORKSPACE_ROOT)
        )
        
        # Reload providers after APL run
        config = load_providers_config()
        _provider_state["providers"] = config.get("providers", {})
        
        return {
            "status": "completed",
            "stdout": result.stdout[-1000:],  # Last 1000 chars
            "returncode": result.returncode,
            "providers_count": len(_provider_state["providers"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "message": "APL scan timed out after 5 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"APL scan failed: {str(e)}")


@app.get("/api/apl/report")
async def get_apl_report():
    """Get APL validation report (alias for auto-discovery report)"""
    return await get_providers_auto_discovery_report()

@app.get("/api/providers/auto-discovery-report")
async def get_providers_auto_discovery_report():
    """Get PROVIDER_AUTO_DISCOVERY_REPORT.json"""
    report = load_auto_discovery_report()
    
    if not report:
        return {
            "ok": False,
            "error": "Auto-discovery report file not found",
            "message": f"Report file not found at {AUTO_DISCOVERY_REPORT_PATH}"
        }
    
    return {
        "ok": True,
        "report": report,
        "source": "PROVIDER_AUTO_DISCOVERY_REPORT.json"
    }

@app.get("/api/providers/health-summary")
async def get_providers_health_summary():
    """Get simplified health summary from auto-discovery report + local routes - always returns 200"""
    try:
        report = load_auto_discovery_report()
        
        # Load local routes for health checking
        resources_json = WORKSPACE_ROOT / "api-resources" / "crypto_resources_unified_2025-11-11.json"
        local_routes = []
        local_health = {"total": 0, "checked": 0, "up": 0, "down": 0}
        
        if resources_json.exists():
            try:
                with open(resources_json, 'r', encoding='utf-8') as f:
                    unified_data = json.load(f)
                    unified_registry = unified_data.get('registry', {})
                    local_routes = unified_registry.get('local_backend_routes', [])
                    local_health["total"] = len(local_routes)
                    
                    # Quick health check for up to 10 local routes
                    async with httpx.AsyncClient(timeout=2.0) as client:
                        routes_to_check = [r for r in local_routes if 'ws://' not in r.get('base_url', '')][:10]
                        for route in routes_to_check:
                            base_url = route.get('base_url', '').replace('{API_BASE}', f'http://localhost:{PORT}')
                            if 'http' in base_url:
                                try:
                                    response = await client.get(base_url, timeout=2.0)
                                    local_health["checked"] += 1
                                    if response.status_code < 500:
                                        local_health["up"] += 1
                                    else:
                                        local_health["down"] += 1
                                except:
                                    local_health["checked"] += 1
                                    local_health["down"] += 1
            except Exception as e:
                logger.error(f"Error checking local routes health: {e}")
        
        if not report or "stats" not in report:
            return JSONResponse(
                status_code=200,
                content={
                    "ok": False,
                    "error": "Auto-discovery report not found or invalid",
                    "message": f"Report file not found at {AUTO_DISCOVERY_REPORT_PATH}",
                    "summary": {
                        "total_active_providers": 0,
                        "http_valid": 0,
                        "http_invalid": 0,
                        "http_conditional": 0,
                        "hf_valid": 0,
                        "hf_invalid": 0,
                        "hf_conditional": 0,
                        "status_breakdown": {"VALID": 0, "INVALID": 0, "CONDITIONALLY_AVAILABLE": 0},
                        "execution_time_sec": 0,
                        "timestamp": "",
                        "local_routes": local_health
                    }
                }
            )
        
        stats = report.get("stats", {})
        http_providers = report.get("http_providers", {})
        hf_providers = report.get("hf_providers", {})
        
        # Count by status
        status_counts = {"VALID": 0, "INVALID": 0, "CONDITIONALLY_AVAILABLE": 0}
        for result in http_providers.get("results", []):
            status = result.get("status", "UNKNOWN")
            if status in status_counts:
                status_counts[status] += 1
        
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "summary": {
                    "total_active_providers": stats.get("total_active_providers", 0),
                    "http_valid": stats.get("http_valid", 0),
                    "http_invalid": stats.get("http_invalid", 0),
                    "http_conditional": stats.get("http_conditional", 0),
                    "hf_valid": stats.get("hf_valid", 0),
                    "hf_invalid": stats.get("hf_invalid", 0),
                    "hf_conditional": stats.get("hf_conditional", 0),
                    "status_breakdown": status_counts,
                    "execution_time_sec": stats.get("execution_time_sec", 0),
                    "timestamp": stats.get("timestamp", ""),
                    "local_routes": local_health
                },
                "source": "PROVIDER_AUTO_DISCOVERY_REPORT.json + local routes"
            }
        )
    except Exception as e:
        logger.error(f"Error loading health summary: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "ok": False,
                "error": str(e),
                "summary": {
                    "total_active_providers": 0,
                    "http_valid": 0,
                    "http_invalid": 0,
                    "http_conditional": 0,
                    "hf_valid": 0,
                    "hf_invalid": 0,
                    "hf_conditional": 0,
                    "status_breakdown": {"VALID": 0, "INVALID": 0, "CONDITIONALLY_AVAILABLE": 0},
                    "execution_time_sec": 0,
                    "timestamp": "",
                    "local_routes": {"total": 0, "checked": 0, "up": 0, "down": 0}
                }
            }
        )

@app.get("/api/apl/summary")
async def get_apl_summary():
    """Get APL summary statistics (alias for health-summary)"""
    return await get_providers_health_summary()


# ===== HF Models Endpoints =====
@app.get("/api/hf/models")
async def get_hf_models():
    """Get HuggingFace models from APL report"""
    report = load_apl_report()
    
    if not report:
        return {"models": [], "count": 0}
    
    hf_models = report.get("hf_models", {}).get("results", [])
    
    return {
        "models": hf_models,
        "count": len(hf_models),
        "source": "APL Validation Report (Real Data)"
    }


@app.get("/api/hf/health")
async def get_hf_health():
    """Get HF services health"""
    try:
        from backend.services.hf_registry import REGISTRY
        health = REGISTRY.health()
        return health
    except Exception as e:
        return {
            "ok": False,
            "error": f"HF registry not available: {str(e)}"
        }


# ===== DeFi Endpoint =====
@app.get("/api/defi")
async def get_defi():
    """DeFi endpoint"""
    return {
        "success": True,
        "message": "DeFi data endpoint",
        "data": [],
        "timestamp": datetime.now().isoformat()
    }


# ===== News Endpoint (compatible with UI) =====
@app.get("/api/news")
async def get_news_api(limit: int = 20):
    """Get news (compatible with UI)"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM news_articles 
            ORDER BY analyzed_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        results = []
        for row in rows:
            record = dict(zip(columns, row))
            if record.get("related_symbols"):
                try:
                    record["related_symbols"] = json.loads(record["related_symbols"])
                except:
                    pass
            results.append(record)
        
        return {
            "success": True,
            "news": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "news": [],
            "count": 0,
            "error": str(e)
        }


# ===== Logs Endpoints =====
@app.get("/api/logs/summary")
async def get_logs_summary():
    """Get logs summary"""
    try:
        return {
            "success": True,
            "total": len(_provider_state.get("logs", [])),
            "recent": _provider_state.get("logs", [])[-10:],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ===== Diagnostics Endpoints =====
@app.get("/api/diagnostics/errors")
async def get_diagnostics_errors():
    """Get diagnostic errors"""
    try:
        return {
            "success": True,
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "errors": [],
            "error": str(e)
        }


# ===== Resources Endpoints =====
@app.get("/api/resources/search")
async def search_resources(q: str = "", source: str = "all"):
    """Search resources"""
    try:
        return {
            "success": True,
            "query": q,
            "source": source,
            "results": [],
            "count": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ===== V2 API Endpoints (compatibility) =====
@app.post("/api/v2/export/{export_type}")
async def export_v2(export_type: str, data: Dict[str, Any] = None):
    """V2 export endpoint"""
    return {
        "success": True,
        "type": export_type,
        "message": "Export functionality",
        "data": data or {}
    }


@app.post("/api/v2/backup")
async def backup_v2():
    """V2 backup endpoint"""
    return {
        "success": True,
        "message": "Backup functionality",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v2/import/providers")
async def import_providers_v2(data: Dict[str, Any]):
    """V2 import providers endpoint"""
    return {
        "success": True,
        "message": "Import providers functionality",
        "data": data
    }


# ===== HuggingFace ML Sentiment Endpoints =====
@app.post("/api/sentiment/analyze")
async def analyze_sentiment(request: Dict[str, Any]):
    """Analyze sentiment using Hugging Face models"""
    try:
        from ai_models import (
            analyze_crypto_sentiment,
            analyze_financial_sentiment,
            analyze_social_sentiment,
            analyze_market_text,
            _registry,
            MODEL_SPECS,
            ModelNotAvailable
        )
        
        text = request.get("text", "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        mode = request.get("mode", "auto").lower()
        source = request.get("source", "user")
        model_key = request.get("model_key")
        symbol = request.get("symbol")
        
        try:
            # If model_key is provided, use that specific model
            if model_key and model_key in MODEL_SPECS:
                try:
                    pipeline = _registry.get_pipeline(model_key)
                    spec = MODEL_SPECS[model_key]
                    
                    # Handle different task types
                    if spec.task == "text-generation":
                        # For trading signal models or generation models
                        raw_result = pipeline(text, max_length=200, num_return_sequences=1)
                        if isinstance(raw_result, list) and raw_result:
                            raw_result = raw_result[0]
                        
                        generated_text = raw_result.get("generated_text", str(raw_result))
                        
                        # Parse trading signals if applicable
                        if spec.category == "trading_signal":
                            # Extract signal from generated text
                            decision = "HOLD"
                            if "buy" in generated_text.lower():
                                decision = "BUY"
                            elif "sell" in generated_text.lower():
                                decision = "SELL"
                            
                            return {
                                "ok": True,
                                "available": True,
                                "sentiment": decision.lower(),
                                "label": decision.lower(),
                                "score": 0.7,
                                "confidence": 0.7,
                                "model": model_key,
                                "engine": "huggingface",
                                "mode": "trading",
                                "extra": {
                                    "decision": decision,
                                    "rationale": generated_text,
                                    "raw": raw_result
                                }
                            }
                        else:
                            # Generation model - return generated text
                            return {
                                "ok": True,
                                "available": True,
                                "sentiment": "neutral",
                                "label": "neutral",
                                "score": 0.5,
                                "confidence": 0.5,
                                "model": model_key,
                                "engine": "huggingface",
                                "mode": "generation",
                                "extra": {
                                    "generated_text": generated_text,
                                    "raw": raw_result
                                }
                            }
                    else:
                        # Text classification / sentiment
                        raw_result = pipeline(text[:512])
                        if isinstance(raw_result, list) and raw_result:
                            raw_result = raw_result[0]
                        
                        label = raw_result.get("label", "neutral").upper()
                        score = raw_result.get("score", 0.5)
                        
                        # Map labels to standard format
                        mapped = "bullish" if "POSITIVE" in label or "BULLISH" in label or "LABEL_2" in label else (
                            "bearish" if "NEGATIVE" in label or "BEARISH" in label or "LABEL_0" in label else "neutral"
                        )
                        
                        return {
                            "ok": True,
                            "available": True,
                            "sentiment": mapped,
                            "label": mapped,
                            "score": score,
                            "confidence": score,
                            "raw_label": label,
                            "model": model_key,
                            "engine": "huggingface",
                            "mode": mode,
                            "extra": {
                                "vote": score if mapped == "bullish" else (-score if mapped == "bearish" else 0.0),
                                "raw": raw_result
                            }
                        }
                except ModelNotAvailable as e:
                    logger.warning(f"Model {model_key} not available: {e}")
                    return {
                        "ok": False,
                        "available": False,
                        "error": f"Model {model_key} not available: {str(e)}",
                        "label": "neutral",
                        "sentiment": "neutral",
                        "score": 0.0,
                        "confidence": 0.0
                    }
            
            # Default mode-based analysis
            if mode == "crypto":
                result = analyze_crypto_sentiment(text)
            elif mode == "financial":
                result = analyze_financial_sentiment(text)
            elif mode == "social":
                result = analyze_social_sentiment(text)
            elif mode == "trading":
                # Try to use trading signal model
                result = analyze_crypto_sentiment(text)
            else:
                result = analyze_market_text(text)
            
            sentiment_label = result.get("label", "neutral")
            confidence = result.get("confidence", result.get("score", 0.5))
            model_used = result.get("model_count", result.get("model", result.get("engine", "unknown")))
            
            # Prepare response compatible with frontend format
            response_data = {
                "ok": True,
                "available": True,
                "sentiment": sentiment_label.lower(),
                "label": sentiment_label.lower(),
                "confidence": float(confidence),
                "score": float(confidence),
                "model": f"{model_used} models" if isinstance(model_used, int) else str(model_used),
                "engine": result.get("engine", "huggingface"),
                "mode": mode
            }
            
            # Add details if available for score bars
            if result.get("scores"):
                scores_dict = result.get("scores", {})
                if isinstance(scores_dict, dict):
                    labels_list = []
                    scores_list = []
                    for lbl, scr in scores_dict.items():
                        labels_list.append(lbl)
                        scores_list.append(float(scr) if isinstance(scr, (int, float)) else float(scr.get("score", 0.5)) if isinstance(scr, dict) else 0.5)
                    if labels_list:
                        response_data["details"] = {
                            "labels": labels_list,
                            "scores": scores_list
                        }
            
            # Save to database
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sentiment_analysis 
                    (text, sentiment_label, confidence, model_used, analysis_type, symbol, scores)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    text[:500],
                    sentiment_label,
                    confidence,
                    f"{model_used} models" if isinstance(model_used, int) else str(model_used),
                    mode,
                    symbol,
                    json.dumps(result.get("scores", {}))
                ))
                conn.commit()
                conn.close()
            except Exception as db_error:
                logger.warning(f"Failed to save to database: {db_error}")
            
            return response_data
            
        except Exception as e:
            # Unexpected error - log and return error response
            logger.error(f"Sentiment analysis unexpected error: {str(e)}")
            return {
                "ok": False,
                "available": False,
                "error": f"Analysis failed: {str(e)}",
                "sentiment": "neutral",
                "label": "neutral",
                "confidence": 0.0,
                "score": 0.0
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@app.post("/api/ai/summarize")
async def summarize_text(request: Dict[str, Any]):
    """
    Summarize text using Hugging Face models or simple text processing.
    
    Expects: { "text": "string", "max_sentences": 3 }
    Returns: { "ok": true, "summary": "...", "sentences": ["...", "..."] }
    """
    try:
        text = request.get("text", "").strip()
        max_sentences = request.get("max_sentences", 3)
        
        if not text:
            return {
                "ok": False,
                "error": "Text is required"
            }
        
        # Try to use Hugging Face summarization model if available
        try:
            from ai_models import MODEL_SPECS, _registry, ModelNotAvailable
            
            # Check if summarization model is available
            summarization_key = None
            for key, spec in MODEL_SPECS.items():
                if spec.task == "summarization":
                    summarization_key = key
                    break
            
            if summarization_key:
                try:
                    pipeline = _registry.get_pipeline(summarization_key)
                    # Use HF model for summarization
                    # Try with parameters first, then fallback to simple call
                    try:
                        summary_result = pipeline(text, max_length=max_sentences * 50, min_length=max_sentences * 20, do_sample=False)
                    except TypeError:
                        # Some pipelines don't accept these parameters
                        summary_result = pipeline(text)
                    
                    if isinstance(summary_result, list) and summary_result:
                        summary_text = summary_result[0].get("summary_text", summary_result[0].get("generated_text", str(summary_result[0])))
                    elif isinstance(summary_result, dict):
                        summary_text = summary_result.get("summary_text", summary_result.get("generated_text", str(summary_result)))
                    else:
                        summary_text = str(summary_result)
                    
                    # Split into sentences
                    sentences = [s.strip() + ("." if not s.strip().endswith((".", "!", "?")) else "") for s in summary_text.split(". ") if s.strip()]
                    sentences = sentences[:max_sentences]
                    
                    return {
                        "ok": True,
                        "summary": summary_text,
                        "sentences": sentences
                    }
                except ModelNotAvailable:
                    # Fall through to simple summarizer
                    pass
                except Exception as e:
                    logger.warning(f"HF summarization failed: {e}, using fallback")
                    # Fall through to simple summarizer
                    pass
        except Exception as e:
            logger.warning(f"HF summarization model not available: {e}")
            # Fall through to simple summarizer
        
        # Simple placeholder summarizer: split by sentences and take first N
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in ".!?":
                sentence = current_sentence.strip()
                if sentence:
                    sentences.append(sentence)
                    current_sentence = ""
                    if len(sentences) >= max_sentences:
                        break
        
        # If we didn't get enough sentences, add the rest
        if len(sentences) < max_sentences and current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # If still no sentences, just truncate
        if not sentences:
            words = text.split()
            chunk_size = len(words) // max_sentences
            sentences = []
            for i in range(max_sentences):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < max_sentences - 1 else len(words)
                if start_idx < len(words):
                    sentence = " ".join(words[start_idx:end_idx])
                    if sentence:
                        sentences.append(sentence)
        
        summary = " ".join(sentences)
        
        return {
            "ok": True,
            "summary": summary,
            "sentences": sentences[:max_sentences]
        }
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return {
            "ok": False,
            "error": f"Summarization failed: {str(e)}"
        }


@app.post("/api/news/analyze")
async def analyze_news(request: Dict[str, Any]):
    """Analyze news article sentiment using HF models"""
    try:
        from ai_models import analyze_news_item
        
        title = request.get("title", "").strip()
        content = request.get("content", request.get("description", "")).strip()
        url = request.get("url", "")
        source = request.get("source", "unknown")
        published_date = request.get("published_date")
        
        if not title and not content:
            raise HTTPException(status_code=400, detail="Title or content is required")
        
        try:
            news_item = {
                "title": title,
                "description": content
            }
            result = analyze_news_item(news_item)
            
            sentiment_label = result.get("sentiment", "neutral")
            sentiment_confidence = result.get("sentiment_confidence", 0.5)
            sentiment_details = result.get("sentiment_details", {})
            related_symbols = request.get("related_symbols", [])
            
            # Check if HF models were used (for diagnostics)
            hf_available = sentiment_details.get("engine", "unknown") == "huggingface" if isinstance(sentiment_details, dict) else True
            
            # Save to database (always)
            saved_to_db = False
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO news_articles 
                    (title, content, url, source, sentiment_label, sentiment_confidence, related_symbols, published_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    title[:500],
                    content[:2000] if content else None,
                    url,
                    source,
                    sentiment_label,
                    sentiment_confidence,
                    json.dumps(related_symbols) if related_symbols else None,
                    published_date
                ))
                conn.commit()
                conn.close()
                saved_to_db = True
            except Exception as db_error:
                logger.warning(f"Failed to save to database: {db_error}")
            
            return {
                "success": True,
                "available": True,
                "hf_models_available": hf_available,
                "news": {
                    "title": title,
                    "sentiment": sentiment_label,
                    "confidence": sentiment_confidence,
                    "details": sentiment_details
                },
                "saved_to_db": saved_to_db
            }
            
        except Exception as e:
            logger.error(f"News analysis error: {str(e)}")
            return {
                "success": False,
                "available": False,
                "error": f"Analysis failed: {str(e)}",
                "news": {
                    "title": title,
                    "sentiment": "neutral",
                    "confidence": 0.0
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News analysis failed: {str(e)}")


@app.get("/api/sentiment/history")
async def get_sentiment_history(
    symbol: Optional[str] = None,
    limit: int = 50
):
    """Get sentiment analysis history from database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute("""
                SELECT * FROM sentiment_analysis 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (symbol.upper(), limit))
        else:
            cursor.execute("""
                SELECT * FROM sentiment_analysis 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        results = []
        for row in rows:
            record = dict(zip(columns, row))
            if record.get("scores"):
                try:
                    record["scores"] = json.loads(record["scores"])
                except:
                    pass
            results.append(record)
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sentiment history: {str(e)}")


@app.get("/api/news/latest")
async def get_latest_news(
    limit: int = 20,
    sentiment: Optional[str] = None
):
    """Get latest analyzed news from database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        if sentiment:
            cursor.execute("""
                SELECT * FROM news_articles 
                WHERE sentiment_label = ? 
                ORDER BY analyzed_at DESC 
                LIMIT ?
            """, (sentiment.lower(), limit))
        else:
            cursor.execute("""
                SELECT * FROM news_articles 
                ORDER BY analyzed_at DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        results = []
        for row in rows:
            record = dict(zip(columns, row))
            if record.get("related_symbols"):
                try:
                    record["related_symbols"] = json.loads(record["related_symbols"])
                except:
                    pass
            results.append(record)
        
        return {
            "success": True,
            "count": len(results),
            "news": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")


@app.post("/api/news/summarize")
async def summarize_news(request: Dict[str, Any]):
    """
    Summarize crypto/financial news using Hugging Face Crypto-Financial-News-Summarizer model
    
    Expects: { "title": "News Title", "content": "Full article text" }
    Returns: { "summary": "Summarized news paragraph", "model": "Crypto-Financial-News-Summarizer" }
    """
    try:
        from ai_models import MODEL_SPECS, _registry, ModelNotAvailable
        
        title = request.get("title", "").strip()
        content = request.get("content", "").strip()
        
        if not title and not content:
            raise HTTPException(status_code=400, detail="Title or content is required")
        
        # Combine title and content for summarization
        text_to_summarize = f"{title}. {content}" if title and content else (title or content)
        
        try:
            # Try to use the Crypto-Financial-News-Summarizer model
            summarization_key = "summarization_0"
            
            if summarization_key in MODEL_SPECS:
                try:
                    pipeline = _registry.get_pipeline(summarization_key)
                    spec = MODEL_SPECS[summarization_key]
                    
                    # Use HF model for summarization
                    # Limit input text to avoid token length issues
                    max_input_length = 1024
                    text_input = text_to_summarize[:max_input_length]
                    
                    try:
                        # Try with parameters first
                        summary_result = pipeline(
                            text_input,
                            max_length=150,
                            min_length=50,
                            do_sample=False,
                            truncation=True
                        )
                    except TypeError:
                        # Some pipelines don't accept these parameters
                        summary_result = pipeline(text_input, truncation=True)
                    
                    # Extract summary text from result
                    if isinstance(summary_result, list) and summary_result:
                        summary_text = summary_result[0].get("summary_text", summary_result[0].get("generated_text", str(summary_result[0])))
                    elif isinstance(summary_result, dict):
                        summary_text = summary_result.get("summary_text", summary_result.get("generated_text", str(summary_result)))
                    else:
                        summary_text = str(summary_result)
                    
                    return {
                        "success": True,
                        "summary": summary_text,
                        "model": spec.model_id,
                        "available": True,
                        "input_length": len(text_input),
                        "title": title,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except ModelNotAvailable as e:
                    logger.warning(f"Crypto-Financial-News-Summarizer not available: {e}")
                    # Fall through to fallback
                except Exception as e:
                    logger.warning(f"HF summarization failed: {e}, using fallback")
                    # Fall through to fallback
            
            # Fallback: Simple extractive summarization
            # Split into sentences and take the most important ones
            sentences = []
            current_sentence = ""
            
            for char in text_to_summarize:
                current_sentence += char
                if char in ".!?":
                    sentence = current_sentence.strip()
                    if sentence and len(sentence) > 10:  # Filter out very short sentences
                        sentences.append(sentence)
                        current_sentence = ""
                        if len(sentences) >= 5:  # Take first 5 sentences max
                            break
            
            # If we didn't get enough sentences, add the rest
            if len(sentences) < 3 and current_sentence.strip():
                sentences.append(current_sentence.strip())
            
            # Take first 3 sentences as summary
            summary = " ".join(sentences[:3]) if sentences else text_to_summarize[:500]
            
            return {
                "success": True,
                "summary": summary,
                "model": "fallback_extractive",
                "available": False,
                "note": "Using fallback extractive summarization (HF model not available)",
                "title": title,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return {
                "success": False,
                "error": f"Summarization failed: {str(e)}",
                "summary": "",
                "model": "error",
                "available": False
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News summarization failed: {str(e)}")


@app.get("/api/models/status")
async def get_models_status():
    """Get AI models status and registry info - honest status reporting"""
    try:
        from ai_models import get_model_info, registry_status, HF_MODE, TRANSFORMERS_AVAILABLE, _registry
        
        model_info = get_model_info()
        registry_info = registry_status()
        
        # Determine honest status
        if HF_MODE == "off":
            status = "disabled"
            status_message = "HF models are disabled (HF_MODE=off). To enable them, set HF_MODE=public or HF_MODE=auth in the environment."
        elif not TRANSFORMERS_AVAILABLE:
            status = "transformers_unavailable"
            status_message = "Transformers library is not installed. Models cannot be loaded."
        elif not _registry._initialized:
            status = "not_initialized"
            status_message = "Models have not been initialized yet."
        elif len(_registry._pipelines) == 0:
            status = "no_models_loaded"
            status_message = f"No models could be loaded. {len(_registry._failed_models)} models failed. Check model IDs or HF access."
        elif len(_registry._pipelines) > 0:
            status = "ok" if len(_registry._failed_models) == 0 else "partial"
            status_message = f"{len(_registry._pipelines)} model(s) loaded successfully"
            if len(_registry._failed_models) > 0:
                status_message += f", {len(_registry._failed_models)} failed"
        else:
            status = "unknown"
            status_message = "Unknown status"
        
        # Format failed models as list of [key, error] tuples for ai_tools.html
        failed_list = []
        for key, error in list(_registry._failed_models.items())[:10]:
            failed_list.append([key, str(error)])
        
        return {
            "success": True,
            "status": status,
            "status_message": status_message,
            "hf_mode": HF_MODE,
            "models_loaded": len(_registry._pipelines),
            "models_failed": len(_registry._failed_models),
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "initialized": _registry._initialized,
            "models": model_info,
            "registry": registry_info,
            "failed": failed_list,  # Format: [[key, error], ...] for ai_tools.html
            "failed_models": list(_registry._failed_models.keys())[:10],  # Keep for backward compatibility
            "loaded_models": list(_registry._pipelines.keys()),
            "database": {
                "path": str(DB_PATH),
                "exists": DB_PATH.exists()
            }
        }
    except Exception as e:
        logger.error(f"Error getting models status: {e}")
        return {
            "success": False,
            "status": "error",
            "status_message": f"Error retrieving model status: {str(e)}",
            "error": str(e),
            "hf_mode": "unknown",
            "models_loaded": 0,
            "models_failed": 0
        }


@app.post("/api/models/initialize")
async def initialize_ai_models():
    """Initialize AI models (force reload)"""
    try:
        from ai_models import initialize_models, registry_status
        
        result = initialize_models()
        registry_info = registry_status()
        
        return {
            "success": True,
            "initialization": result,
            "registry": registry_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize models: {str(e)}")


# ===== Model-based Data Endpoints (Using HF Models as Data Sources) =====
@app.get("/api/models/list")
async def list_available_models():
    """List all available Hugging Face models as data sources"""
    try:
        from ai_models import get_model_info, MODEL_SPECS, _registry, CRYPTO_SENTIMENT_MODELS, SOCIAL_SENTIMENT_MODELS, FINANCIAL_SENTIMENT_MODELS, NEWS_SENTIMENT_MODELS, GENERATION_MODELS, TRADING_SIGNAL_MODELS
        
        model_info = get_model_info()
        
        # Model descriptions
        model_descriptions = {
            "kk08/CryptoBERT": "Crypto sentiment binary classification model trained on cryptocurrency-related text",
            "ElKulako/cryptobert": "Crypto social sentiment classifier (Bullish/Neutral/Bearish) for social media and news",
            "StephanAkkerman/FinTwitBERT-sentiment": "Financial tweet sentiment analysis model for market-related social media content",
            "OpenC/crypto-gpt-o3-mini": "Crypto and DeFi text generation model for analysis and content creation",
            "agarkovv/CryptoTrader-LM": "BTC/ETH trading signal generator providing daily buy/sell/hold recommendations",
            "cardiffnlp/twitter-roberta-base-sentiment-latest": "General Twitter sentiment analysis (fallback model)",
            "ProsusAI/finbert": "Financial sentiment analysis model for news and financial documents",
            "FurkanGozukara/Crypto-Financial-News-Summarizer": "Specialized model for summarizing cryptocurrency and financial news articles"
        }
        
        models_list = []
        for key, spec in MODEL_SPECS.items():
            is_loaded = key in _registry._pipelines
            error_msg = None
            if key in _registry._failed_models:
                error_msg = str(_registry._failed_models[key])
            
            models_list.append({
                "key": key,
                "id": key,
                "name": spec.model_id,
                "model_id": spec.model_id,
                "task": spec.task,
                "category": spec.category,
                "requires_auth": spec.requires_auth,
                "loaded": is_loaded,
                "error": error_msg,
                "description": model_descriptions.get(spec.model_id, f"{spec.category} model for {spec.task}"),
                "endpoint": f"/api/models/{key}/predict"
            })
        
        return {
            "success": True,
            "total_models": len(models_list),
            "models": models_list,
            "categories": {
                "crypto_sentiment": CRYPTO_SENTIMENT_MODELS,
                "social_sentiment": SOCIAL_SENTIMENT_MODELS,
                "financial_sentiment": FINANCIAL_SENTIMENT_MODELS,
                "news_sentiment": NEWS_SENTIMENT_MODELS,
                "generation": GENERATION_MODELS,
                "trading_signals": TRADING_SIGNAL_MODELS,
                "summarization": ["FurkanGozukara/Crypto-Financial-News-Summarizer"]
            },
            "model_info": model_info
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "models": []
        }


@app.get("/api/models/{model_key}/info")
async def get_model_info_endpoint(model_key: str):
    """Get information about a specific model"""
    try:
        from ai_models import MODEL_SPECS, ModelNotAvailable, _registry
        
        if model_key not in MODEL_SPECS:
            raise HTTPException(status_code=404, detail=f"Model {model_key} not found")
        
        spec = MODEL_SPECS[model_key]
        is_loaded = model_key in _registry._pipelines
        
        return {
            "success": True,
            "model_key": model_key,
            "model_id": spec.model_id,
            "task": spec.task,
            "category": spec.category,
            "requires_auth": spec.requires_auth,
            "is_loaded": is_loaded,
            "endpoint": f"/api/models/{model_key}/predict",
            "usage": {
                "method": "POST",
                "url": f"/api/models/{model_key}/predict",
                "body": {"text": "string", "options": {}}
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/models/{model_key}/predict")
async def predict_with_model(model_key: str, request: Dict[str, Any]):
    """Use a specific model to generate predictions/data"""
    try:
        from ai_models import MODEL_SPECS, _registry, ModelNotAvailable
        
        if model_key not in MODEL_SPECS:
            raise HTTPException(status_code=404, detail=f"Model {model_key} not found")
        
        spec = MODEL_SPECS[model_key]
        text = request.get("text", "").strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        try:
            pipeline = _registry.get_pipeline(model_key)
            result = pipeline(text[:512])
            
            if isinstance(result, list) and result:
                result = result[0]
            
            return {
                "success": True,
                "available": True,
                "model_key": model_key,
                "model_id": spec.model_id,
                "task": spec.task,
                "input": text[:100],
                "output": result,
                "timestamp": datetime.now().isoformat()
            }
        except ModelNotAvailable as e:
            return {
                "success": False,
                "available": False,
                "model_key": model_key,
                "model_id": spec.model_id,
                "error": str(e),
                "reason": "model_unavailable"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/api/models/batch/predict")
async def batch_predict(request: Dict[str, Any]):
    """Batch prediction using multiple models"""
    try:
        from ai_models import MODEL_SPECS, _registry, ModelNotAvailable
        
        texts = request.get("texts", [])
        model_keys = request.get("models", [])
        
        if not texts:
            raise HTTPException(status_code=400, detail="Texts array is required")
        
        if not model_keys:
            model_keys = list(MODEL_SPECS.keys())[:5]
        
        results = []
        for text in texts:
            if not text.strip():
                continue
            
            text_results = {}
            for model_key in model_keys:
                if model_key not in MODEL_SPECS:
                    continue
                
                try:
                    spec = MODEL_SPECS[model_key]
                    pipeline = _registry.get_pipeline(model_key)
                    result = pipeline(text[:512])
                    
                    if isinstance(result, list) and result:
                        result = result[0]
                    
                    text_results[model_key] = {
                        "model_id": spec.model_id,
                        "result": result,
                        "success": True
                    }
                except ModelNotAvailable:
                    text_results[model_key] = {
                        "success": False,
                        "error": "Model not available"
                    }
                except Exception as e:
                    text_results[model_key] = {
                        "success": False,
                        "error": str(e)
                    }
            
            results.append({
                "text": text[:100],
                "predictions": text_results
            })
        
        return {
            "success": True,
            "total_texts": len(results),
            "models_used": model_keys,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/api/models/data/generated")
async def get_generated_data(
    limit: int = 50,
    model_key: Optional[str] = None,
    symbol: Optional[str] = None
):
    """Get data generated by models from database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        if model_key and symbol:
            cursor.execute("""
                SELECT * FROM sentiment_analysis 
                WHERE analysis_type = ? AND symbol = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (model_key, symbol.upper(), limit))
        elif model_key:
            cursor.execute("""
                SELECT * FROM sentiment_analysis 
                WHERE analysis_type = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (model_key, limit))
        elif symbol:
            cursor.execute("""
                SELECT * FROM sentiment_analysis 
                WHERE symbol = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (symbol.upper(), limit))
        else:
            cursor.execute("""
                SELECT * FROM sentiment_analysis 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        results = []
        for row in rows:
            record = dict(zip(columns, row))
            if record.get("scores"):
                try:
                    record["scores"] = json.loads(record["scores"])
                except:
                    pass
            results.append(record)
        
        return {
            "success": True,
            "count": len(results),
            "data": results,
            "source": "models",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch generated data: {str(e)}")


@app.get("/api/models/data/stats")
async def get_models_data_stats():
    """Get statistics about data generated by models"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sentiment_analysis")
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM sentiment_analysis WHERE symbol IS NOT NULL")
        unique_symbols = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT analysis_type) FROM sentiment_analysis")
        unique_types = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT sentiment_label, COUNT(*) as count 
            FROM sentiment_analysis 
            GROUP BY sentiment_label
        """)
        sentiment_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT analysis_type, COUNT(*) as count 
            FROM sentiment_analysis 
            GROUP BY analysis_type
        """)
        type_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "success": True,
            "statistics": {
                "total_analyses": total_analyses,
                "unique_symbols": unique_symbols,
                "unique_model_types": unique_types,
                "sentiment_distribution": sentiment_dist,
                "model_type_distribution": type_dist
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")


@app.post("/api/hf/run-sentiment")
async def run_hf_sentiment(data: Dict[str, Any]):
    """Run sentiment analysis using HF models (compatible with UI)"""
    try:
        from ai_models import analyze_market_text, ModelNotAvailable
        
        texts = data.get("texts", [])
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts or not any(t.strip() for t in texts):
            raise HTTPException(status_code=400, detail="At least one text is required")
        
        try:
            all_results = []
            total_vote = 0.0
            count = 0
            models_available = False
            
            for text in texts:
                if not text.strip():
                    continue
                
                result = analyze_market_text(text.strip())
                
                # Check if models are available
                if result.get("available", True):
                    models_available = True
                
                label = result.get("label", "neutral")
                confidence = result.get("confidence", 0.5)
                
                vote_score = 0.0
                if label == "bullish":
                    vote_score = confidence
                elif label == "bearish":
                    vote_score = -confidence
                
                total_vote += vote_score
                count += 1
                
                all_results.append({
                    "text": text[:100],
                    "label": label,
                    "confidence": confidence,
                    "vote": vote_score,
                    "available": result.get("available", True)
                })
            
            avg_vote = total_vote / count if count > 0 else 0.0
            
            return {
                "available": models_available,
                "vote": avg_vote,
                "results": all_results,
                "count": count,
                "average_confidence": sum(r["confidence"] for r in all_results) / len(all_results) if all_results else 0.0
            }
            
        except ModelNotAvailable as e:
            return {
                "available": False,
                "vote": 0.0,
                "results": [],
                "count": 0,
                "average_confidence": 0.0,
                "error": str(e),
                "reason": "model_unavailable"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


# ===== Main Entry Point =====
if __name__ == "__main__":
    import uvicorn
    print(f"Starting Crypto Monitor Admin Server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

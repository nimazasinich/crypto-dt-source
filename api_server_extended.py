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
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager
from collections import defaultdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Environment variables
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
PORT = int(os.getenv("PORT", "7860"))

# Paths
WORKSPACE_ROOT = Path("/workspace" if Path("/workspace").exists() else ".")
DB_PATH = WORKSPACE_ROOT / "data" / "database" / "crypto_monitor.db"
LOG_DIR = WORKSPACE_ROOT / "logs"
PROVIDERS_CONFIG_PATH = WORKSPACE_ROOT / "providers_config_extended.json"
APL_REPORT_PATH = WORKSPACE_ROOT / "PROVIDER_AUTO_DISCOVERY_REPORT.json"

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

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_symbol ON prices(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp)")

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
    """Load providers from config file"""
    try:
        if PROVIDERS_CONFIG_PATH.exists():
            with open(PROVIDERS_CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {"providers": {}}
    except Exception as e:
        print(f"Error loading providers config: {e}")
        return {"providers": {}}


def load_apl_report() -> Dict[str, Any]:
    """Load APL validation report"""
    try:
        if APL_REPORT_PATH.exists():
            with open(APL_REPORT_PATH, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading APL report: {e}")
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
    
    # Load APL report
    apl_report = load_apl_report()
    if apl_report:
        print(f"✓ Loaded APL report with validation data")
    
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

# Mount static files
try:
    static_path = WORKSPACE_ROOT / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        print(f"✓ Mounted static files from {static_path}")
except Exception as e:
    print(f"⚠ Could not mount static files: {e}")


# ===== HTML UI Endpoints =====
@app.get("/", response_class=HTMLResponse)
async def serve_admin_dashboard():
    """Serve admin dashboard"""
    html_path = WORKSPACE_ROOT / "admin.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse("<h1>Admin Dashboard</h1><p>admin.html not found</p>")


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
        "apl_available": APL_REPORT_PATH.exists(),
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
    """Get all providers - REAL DATA from config"""
    config = load_providers_config()
    providers = config.get("providers", {})
    
    result = []
    for provider_id, provider_data in providers.items():
        result.append({
            "provider_id": provider_id,
            "name": provider_data.get("name", provider_id),
            "category": provider_data.get("category", "unknown"),
            "type": provider_data.get("type", "unknown"),
            "status": "validated" if provider_data.get("validated") else "unvalidated",
            "validated_at": provider_data.get("validated_at"),
            "response_time_ms": provider_data.get("response_time_ms"),
            "added_by": provider_data.get("added_by", "manual")
        })
    
    return {
        "providers": result,
        "total": len(result),
        "source": "providers_config_extended.json (Real Data)"
    }


@app.get("/api/providers/{provider_id}")
async def get_provider_detail(provider_id: str):
    """Get specific provider details"""
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
    
    # Check APL report
    if not APL_REPORT_PATH.exists():
        issues.append({"type": "apl", "message": "APL report not found"})
    
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
    """Get APL validation report"""
    report = load_apl_report()
    
    if not report:
        return {
            "status": "not_available",
            "message": "APL report not found. Run APL scan first."
        }
    
    return report


@app.get("/api/apl/summary")
async def get_apl_summary():
    """Get APL summary statistics"""
    report = load_apl_report()
    
    if not report or "stats" not in report:
        return {
            "status": "not_available",
            "message": "APL report not found"
        }
    
    stats = report.get("stats", {})
    return {
        "http_candidates": stats.get("total_http_candidates", 0),
        "http_valid": stats.get("http_valid", 0),
        "http_invalid": stats.get("http_invalid", 0),
        "http_conditional": stats.get("http_conditional", 0),
        "hf_candidates": stats.get("total_hf_candidates", 0),
        "hf_valid": stats.get("hf_valid", 0),
        "hf_invalid": stats.get("hf_invalid", 0),
        "hf_conditional": stats.get("hf_conditional", 0),
        "total_active": stats.get("total_active_providers", 0),
        "timestamp": stats.get("timestamp", "")
    }


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


# ===== DeFi Endpoint - NOT IMPLEMENTED =====
@app.get("/api/defi")
async def get_defi():
    """DeFi endpoint - Not implemented"""
    raise HTTPException(status_code=503, detail="DeFi endpoint not implemented. Real data only - no fakes.")


# ===== HuggingFace ML Sentiment - NOT IMPLEMENTED =====
@app.post("/api/hf/run-sentiment")
async def run_sentiment(data: Dict[str, Any]):
    """ML sentiment analysis - Not implemented"""
    raise HTTPException(status_code=501, detail="ML sentiment not implemented. Real data only - no fakes.")


# ===== Main Entry Point =====
if __name__ == "__main__":
    import uvicorn
    print(f"Starting Crypto Monitor Admin Server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

"""Simple FastAPI server for testing HF integration"""

import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Create FastAPI app
app = FastAPI(title="Crypto API Monitor - Simple", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include HF router
try:
    from backend.routers import hf_connect

    app.include_router(hf_connect.router)
    print("✓ HF router loaded")
except Exception as e:
    print(f"✗ HF router failed: {e}")


# Background task for HF registry
@app.on_event("startup")
async def startup_hf():
    try:
        from backend.services.hf_registry import periodic_refresh

        asyncio.create_task(periodic_refresh())
        print("✓ HF background refresh started")
    except Exception as e:
        print(f"✗ HF background refresh failed: {e}")


# Health endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "crypto-api-monitor"}


@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "service": "crypto-api-monitor-api"}


# Serve static files
@app.get("/")
async def root():
    return FileResponse("index.html")


@app.get("/index.html")
async def index():
    return FileResponse("index.html")


@app.get("/hf_console.html")
async def hf_console():
    return FileResponse("hf_console.html")


# Mock API endpoints for dashboard
@app.get("/api/status")
async def api_status():
    """Mock status endpoint"""
    return {
        "total_providers": 9,
        "online": 7,
        "degraded": 1,
        "offline": 1,
        "avg_response_time_ms": 245,
        "total_requests_hour": 156,
        "total_failures_hour": 3,
        "system_health": "healthy",
        "timestamp": "2025-11-11T01:30:00Z",
    }


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
            "status": "online",
        },
        {
            "name": "blockchain_explorers",
            "total_sources": 3,
            "online_sources": 2,
            "avg_response_time_ms": 320,
            "rate_limited_count": 1,
            "last_updated": "2025-11-11T01:29:00Z",
            "status": "online",
        },
        {
            "name": "news",
            "total_sources": 2,
            "online_sources": 2,
            "avg_response_time_ms": 450,
            "rate_limited_count": 0,
            "last_updated": "2025-11-11T01:28:00Z",
            "status": "online",
        },
        {
            "name": "sentiment",
            "total_sources": 1,
            "online_sources": 1,
            "avg_response_time_ms": 200,
            "rate_limited_count": 0,
            "last_updated": "2025-11-11T01:30:00Z",
            "status": "online",
        },
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
            "rate_limit": None,
        },
        {
            "id": 2,
            "name": "Binance",
            "category": "market_data",
            "status": "online",
            "response_time_ms": 120,
            "last_fetch": "2025-11-11T01:30:00Z",
            "has_key": False,
            "rate_limit": None,
        },
        {
            "id": 3,
            "name": "Alternative.me",
            "category": "sentiment",
            "status": "online",
            "response_time_ms": 200,
            "last_fetch": "2025-11-11T01:29:00Z",
            "has_key": False,
            "rate_limit": None,
        },
        {
            "id": 4,
            "name": "Etherscan",
            "category": "blockchain_explorers",
            "status": "online",
            "response_time_ms": 280,
            "last_fetch": "2025-11-11T01:29:30Z",
            "has_key": True,
            "rate_limit": {"used": 45, "total": 100},
        },
        {
            "id": 5,
            "name": "CryptoPanic",
            "category": "news",
            "status": "online",
            "response_time_ms": 380,
            "last_fetch": "2025-11-11T01:28:00Z",
            "has_key": False,
            "rate_limit": None,
        },
    ]


@app.get("/api/charts/health-history")
async def api_health_history(hours: int = 24):
    """Mock health history chart data"""
    import random
    from datetime import datetime, timedelta

    now = datetime.now()
    timestamps = [(now - timedelta(hours=i)).isoformat() for i in range(23, -1, -1)]
    return {"timestamps": timestamps, "success_rate": [random.randint(85, 100) for _ in range(24)]}


@app.get("/api/charts/compliance")
async def api_compliance(days: int = 7):
    """Mock compliance chart data"""
    import random
    from datetime import datetime, timedelta

    now = datetime.now()
    dates = [(now - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    return {"dates": dates, "compliance_percentage": [random.randint(90, 100) for _ in range(7)]}


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
            "error_message": None,
        },
        {
            "timestamp": "2025-11-11T01:29:30Z",
            "provider": "Binance",
            "endpoint": "/api/v3/klines",
            "status": "success",
            "response_time_ms": 120,
            "http_code": 200,
            "error_message": None,
        },
        {
            "timestamp": "2025-11-11T01:29:00Z",
            "provider": "Alternative.me",
            "endpoint": "/fng/",
            "status": "success",
            "response_time_ms": 200,
            "http_code": 200,
            "error_message": None,
        },
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
            "reset_in_seconds": 45,
        },
        {
            "provider": "Etherscan",
            "limit_type": "per_second",
            "limit_value": 5,
            "current_usage": 3,
            "percentage": 60.0,
            "reset_in_seconds": 1,
        },
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
            "Etherscan": [random.randint(40, 80) for _ in range(24)],
        },
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
            "status": "active",
        },
        {
            "provider": "Binance",
            "category": "market_data",
            "schedule": "every_1_min",
            "last_run": "2025-11-11T01:30:00Z",
            "next_run": "2025-11-11T01:31:00Z",
            "on_time_percentage": 99.2,
            "status": "active",
        },
        {
            "provider": "Alternative.me",
            "category": "sentiment",
            "schedule": "every_15_min",
            "last_run": "2025-11-11T01:15:00Z",
            "next_run": "2025-11-11T01:30:00Z",
            "on_time_percentage": 97.8,
            "status": "active",
        },
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
            "status": "fresh",
        },
        {
            "provider": "Binance",
            "category": "market_data",
            "fetch_time": "2025-11-11T01:30:00Z",
            "data_timestamp": "2025-11-11T01:29:58Z",
            "staleness_minutes": 0.03,
            "ttl_minutes": 5,
            "status": "fresh",
        },
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
                "retry_result": "success",
            }
        ],
        "error_type_distribution": {"timeout": 2, "rate_limit": 1, "connection_error": 0},
        "top_failing_providers": [
            {"provider": "NewsAPI", "failure_count": 2},
            {"provider": "TronScan", "failure_count": 1},
        ],
        "remediation_suggestions": [
            {
                "provider": "NewsAPI",
                "issue": "Frequent timeouts",
                "suggestion": "Consider increasing timeout threshold or checking network connectivity",
            }
        ],
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
            "Binance": [random.uniform(0.05, 1.5) for _ in range(24)],
        },
    }


@app.get("/api/config/keys")
async def api_config_keys():
    """Mock API keys config"""
    return [
        {
            "provider": "Etherscan",
            "key_masked": "YourApiKeyToken...abc123",
            "expires_at": None,
            "status": "active",
        },
        {
            "provider": "CoinMarketCap",
            "key_masked": "b54bcf4d-1bca...xyz789",
            "expires_at": "2025-12-31",
            "status": "active",
        },
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

    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")

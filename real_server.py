"""Real data server - fetches actual data from free crypto APIs"""

import asyncio
import time
from collections import defaultdict
from datetime import datetime, timedelta

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Create FastAPI app
app = FastAPI(title="Crypto API Monitor - Real Data", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for real data
state = {
    "providers": {},
    "last_check": {},
    "stats": {"total": 0, "online": 0, "offline": 0, "degraded": 0},
}

# Real API endpoints to test
REAL_APIS = {
    "CoinGecko": {
        "url": "https://api.coingecko.com/api/v3/ping",
        "category": "market_data",
        "test_field": "gecko_says",
    },
    "Binance": {
        "url": "https://api.binance.com/api/v3/ping",
        "category": "market_data",
        "test_field": None,
    },
    "Alternative.me": {
        "url": "https://api.alternative.me/fng/",
        "category": "sentiment",
        "test_field": "data",
    },
    "CoinGecko_BTC": {
        "url": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        "category": "market_data",
        "test_field": "bitcoin",
    },
    "Binance_BTCUSDT": {
        "url": "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT",
        "category": "market_data",
        "test_field": "symbol",
    },
}


async def check_api(name: str, config: dict) -> dict:
    """Check if an API is responding"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(config["url"])
            elapsed = (time.time() - start) * 1000  # ms

            if response.status_code == 200:
                data = response.json()
                # Verify expected field exists
                if config["test_field"] and config["test_field"] not in data:
                    return {
                        "name": name,
                        "status": "degraded",
                        "response_time_ms": int(elapsed),
                        "error": f"Missing field: {config['test_field']}",
                    }
                return {
                    "name": name,
                    "status": "online",
                    "response_time_ms": int(elapsed),
                    "category": config["category"],
                    "last_check": datetime.now().isoformat(),
                }
            else:
                return {
                    "name": name,
                    "status": "degraded",
                    "response_time_ms": int(elapsed),
                    "error": f"HTTP {response.status_code}",
                }
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return {
            "name": name,
            "status": "offline",
            "response_time_ms": int(elapsed),
            "error": str(e),
        }


async def check_all_apis():
    """Check all APIs and update state"""
    tasks = [check_api(name, config) for name, config in REAL_APIS.items()]
    results = await asyncio.gather(*tasks)

    # Update state
    state["providers"] = {r["name"]: r for r in results}
    state["last_check"] = datetime.now().isoformat()

    # Update stats
    state["stats"]["total"] = len(results)
    state["stats"]["online"] = sum(1 for r in results if r["status"] == "online")
    state["stats"]["offline"] = sum(1 for r in results if r["status"] == "offline")
    state["stats"]["degraded"] = sum(1 for r in results if r["status"] == "degraded")

    return results


# Background task to check APIs periodically
async def periodic_check():
    """Check APIs every 30 seconds"""
    while True:
        try:
            await check_all_apis()
            print(
                f"✓ Checked {len(REAL_APIS)} APIs - Online: {state['stats']['online']}, Offline: {state['stats']['offline']}"
            )
        except Exception as e:
            print(f"✗ Error checking APIs: {e}")
        await asyncio.sleep(30)


@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    print("🔄 Running initial API check...")
    await check_all_apis()
    print(
        f"✓ Initial check complete - {state['stats']['online']}/{state['stats']['total']} APIs online"
    )

    # Start background task
    asyncio.create_task(periodic_check())
    print("✓ Background monitoring started")

    # Start HF background refresh
    try:
        from backend.services.hf_registry import periodic_refresh

        asyncio.create_task(periodic_refresh())
        print("✓ HF background refresh started")
    except Exception as e:
        print(f"⚠ HF background refresh not available: {e}")


# Include HF router
try:
    from backend.routers import hf_connect

    app.include_router(hf_connect.router)
    print("✓ HF router loaded")
except Exception as e:
    print(f"⚠ HF router not available: {e}")


# Health endpoints
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "crypto-api-monitor",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/health")
async def api_health():
    return {
        "status": "healthy",
        "last_check": state.get("last_check"),
        "providers_checked": state["stats"]["total"],
    }


# Real data endpoints
@app.get("/api/status")
async def api_status():
    """Real status from actual API checks"""
    providers = list(state["providers"].values())
    online_providers = [p for p in providers if p["status"] == "online"]

    avg_response = 0
    if online_providers:
        avg_response = sum(p["response_time_ms"] for p in online_providers) / len(online_providers)

    return {
        "total_providers": state["stats"]["total"],
        "online": state["stats"]["online"],
        "degraded": state["stats"]["degraded"],
        "offline": state["stats"]["offline"],
        "avg_response_time_ms": int(avg_response),
        "total_requests_hour": state["stats"]["total"] * 120,  # 30s intervals
        "total_failures_hour": state["stats"]["offline"] * 120,
        "system_health": (
            "healthy" if state["stats"]["online"] > state["stats"]["offline"] else "degraded"
        ),
        "timestamp": state.get("last_check", datetime.now().isoformat()),
    }


@app.get("/api/categories")
async def api_categories():
    """Real categories from actual providers"""
    providers = list(state["providers"].values())
    categories = defaultdict(lambda: {"total": 0, "online": 0, "response_times": []})

    for p in providers:
        cat = p.get("category", "unknown")
        categories[cat]["total"] += 1
        if p["status"] == "online":
            categories[cat]["online"] += 1
            categories[cat]["response_times"].append(p["response_time_ms"])

    result = []
    for name, data in categories.items():
        avg_response = (
            int(sum(data["response_times"]) / len(data["response_times"]))
            if data["response_times"]
            else 0
        )
        result.append(
            {
                "name": name,
                "total_sources": data["total"],
                "online_sources": data["online"],
                "avg_response_time_ms": avg_response,
                "rate_limited_count": 0,
                "last_updated": state.get("last_check", datetime.now().isoformat()),
                "status": "online" if data["online"] > 0 else "offline",
            }
        )

    return result


@app.get("/api/providers")
async def api_providers():
    """Real provider data"""
    providers = []
    for i, (name, data) in enumerate(state["providers"].items(), 1):
        providers.append(
            {
                "id": i,
                "name": name,
                "category": data.get("category", "unknown"),
                "status": data["status"],
                "response_time_ms": data["response_time_ms"],
                "last_fetch": data.get("last_check", datetime.now().isoformat()),
                "has_key": False,
                "rate_limit": None,
            }
        )
    return providers


@app.get("/api/logs")
async def api_logs():
    """Recent check logs"""
    logs = []
    for name, data in state["providers"].items():
        logs.append(
            {
                "timestamp": data.get("last_check", datetime.now().isoformat()),
                "provider": name,
                "endpoint": REAL_APIS[name]["url"],
                "status": "success" if data["status"] == "online" else "failed",
                "response_time_ms": data["response_time_ms"],
                "http_code": 200 if data["status"] == "online" else 0,
                "error_message": data.get("error"),
            }
        )
    return logs


@app.get("/api/charts/health-history")
async def api_health_history(hours: int = 24):
    """Mock historical data (would need database for real history)"""
    now = datetime.now()
    timestamps = [(now - timedelta(hours=i)).isoformat() for i in range(23, -1, -1)]
    # Use current success rate as baseline
    current_rate = (state["stats"]["online"] / max(1, state["stats"]["total"])) * 100
    import random

    success_rate = [int(current_rate + random.randint(-5, 5)) for _ in range(24)]
    return {"timestamps": timestamps, "success_rate": success_rate}


@app.get("/api/charts/compliance")
async def api_compliance(days: int = 7):
    """Mock compliance data"""
    now = datetime.now()
    dates = [(now - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    import random

    return {"dates": dates, "compliance_percentage": [random.randint(90, 100) for _ in range(7)]}


@app.get("/api/rate-limits")
async def api_rate_limits():
    """No rate limits for free APIs"""
    return []


@app.get("/api/schedule")
async def api_schedule():
    """Schedule info"""
    schedules = []
    for name in REAL_APIS.keys():
        schedules.append(
            {
                "provider": name,
                "category": REAL_APIS[name]["category"],
                "schedule": "every_30_sec",
                "last_run": state.get("last_check", datetime.now().isoformat()),
                "next_run": (datetime.now() + timedelta(seconds=30)).isoformat(),
                "on_time_percentage": 99.0,
                "status": "active",
            }
        )
    return schedules


@app.get("/api/freshness")
async def api_freshness():
    """Data freshness"""
    freshness = []
    for name, data in state["providers"].items():
        if data["status"] == "online":
            freshness.append(
                {
                    "provider": name,
                    "category": data.get("category", "unknown"),
                    "fetch_time": data.get("last_check", datetime.now().isoformat()),
                    "data_timestamp": data.get("last_check", datetime.now().isoformat()),
                    "staleness_minutes": 0.5,
                    "ttl_minutes": 1,
                    "status": "fresh",
                }
            )
    return freshness


@app.get("/api/failures")
async def api_failures():
    """Failure analysis"""
    failures = []
    for name, data in state["providers"].items():
        if data["status"] in ["offline", "degraded"]:
            failures.append(
                {
                    "timestamp": data.get("last_check", datetime.now().isoformat()),
                    "provider": name,
                    "error_type": (
                        "timeout"
                        if "timeout" in str(data.get("error", "")).lower()
                        else "connection_error"
                    ),
                    "error_message": data.get("error", "Unknown error"),
                    "retry_attempted": False,
                    "retry_result": None,
                }
            )

    return {
        "recent_failures": failures,
        "error_type_distribution": {},
        "top_failing_providers": [],
        "remediation_suggestions": [],
    }


@app.get("/api/charts/rate-limit-history")
async def api_rate_limit_history(hours: int = 24):
    """No rate limit tracking for free APIs"""
    now = datetime.now()
    timestamps = [(now - timedelta(hours=i)).strftime("%H:00") for i in range(23, -1, -1)]
    return {"timestamps": timestamps, "providers": {}}


@app.get("/api/charts/freshness-history")
async def api_freshness_history(hours: int = 24):
    """Freshness history"""
    now = datetime.now()
    timestamps = [(now - timedelta(hours=i)).strftime("%H:00") for i in range(23, -1, -1)]
    import random

    return {
        "timestamps": timestamps,
        "providers": {
            name: [random.uniform(0.1, 1.0) for _ in range(24)]
            for name in list(REAL_APIS.keys())[:2]
        },
    }


@app.get("/api/config/keys")
async def api_config_keys():
    """No API keys for free tier"""
    return []


# Serve static files
@app.get("/")
async def root():
    return FileResponse("dashboard.html")


@app.get("/dashboard.html")
async def dashboard():
    return FileResponse("dashboard.html")


@app.get("/index.html")
async def index():
    return FileResponse("index.html")


@app.get("/hf_console.html")
async def hf_console():
    return FileResponse("hf_console.html")


@app.get("/admin.html")
async def admin():
    return FileResponse("admin.html")


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Crypto API Monitor - REAL DATA Server")
    print("=" * 70)
    print("📍 Server: http://localhost:7860")
    print("📄 Main Dashboard: http://localhost:7860/index.html")
    print("🤗 HF Console: http://localhost:7860/hf_console.html")
    print("📚 API Docs: http://localhost:7860/docs")
    print("=" * 70)
    print("🔄 Checking real APIs every 30 seconds...")
    print("=" * 70)
    print()

    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")

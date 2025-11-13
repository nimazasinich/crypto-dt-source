#!/usr/bin/env python3
"""
API Server Extended - سرور FastAPI با پشتیبانی کامل از Provider Management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import uvicorn

from provider_manager import ProviderManager, RotationStrategy, Provider, ProviderPool
from log_manager import LogManager, LogLevel, LogCategory, get_log_manager
from resource_manager import ResourceManager
from backend.services.connection_manager import get_connection_manager, ConnectionManager
from backend.services.auto_discovery_service import AutoDiscoveryService
from backend.services.diagnostics_service import DiagnosticsService

# ایجاد اپلیکیشن FastAPI
app = FastAPI(
    title="Crypto Monitor Extended API",
    description="API کامل برای مانیتورینگ کریپتو با پشتیبانی از Provider Pools",
    version="3.0.0"
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
from pathlib import Path
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# مدیر ارائه‌دهندگان
manager = ProviderManager()

# مدیر لاگ‌ها
log_manager = get_log_manager()

# مدیر منابع
resource_manager = ResourceManager()

# مدیر اتصالات WebSocket
conn_manager = get_connection_manager()

# سرویس کشف خودکار منابع
auto_discovery_service = AutoDiscoveryService(resource_manager, manager)

# سرویس اشکال‌یابی و تعمیر خودکار
diagnostics_service = DiagnosticsService(resource_manager, manager, auto_discovery_service)


class StartupValidationError(RuntimeError):
    """خطای مربوط به بررسی راه‌اندازی"""
    pass


async def run_startup_validation():
    """مجموعه بررسی‌های اولیه برای اطمینان از آماده بودن سرویس"""
    issues: List[str] = []

    required_files = [
        Path("providers_config_extended.json"),
        Path("providers_config_ultimate.json"),
        Path("crypto_resources_unified_2025-11-11.json"),
    ]
    for file_path in required_files:
        if not file_path.exists():
            issues.append(f"فایل ضروری یافت نشد: {file_path}")

    required_dirs = [Path("data"), Path("data/exports"), Path("logs")]
    for directory in required_dirs:
        if not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                issues.append(f"امکان ساخت دایرکتوری {directory} وجود ندارد: {exc}")

    try:
        stats = resource_manager.get_statistics()
        if stats.get("total_providers", 0) == 0:
            issues.append("هیچ ارائه‌دهنده‌ای در پیکربندی منابع یافت نشد.")
    except Exception as exc:
        issues.append(f"دسترسی به ResourceManager با خطا مواجه شد: {exc}")

    if not manager.providers:
        issues.append("هیچ ارائه‌دهنده‌ای در ProviderManager بارگذاری نشده است.")
    else:
        sample_providers = list(manager.providers.values())[:5]
        try:
            health_results = await asyncio.gather(*(manager.health_check(provider) for provider in sample_providers))
            success_count = sum(1 for result in health_results if result)
            if success_count == 0:
                issues.append("هیچ ارائه‌دهنده‌ای در تست سلامت اولیه موفق نبود.")
        except Exception as exc:
            issues.append(f"اجرای تست سلامت اولیه با خطا مواجه شد: {exc}")

    if manager.session is None:
        await manager.init_session()

    critical_endpoints = [
        ("CoinGecko", "https://api.coingecko.com/api/v3/ping"),
        ("Etherscan", "https://api.etherscan.io/api?module=stats&action=ethsupply"),
        ("Binance", "https://api.binance.com/api/v3/ping"),
    ]
    failures = 0
    for name, url in critical_endpoints:
        try:
            async with manager.session.get(url, timeout=10) as response:
                if response.status >= 500:
                    issues.append(f"پاسخ نامعتبر از سرویس {name}: status={response.status}")
                    failures += 1
        except Exception as exc:
            issues.append(f"عدم دسترسی به سرویس {name}: {exc}")
            failures += 1
    if failures == len(critical_endpoints):
        issues.append("اتصال به سرویس‌های کلیدی برقرار نشد. اتصال اینترنت را بررسی کنید.")

    if issues:
        # Log issues but don't fail startup (allow degraded mode)
        for issue in issues:
            log_manager.add_log(
                LogLevel.WARNING,
                LogCategory.SYSTEM,
                "Startup validation issue (non-critical)",
                extra_data={"detail": issue},
            )
        print(f"⚠️  Startup validation found {len(issues)} issues (running in degraded mode)")
        # Only raise error if ALL critical services are down
        critical_failures = [i for i in issues if "هیچ ارائه‌دهنده" in i or "فایل ضروری" in i]
        if len(critical_failures) >= 2:
            raise StartupValidationError("Critical startup validation failed. جزئیات در لاگ‌ها موجود است.")

    log_manager.add_log(
        LogLevel.INFO,
        LogCategory.SYSTEM,
        "Startup validation passed",
        extra_data={"checked_providers": min(len(manager.providers), 5)},
    )


# ===== Pydantic Models =====

class PoolCreateRequest(BaseModel):
    name: str
    category: str
    rotation_strategy: str
    description: Optional[str] = None


class PoolMemberRequest(BaseModel):
    provider_id: str
    priority: int = 5
    weight: int = 50


class RotateRequest(BaseModel):
    reason: str = "manual"


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    providers_count: int
    online_count: int


# ===== Startup/Shutdown Events =====

@app.on_event("startup")
async def startup_event():
    """رویداد شروع سرور"""
    print("🚀 راه‌اندازی سرور...")
    await manager.init_session()
    await run_startup_validation()
    
    # ثبت لاگ شروع
    log_manager.add_log(
        LogLevel.INFO,
        LogCategory.SYSTEM,
        "Server started",
        extra_data={"version": "3.0.0"}
    )
    
    # شروع بررسی سلامت دوره‌ای
    asyncio.create_task(periodic_health_check())
    await auto_discovery_service.start()
    
    # شروع heartbeat برای WebSocket
    asyncio.create_task(websocket_heartbeat())
    
    print("✅ سرور آماده است")


@app.on_event("shutdown")
async def shutdown_event():
    """رویداد خاموش شدن سرور"""
    print("🛑 خاموش‌سازی سرور...")
    await auto_discovery_service.stop()
    await manager.close_session()
    print("✅ سرور خاموش شد")


# ===== Background Tasks =====

async def periodic_health_check():
    """بررسی سلامت دوره‌ای هر ۵ دقیقه"""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            await manager.health_check_all(silent=True)  # بدون چاپ لاگ
            
            # ارسال به‌روزرسانی آمار به کلاینت‌های متصل
            stats = manager.get_all_stats()
            await conn_manager.broadcast({
                'type': 'provider_stats',
                'data': stats,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"❌ خطا در بررسی سلامت دوره‌ای: {e}")


async def websocket_heartbeat():
    """ارسال heartbeat هر ۱۰ ثانیه"""
    while True:
        try:
            await asyncio.sleep(10)
            await conn_manager.heartbeat()
        except Exception as e:
            print(f"❌ خطا در heartbeat: {e}")


# ===== Root Endpoints =====

@app.get("/")
async def root():
    """صفحه اصلی"""
    return FileResponse("unified_dashboard.html")


@app.get("/test_websocket.html")
async def test_websocket():
    """صفحه تست WebSocket"""
    return FileResponse("test_websocket.html")


@app.get("/test_websocket_dashboard.html")
async def test_websocket_dashboard():
    """صفحه داشبورد تست WebSocket"""
    return FileResponse("test_websocket_dashboard.html")


@app.get("/health")
async def health():
    """بررسی سلامت سرور"""
    stats = manager.get_all_stats()
    conn_stats = conn_manager.get_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "providers_count": stats['summary']['total_providers'],
        "online_count": stats['summary']['online'],
        "connected_clients": conn_stats['active_connections'],
        "total_sessions": conn_stats['total_sessions']
    }


# ===== Provider Endpoints =====

@app.get("/api/providers")
async def get_all_providers():
    """دریافت لیست همه ارائه‌دهندگان"""
    providers = []
    for provider_id, provider in manager.providers.items():
        providers.append({
            "provider_id": provider_id,
            "name": provider.name,
            "category": provider.category,
            "status": provider.status.value,
            "success_rate": provider.success_rate,
            "total_requests": provider.total_requests,
            "avg_response_time": provider.avg_response_time,
            "is_available": provider.is_available,
            "priority": provider.priority,
            "weight": provider.weight,
            "requires_auth": provider.requires_auth,
            "last_check": provider.last_check.isoformat() if provider.last_check else None,
            "last_error": provider.last_error
        })
    
    return {"providers": providers, "total": len(providers)}


@app.get("/api/providers/{provider_id}")
async def get_provider(provider_id: str):
    """دریافت اطلاعات یک ارائه‌دهنده"""
    provider = manager.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return {
        "provider_id": provider_id,
        "name": provider.name,
        "category": provider.category,
        "base_url": provider.base_url,
        "endpoints": provider.endpoints,
        "status": provider.status.value,
        "success_rate": provider.success_rate,
        "total_requests": provider.total_requests,
        "successful_requests": provider.successful_requests,
        "failed_requests": provider.failed_requests,
        "avg_response_time": provider.avg_response_time,
        "is_available": provider.is_available,
        "priority": provider.priority,
        "weight": provider.weight,
        "requires_auth": provider.requires_auth,
        "consecutive_failures": provider.consecutive_failures,
        "circuit_breaker_open": provider.circuit_breaker_open,
        "last_check": provider.last_check.isoformat() if provider.last_check else None,
        "last_error": provider.last_error
    }


@app.post("/api/providers/{provider_id}/health-check")
async def check_provider_health(provider_id: str):
    """بررسی سلامت یک ارائه‌دهنده"""
    provider = manager.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    is_healthy = await manager.health_check(provider)
    
    return {
        "provider_id": provider_id,
        "name": provider.name,
        "is_healthy": is_healthy,
        "status": provider.status.value,
        "response_time": provider.avg_response_time,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/providers/category/{category}")
async def get_providers_by_category(category: str):
    """دریافت ارائه‌دهندگان بر اساس دسته‌بندی"""
    providers = [
        {
            "provider_id": pid,
            "name": p.name,
            "status": p.status.value,
            "is_available": p.is_available,
            "success_rate": p.success_rate
        }
        for pid, p in manager.providers.items()
        if p.category == category
    ]
    
    return {"category": category, "providers": providers, "count": len(providers)}


# ===== Pool Endpoints =====

@app.get("/api/pools")
async def get_all_pools():
    """دریافت لیست همه Pool‌ها"""
    pools = []
    for pool_id, pool in manager.pools.items():
        current_provider = None
        if pool.providers:
            next_p = pool.get_next_provider()
            if next_p:
                current_provider = {
                    "provider_id": next_p.provider_id,
                    "name": next_p.name,
                    "status": next_p.status.value
                }
        
        pools.append({
            "pool_id": pool_id,
            "pool_name": pool.pool_name,
            "category": pool.category,
            "rotation_strategy": pool.rotation_strategy.value,
            "enabled": pool.enabled,
            "total_rotations": pool.total_rotations,
            "total_providers": len(pool.providers),
            "available_providers": len([p for p in pool.providers if p.is_available]),
            "current_provider": current_provider,
            "members": [
                {
                    "provider_id": p.provider_id,
                    "provider_name": p.name,
                    "status": p.status.value,
                    "success_rate": p.success_rate,
                    "use_count": p.total_requests,
                    "priority": p.priority,
                    "weight": p.weight,
                    "rate_limit": {
                        "usage": p.rate_limit.current_usage if p.rate_limit else 0,
                        "limit": p.rate_limit.requests_per_minute or p.rate_limit.requests_per_day or 100 if p.rate_limit else 100,
                        "percentage": min(100, (p.rate_limit.current_usage / (p.rate_limit.requests_per_minute or 100) * 100)) if p.rate_limit and p.rate_limit.requests_per_minute else 0
                    }
                }
                for p in pool.providers
            ]
        })
    
    return {"pools": pools, "total": len(pools)}


@app.get("/api/pools/{pool_id}")
async def get_pool(pool_id: str):
    """دریافت اطلاعات یک Pool"""
    pool = manager.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    return pool.get_stats()


@app.post("/api/pools")
async def create_pool(request: PoolCreateRequest):
    """ایجاد Pool جدید"""
    pool_id = request.name.lower().replace(' ', '_')
    
    if pool_id in manager.pools:
        raise HTTPException(status_code=400, detail="Pool already exists")
    
    try:
        rotation_strategy = RotationStrategy(request.rotation_strategy)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rotation strategy")
    
    pool = ProviderPool(
        pool_id=pool_id,
        pool_name=request.name,
        category=request.category,
        rotation_strategy=rotation_strategy
    )
    
    manager.pools[pool_id] = pool
    
    return {
        "message": "Pool created successfully",
        "pool_id": pool_id,
        "pool": pool.get_stats()
    }


@app.delete("/api/pools/{pool_id}")
async def delete_pool(pool_id: str):
    """حذف Pool"""
    if pool_id not in manager.pools:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    del manager.pools[pool_id]
    
    return {"message": "Pool deleted successfully", "pool_id": pool_id}


@app.post("/api/pools/{pool_id}/members")
async def add_member_to_pool(pool_id: str, request: PoolMemberRequest):
    """افزودن عضو به Pool"""
    pool = manager.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    provider = manager.get_provider(request.provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # تنظیم اولویت و وزن
    provider.priority = request.priority
    provider.weight = request.weight
    
    pool.add_provider(provider)
    
    return {
        "message": "Provider added to pool successfully",
        "pool_id": pool_id,
        "provider_id": request.provider_id
    }


@app.delete("/api/pools/{pool_id}/members/{provider_id}")
async def remove_member_from_pool(pool_id: str, provider_id: str):
    """حذف عضو از Pool"""
    pool = manager.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    pool.remove_provider(provider_id)
    
    return {
        "message": "Provider removed from pool successfully",
        "pool_id": pool_id,
        "provider_id": provider_id
    }


@app.post("/api/pools/{pool_id}/rotate")
async def rotate_pool(pool_id: str, request: RotateRequest):
    """چرخش دستی Pool"""
    pool = manager.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    provider = pool.get_next_provider()
    if not provider:
        raise HTTPException(status_code=503, detail="No available provider in pool")
    
    return {
        "message": "Pool rotated successfully",
        "pool_id": pool_id,
        "provider_id": provider.provider_id,
        "provider_name": provider.name,
        "reason": request.reason,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/pools/history")
async def get_rotation_history(limit: int = 20):
    """تاریخچه چرخش‌ها"""
    # این endpoint نیاز به یک سیستم لاگ دارد که می‌توان بعداً اضافه کرد
    # فعلاً یک نمونه ساده برمی‌گردانیم
    history = []
    for pool_id, pool in manager.pools.items():
        if pool.total_rotations > 0:
            history.append({
                "pool_id": pool_id,
                "pool_name": pool.pool_name,
                "total_rotations": pool.total_rotations,
                "provider_name": pool.providers[0].name if pool.providers else "N/A",
                "timestamp": datetime.now().isoformat(),
                "reason": "automatic"
            })
    
    return {"history": history[:limit], "total": len(history)}


# ===== Status & Statistics Endpoints =====

@app.get("/api/status")
async def get_status():
    """وضعیت کلی سیستم"""
    stats = manager.get_all_stats()
    summary = stats['summary']
    
    # محاسبه میانگین زمان پاسخ
    response_times = [p.avg_response_time for p in manager.providers.values() if p.avg_response_time > 0]
    avg_response = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        "status": "operational" if summary['online'] > summary['offline'] else "degraded",
        "timestamp": datetime.now().isoformat(),
        "total_providers": summary['total_providers'],
        "online": summary['online'],
        "offline": summary['offline'],
        "degraded": summary['degraded'],
        "avg_response_time_ms": round(avg_response, 2),
        "total_requests": summary['total_requests'],
        "successful_requests": summary['successful_requests'],
        "success_rate": round(summary['overall_success_rate'], 2)
    }


@app.get("/api/stats")
async def get_statistics():
    """آمار کامل سیستم"""
    return manager.get_all_stats()


@app.get("/api/stats/export")
async def export_stats():
    """صادرکردن آمار"""
    filepath = f"stats_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    manager.export_stats(filepath)
    return {
        "message": "Statistics exported successfully",
        "filepath": filepath,
        "timestamp": datetime.now().isoformat()
    }


# ===== Mock Data Endpoints (برای داشبورد) =====

@app.get("/api/market")
async def get_market_data():
    """داده‌های بازار (Mock)"""
    return {
        "cryptocurrencies": [
            {
                "rank": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "price": 43250.50,
                "change_24h": 2.35,
                "market_cap": 845000000000,
                "volume_24h": 28500000000,
                "image": "https://assets.coingecko.com/coins/images/1/small/bitcoin.png"
            },
            {
                "rank": 2,
                "name": "Ethereum",
                "symbol": "ETH",
                "price": 2280.75,
                "change_24h": -1.20,
                "market_cap": 274000000000,
                "volume_24h": 15200000000,
                "image": "https://assets.coingecko.com/coins/images/279/small/ethereum.png"
            }
        ],
        "global": {
            "btc_dominance": 52.3,
            "eth_dominance": 17.8
        }
    }


@app.get("/api/stats")
async def get_market_stats():
    """آمار بازار (Mock)"""
    return {
        "market": {
            "total_market_cap": 1650000000000,
            "total_volume": 85000000000,
            "btc_dominance": 52.3
        }
    }


@app.get("/api/sentiment")
async def get_sentiment():
    """احساسات بازار (Mock)"""
    return {
        "fear_greed_index": {
            "value": 62,
            "classification": "Greed"
        }
    }


@app.get("/api/trending")
async def get_trending():
    """ترندینگ (Mock)"""
    return {
        "trending": [
            {"name": "Solana", "symbol": "SOL", "thumb": ""},
            {"name": "Cardano", "symbol": "ADA", "thumb": ""}
        ]
    }


@app.get("/api/defi")
async def get_defi():
    """داده‌های DeFi (Mock)"""
    return {
        "total_tvl": 48500000000,
        "protocols": [
            {"name": "Lido", "chain": "Ethereum", "tvl": 18500000000, "change_24h": 1.5},
            {"name": "Aave", "chain": "Multi-chain", "tvl": 12300000000, "change_24h": -0.8}
        ]
    }


# ===== HuggingFace Endpoints =====

@app.get("/api/hf/health")
async def hf_health():
    """سلامت HuggingFace"""
    return {
        "status": "operational",
        "models_available": 4,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/hf/run-sentiment")
async def run_sentiment(data: Dict[str, Any]):
    """تحلیل احساسات (Mock)"""
    texts = data.get("texts", [])
    
    # شبیه‌سازی نتیجه
    results = []
    for text in texts:
        sentiment = "positive" if "bullish" in text.lower() or "strong" in text.lower() else "negative" if "weak" in text.lower() else "neutral"
        score = 0.8 if sentiment == "positive" else -0.6 if sentiment == "negative" else 0.1
        results.append({"text": text, "sentiment": sentiment, "score": score})
    
    vote = sum(r["score"] for r in results) / len(results) if results else 0
    
    return {
        "vote": vote,
        "results": results,
        "count": len(results)
    }


# ===== Log Management Endpoints =====

@app.get("/api/logs")
async def get_logs(
    level: Optional[str] = None,
    category: Optional[str] = None,
    provider_id: Optional[str] = None,
    pool_id: Optional[str] = None,
    limit: int = 100,
    search: Optional[str] = None
):
    """دریافت لاگ‌ها با فیلتر"""
    log_level = LogLevel(level) if level else None
    log_category = LogCategory(category) if category else None
    
    if search:
        logs = log_manager.search_logs(search, limit)
    else:
        logs = log_manager.filter_logs(
            level=log_level,
            category=log_category,
            provider_id=provider_id,
            pool_id=pool_id
        )[-limit:]
    
    return {
        "logs": [log.to_dict() for log in logs],
        "total": len(logs)
    }


@app.get("/api/logs/recent")
async def get_recent_logs(limit: int = 50):
    """دریافت آخرین لاگ‌ها"""
    logs = log_manager.get_recent_logs(limit)
    return {
        "logs": [log.to_dict() for log in logs],
        "total": len(logs)
    }


@app.get("/api/logs/errors")
async def get_error_logs(limit: int = 50):
    """دریافت لاگ‌های خطا"""
    logs = log_manager.get_error_logs(limit)
    return {
        "logs": [log.to_dict() for log in logs],
        "total": len(logs)
    }


@app.get("/api/logs/stats")
async def get_log_stats():
    """آمار لاگ‌ها"""
    return log_manager.get_statistics()


@app.get("/api/logs/export/json")
async def export_logs_json(
    level: Optional[str] = None,
    category: Optional[str] = None,
    provider_id: Optional[str] = None
):
    """صادرکردن لاگ‌ها به JSON"""
    log_level = LogLevel(level) if level else None
    log_category = LogCategory(category) if category else None
    
    filtered = log_manager.filter_logs(
        level=log_level,
        category=log_category,
        provider_id=provider_id
    )
    
    filepath = f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_manager.export_to_json(filepath, filtered=filtered)
    
    return {
        "message": "Logs exported successfully",
        "filepath": filepath,
        "count": len(filtered)
    }


@app.get("/api/logs/export/csv")
async def export_logs_csv(
    level: Optional[str] = None,
    category: Optional[str] = None
):
    """صادرکردن لاگ‌ها به CSV"""
    log_level = LogLevel(level) if level else None
    log_category = LogCategory(category) if category else None
    
    filtered = log_manager.filter_logs(
        level=log_level,
        category=log_category
    )
    
    filepath = f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    log_manager.export_to_csv(filepath)
    
    return {
        "message": "Logs exported successfully",
        "filepath": filepath,
        "count": len(filtered)
    }


@app.delete("/api/logs")
async def clear_logs():
    """پاک کردن همه لاگ‌ها"""
    log_manager.clear_logs()
    return {"message": "All logs cleared"}


# ===== Resource Management Endpoints =====

@app.get("/api/resources")
async def get_resources():
    """دریافت همه منابع"""
    return {
        "providers": resource_manager.get_all_providers(),
        "statistics": resource_manager.get_statistics()
    }


@app.get("/api/resources/category/{category}")
async def get_resources_by_category(category: str):
    """دریافت منابع بر اساس دسته"""
    providers = resource_manager.get_providers_by_category(category)
    return {
        "category": category,
        "providers": providers,
        "count": len(providers)
    }


@app.post("/api/resources/import/json")
async def import_resources_json(file_path: str, merge: bool = True):
    """وارد کردن منابع از JSON"""
    success = resource_manager.import_from_json(file_path, merge=merge)
    if success:
        resource_manager.save_resources()
        return {"message": "Resources imported successfully", "merged": merge}
    else:
        raise HTTPException(status_code=400, detail="Failed to import resources")


@app.get("/api/resources/export/json")
async def export_resources_json():
    """صادرکردن منابع به JSON"""
    filepath = f"resources_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    resource_manager.export_to_json(filepath)
    return {
        "message": "Resources exported successfully",
        "filepath": filepath
    }


@app.get("/api/resources/export/csv")
async def export_resources_csv():
    """صادرکردن منابع به CSV"""
    filepath = f"resources_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    resource_manager.export_to_csv(filepath)
    return {
        "message": "Resources exported successfully",
        "filepath": filepath
    }


@app.post("/api/resources/backup")
async def backup_resources():
    """پشتیبان‌گیری از منابع"""
    backup_file = resource_manager.backup()
    return {
        "message": "Backup created successfully",
        "filepath": backup_file
    }


@app.post("/api/resources/provider")
async def add_provider(provider_data: Dict[str, Any]):
    """افزودن provider جدید"""
    is_valid, message = resource_manager.validate_provider(provider_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    provider_id = resource_manager.add_provider(provider_data)
    resource_manager.save_resources()
    
    log_manager.add_log(
        LogLevel.INFO,
        LogCategory.PROVIDER,
        f"Provider added: {provider_id}",
        provider_id=provider_id
    )
    
    return {
        "message": "Provider added successfully",
        "provider_id": provider_id
    }


@app.delete("/api/resources/provider/{provider_id}")
async def remove_provider(provider_id: str):
    """حذف provider"""
    success = resource_manager.remove_provider(provider_id)
    if success:
        resource_manager.save_resources()
        log_manager.add_log(
            LogLevel.INFO,
            LogCategory.PROVIDER,
            f"Provider removed: {provider_id}",
            provider_id=provider_id
        )
        return {"message": "Provider removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Provider not found")


@app.get("/api/resources/discovery/status")
async def get_auto_discovery_status():
    """وضعیت سرویس کشف خودکار منابع"""
    return auto_discovery_service.get_status()


@app.post("/api/resources/discovery/run")
async def run_auto_discovery():
    """اجرای دستی کشف منابع جدید"""
    result = await auto_discovery_service.trigger_manual_discovery()
    if result.get("status") == "disabled":
        raise HTTPException(status_code=503, detail="Auto discovery service is disabled.")
    return result


# ===== WebSocket & Session Endpoints =====

from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint برای ارتباط بلادرنگ"""
    session_id = None
    try:
        # اتصال کلاینت
        session_id = await conn_manager.connect(
            websocket,
            client_type='browser',
            metadata={'source': 'unified_dashboard'}
        )
        
        # ارسال پیام خوش‌آمدگویی
        await conn_manager.send_personal_message({
            'type': 'welcome',
            'session_id': session_id,
            'message': 'به سیستم مانیتورینگ کریپتو خوش آمدید',
            'timestamp': datetime.now().isoformat()
        }, session_id)
        
        # دریافت و پردازش پیام‌ها
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Subscribe به گروه خاص
                group = data.get('group', 'all')
                conn_manager.subscribe(session_id, group)
                await conn_manager.send_personal_message({
                    'type': 'subscribed',
                    'group': group
                }, session_id)
            
            elif message_type == 'unsubscribe':
                # Unsubscribe از گروه
                group = data.get('group')
                conn_manager.unsubscribe(session_id, group)
                await conn_manager.send_personal_message({
                    'type': 'unsubscribed',
                    'group': group
                }, session_id)
            
            elif message_type == 'get_stats':
                # درخواست آمار فوری
                stats = manager.get_all_stats()
                conn_stats = conn_manager.get_stats()
                
                # ارسال آمار provider
                await conn_manager.send_personal_message({
                    'type': 'stats_response',
                    'data': stats
                }, session_id)
                
                # ارسال آمار اتصالات
                await conn_manager.send_personal_message({
                    'type': 'stats_update',
                    'data': conn_stats
                }, session_id)
            
            elif message_type == 'ping':
                # پاسخ به ping
                await conn_manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }, session_id)
            
            conn_manager.total_messages_received += 1
            
    except WebSocketDisconnect:
        if session_id:
            conn_manager.disconnect(session_id)
    except Exception as e:
        print(f"❌ خطا در WebSocket: {e}")
        if session_id:
            conn_manager.disconnect(session_id)


@app.get("/api/sessions")
async def get_sessions():
    """دریافت لیست session‌های فعال"""
    return {
        "sessions": conn_manager.get_sessions(),
        "stats": conn_manager.get_stats()
    }


@app.get("/api/sessions/stats")
async def get_session_stats():
    """دریافت آمار اتصالات"""
    return conn_manager.get_stats()


@app.post("/api/broadcast")
async def broadcast_message(message: Dict[str, Any], group: str = 'all'):
    """ارسال پیام به همه کلاینت‌ها"""
    await conn_manager.broadcast(message, group)
    return {"status": "sent", "group": group}


# ===== Reports & Diagnostics Endpoints =====

@app.get("/api/reports/discovery")
async def get_discovery_report():
    """گزارش عملکرد Auto-Discovery Service"""
    status = auto_discovery_service.get_status()
    
    # محاسبه زمان اجرای بعدی
    next_run_estimate = None
    if status.get("enabled") and status.get("last_run"):
        last_run = status.get("last_run")
        interval_seconds = status.get("interval_seconds", 43200)  # پیش‌فرض 12 ساعت
        
        if last_run and "finished_at" in last_run:
            try:
                finished_at = datetime.fromisoformat(last_run["finished_at"].replace('Z', '+00:00'))
                if finished_at.tzinfo is None:
                    finished_at = finished_at.replace(tzinfo=datetime.now().astimezone().tzinfo)
                next_run = finished_at + timedelta(seconds=interval_seconds)
                next_run_estimate = next_run.isoformat()
            except Exception:
                pass
    
    return {
        "service_status": status,
        "enabled": status.get("enabled", False),
        "model": status.get("model"),
        "interval_seconds": status.get("interval_seconds"),
        "last_run": status.get("last_run"),
        "next_run_estimate": next_run_estimate,
    }


@app.get("/api/reports/models")
async def get_models_report():
    """گزارش وضعیت مدل‌های HuggingFace"""
    models_status = []
    
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        
        models_to_check = [
            'HuggingFaceH4/zephyr-7b-beta',
            'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'BAAI/bge-m3',
        ]
        
        for model_id in models_to_check:
            try:
                model_info = api.model_info(model_id, timeout=5.0)
                models_status.append({
                    "model_id": model_id,
                    "status": "available",
                    "downloads": getattr(model_info, 'downloads', None),
                    "likes": getattr(model_info, 'likes', None),
                    "pipeline_tag": getattr(model_info, 'pipeline_tag', None),
                    "last_updated": getattr(model_info, 'last_modified', None),
                })
            except Exception as e:
                models_status.append({
                    "model_id": model_id,
                    "status": "error",
                    "error": str(e),
                })
    except ImportError:
        return {
            "error": "huggingface_hub not installed",
            "models_status": [],
        }
    
    return {
        "total_models": len(models_status),
        "available": sum(1 for m in models_status if m.get("status") == "available"),
        "errors": sum(1 for m in models_status if m.get("status") == "error"),
        "models": models_status,
    }


@app.post("/api/diagnostics/run")
async def run_diagnostics(auto_fix: bool = False):
    """اجرای اشکال‌یابی خودکار"""
    try:
        report = await diagnostics_service.run_full_diagnostics(auto_fix=auto_fix)
        
        # تبدیل به dict برای JSON
        report_dict = {
            "timestamp": report.timestamp,
            "total_issues": report.total_issues,
            "critical_issues": report.critical_issues,
            "warnings": report.warnings,
            "info_issues": report.info_issues,
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "title": issue.title,
                    "description": issue.description,
                    "fixable": issue.fixable,
                    "fix_action": issue.fix_action,
                    "auto_fixed": issue.auto_fixed,
                    "timestamp": issue.timestamp,
                }
                for issue in report.issues
            ],
            "fixed_issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "title": issue.title,
                    "description": issue.description,
                    "fixable": issue.fixable,
                    "fix_action": issue.fix_action,
                    "auto_fixed": issue.auto_fixed,
                    "timestamp": issue.timestamp,
                }
                for issue in report.fixed_issues
            ],
            "system_info": report.system_info,
            "duration_ms": report.duration_ms,
        }
        
        return report_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در اجرای اشکال‌یابی: {str(e)}")


@app.get("/api/diagnostics/last")
async def get_last_diagnostics():
    """دریافت آخرین گزارش اشکال‌یابی"""
    report = diagnostics_service.get_last_report()
    if report:
        return report
    return {"message": "هیچ گزارشی موجود نیست"}


# ===== Main =====

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   🚀 Crypto Monitor Extended API Server                  ║
    ║   Version: 2.0.0                                          ║
    ║   با پشتیبانی کامل از Provider Management & Pools       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


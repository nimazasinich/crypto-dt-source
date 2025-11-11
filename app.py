"""
Crypto API Monitoring System - Main Application
Production-ready FastAPI application with comprehensive monitoring and WebSocket support
"""

import asyncio
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import API modules
from api.endpoints import router as api_router
from api.websocket import router as websocket_router, manager as ws_manager
from api.pool_endpoints import router as pool_router

# Import new WebSocket service routers
from api.ws_unified_router import router as ws_unified_router, start_all_websocket_streams
from api.ws_data_services import router as ws_data_router
from api.ws_monitoring_services import router as ws_monitoring_router
from api.ws_integration_services import router as ws_integration_router

# Import monitoring and database modules
from monitoring.scheduler import task_scheduler
from monitoring.rate_limiter import rate_limiter
from database.db_manager import db_manager
from config import config
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("main", level="INFO")

# Import HF router (optional, graceful fallback)
try:
    from backend.routers import hf_connect
    HF_ROUTER_AVAILABLE = True
except Exception as e:
    logger.warning(f"HF router not available: {e}")
    HF_ROUTER_AVAILABLE = False


# ============================================================================
# Lifespan Context Manager for Startup/Shutdown Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown

    Handles:
    - Database initialization
    - Scheduler startup
    - Rate limiter configuration
    - WebSocket background tasks
    - Graceful shutdown
    """
    logger.info("=" * 80)
    logger.info("Starting Crypto API Monitoring System")
    logger.info("=" * 80)

    try:
        # ===== STARTUP SEQUENCE =====

        # 1. Initialize database
        logger.info("Initializing database...")
        db_manager.init_database()

        # Verify database health
        db_health = db_manager.health_check()
        if db_health.get('status') == 'healthy':
            logger.info(f"Database initialized successfully: {db_health.get('database_path')}")
        else:
            logger.error(f"Database health check failed: {db_health}")

        # 2. Configure rate limiters for all providers
        logger.info("Configuring rate limiters...")
        providers = config.get_all_providers()

        for provider in providers:
            if provider.rate_limit_type and provider.rate_limit_value:
                rate_limiter.configure_limit(
                    provider=provider.name,
                    limit_type=provider.rate_limit_type,
                    limit_value=provider.rate_limit_value
                )
                logger.info(
                    f"Configured rate limit for {provider.name}: "
                    f"{provider.rate_limit_value} {provider.rate_limit_type}"
                )

        logger.info(f"Configured rate limiters for {len(providers)} providers")

        # 3. Populate database with provider configurations
        logger.info("Populating database with provider configurations...")

        for provider in providers:
            # Check if provider already exists in database
            db_provider = db_manager.get_provider(name=provider.name)

            if not db_provider:
                # Create new provider in database
                db_provider = db_manager.create_provider(
                    name=provider.name,
                    category=provider.category,
                    endpoint_url=provider.endpoint_url,
                    requires_key=provider.requires_key,
                    api_key_masked=provider._mask_key() if provider.api_key else None,
                    rate_limit_type=provider.rate_limit_type,
                    rate_limit_value=provider.rate_limit_value,
                    timeout_ms=provider.timeout_ms,
                    priority_tier=provider.priority_tier
                )

                if db_provider:
                    logger.info(f"Added provider to database: {provider.name}")

                    # Create schedule configuration for the provider
                    # Set interval based on category
                    interval_map = {
                        'market_data': 'every_1_min',
                        'blockchain_explorers': 'every_5_min',
                        'news': 'every_10_min',
                        'sentiment': 'every_15_min',
                        'onchain_analytics': 'every_5_min',
                        'rpc_nodes': 'every_5_min',
                        'cors_proxies': 'every_30_min'
                    }

                    schedule_interval = interval_map.get(provider.category, 'every_5_min')

                    schedule_config = db_manager.create_schedule_config(
                        provider_id=db_provider.id,
                        schedule_interval=schedule_interval,
                        enabled=True
                    )

                    if schedule_config:
                        logger.info(
                            f"Created schedule config for {provider.name}: {schedule_interval}"
                        )

        # 4. Start HF registry background refresh (if available)
        if HF_ROUTER_AVAILABLE:
            try:
                from backend.services.hf_registry import periodic_refresh
                logger.info("Starting HF registry background refresh...")
                asyncio.create_task(periodic_refresh())
                logger.info("HF registry background refresh started")
            except Exception as e:
                logger.warning(f"Could not start HF background refresh: {e}")

        # 5. Start WebSocket background tasks
        logger.info("Starting WebSocket background tasks...")
        await ws_manager.start_background_tasks()
        logger.info("WebSocket background tasks started")

        # 5.1 Start new WebSocket service streams
        logger.info("Starting WebSocket service streams...")
        asyncio.create_task(start_all_websocket_streams())
        logger.info("WebSocket service streams started")

        # 6. Start task scheduler
        logger.info("Starting task scheduler...")
        task_scheduler.start()
        logger.info("Task scheduler started successfully")

        # Log startup summary
        logger.info("=" * 80)
        logger.info("Crypto API Monitoring System started successfully")
        logger.info(f"Total providers configured: {len(providers)}")
        logger.info(f"Database: {db_health.get('database_path')}")
        logger.info(f"Scheduler running: {task_scheduler.is_running()}")
        logger.info(f"WebSocket manager active: {ws_manager._is_running}")
        logger.info("=" * 80)

        yield  # Application runs here

        # ===== SHUTDOWN SEQUENCE =====

        logger.info("=" * 80)
        logger.info("Shutting down Crypto API Monitoring System...")
        logger.info("=" * 80)

        # 1. Stop task scheduler
        logger.info("Stopping task scheduler...")
        task_scheduler.stop()
        logger.info("Task scheduler stopped")

        # 2. Stop WebSocket background tasks
        logger.info("Stopping WebSocket background tasks...")
        await ws_manager.stop_background_tasks()
        logger.info("WebSocket background tasks stopped")

        # 3. Close all WebSocket connections
        logger.info("Closing WebSocket connections...")
        await ws_manager.close_all_connections()
        logger.info("WebSocket connections closed")

        logger.info("=" * 80)
        logger.info("Crypto API Monitoring System shut down successfully")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error during application lifecycle: {e}", exc_info=True)
        raise


# ============================================================================
# Create FastAPI Application
# ============================================================================

app = FastAPI(
    title="Crypto API Monitoring System",
    description="""
    Comprehensive cryptocurrency API monitoring system with real-time WebSocket updates.

    Features:
    - Multi-provider API monitoring
    - Real-time WebSocket streaming for all services
    - Data collection APIs: Market data, News, Sentiment, Whale tracking, RPC nodes, On-chain analytics
    - Monitoring APIs: Health checks, Pool management, Scheduler status
    - Integration APIs: HuggingFace AI/ML, Persistence services
    - Subscription-based message routing
    - Rate limit tracking
    - Automated health checks
    - Scheduled data collection
    - Failure detection and alerts
    - Historical analytics

    WebSocket Endpoints:
    - Master: /ws, /ws/master, /ws/all
    - Data Collection: /ws/data, /ws/market_data, /ws/news, /ws/sentiment, /ws/whale_tracking
    - Monitoring: /ws/monitoring, /ws/health, /ws/pool_status, /ws/scheduler_status
    - Integration: /ws/integration, /ws/huggingface, /ws/ai, /ws/persistence
    - Legacy: /ws/live
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# CORS Middleware Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions

    Args:
        request: Request object
        exc: Exception that was raised

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# Include Routers
# ============================================================================

# Include API endpoints router
app.include_router(
    api_router,
    prefix="/api",
    tags=["API"]
)

# Include WebSocket router
app.include_router(
    websocket_router,
    tags=["WebSocket"]
)

# Include Pool Management router
app.include_router(
    pool_router,
    tags=["Pool Management"]
)

# Include HF router (if available)
if HF_ROUTER_AVAILABLE:
    try:
        app.include_router(
            hf_connect.router,
            tags=["HuggingFace"]
        )
        logger.info("HF router included successfully")
    except Exception as e:
        logger.warning(f"Could not include HF router: {e}")

# Include new WebSocket service routers
app.include_router(
    ws_unified_router,
    tags=["WebSocket Services"]
)

app.include_router(
    ws_data_router,
    tags=["WebSocket - Data Collection"]
)

app.include_router(
    ws_monitoring_router,
    tags=["WebSocket - Monitoring"]
)

app.include_router(
    ws_integration_router,
    tags=["WebSocket - Integration"]
)

logger.info("All WebSocket service routers included successfully")


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information and available endpoints

    Returns:
        API information and endpoint listing
    """
    return {
        "name": "Crypto API Monitoring System",
        "version": "2.0.0",
        "description": "Comprehensive cryptocurrency API monitoring with real-time updates",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            },
            "health": "/health",
            "api": {
                "providers": "/api/providers",
                "status": "/api/status",
                "rate_limits": "/api/rate-limits",
                "logs": "/api/logs/{log_type}",
                "alerts": "/api/alerts",
                "scheduler": "/api/scheduler/status",
                "database": "/api/database/stats",
                "analytics": "/api/analytics/failures"
            },
            "websocket": {
                "master": {
                    "default": "/ws",
                    "master": "/ws/master",
                    "all_services": "/ws/all",
                    "stats": "/ws/stats",
                    "services": "/ws/services",
                    "endpoints": "/ws/endpoints"
                },
                "data_collection": {
                    "unified": "/ws/data",
                    "market_data": "/ws/market_data",
                    "whale_tracking": "/ws/whale_tracking",
                    "news": "/ws/news",
                    "sentiment": "/ws/sentiment"
                },
                "monitoring": {
                    "unified": "/ws/monitoring",
                    "health": "/ws/health",
                    "pool_status": "/ws/pool_status",
                    "scheduler": "/ws/scheduler_status"
                },
                "integration": {
                    "unified": "/ws/integration",
                    "huggingface": "/ws/huggingface",
                    "ai": "/ws/ai",
                    "persistence": "/ws/persistence"
                },
                "legacy": {
                    "live": "/ws/live"
                }
            }
        },
        "features": [
            "Multi-provider API monitoring",
            "Real-time WebSocket updates for all services",
            "Data collection WebSocket APIs (market data, news, sentiment, whale tracking, etc.)",
            "Monitoring WebSocket APIs (health checks, pool management, scheduler)",
            "Integration WebSocket APIs (HuggingFace AI, persistence)",
            "Rate limit tracking",
            "Automated health checks",
            "Scheduled data collection",
            "Failure detection and alerts",
            "Historical analytics",
            "Subscription-based message routing"
        ],
        "system_info": {
            "total_providers": len(config.get_all_providers()),
            "categories": config.get_categories(),
            "scheduler_running": task_scheduler.is_running(),
            "websocket_connections": ws_manager.get_connection_count(),
            "database_path": db_manager.db_path
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint

    Returns:
        System health status
    """
    try:
        # Check database health
        db_health = db_manager.health_check()

        # Get latest system metrics
        latest_metrics = db_manager.get_latest_system_metrics()

        # Check scheduler status
        scheduler_status = task_scheduler.is_running()

        # Check WebSocket status
        ws_status = ws_manager._is_running
        ws_connections = ws_manager.get_connection_count()

        # Determine overall health
        overall_health = "healthy"

        if db_health.get('status') != 'healthy':
            overall_health = "degraded"

        if not scheduler_status:
            overall_health = "degraded"

        if latest_metrics and latest_metrics.system_health == "critical":
            overall_health = "critical"

        return {
            "status": overall_health,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": {
                    "status": db_health.get('status', 'unknown'),
                    "path": db_health.get('database_path'),
                    "size_mb": db_health.get('stats', {}).get('database_size_mb', 0)
                },
                "scheduler": {
                    "status": "running" if scheduler_status else "stopped",
                    "active_jobs": task_scheduler.get_job_status().get('total_jobs', 0)
                },
                "websocket": {
                    "status": "running" if ws_status else "stopped",
                    "active_connections": ws_connections
                },
                "providers": {
                    "total": len(config.get_all_providers()),
                    "online": latest_metrics.online_count if latest_metrics else 0,
                    "degraded": latest_metrics.degraded_count if latest_metrics else 0,
                    "offline": latest_metrics.offline_count if latest_metrics else 0
                }
            },
            "metrics": {
                "avg_response_time_ms": latest_metrics.avg_response_time_ms if latest_metrics else 0,
                "total_requests_hour": latest_metrics.total_requests_hour if latest_metrics else 0,
                "total_failures_hour": latest_metrics.total_failures_hour if latest_metrics else 0,
                "system_health": latest_metrics.system_health if latest_metrics else "unknown"
            }
        }

    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@app.get("/info", tags=["Root"])
async def system_info():
    """
    Get detailed system information

    Returns:
        Detailed system information
    """
    try:
        # Get configuration stats
        config_stats = config.stats()

        # Get database stats
        db_stats = db_manager.get_database_stats()

        # Get rate limit statuses
        rate_limit_count = len(rate_limiter.get_all_statuses())

        # Get scheduler info
        scheduler_info = task_scheduler.get_job_status()

        return {
            "application": {
                "name": "Crypto API Monitoring System",
                "version": "2.0.0",
                "environment": "production"
            },
            "configuration": config_stats,
            "database": db_stats,
            "rate_limits": {
                "configured_providers": rate_limit_count
            },
            "scheduler": {
                "running": task_scheduler.is_running(),
                "total_jobs": scheduler_info.get('total_jobs', 0),
                "jobs": scheduler_info.get('jobs', [])
            },
            "websocket": {
                "active_connections": ws_manager.get_connection_count(),
                "background_tasks_running": ws_manager._is_running
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"System info error: {e}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    """
    Run the application with uvicorn

    Configuration:
    - Host: 0.0.0.0 (all interfaces)
    - Port: 7860
    - Log level: info
    - Reload: disabled (production mode)
    """
    logger.info("Starting Crypto API Monitoring System on 0.0.0.0:7860")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info",
        access_log=True,
        use_colors=True
    )

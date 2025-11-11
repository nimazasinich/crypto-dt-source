"""
Crypto API Monitor - FastAPI Backend
Real-time cryptocurrency API monitoring and management
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import asyncio

from config import config
from database.db import init_database
from api.endpoints import router as api_router
from api.websocket import websocket_endpoint, manager
from monitoring.health_monitor import health_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background tasks
background_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Crypto API Monitor...")

    # Initialize database
    init_database()

    # Start health monitoring
    task = asyncio.create_task(health_monitor.start())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    logger.info("Crypto API Monitor started successfully")
    logger.info(f"Monitoring {len(config.PROVIDERS)} providers")
    logger.info(f"API Keys loaded: {', '.join([k for k, v in config.API_KEYS.items() if v])}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    health_monitor.stop()

    # Cancel all background tasks
    for task in background_tasks:
        task.cancel()

    await asyncio.gather(*background_tasks, return_exceptions=True)

    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Crypto API Monitor",
    description="Real-time cryptocurrency API resource monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)


# WebSocket endpoint
@app.websocket("/ws/live")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "providers": len(config.PROVIDERS),
        "websocket_clients": len(manager.active_connections),
        "api_keys_configured": sum(1 for v in config.API_KEYS.values() if v)
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Crypto API Monitor Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws/live"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
        log_level="info"
    )

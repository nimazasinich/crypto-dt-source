"""
Enhanced Production Server
Integrates all services for comprehensive crypto data tracking
with real-time updates, persistence, and scheduling
"""
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

# Import services
from backend.services.unified_config_loader import UnifiedConfigLoader
from backend.services.scheduler_service import SchedulerService
from backend.services.persistence_service import PersistenceService
from backend.services.websocket_service import WebSocketService

# Import database manager
try:
    from database.db_manager import DatabaseManager
except ImportError:
    DatabaseManager = None

# Import routers
from backend.routers.integrated_api import router as integrated_router, set_services
from backend.routers.advanced_api import router as advanced_router
from backend.routers.hf_space_api import router as hf_space_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
config_loader = None
scheduler_service = None
persistence_service = None
websocket_service = None
db_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global config_loader, scheduler_service, persistence_service, websocket_service, db_manager

    logger.info("=" * 80)
    logger.info("🚀 Starting Enhanced Crypto Data Tracker")
    logger.info("=" * 80)

    try:
        # Initialize database manager
        if DatabaseManager:
            db_manager = DatabaseManager("data/crypto_tracker.db")
            db_manager.init_database()
            logger.info("✓ Database initialized")
        else:
            logger.warning("⚠ Database manager not available")

        # Initialize configuration loader
        logger.info("📥 Loading configurations...")
        config_loader = UnifiedConfigLoader()
        logger.info(f"✓ Loaded {len(config_loader.apis)} APIs from config files")

        # Initialize persistence service
        logger.info("💾 Initializing persistence service...")
        persistence_service = PersistenceService(db_manager=db_manager)
        logger.info("✓ Persistence service ready")

        # Initialize scheduler service
        logger.info("⏰ Initializing scheduler service...")
        scheduler_service = SchedulerService(
            config_loader=config_loader,
            db_manager=db_manager
        )

        # Initialize WebSocket service
        logger.info("🔌 Initializing WebSocket service...")
        websocket_service = WebSocketService(
            scheduler_service=scheduler_service,
            persistence_service=persistence_service
        )
        logger.info("✓ WebSocket service ready")

        # Set services in router
        set_services(config_loader, scheduler_service, persistence_service, websocket_service)
        logger.info("✓ Services registered with API router")

        # Setup data update callback
        def data_update_callback(api_id: str, data: dict):
            """Callback for data updates from scheduler"""
            # Save to persistence
            asyncio.create_task(persistence_service.save_api_data(
                api_id,
                data,
                metadata={'source': 'scheduler'}
            ))

            # Notify WebSocket clients
            asyncio.create_task(websocket_service.notify_data_update(
                api_id,
                data,
                metadata={'source': 'scheduler'}
            ))

        # Register callback with scheduler (for each API)
        for api_id in config_loader.apis.keys():
            scheduler_service.register_callback(api_id, data_update_callback)

        logger.info("✓ Data update callbacks registered")

        # Start scheduler
        logger.info("▶️  Starting scheduler...")
        await scheduler_service.start()
        logger.info("✓ Scheduler started")

        logger.info("=" * 80)
        logger.info("✅ All services started successfully!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📊 Service Summary:")
        logger.info(f"   • APIs configured: {len(config_loader.apis)}")
        logger.info(f"   • Categories: {len(config_loader.get_categories())}")
        logger.info(f"   • Scheduled tasks: {len(scheduler_service.tasks)}")
        logger.info(f"   • Real-time tasks: {len(scheduler_service.realtime_tasks)}")
        logger.info("")
        logger.info("🌐 Access points:")
        logger.info("   • Main Dashboard: http://localhost:8000/")
        logger.info("   • API Documentation: http://localhost:8000/docs")
        logger.info("   • WebSocket: ws://localhost:8000/api/v2/ws")
        logger.info("")

        yield

        # Shutdown
        logger.info("")
        logger.info("=" * 80)
        logger.info("🛑 Shutting down services...")
        logger.info("=" * 80)

        # Stop scheduler
        if scheduler_service:
            logger.info("⏸️  Stopping scheduler...")
            await scheduler_service.stop()
            logger.info("✓ Scheduler stopped")

        # Create final backup
        if persistence_service:
            logger.info("💾 Creating final backup...")
            try:
                backup_file = await persistence_service.backup_all_data()
                logger.info(f"✓ Backup created: {backup_file}")
            except Exception as e:
                logger.error(f"✗ Backup failed: {e}")

        logger.info("=" * 80)
        logger.info("✅ Shutdown complete")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Error during startup: {e}", exc_info=True)
        raise


# Create FastAPI app
app = FastAPI(
    title="Enhanced Crypto Data Tracker",
    description="""
    Comprehensive cryptocurrency data tracking API with:
    - Market data (pairs, OHLC, depth, tickers)
    - Trading signals and ML model predictions
    - News and sentiment analysis
    - Whale tracking and large transactions
    - Blockchain statistics and gas prices
    - Automatic fallback to multiple data providers
    - Real-time WebSocket updates
    - Full OpenAPI/Swagger documentation
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(integrated_router)
app.include_router(advanced_router)
app.include_router(hf_space_router)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    logger.warning("⚠ Static files directory not found")

# Serve HTML files
from fastapi.responses import HTMLResponse, FileResponse


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    else:
        return HTMLResponse("""
        <html>
            <head>
                <title>Enhanced Crypto Data Tracker</title>
                <style>
                    body {
                        font-family: 'Inter', sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container {
                        text-align: center;
                        background: rgba(255, 255, 255, 0.1);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                    }
                    h1 { margin: 0 0 20px 0; }
                    .links { margin-top: 30px; }
                    a {
                        color: white;
                        text-decoration: none;
                        padding: 10px 20px;
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        margin: 0 10px;
                        display: inline-block;
                    }
                    a:hover {
                        background: rgba(255, 255, 255, 0.3);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Enhanced Crypto Data Tracker</h1>
                    <p>Real-time cryptocurrency data tracking and monitoring</p>
                    <div class="links">
                        <a href="/docs">📚 API Documentation</a>
                        <a href="/api/v2/status">📊 System Status</a>
                    </div>
                </div>
            </body>
        </html>
        """)


@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard():
    """Serve simple dashboard"""
    if os.path.exists("dashboard.html"):
        return FileResponse("dashboard.html")
    return HTMLResponse("<h1>Dashboard not found</h1>")


@app.get("/hf_console.html", response_class=HTMLResponse)
async def hf_console():
    """Serve HuggingFace console"""
    if os.path.exists("hf_console.html"):
        return FileResponse("hf_console.html")
    return HTMLResponse("<h1>HF Console not found</h1>")


@app.get("/admin.html", response_class=HTMLResponse)
async def admin():
    """Serve admin panel"""
    if os.path.exists("admin.html"):
        return FileResponse("admin.html")
    return HTMLResponse("<h1>Admin panel not found</h1>")


@app.get("/admin_advanced.html", response_class=HTMLResponse)
async def admin_advanced():
    """Serve advanced admin panel"""
    if os.path.exists("admin_advanced.html"):
        return FileResponse("admin_advanced.html")
    return HTMLResponse("<h1>Advanced admin panel not found</h1>")


if __name__ == "__main__":
    # Ensure data directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)
    os.makedirs("data/backups", exist_ok=True)

    # Run server
    uvicorn.run(
        "enhanced_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production
        log_level="info"
    )

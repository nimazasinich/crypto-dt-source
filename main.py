"""
Main entry point for HuggingFace Space
Loads the unified API server with all endpoints
Runs with uvicorn on port 7860 (Hugging Face Spaces standard)
"""
import os
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", os.getenv("HF_PORT", "7860")))

# Import the unified server app with fallback
try:
    from hf_unified_server import app
    logger.info("✅ Loaded hf_unified_server")
except ImportError as e:
    logger.warning(f"⚠️ Error importing hf_unified_server: {e}")
    logger.info("Falling back to basic app...")
    # Fallback to basic FastAPI app
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Crypto API - Fallback Mode")
        
        @app.get("/health")
        def health():
            return {
                "status": "fallback",
                "message": "Server is running in fallback mode",
                "error": str(e)
            }
        
        @app.get("/")
        def root():
            return {
                "message": "Cryptocurrency Data API - Fallback Mode",
                "note": "Main server module not available"
            }
        logger.info("✅ Fallback FastAPI app created")
    except ImportError as fastapi_error:
        logger.error(f"❌ FastAPI not available: {fastapi_error}")
        logger.error("Please install: pip install fastapi uvicorn")
        sys.exit(1)
except Exception as e:
    logger.error(f"❌ Unexpected error loading server: {e}")
    import traceback
    traceback.print_exc()
    # Still create fallback app
    from fastapi import FastAPI
    app = FastAPI(title="Crypto API - Error Mode")
    
    @app.get("/health")
    def health():
        return {"status": "error", "message": str(e)}

# Export app for uvicorn
__all__ = ["app"]

# Run server if executed directly
if __name__ == "__main__":
    try:
        import uvicorn
        
        logger.info("=" * 70)
        logger.info("🚀 Starting FastAPI Server with Uvicorn")
        logger.info("=" * 70)
        logger.info(f"📍 Host: {HOST}")
        logger.info(f"📍 Port: {PORT}")
        logger.info(f"🌐 Server URL: http://{HOST}:{PORT}")
        logger.info(f"📊 Dashboard: http://{HOST}:{PORT}/")
        logger.info(f"📚 API Docs: http://{HOST}:{PORT}/docs")
        logger.info(f"📊 System Monitor: http://{HOST}:{PORT}/system-monitor")
        logger.info("=" * 70)
        logger.info("")
        logger.info("💡 Tips:")
        logger.info("   - Press Ctrl+C to stop the server")
        logger.info("   - Set PORT environment variable to change port")
        logger.info("   - Set HOST environment variable to change host")
        logger.info("")
        
        uvicorn.run(
            "main:app",  # Use string reference for better reload support
            host=HOST,
            port=PORT,
            log_level="info",
            access_log=True,
            # Optimizations for production
            timeout_keep_alive=30,
            limit_concurrency=100,
            limit_max_requests=1000,
            # Reload only in development (if DEBUG env var is set)
            reload=os.getenv("DEBUG", "false").lower() == "true"
        )
    except ImportError:
        logger.error("❌ uvicorn not installed")
        logger.error("Please install with: pip install uvicorn")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

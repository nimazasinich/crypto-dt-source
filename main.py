"""
Main entry point for HuggingFace Space
Loads the unified API server with all endpoints
"""
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

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

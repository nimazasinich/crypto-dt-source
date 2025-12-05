#!/usr/bin/env python3
"""
Unified Server for Crypto Intelligence Hub
Serves static frontend and API backend
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment setup - MUST be set BEFORE importing ai_models
os.environ.setdefault("SPACE_ID", "crypto-intelligence-hub")
os.environ.setdefault("HF_MODE", "public")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "0")
os.environ.setdefault("USE_MOCK_DATA", "false")

PORT = int(os.getenv("PORT", "7860"))
HOST = os.getenv("HOST", "0.0.0.0")
WORKSPACE_ROOT = Path("/app" if Path("/app").exists() else Path("."))

logger.info(f"🚀 Starting Crypto Intelligence Hub")
logger.info(f"📁 Workspace: {WORKSPACE_ROOT}")
logger.info(f"🌐 Server: {HOST}:{PORT}")

# Initialize database (non-critical)
try:
    from api_server_extended import init_database
    init_database()
    logger.info("✅ Database initialized")
except ImportError as e:
    logger.warning(f"⚠️ Database module not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Database initialization issue: {e} (continuing anyway)")

# Import and run FastAPI app
try:
    from api_server_extended import app
    logger.info("✅ FastAPI app loaded")
    
    # Initialize AI models in background (non-critical)
    try:
        from ai_models import initialize_models
        result = initialize_models()
        status = result.get('status', 'unknown')
        models_loaded = result.get('models_loaded', 0)
        logger.info(f"✅ AI Models initialized: status={status}, loaded={models_loaded}")
        if status == "fallback_only":
            logger.info("ℹ️ Using fallback mode - models will use keyword analysis")
    except ImportError as e:
        logger.warning(f"⚠️ AI Models module not available: {e}")
    except Exception as e:
        logger.warning(f"⚠️ AI Models initialization failed: {e} (continuing with fallback)")
    
    # Start server
    if __name__ == "__main__":
        try:
            import uvicorn
            logger.info(f"🌐 Starting server on {HOST}:{PORT}")
            uvicorn.run(
                app,
                host=HOST,
                port=PORT,
                log_level="info",
                access_log=True
            )
        except ImportError:
            logger.error("❌ uvicorn not installed. Install with: pip install uvicorn")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
except ImportError as e:
    logger.error(f"❌ Failed to import FastAPI app: {e}")
    logger.error("Please ensure api_server_extended.py exists and all dependencies are installed")
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Failed to start server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


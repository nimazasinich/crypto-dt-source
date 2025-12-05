#!/usr/bin/env python3
"""
Hugging Face Spaces Optimized Server
FastAPI-only, No WebSocket, Lightweight AI Models
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

# Force environment for HF Spaces
os.environ["USE_FASTAPI_HTML"] = "true"
os.environ["USE_GRADIO"] = "false"
os.environ["USE_WEBSOCKET"] = "false"
os.environ["HF_SPACES"] = "true"
os.environ["USE_MOCK_DATA"] = "false"
os.environ["SPACE_ID"] = "crypto-intelligence-hub"  # Enable HF Space mode
os.environ["HF_MODE"] = "public"  # Enable public HF models
os.environ["TRANSFORMERS_OFFLINE"] = "0"  # Allow model downloads

# Workspace setup
WORKSPACE_ROOT = Path("/app" if Path("/app").exists() else Path("."))
PORT = int(os.getenv("PORT", "7860"))
HOST = os.getenv("HOST", "0.0.0.0")

logger.info("=" * 60)
logger.info("🚀 CRYPTO INTELLIGENCE HUB - HUGGING FACE SPACES")
logger.info("=" * 60)
logger.info(f"📁 Workspace: {WORKSPACE_ROOT}")
logger.info(f"🌐 Server: {HOST}:{PORT}")
logger.info(f"🔧 WebSocket: DISABLED (HF Spaces)")
logger.info(f"🎯 Mode: FastAPI + Static HTML")
logger.info("=" * 60)

# Import resources manager
try:
    from api_resources_manager import get_resources_manager
    resources_mgr = get_resources_manager(WORKSPACE_ROOT)
    stats = resources_mgr.get_stats()
    logger.info(f"✅ Resources Manager: {stats['unified_resources']['total']} APIs loaded")
except Exception as e:
    logger.warning(f"⚠️ Resources Manager: {e}")

# Initialize database
try:
    from api_server_extended import init_database
    init_database()
    logger.info("✅ Database initialized")
except Exception as e:
    logger.warning(f"⚠️ Database: {e}")

# Import FastAPI app
try:
    from api_server_extended import app
    logger.info("✅ FastAPI app loaded")
    
    # Initialize AI models in background (lightweight mode)
    try:
        from ai_models import initialize_models
        logger.info("🤖 Initializing AI models (lightweight mode)...")
        result = initialize_models()
        logger.info(f"✅ AI Models: {result.get('status', 'initialized')}")
    except Exception as e:
        logger.warning(f"⚠️ AI Models (non-critical): {e}")
    
    logger.info("=" * 60)
    logger.info("✅ ALL SYSTEMS READY")
    logger.info(f"🌐 Access at: http://{HOST}:{PORT}")
    logger.info(f"📚 API Docs: http://{HOST}:{PORT}/docs")
    logger.info("=" * 60)
    
    # Start server
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info",
            access_log=True,
            # HF Spaces optimizations
            timeout_keep_alive=30,
            limit_concurrency=100,
            limit_max_requests=1000
        )

except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


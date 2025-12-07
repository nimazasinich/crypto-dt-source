#!/usr/bin/env python3
"""
Hugging Face Space Entry Point
Automatically runs the cryptocurrency server on port 7860
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

# Add current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

# Import the FastAPI app
try:
    from crypto_server import app
    logger.info("✅ Successfully imported crypto_server app")
except ImportError as e:
    logger.error(f"❌ Failed to import crypto_server: {e}")
    logger.error("Make sure crypto_server.py is in the same directory")
    sys.exit(1)

# Hugging Face Spaces configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 7860))

if __name__ == "__main__":
    try:
        import uvicorn
        
        logger.info("="*70)
        logger.info("🚀 Starting Cryptocurrency Data Server on Hugging Face Space")
        logger.info("="*70)
        logger.info(f"Host: {HOST}")
        logger.info(f"Port: {PORT}")
        logger.info("API Documentation: /docs")
        logger.info("Health Check: /health")
        logger.info("WebSocket: /ws")
        logger.info("="*70)
        
        # Run the server with Hugging Face Spaces configuration
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info",
            access_log=True,
            # Enable WebSocket support
            ws="auto",
            # Timeout settings for long-running requests
            timeout_keep_alive=75,
        )
    
    except ImportError:
        logger.error("❌ uvicorn is not installed")
        logger.error("Install: pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

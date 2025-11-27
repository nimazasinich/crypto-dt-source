"""
Main entry point for HuggingFace Space
Loads the unified API server with all endpoints
"""

from pathlib import Path
import sys

# Add current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

# Import the unified server app
try:
    from hf_unified_server import app
except ImportError as e:
    print(f"Error importing hf_unified_server: {e}")
    print("Falling back to basic app...")
    # Fallback to basic FastAPI app
    from fastapi import FastAPI

    app = FastAPI(title="Crypto API - Loading...")

    @app.get("/health")
    def health():
        return {"status": "loading", "message": "Server is starting up..."}

    @app.get("/")
    def root():
        return {"message": "Cryptocurrency Data API - Initializing..."}


# Export app for uvicorn
__all__ = ["app"]

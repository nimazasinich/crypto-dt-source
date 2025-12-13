#!/usr/bin/env python3
"""
FastAPI Server Runner
Simple script to run the FastAPI server with uvicorn on port 7860
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def main():
    """Run the FastAPI server"""
    try:
        import uvicorn
    except ImportError:
        print("❌ uvicorn is not installed!")
        print("Please install with: pip install uvicorn")
        sys.exit(1)
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("HF_PORT", "7860")))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print("=" * 70)
    print("🚀 Starting Crypto Intelligence Hub - FastAPI Server")
    print("=" * 70)
    print(f"📍 Host: {host}")
    print(f"📍 Port: {port}")
    print(f"🌐 Server URL: http://{host}:{port}")
    print(f"📊 Dashboard: http://{host}:{port}/")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"📊 System Monitor: http://{host}:{port}/system-monitor")
    print("=" * 70)
    print("")
    print("💡 Tips:")
    print("   - Press Ctrl+C to stop the server")
    print("   - Set PORT environment variable to change port")
    print("   - Set HOST environment variable to change host")
    print("   - Set DEBUG=true for auto-reload during development")
    print("")
    
    try:
        uvicorn.run(
            "main:app",  # Import from main.py
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            # Production optimizations
            timeout_keep_alive=30,
            limit_concurrency=100,
            limit_max_requests=1000,
            # Reload in debug mode
            reload=debug
        )
    except KeyboardInterrupt:
        print("")
        print("🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


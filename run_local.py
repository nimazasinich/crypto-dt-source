#!/usr/bin/env python3
"""
Simple local development server runner.

On Windows, `uvicorn`'s reload mechanism uses multiprocessing under the hood,
which requires the usual `if __name__ == "__main__"` protection to avoid
the "freeze_support()" bootstrapping error. We also disable auto‑reload on
Windows to prevent duplicate process spawns.
"""
import os
import sys
from pathlib import Path

import uvicorn

# Check if we're in the right directory
def main() -> None:
    """
    Entry point for running the local development server.

    Performs basic sanity checks on the working directory and static assets,
    then starts the `simple_server:app` FastAPI application via uvicorn.
    """
    if not Path("static").exists():
        print("❌ Error: 'static' directory not found!")
        print("   Please run this script from the project root directory.")
        sys.exit(1)

    if not Path("static/pages/dashboard/index.html").exists():
        print("❌ Error: Dashboard not found at 'static/pages/dashboard/index.html'")
        sys.exit(1)

    # Allow overriding the default port via environment variables for local
    # development flexibility while still defaulting to 7860.
    port_str = os.getenv("PORT", os.getenv("HF_PORT", "7860"))
    try:
        port = int(port_str)
    except ValueError:
        print(f"❌ Invalid port value in environment: {port_str!r}")
        sys.exit(1)

    print("=" * 70)
    print("🚀 Starting Local Development Server")
    print("=" * 70)
    print(f"📍 Server URL: http://localhost:{port}")
    print(f"📊 Dashboard: http://localhost:{port}/")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print("=" * 70)
    print()
    print("💡 Tips:")
    print(f"   - The dashboard will be available at http://localhost:{port}")
    print("   - Press Ctrl+C to stop the server")
    print("   - Static files are served from the 'static' directory")
    print()

    # Reload is helpful during development but problematic on Windows due to
    # multiprocessing spawn semantics, so disable reload on Windows.
    reload_enabled = os.name != "nt"

    try:
        # Use the lightweight simple_server for local UI testing; this avoids
        # heavy startup and encoding issues from the full backend while still
        # exposing the key dashboard APIs.
        uvicorn.run(
            "simple_server:app",
            host="127.0.0.1",
            port=port,
            log_level="info",
            reload=reload_enabled,
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
    except Exception as exc:
        print(f"\n❌ Error starting server: {exc}")
        print("\n💡 Make sure you have installed dependencies:")
        print("   pip install -r requirements-simple.txt")
        print("   (or pip install -r requirements.txt for full features)")
        sys.exit(1)


if __name__ == "__main__":
    main()


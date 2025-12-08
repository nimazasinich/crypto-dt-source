#!/bin/bash
# FastAPI Server Startup Script for Linux/Mac

echo "========================================"
echo "Starting FastAPI Server"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if uvicorn is installed
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "ERROR: uvicorn is not installed"
    echo "Installing uvicorn..."
    pip3 install uvicorn[standard]
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install uvicorn"
        exit 1
    fi
fi

# Set default port if not set
export PORT=${PORT:-7860}
export HOST=${HOST:-0.0.0.0}

echo "Starting server on $HOST:$PORT..."
echo ""
echo "Access points:"
echo "  - Dashboard: http://localhost:$PORT/"
echo "  - API Docs: http://localhost:$PORT/docs"
echo "  - System Monitor: http://localhost:$PORT/system-monitor"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
python3 main.py


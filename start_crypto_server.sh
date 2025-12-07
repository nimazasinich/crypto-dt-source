#!/bin/bash

# Cryptocurrency Server Startup Script

echo "=========================================="
echo "Cryptocurrency Data Server"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI not found. Installing dependencies..."
    pip install -r requirements_crypto_server.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies found"
fi

echo ""
echo "=========================================="
echo "Starting Server..."
echo "=========================================="
echo ""

# Set default values
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "Server will start on: http://${HOST}:${PORT}"
echo "API Documentation: http://localhost:${PORT}/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 crypto_server.py

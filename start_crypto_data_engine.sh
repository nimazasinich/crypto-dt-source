#!/bin/bash
# Quick start script for Cryptocurrency Data Engine API
# Starts the server with real data endpoints

echo "=================================================="
echo "Cryptocurrency Data Engine API - Real Data Only"
echo "=================================================="
echo ""

# Check if HF_API_TOKEN is set
if [ -z "$HF_API_TOKEN" ]; then
    echo "⚠️  WARNING: HF_API_TOKEN not set"
    echo "   Sentiment analysis endpoint will not work"
    echo "   Get your token from: https://huggingface.co/settings/tokens"
    echo ""
fi

# Check if NEWSAPI_KEY is set
if [ -z "$NEWSAPI_KEY" ]; then
    echo "ℹ️  INFO: NEWSAPI_KEY not set (optional)"
    echo "   News endpoint will fallback to RSS feeds"
    echo ""
fi

echo "Starting server..."
echo ""
echo "Available endpoints:"
echo "  - Health Check: http://localhost:8000/api/health"
echo "  - Market Prices: http://localhost:8000/api/market"
echo "  - OHLCV History: http://localhost:8000/api/market/history"
echo "  - Sentiment: http://localhost:8000/api/sentiment/analyze"
echo "  - News: http://localhost:8000/api/news/latest"
echo "  - Trending: http://localhost:8000/api/trending"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "=================================================="
echo ""

# Start the server
python crypto_data_engine_server.py

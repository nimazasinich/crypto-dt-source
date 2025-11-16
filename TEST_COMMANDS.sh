#!/bin/bash
# Test commands for verifying the deployed application
# Run these commands after starting the server

BASE_URL="${BASE_URL:-http://localhost:7860}"

echo "Testing Crypto Monitor API Endpoints"
echo "====================================="
echo ""

echo "1. Health Check:"
curl -s "$BASE_URL/health" | jq
echo ""

echo "2. Market Data (Real CoinGecko):"
curl -s "$BASE_URL/api/market" | jq '.cryptocurrencies[0] | {name, symbol, price, provider: .provider}'
echo ""

echo "3. Sentiment (Real Alternative.me):"
curl -s "$BASE_URL/api/sentiment" | jq '.fear_greed_index'
echo ""

echo "4. Trending (Real CoinGecko):"
curl -s "$BASE_URL/api/trending" | jq '.trending[0:3] | .[] | {name, symbol}'
echo ""

echo "5. Market History (Database):"
curl -s "$BASE_URL/api/market/history?symbol=BTC&limit=5" | jq
echo ""

echo "6. DeFi Endpoint (Should return 503):"
curl -s -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/api/defi" | jq
echo ""

echo "7. HF Sentiment (Should return 501):"
curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL/api/hf/run-sentiment" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Bitcoin is bullish"]}' | jq
echo ""

echo "All tests completed!"

#!/bin/bash
# Test Script for New API Endpoints
# Run this after server is started to verify all new endpoints work

BASE_URL="http://localhost:7860"

echo "============================================"
echo "🧪 Testing New API Endpoints"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo "Testing: $description"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_status=$(echo "$response" | grep "HTTP_STATUS" | cut -d':' -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    
    if [ "$http_status" == "200" ] || [ "$http_status" == "201" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_status)"
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_status)"
        echo "Response: $body"
    fi
    echo "---"
    echo ""
}

echo "📊 1. MARKET DATA ENDPOINTS (7 endpoints)"
echo "============================================"
test_endpoint "POST" "/api/coins/search" '{"q":"bitcoin","limit":5}' "Search coins"
test_endpoint "GET" "/api/coins/bitcoin/details" "" "Get coin details"
test_endpoint "GET" "/api/coins/bitcoin/history?days=7" "" "Get historical data"
test_endpoint "GET" "/api/coins/bitcoin/chart?timeframe=7d" "" "Get chart data"
test_endpoint "GET" "/api/market/categories" "" "Get market categories"
test_endpoint "GET" "/api/market/gainers?limit=5" "" "Get top gainers"
test_endpoint "GET" "/api/market/losers?limit=5" "" "Get top losers"
echo ""

echo "⚙️ 2. TRADING & ANALYSIS ENDPOINTS (5 endpoints)"
echo "============================================"
test_endpoint "GET" "/api/trading/volume?symbol=BTC" "" "Get volume analysis"
test_endpoint "GET" "/api/trading/orderbook?symbol=BTC&depth=10" "" "Get order book"
test_endpoint "GET" "/api/indicators/BTC?interval=1h&indicators=rsi,macd" "" "Get technical indicators"
test_endpoint "POST" "/api/backtest" '{"symbol":"BTC","strategy":"sma_cross","start_date":"2025-11-01","end_date":"2025-12-01","initial_capital":10000}' "Backtest strategy"
test_endpoint "GET" "/api/correlations?symbols=BTC,ETH,BNB&days=7" "" "Get correlations"
echo ""

echo "🤖 3. AI & PREDICTION ENDPOINTS (4 endpoints)"
echo "============================================"
test_endpoint "GET" "/api/ai/predictions/BTC?days=7" "" "Get price predictions"
test_endpoint "GET" "/api/ai/sentiment/BTC" "" "Get coin sentiment"
test_endpoint "POST" "/api/ai/analyze" '{"symbol":"BTC","analysis_type":"trend","timeframe":"30d"}' "Custom AI analysis"
test_endpoint "GET" "/api/ai/models" "" "Get AI models info"
echo ""

echo "📰 4. NEWS & SOCIAL ENDPOINTS (4 endpoints)"
echo "============================================"
test_endpoint "GET" "/api/news/BTC?limit=5" "" "Get coin news"
test_endpoint "GET" "/api/social/trending?limit=5" "" "Get social trends"
test_endpoint "GET" "/api/social/sentiment?coin=BTC" "" "Get social sentiment"
test_endpoint "GET" "/api/events?days=30" "" "Get upcoming events"
echo ""

echo "💼 5. PORTFOLIO & ALERTS ENDPOINTS (3 endpoints)"
echo "============================================"
test_endpoint "POST" "/api/portfolio/simulate" '{"holdings":[{"symbol":"BTC","amount":0.5}],"initial_investment":10000,"strategy":"hodl","period_days":30}' "Portfolio simulation"
test_endpoint "GET" "/api/alerts/prices?symbols=BTC,ETH" "" "Get price alerts"
test_endpoint "POST" "/api/watchlist" '{"action":"list","name":"default"}' "Watchlist management"
echo ""

echo "🔧 6. SYSTEM & METADATA ENDPOINTS (3 endpoints)"
echo "============================================"
test_endpoint "GET" "/api/exchanges?limit=10" "" "Get exchanges list"
test_endpoint "GET" "/api/metadata/coins?limit=10" "" "Get coins metadata"
test_endpoint "GET" "/api/cache/stats" "" "Get cache statistics"
echo ""

echo "============================================"
echo "✅ Test Script Complete"
echo "============================================"
echo ""
echo "Review the output above to verify all endpoints are working."
echo "All tests should show '✅ PASS' with HTTP 200 status."
echo ""
echo "If any tests failed:"
echo "  1. Make sure the server is running (python run_server.py)"
echo "  2. Check server logs for errors"
echo "  3. Verify external APIs are accessible"
echo "  4. Check network connectivity"
echo ""

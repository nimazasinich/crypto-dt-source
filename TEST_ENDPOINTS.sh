#!/bin/bash
# Script to test all HuggingFace Space endpoints

BASE_URL="https://really-amin-datasourceforcryptocurrency.hf.space"

echo "=================================="
echo "🧪 Testing HuggingFace Space API"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local endpoint=$2
    
    echo -n "Testing $name ... "
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "  Response: $body"
        return 1
    fi
}

# Core Endpoints
echo "📊 Core Endpoints"
echo "==================="
test_endpoint "Health" "/health"
test_endpoint "Info" "/info"
test_endpoint "Providers" "/api/providers"
echo ""

# Data Endpoints
echo "💰 Market Data Endpoints"
echo "========================="
test_endpoint "OHLCV (BTC)" "/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=10"
test_endpoint "Top Prices" "/api/crypto/prices/top?limit=5"
test_endpoint "BTC Price" "/api/crypto/price/BTC"
test_endpoint "Market Overview" "/api/crypto/market-overview"
test_endpoint "Multiple Prices" "/api/market/prices?symbols=BTC,ETH,SOL"
test_endpoint "Market Data Prices" "/api/market-data/prices?symbols=BTC,ETH"
echo ""

# Analysis Endpoints
echo "📈 Analysis Endpoints"
echo "====================="
test_endpoint "Trading Signals" "/api/analysis/signals?symbol=BTCUSDT"
test_endpoint "SMC Analysis" "/api/analysis/smc?symbol=BTCUSDT"
test_endpoint "Scoring Snapshot" "/api/scoring/snapshot?symbol=BTCUSDT"
test_endpoint "All Signals" "/api/signals"
test_endpoint "Sentiment" "/api/sentiment"
echo ""

# System Endpoints
echo "⚙️  System Endpoints"
echo "===================="
test_endpoint "System Status" "/api/system/status"
test_endpoint "System Config" "/api/system/config"
test_endpoint "Categories" "/api/categories"
test_endpoint "Rate Limits" "/api/rate-limits"
test_endpoint "Logs" "/api/logs?limit=10"
test_endpoint "Alerts" "/api/alerts"
echo ""

# HuggingFace Endpoints
echo "🤗 HuggingFace Endpoints"
echo "========================="
test_endpoint "HF Health" "/api/hf/health"
test_endpoint "HF Registry" "/api/hf/registry?kind=models"
echo ""

echo "=================================="
echo "✅ Testing Complete!"
echo "=================================="
echo ""
echo "📖 Full documentation: ${BASE_URL}/docs"
echo "📋 API Guide: See HUGGINGFACE_API_GUIDE.md"

#!/bin/bash
# ============================================================================
# Unified Query Service API - Usage Examples
# ============================================================================
# 
# This file contains curl examples for all endpoints in the Unified Service API.
# The service follows HF-first → WS-exception → fallback resolution pattern.
#
# Base URL for HuggingFace Space:
BASE_URL="https://really-amin-datasourceforcryptocurrency.hf.space"
#
# Expected meta.source values:
# - "hf" : Data served from HuggingFace Space (preferred)
# - "hf-ws" : Data from WebSocket real-time stream
# - "hf-model" : Data from HF AI models
# - External provider URLs (e.g., "https://api.coingecko.com", "https://api.binance.com")
# - "none" : No data available
#
# meta.attempted array shows all sources tried before success/failure
# ============================================================================

echo "=========================================="
echo "Unified Query Service API - Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# 1. GET /api/service/rate - Single pair rate
# ============================================================================
echo -e "${BLUE}1. Testing Single Pair Rate (BTC/USDT)${NC}"
echo "Endpoint: GET /api/service/rate?pair=BTC/USDT"
echo ""

curl -X GET "${BASE_URL}/api/service/rate?pair=BTC/USDT" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 2. GET /api/service/rate/batch - Multiple pairs
# ============================================================================
echo -e "${BLUE}2. Testing Batch Rates (BTC/USDT, ETH/USDT)${NC}"
echo "Endpoint: GET /api/service/rate/batch?pairs=BTC/USDT,ETH/USDT"
echo ""

curl -X GET "${BASE_URL}/api/service/rate/batch?pairs=BTC/USDT,ETH/USDT" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 3. GET /api/service/pair/{pair} - Pair metadata (MUST be HF first)
# ============================================================================
echo -e "${BLUE}3. Testing Pair Metadata (BTC-USDT)${NC}"
echo "Endpoint: GET /api/service/pair/BTC-USDT"
echo "Note: This endpoint MUST be served by HF HTTP first (meta.source='hf')"
echo ""

curl -X GET "${BASE_URL}/api/service/pair/BTC-USDT" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 4. GET /api/service/sentiment - Sentiment analysis
# ============================================================================
echo -e "${BLUE}4. Testing Sentiment Analysis${NC}"
echo "Endpoint: GET /api/service/sentiment"
echo ""

# With text parameter (URL encoded)
curl -G "${BASE_URL}/api/service/sentiment" \
  --data-urlencode "text=Bitcoin is surging to new all-time highs" \
  --data-urlencode "mode=crypto" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# With symbol parameter
echo -e "${BLUE}4b. Testing Sentiment Analysis (by symbol)${NC}"
curl -X GET "${BASE_URL}/api/service/sentiment?symbol=BTC&mode=crypto" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 5. POST /api/service/econ-analysis - Economic analysis
# ============================================================================
echo -e "${BLUE}5. Testing Economic Analysis${NC}"
echo "Endpoint: POST /api/service/econ-analysis"
echo ""

curl -X POST "${BASE_URL}/api/service/econ-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "BTC",
    "period": "1M",
    "context": "inflation, macro, federal reserve policy"
  }' \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 6. GET /api/service/history - Historical OHLC data
# ============================================================================
echo -e "${BLUE}6. Testing Historical Data (BTC)${NC}"
echo "Endpoint: GET /api/service/history?symbol=BTC&interval=60&limit=200"
echo ""

curl -X GET "${BASE_URL}/api/service/history?symbol=BTC&interval=60&limit=200" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 7. GET /api/service/market-status - Market overview
# ============================================================================
echo -e "${BLUE}7. Testing Market Status${NC}"
echo "Endpoint: GET /api/service/market-status"
echo ""

curl -X GET "${BASE_URL}/api/service/market-status" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 8. GET /api/service/top - Top N coins
# ============================================================================
echo -e "${BLUE}8a. Testing Top 10 Coins${NC}"
echo "Endpoint: GET /api/service/top?n=10"
echo ""

curl -X GET "${BASE_URL}/api/service/top?n=10" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

echo -e "${BLUE}8b. Testing Top 50 Coins${NC}"
echo "Endpoint: GET /api/service/top?n=50"
echo ""

curl -X GET "${BASE_URL}/api/service/top?n=50" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 9. GET /api/service/whales - Whale movements
# ============================================================================
echo -e "${BLUE}9. Testing Whale Movements${NC}"
echo "Endpoint: GET /api/service/whales?chain=ethereum&min_amount_usd=100000&limit=50"
echo ""

curl -X GET "${BASE_URL}/api/service/whales?chain=ethereum&min_amount_usd=100000&limit=50" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 10. GET /api/service/onchain - On-chain data
# ============================================================================
echo -e "${BLUE}10. Testing On-chain Data${NC}"
echo "Endpoint: GET /api/service/onchain?address=0xabc...&chain=ethereum"
echo ""

curl -X GET "${BASE_URL}/api/service/onchain?address=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1&chain=ethereum&limit=50" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 11. POST /api/service/query - Generic query endpoint
# ============================================================================
echo -e "${BLUE}11. Testing Generic Query Endpoint${NC}"
echo "Endpoint: POST /api/service/query"
echo ""

# Example 1: Rate query
echo "11a. Generic Query - Rate"
curl -X POST "${BASE_URL}/api/service/query" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "rate",
    "payload": {"pair": "BTC/USDT"},
    "options": {"prefer_hf": true, "persist": true}
  }' \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# Example 2: History query
echo "11b. Generic Query - History"
curl -X POST "${BASE_URL}/api/service/query" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "history",
    "payload": {"symbol": "ETH", "interval": 60, "limit": 100},
    "options": {"prefer_hf": true, "persist": true}
  }' \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# Example 3: Sentiment query
echo "11c. Generic Query - Sentiment"
curl -X POST "${BASE_URL}/api/service/query" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sentiment",
    "payload": {"text": "Ethereum upgrade successful", "mode": "crypto"},
    "options": {"prefer_hf": true, "persist": true}
  }' \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# 12. WebSocket Connection Test
# ============================================================================
echo -e "${BLUE}12. WebSocket Connection (JavaScript Example)${NC}"
echo "Endpoint: wss://${BASE_URL#https://}/ws"
echo ""

cat << 'EOF'
// WebSocket connection example (run in browser console or Node.js)
const ws = new WebSocket('wss://really-amin-datasourceforcryptocurrency.hf.space/ws');

ws.onopen = () => {
  console.log('Connected to WebSocket');
  
  // Subscribe to market data
  ws.send(JSON.stringify({
    "action": "subscribe",
    "service": "market_data",
    "symbols": ["BTC", "ETH", "BNB"]
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  // Data will be persisted automatically on server side
  // Expected format:
  // {
  //   "type": "update" | "subscribed",
  //   "service": "market_data",
  //   "symbol": "BTC",
  //   "data": { ... },
  //   "timestamp": "2025-11-24T12:00:00Z"
  // }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket connection closed');
};
EOF

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# Health Check
# ============================================================================
echo -e "${BLUE}13. Health Check${NC}"
echo "Endpoint: GET /api/health"
echo ""

curl -X GET "${BASE_URL}/api/health" \
  -H "Accept: application/json" \
  | python3 -m json.tool

echo ""
echo "----------------------------------------"
echo ""

# ============================================================================
# OpenAPI Documentation
# ============================================================================
echo -e "${BLUE}14. API Documentation${NC}"
echo "Swagger UI: ${BASE_URL}/docs"
echo "OpenAPI JSON: ${BASE_URL}/openapi.json"
echo ""

echo "To view interactive documentation, open in browser:"
echo "  ${BASE_URL}/docs"
echo ""

# ============================================================================
# Response Format Documentation
# ============================================================================
echo -e "${GREEN}=========================================="
echo "RESPONSE FORMAT DOCUMENTATION"
echo "==========================================${NC}"
echo ""
echo "All successful responses follow this format:"
echo ""
cat << 'EOF'
{
  "data": <domain-specific payload>,
  "meta": {
    "source": "hf" | "hf-ws" | "<provider-url>",
    "generated_at": "2025-11-24T12:00:00Z",
    "cache_ttl_seconds": 30,
    "confidence": 0.85,              // Optional: for AI-generated data
    "attempted": ["hf", "hf-ws"]     // Only on fallback/failure
  }
}
EOF

echo ""
echo "On failure:"
echo ""
cat << 'EOF'
{
  "data": null,
  "meta": {
    "source": "none",
    "attempted": ["hf", "hf-ws", "binance", "coingecko"],
    "generated_at": "2025-11-24T12:00:00Z",
    "error": "DATA_NOT_AVAILABLE"
  }
}
EOF

echo ""
echo -e "${GREEN}=========================================="
echo "META.SOURCE VALUES EXPLAINED"
echo "==========================================${NC}"
echo ""
echo "• 'hf'         : Data from HuggingFace Space (preferred source)"
echo "• 'hf-ws'      : Real-time data from HF WebSocket"
echo "• 'hf-model'   : AI-generated data from HF models"
echo "• 'default'    : Default/fallback values when all sources fail"
echo "• 'none'       : No data available from any source"
echo "• External URLs: Fallback provider that served the data"
echo ""
echo "The 'attempted' array shows resolution order when HF couldn't serve the request."
echo ""

echo -e "${GREEN}=========================================="
echo "PERSISTENCE INFORMATION"
echo "==========================================${NC}"
echo ""
echo "All returned datasets are automatically persisted to the Space database with:"
echo "• stored_from : Source that provided the data"
echo "• stored_at   : Timestamp when data was stored"
echo "• Full meta object for audit trail"
echo ""
echo "Retention policy:"
echo "• High-frequency data (rates, ticks): 7 days"
echo "• Aggregated summaries: 30 days"
echo "• Historical data: Indefinite"
echo ""

echo -e "${GREEN}=========================================="
echo "TEST COMPLETE!"
echo "==========================================${NC}"
echo ""
echo "All endpoints have been tested. Check the responses above for:"
echo "1. Proper data structure"
echo "2. meta.source values (should prefer 'hf' when available)"
echo "3. meta.attempted arrays on fallbacks"
echo "4. Correct timestamp formats"
echo ""
echo "For production use, ensure:"
echo "• HF_SPACE_BASE_URL environment variable is set"
echo "• Database persistence is configured"
echo "• Provider API keys are configured in /mnt/data/api-config-complete.txt"
echo ""
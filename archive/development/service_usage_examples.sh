#!/bin/bash

# ============================================
# HF Space UI Service Usage Examples
# Complete curl commands for all endpoints
# ============================================

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
API_PREFIX="/api/service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to print section headers
print_section() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

# Helper function to execute and show curl command
exec_curl() {
    local description="$1"
    local curl_cmd="$2"
    
    echo -e "${YELLOW}▶ $description${NC}"
    echo -e "${BLUE}Command:${NC} $curl_cmd"
    echo -e "${GREEN}Response:${NC}"
    eval "$curl_cmd" | jq '.' 2>/dev/null || eval "$curl_cmd"
    echo -e "\n"
}

# ============================================
# HEALTH & DIAGNOSTICS
# ============================================

print_section "🏥 HEALTH & DIAGNOSTICS"

exec_curl "Health Check" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/health'"

exec_curl "Detailed Diagnostics" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/diagnostics'"

# ============================================
# A. REAL-TIME MARKET DATA
# ============================================

print_section "📈 A. REAL-TIME MARKET DATA"

exec_curl "Get single rate (BTC/USDT)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/rate?pair=BTC/USDT'"

exec_curl "Get single rate (ETH/USDT)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/rate?pair=ETH/USDT'"

exec_curl "Get batch rates" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/rate/batch?pairs=BTC/USDT,ETH/USDT,SOL/USDT'"

# ============================================
# B. PAIR METADATA (MUST BE HF)
# ============================================

print_section "🔍 B. PAIR METADATA (HF Priority)"

exec_curl "Get BTC-USDT pair metadata" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/pair/BTC-USDT'"

exec_curl "Get ETH-USDT pair metadata" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/pair/ETH-USDT'"

exec_curl "Get SOL-USDT pair metadata" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/pair/SOL-USDT'"

# Validate HF source
echo -e "${YELLOW}⚠️  Validating HF source for pair metadata...${NC}"
PAIR_RESPONSE=$(curl -s -X GET "${BASE_URL}${API_PREFIX}/pair/BTC-USDT")
SOURCE=$(echo "$PAIR_RESPONSE" | jq -r '.meta.source')
if [ "$SOURCE" == "hf" ]; then
    echo -e "${GREEN}✓ Pair metadata correctly served from HF${NC}"
else
    echo -e "${RED}✗ WARNING: Pair metadata source is '$SOURCE', expected 'hf'${NC}"
fi

# ============================================
# C. HISTORICAL DATA (OHLC)
# ============================================

print_section "📊 C. HISTORICAL DATA (OHLC)"

exec_curl "Get BTC 1-minute candles (limit 10)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/history?symbol=BTC&interval=60&limit=10'"

exec_curl "Get ETH 5-minute candles (limit 20)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/history?symbol=ETH&interval=300&limit=20'"

exec_curl "Get BTC 1-hour candles (limit 100)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/history?symbol=BTC&interval=3600&limit=100'"

# ============================================
# D. MARKET OVERVIEW & TOP MOVERS
# ============================================

print_section "🌐 D. MARKET OVERVIEW & TOP MOVERS"

exec_curl "Get market overview/status" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/market-status'"

exec_curl "Get top 10 movers" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/top?n=10'"

exec_curl "Get top 50 movers" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/top?n=50'"

# ============================================
# E. SENTIMENT & NEWS ANALYSIS
# ============================================

print_section "📰 E. SENTIMENT & NEWS ANALYSIS"

exec_curl "Analyze text sentiment" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/sentiment' \
        -H 'Content-Type: application/json' \
        -d '{\"text\": \"Bitcoin is showing strong bullish signals\", \"mode\": \"general\"}'"

exec_curl "Analyze symbol sentiment (BTC)" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/sentiment' \
        -H 'Content-Type: application/json' \
        -d '{\"symbol\": \"BTC\", \"mode\": \"news\"}'"

exec_curl "Get latest news (limit 10)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/news?limit=10'"

exec_curl "Get latest news (limit 25)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/news?limit=25'"

exec_curl "Analyze news URL" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/news/analyze' \
        -H 'Content-Type: application/json' \
        -d '{\"url\": \"https://example.com/crypto-news\"}'"

exec_curl "Analyze news text" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/news/analyze' \
        -H 'Content-Type: application/json' \
        -d '{\"text\": \"Federal Reserve announces new crypto regulations\"}'"

# ============================================
# F. ECONOMIC / MACRO ANALYSIS
# ============================================

print_section "💰 F. ECONOMIC / MACRO ANALYSIS"

exec_curl "Economic analysis for USD (1 month)" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/econ-analysis' \
        -H 'Content-Type: application/json' \
        -d '{\"currency\": \"USD\", \"period\": \"1M\"}'"

exec_curl "Economic analysis for EUR (3 months)" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/econ-analysis' \
        -H 'Content-Type: application/json' \
        -d '{\"currency\": \"EUR\", \"period\": \"3M\", \"context\": \"ECB policy impact\"}'"

exec_curl "Economic analysis for JPY (1 year)" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/econ-analysis' \
        -H 'Content-Type: application/json' \
        -d '{\"currency\": \"JPY\", \"period\": \"1Y\"}'"

# ============================================
# G. WHALE TRACKING / ON-CHAIN
# ============================================

print_section "🐋 G. WHALE TRACKING / ON-CHAIN"

exec_curl "Get whale transactions (Ethereum, >$100k)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/whales?chain=ethereum&min_amount_usd=100000&limit=10'"

exec_curl "Get whale transactions (BSC, >$500k)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/whales?chain=bsc&min_amount_usd=500000&limit=20'"

exec_curl "Get whale transactions (Polygon, >$1M)" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/whales?chain=polygon&min_amount_usd=1000000&limit=50'"

exec_curl "Get on-chain data for address" \
    "curl -X GET '${BASE_URL}${API_PREFIX}/onchain?address=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb3&chain=ethereum'"

# ============================================
# H. MODEL PREDICTIONS / SIGNALS
# ============================================

print_section "🤖 H. MODEL PREDICTIONS / SIGNALS"

exec_curl "Get prediction from single model" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/models/price_lstm/predict' \
        -H 'Content-Type: application/json' \
        -d '{\"symbol\": \"BTC\", \"horizon\": \"24h\"}'"

exec_curl "Get prediction with features" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/models/sentiment_rf/predict' \
        -H 'Content-Type: application/json' \
        -d '{
            \"symbol\": \"ETH\", 
            \"horizon\": \"48h\",
            \"features\": {
                \"rsi\": 65,
                \"volume_24h\": 15000000000,
                \"sentiment_score\": 0.72
            }
        }'"

exec_curl "Batch model predictions" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/models/batch/predict' \
        -H 'Content-Type: application/json' \
        -d '{
            \"models\": [\"price_lstm\", \"sentiment_rf\", \"technical_xgb\"],
            \"request\": {
                \"symbol\": \"SOL\",
                \"horizon\": \"12h\"
            }
        }'"

# ============================================
# I. GENERIC QUERY ENDPOINT
# ============================================

print_section "🔧 I. GENERIC QUERY ENDPOINT"

exec_curl "Generic query - Get rate" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/query' \
        -H 'Content-Type: application/json' \
        -d '{\"type\": \"rate\", \"payload\": {\"pair\": \"BTC/USDT\"}}'"

exec_curl "Generic query - Get history" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/query' \
        -H 'Content-Type: application/json' \
        -d '{\"type\": \"history\", \"payload\": {\"symbol\": \"ETH\", \"interval\": 60, \"limit\": 5}}'"

exec_curl "Generic query - Sentiment analysis" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/query' \
        -H 'Content-Type: application/json' \
        -d '{\"type\": \"sentiment\", \"payload\": {\"text\": \"Crypto market rally\"}}'"

exec_curl "Generic query - Whale tracking" \
    "curl -X POST '${BASE_URL}${API_PREFIX}/query' \
        -H 'Content-Type: application/json' \
        -d '{\"type\": \"whales\", \"payload\": {\"chain\": \"ethereum\", \"min_amount_usd\": 250000}}'"

# ============================================
# SMOKE TESTS SUMMARY
# ============================================

print_section "✅ SMOKE TESTS SUMMARY"

echo -e "${YELLOW}Running comprehensive smoke tests...${NC}\n"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local cmd="$2"
    local expected_field="$3"
    
    echo -n "Testing $name... "
    
    RESPONSE=$(eval "$cmd" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$RESPONSE" ]; then
        if [ -n "$expected_field" ]; then
            FIELD_VALUE=$(echo "$RESPONSE" | jq -r "$expected_field" 2>/dev/null)
            if [ "$FIELD_VALUE" != "null" ] && [ -n "$FIELD_VALUE" ]; then
                echo -e "${GREEN}✓ PASSED${NC}"
                ((TESTS_PASSED++))
            else
                echo -e "${RED}✗ FAILED (missing $expected_field)${NC}"
                ((TESTS_FAILED++))
            fi
        else
            echo -e "${GREEN}✓ PASSED${NC}"
            ((TESTS_PASSED++))
        fi
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
}

# Run smoke tests
test_endpoint "Health" "curl -s '${BASE_URL}${API_PREFIX}/health'" ".status"
test_endpoint "Pair Metadata (HF)" "curl -s '${BASE_URL}${API_PREFIX}/pair/BTC-USDT'" ".meta.source"
test_endpoint "Rate" "curl -s '${BASE_URL}${API_PREFIX}/rate?pair=BTC/USDT'" ".price"
test_endpoint "History" "curl -s '${BASE_URL}${API_PREFIX}/history?symbol=BTC&interval=60&limit=5'" ".items[0].open"
test_endpoint "Market Status" "curl -s '${BASE_URL}${API_PREFIX}/market-status'" ".total_market_cap"
test_endpoint "Top Movers" "curl -s '${BASE_URL}${API_PREFIX}/top?n=5'" ".movers[0].symbol"
test_endpoint "News" "curl -s '${BASE_URL}${API_PREFIX}/news?limit=5'" ".items[0].id"
test_endpoint "Whales" "curl -s '${BASE_URL}${API_PREFIX}/whales?chain=ethereum&min_amount_usd=100000&limit=5'" ".transactions"
test_endpoint "Generic Query" "curl -s -X POST '${BASE_URL}${API_PREFIX}/query' -H 'Content-Type: application/json' -d '{\"type\":\"rate\",\"payload\":{\"pair\":\"BTC/USDT\"}}'" ".price"

# Summary
echo -e "\n${BLUE}============================================${NC}"
echo -e "${GREEN}SMOKE TEST RESULTS:${NC}"
echo -e "  Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "  Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ ALL SMOKE TESTS PASSED!${NC}"
else
    echo -e "\n${RED}✗ SOME TESTS FAILED - REVIEW REQUIRED${NC}"
fi

echo -e "${BLUE}============================================${NC}"

# ============================================
# PERFORMANCE TEST
# ============================================

print_section "⚡ PERFORMANCE TEST"

echo -e "${YELLOW}Testing response times...${NC}\n"

# Function to measure response time
measure_time() {
    local name="$1"
    local cmd="$2"
    
    echo -n "$name: "
    
    START=$(date +%s%N)
    eval "$cmd" > /dev/null 2>&1
    END=$(date +%s%N)
    
    ELAPSED=$((($END - $START) / 1000000))
    
    if [ $ELAPSED -lt 1500 ]; then
        echo -e "${GREEN}${ELAPSED}ms ✓${NC}"
    elif [ $ELAPSED -lt 4000 ]; then
        echo -e "${YELLOW}${ELAPSED}ms ⚠${NC}"
    else
        echo -e "${RED}${ELAPSED}ms ✗${NC}"
    fi
}

measure_time "Rate endpoint" "curl -s '${BASE_URL}${API_PREFIX}/rate?pair=BTC/USDT'"
measure_time "Pair metadata" "curl -s '${BASE_URL}${API_PREFIX}/pair/BTC-USDT'"
measure_time "History (small)" "curl -s '${BASE_URL}${API_PREFIX}/history?symbol=BTC&interval=60&limit=10'"
measure_time "Market status" "curl -s '${BASE_URL}${API_PREFIX}/market-status'"
measure_time "Top movers" "curl -s '${BASE_URL}${API_PREFIX}/top?n=10'"

# ============================================
# META VALIDATION
# ============================================

print_section "🔍 META BLOCK VALIDATION"

echo -e "${YELLOW}Validating meta blocks in responses...${NC}\n"

validate_meta() {
    local name="$1"
    local cmd="$2"
    
    echo -n "$name: "
    
    RESPONSE=$(eval "$cmd" 2>/dev/null)
    META=$(echo "$RESPONSE" | jq '.meta' 2>/dev/null)
    
    if [ -n "$META" ] && [ "$META" != "null" ]; then
        SOURCE=$(echo "$META" | jq -r '.source')
        GENERATED=$(echo "$META" | jq -r '.generated_at')
        TTL=$(echo "$META" | jq -r '.cache_ttl_seconds')
        
        if [ -n "$SOURCE" ] && [ -n "$GENERATED" ] && [ -n "$TTL" ]; then
            echo -e "${GREEN}✓ Valid meta (source: $SOURCE, ttl: ${TTL}s)${NC}"
        else
            echo -e "${YELLOW}⚠ Partial meta${NC}"
        fi
    else
        echo -e "${RED}✗ Missing meta${NC}"
    fi
}

validate_meta "Rate" "curl -s '${BASE_URL}${API_PREFIX}/rate?pair=BTC/USDT'"
validate_meta "Pair" "curl -s '${BASE_URL}${API_PREFIX}/pair/BTC-USDT'"
validate_meta "History" "curl -s '${BASE_URL}${API_PREFIX}/history?symbol=BTC&interval=60&limit=5'"
validate_meta "News" "curl -s '${BASE_URL}${API_PREFIX}/news?limit=5'"
validate_meta "Whales" "curl -s '${BASE_URL}${API_PREFIX}/whales?chain=ethereum&min_amount_usd=100000&limit=5'"

# ============================================
# FINAL MESSAGE
# ============================================

echo -e "\n${BLUE}============================================${NC}"
echo -e "${GREEN}📋 SERVICE USAGE EXAMPLES COMPLETE${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "\nTo run specific tests:"
echo -e "  ${YELLOW}./service_usage_examples.sh${NC} - Run all tests"
echo -e "  ${YELLOW}BASE_URL=https://your-space.hf.space ./service_usage_examples.sh${NC} - Test remote"
echo -e "\nFor production deployment:"
echo -e "  1. Ensure all smoke tests pass"
echo -e "  2. Verify pair metadata source is 'hf'"
echo -e "  3. Check response times are < 1.5s (cached) or < 4s (fallback)"
echo -e "  4. Confirm all responses include valid meta blocks"
echo -e "${BLUE}============================================${NC}"
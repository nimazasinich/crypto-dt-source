#!/bin/bash

# HuggingFace Space Integration Diagnostic Tool
# Version: 2.0
# Usage: bash diagnostic.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
HF_SPACE_URL="https://really-amin-datasourceforcryptocurrency.hf.space"
RESULTS_FILE="diagnostic_results_$(date +%Y%m%d_%H%M%S).log"

# Counter for tests
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Function to print section header
print_header() {
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo -e "${CYAN}$1${NC}"
    echo "════════════════════════════════════════════════════════"
}

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    local expected_status=${3:-200}

    echo -e "\n${BLUE}Testing:${NC} $description"
    echo "Endpoint: $endpoint"

    response=$(curl -s -w "\n%{http_code}" --connect-timeout 10 "$endpoint" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "HTTP Status: $http_code"

    if [ "$http_code" = "$expected_status" ]; then
        print_status 0 "$description"
        echo "Response preview:"
        echo "$body" | head -n 3
        return 0
    else
        print_status 1 "$description (Expected $expected_status, got $http_code)"
        echo "Error details:"
        echo "$body" | head -n 2
        return 1
    fi
}

# Start logging
exec > >(tee -a "$RESULTS_FILE")
exec 2>&1

# Print banner
clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║   HuggingFace Space Integration Diagnostic Tool       ║"
echo "║                     Version 2.0                        ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Starting diagnostic at $(date)"
echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Test 1: System Requirements
print_header "TEST 1: System Requirements"

echo "Checking required tools..."

node --version > /dev/null 2>&1
print_status $? "Node.js installed ($(node --version 2>/dev/null || echo 'N/A'))"

npm --version > /dev/null 2>&1
print_status $? "npm installed ($(npm --version 2>/dev/null || echo 'N/A'))"

curl --version > /dev/null 2>&1
print_status $? "curl installed"

git --version > /dev/null 2>&1
print_status $? "git installed"

command -v jq > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_status 0 "jq installed (JSON processor)"
else
    print_status 1 "jq installed (optional but recommended)"
fi

# Test 2: Project Structure
print_header "TEST 2: Project Structure"

[ -f "package.json" ]
print_status $? "package.json exists"

[ -f ".env.example" ]
print_status $? ".env.example exists"

[ -d "hf-data-engine" ]
print_status $? "hf-data-engine directory exists"

[ -f "hf-data-engine/main.py" ]
print_status $? "HuggingFace engine implementation exists"

[ -f "hf-data-engine/requirements.txt" ]
print_status $? "Python requirements.txt exists"

[ -f "HUGGINGFACE_DIAGNOSTIC_GUIDE.md" ]
print_status $? "Diagnostic guide documentation exists"

# Test 3: Environment Configuration
print_header "TEST 3: Environment Configuration"

if [ -f ".env" ]; then
    print_status 0 ".env file exists"

    grep -q "PRIMARY_DATA_SOURCE" .env
    print_status $? "PRIMARY_DATA_SOURCE configured"

    grep -q "HF_SPACE_BASE_URL\|HF_SPACE_URL" .env
    print_status $? "HuggingFace Space URL configured"

    echo ""
    echo "Current configuration (sensitive values hidden):"
    grep "PRIMARY_DATA_SOURCE\|HF_SPACE\|FALLBACK" .env | sed 's/=.*/=***/' | sort || true
else
    print_status 1 ".env file exists"
    echo ""
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env created. Edit it with your configuration."
    fi
fi

# Test 4: HuggingFace Space Connectivity
print_header "TEST 4: HuggingFace Space Connectivity"

echo "Resolving DNS..."
host really-amin-datasourceforcryptocurrency.hf.space > /dev/null 2>&1
print_status $? "DNS resolution for HF Space"

echo ""
echo "Testing basic connectivity..."
ping -c 1 -W 5 hf.space > /dev/null 2>&1
print_status $? "Network connectivity to hf.space"

# Test 5: HuggingFace Space Endpoints
print_header "TEST 5: HuggingFace Space Endpoints"

echo "Testing primary endpoints..."

test_endpoint "$HF_SPACE_URL/api/health" "Health check endpoint"
test_endpoint "$HF_SPACE_URL/api/prices?symbols=BTC,ETH" "Prices endpoint"
test_endpoint "$HF_SPACE_URL/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=10" "OHLCV endpoint"
test_endpoint "$HF_SPACE_URL/api/market/overview" "Market overview endpoint"
test_endpoint "$HF_SPACE_URL/api/sentiment" "Sentiment endpoint"

# Test 6: CORS Configuration
print_header "TEST 6: CORS Configuration"

echo "Checking CORS headers..."
cors_response=$(curl -s -I -H "Origin: http://localhost:5173" "$HF_SPACE_URL/api/prices?symbols=BTC" 2>&1)
cors_headers=$(echo "$cors_response" | grep -i "access-control")

if [ -z "$cors_headers" ]; then
    print_status 1 "CORS headers present"
    echo ""
    echo "⚠️  No CORS headers found. This may cause browser errors."
    echo "    Solution: Use Vite proxy (see Configuration Guide)"
else
    print_status 0 "CORS headers present"
    echo "CORS headers found:"
    echo "$cors_headers" | sed 's/^/    /'
fi

# Test 7: Response Format Validation
print_header "TEST 7: Response Format Validation"

echo "Fetching sample data..."
sample_response=$(curl -s "$HF_SPACE_URL/api/prices?symbols=BTC" 2>&1)

if command -v jq > /dev/null 2>&1; then
    if echo "$sample_response" | jq . > /dev/null 2>&1; then
        print_status 0 "Valid JSON response"
        echo ""
        echo "Response structure:"
        if echo "$sample_response" | jq 'keys' 2>/dev/null | grep -q "."; then
            echo "$sample_response" | jq 'if type == "array" then .[0] else . end | keys' 2>/dev/null | sed 's/^/    /'
        else
            echo "    (Unable to determine structure)"
        fi
    else
        print_status 1 "Valid JSON response"
        echo "Response is not valid JSON:"
        echo "$sample_response" | head -n 2 | sed 's/^/    /'
    fi
else
    echo "⚠️  jq not installed, skipping JSON validation"
    echo "    Install with: sudo apt-get install jq (Ubuntu) or brew install jq (Mac)"
fi

# Test 8: Node Dependencies
print_header "TEST 8: Node Dependencies"

if [ -d "node_modules" ]; then
    print_status 0 "node_modules exists"

    [ -d "node_modules/typescript" ]
    print_status $? "TypeScript installed"

    [ -d "node_modules/vite" ]
    print_status $? "Vite installed"

    [ -d "node_modules/react" ]
    print_status $? "React installed"

    # Count total packages
    package_count=$(ls -1 node_modules 2>/dev/null | grep -v "^\." | wc -l)
    echo "    Total packages installed: $package_count"
else
    print_status 1 "node_modules exists"
    echo ""
    echo "⚠️  Run: npm install"
fi

# Test 9: Python Dependencies (if backend is present)
print_header "TEST 9: Python Dependencies"

if [ -f "hf-data-engine/requirements.txt" ]; then
    print_status 0 "requirements.txt exists"

    python3 -c "import fastapi" 2>/dev/null
    [ $? -eq 0 ] && fastapi_status="✅" || fastapi_status="❌"
    echo "    FastAPI: $fastapi_status"

    python3 -c "import aiohttp" 2>/dev/null
    [ $? -eq 0 ] && aiohttp_status="✅" || aiohttp_status="❌"
    echo "    aiohttp: $aiohttp_status"

    python3 -c "import pydantic" 2>/dev/null
    [ $? -eq 0 ] && pydantic_status="✅" || pydantic_status="❌"
    echo "    pydantic: $pydantic_status"
else
    print_status 1 "requirements.txt exists"
fi

# Summary
print_header "DIAGNOSTIC SUMMARY"

total_status=$((PASSED_TESTS + FAILED_TESTS))
if [ $total_status -gt 0 ]; then
    pass_rate=$((PASSED_TESTS * 100 / total_status))
    echo "Results: ${GREEN}$PASSED_TESTS passed${NC}, ${RED}$FAILED_TESTS failed${NC} (${pass_rate}%)"
fi
echo ""
echo "Results saved to: $RESULTS_FILE"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: npm run dev"
    echo "  2. Open: http://localhost:5173"
    echo "  3. Check browser console (F12) for any errors"
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review the failed tests above"
    echo "  2. Check HUGGINGFACE_DIAGNOSTIC_GUIDE.md for solutions"
    echo "  3. Run this script again after fixes"
fi

echo ""
echo "Full diagnostic completed at $(date)"
echo ""

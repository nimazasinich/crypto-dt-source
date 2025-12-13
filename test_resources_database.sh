#!/bin/bash

# Test script for Resources Database API endpoints
# Tests all 6 new endpoints with various parameters

BASE_URL="http://localhost:7860"
PASS=0
FAIL=0

echo "========================================="
echo "Testing Resources Database API Endpoints"
echo "========================================="
echo ""

# Test 1: Get all resources
echo "Test 1: GET /api/resources/database (all resources)"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database?source=all&limit=10")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 2: Get unified resources only
echo "Test 2: GET /api/resources/database (unified only)"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database?source=unified&limit=5")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 3: Get pipeline resources only
echo "Test 3: GET /api/resources/database (pipeline only)"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database?source=pipeline&limit=5")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 4: Get categories
echo "Test 4: GET /api/resources/database/categories"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/categories")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 5: Get resources by category (RPC nodes)
echo "Test 5: GET /api/resources/database/category/rpc_nodes"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/category/rpc_nodes")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 6: Get resources by category (block explorers)
echo "Test 6: GET /api/resources/database/category/block_explorers"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/category/block_explorers?limit=10")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 7: Get resources by category (market data)
echo "Test 7: GET /api/resources/database/category/market_data_apis"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/category/market_data_apis")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 8: Search resources (bitcoin)
echo "Test 8: GET /api/resources/database/search?q=bitcoin"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/search?q=bitcoin&limit=10")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 9: Search resources (coingecko)
echo "Test 9: GET /api/resources/database/search?q=coingecko"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/search?q=coingecko&fields=name,url&limit=5")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 10: Search resources (binance)
echo "Test 10: GET /api/resources/database/search?q=binance"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/search?q=binance&fields=name,desc&limit=10")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 11: Get database stats
echo "Test 11: GET /api/resources/database/stats"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/stats")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 12: Get random resources (default count)
echo "Test 12: GET /api/resources/database/random"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/random")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 13: Get random resources (custom count)
echo "Test 13: GET /api/resources/database/random?count=5"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/random?count=5")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 14: Get random resources from specific category
echo "Test 14: GET /api/resources/database/random?count=3&category=market_data_apis"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database/random?count=3&category=market_data_apis")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Test 15: Get resources with filter by category parameter
echo "Test 15: GET /api/resources/database?category=news_apis"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/resources/database?category=news_apis&source=all")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS - Status: $RESPONSE"
    ((PASS++))
else
    echo "❌ FAIL - Status: $RESPONSE (expected 200)"
    ((FAIL++))
fi
echo ""

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "Total Tests: $((PASS + FAIL))"
echo "✅ Passed: $PASS"
echo "❌ Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed"
    exit 1
fi

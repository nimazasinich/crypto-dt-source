#!/bin/bash
# CLI Sanity Checks for Chart Endpoints
# Run these commands to validate the chart endpoints are working correctly

set -e  # Exit on error

BASE_URL="http://localhost:7860"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}=== Chart Endpoints Sanity Checks ===${NC}\n"

# Function to print test results
print_test() {
    local test_name="$1"
    local status="$2"
    if [ "$status" -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $test_name"
    else
        echo -e "${RED}✗${NC} $test_name"
        return 1
    fi
}

# Test 1: Rate-limit history (defaults: last 24h, up to 5 providers)
echo -e "${BOLD}Test 1: Rate Limit History (default parameters)${NC}"
RESPONSE=$(curl -s "${BASE_URL}/api/charts/rate-limit-history")
PROVIDER=$(echo "$RESPONSE" | jq -r '.[0].provider // empty')
SERIES_LENGTH=$(echo "$RESPONSE" | jq '.[0].series | length // 0')

if [ -n "$PROVIDER" ] && [ "$SERIES_LENGTH" -gt 0 ]; then
    echo "$RESPONSE" | jq '.[0] | {provider, series_count: (.series|length), hours}'
    print_test "Rate limit history with defaults" 0
else
    echo "Response: $RESPONSE"
    print_test "Rate limit history with defaults" 1
fi
echo ""

# Test 2: Freshness history (defaults: last 24h, up to 5 providers)
echo -e "${BOLD}Test 2: Freshness History (default parameters)${NC}"
RESPONSE=$(curl -s "${BASE_URL}/api/charts/freshness-history")
PROVIDER=$(echo "$RESPONSE" | jq -r '.[0].provider // empty')
SERIES_LENGTH=$(echo "$RESPONSE" | jq '.[0].series | length // 0')

if [ -n "$PROVIDER" ] && [ "$SERIES_LENGTH" -gt 0 ]; then
    echo "$RESPONSE" | jq '.[0] | {provider, series_count: (.series|length), hours}'
    print_test "Freshness history with defaults" 0
else
    echo "Response: $RESPONSE"
    print_test "Freshness history with defaults" 1
fi
echo ""

# Test 3: Custom time ranges & selection (48 hours)
echo -e "${BOLD}Test 3: Rate Limit History (48 hours, specific providers)${NC}"
RESPONSE=$(curl -s "${BASE_URL}/api/charts/rate-limit-history?hours=48&providers=coingecko,cmc,etherscan")
SERIES_COUNT=$(echo "$RESPONSE" | jq 'length')

echo "Providers returned: $SERIES_COUNT"
echo "$RESPONSE" | jq '.[] | {provider, hours, series_count: (.series|length)}'

if [ "$SERIES_COUNT" -le 3 ] && [ "$SERIES_COUNT" -gt 0 ]; then
    print_test "Rate limit history with custom parameters" 0
else
    print_test "Rate limit history with custom parameters" 1
fi
echo ""

# Test 4: Custom freshness query (72 hours)
echo -e "${BOLD}Test 4: Freshness History (72 hours, specific providers)${NC}"
RESPONSE=$(curl -s "${BASE_URL}/api/charts/freshness-history?hours=72&providers=coingecko,binance")
SERIES_COUNT=$(echo "$RESPONSE" | jq 'length')

echo "Providers returned: $SERIES_COUNT"
echo "$RESPONSE" | jq '.[] | {provider, hours, series_count: (.series|length)}'

if [ "$SERIES_COUNT" -le 2 ] && [ "$SERIES_COUNT" -ge 0 ]; then
    print_test "Freshness history with custom parameters" 0
else
    print_test "Freshness history with custom parameters" 1
fi
echo ""

# Test 5: Validate response schema (Rate Limit)
echo -e "${BOLD}Test 5: Validate Rate Limit Response Schema${NC}"
RESPONSE=$(curl -s "${BASE_URL}/api/charts/rate-limit-history")

# Check required fields
HAS_PROVIDER=$(echo "$RESPONSE" | jq '.[0] | has("provider")')
HAS_HOURS=$(echo "$RESPONSE" | jq '.[0] | has("hours")')
HAS_SERIES=$(echo "$RESPONSE" | jq '.[0] | has("series")')
HAS_META=$(echo "$RESPONSE" | jq '.[0] | has("meta")')

# Check point structure
FIRST_POINT=$(echo "$RESPONSE" | jq '.[0].series[0]')
HAS_T=$(echo "$FIRST_POINT" | jq 'has("t")')
HAS_PCT=$(echo "$FIRST_POINT" | jq 'has("pct")')
PCT_VALID=$(echo "$FIRST_POINT" | jq '.pct >= 0 and .pct <= 100')

echo "Schema validation:"
echo "  - Has provider: $HAS_PROVIDER"
echo "  - Has hours: $HAS_HOURS"
echo "  - Has series: $HAS_SERIES"
echo "  - Has meta: $HAS_META"
echo "  - Point has timestamp (t): $HAS_T"
echo "  - Point has percentage (pct): $HAS_PCT"
echo "  - Percentage in range [0,100]: $PCT_VALID"

if [ "$HAS_PROVIDER" == "true" ] && [ "$HAS_SERIES" == "true" ] && [ "$PCT_VALID" == "true" ]; then
    print_test "Rate limit schema validation" 0
else
    print_test "Rate limit schema validation" 1
fi
echo ""

# Test 6: Validate response schema (Freshness)
echo -e "${BOLD}Test 6: Validate Freshness Response Schema${NC}"
RESPONSE=$(curl -s "${BASE_URL}/api/charts/freshness-history")

# Check point structure
FIRST_POINT=$(echo "$RESPONSE" | jq '.[0].series[0]')
HAS_STALENESS=$(echo "$FIRST_POINT" | jq 'has("staleness_min")')
HAS_TTL=$(echo "$FIRST_POINT" | jq 'has("ttl_min")')
HAS_STATUS=$(echo "$FIRST_POINT" | jq 'has("status")')
STATUS_VALUE=$(echo "$FIRST_POINT" | jq -r '.status')

echo "Schema validation:"
echo "  - Point has staleness_min: $HAS_STALENESS"
echo "  - Point has ttl_min: $HAS_TTL"
echo "  - Point has status: $HAS_STATUS"
echo "  - Status value: $STATUS_VALUE"

if [ "$HAS_STALENESS" == "true" ] && [ "$HAS_TTL" == "true" ] && [ -n "$STATUS_VALUE" ]; then
    print_test "Freshness schema validation" 0
else
    print_test "Freshness schema validation" 1
fi
echo ""

# Test 7: Edge case - Invalid provider
echo -e "${BOLD}Test 7: Edge Case - Invalid Provider${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/charts/rate-limit-history?providers=invalid_xyz")
echo "HTTP Status for invalid provider: $HTTP_STATUS"

if [ "$HTTP_STATUS" -eq 400 ] || [ "$HTTP_STATUS" -eq 404 ]; then
    print_test "Invalid provider rejection" 0
else
    print_test "Invalid provider rejection" 1
fi
echo ""

# Test 8: Edge case - Hours out of bounds
echo -e "${BOLD}Test 8: Edge Case - Hours Clamping${NC}"
HTTP_STATUS_LOW=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/charts/rate-limit-history?hours=0")
HTTP_STATUS_HIGH=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/charts/rate-limit-history?hours=999")
echo "HTTP Status for hours=0: $HTTP_STATUS_LOW"
echo "HTTP Status for hours=999: $HTTP_STATUS_HIGH"

if [ "$HTTP_STATUS_LOW" -eq 200 ] || [ "$HTTP_STATUS_LOW" -eq 422 ]; then
    if [ "$HTTP_STATUS_HIGH" -eq 200 ] || [ "$HTTP_STATUS_HIGH" -eq 422 ]; then
        print_test "Hours parameter validation" 0
    else
        print_test "Hours parameter validation" 1
    fi
else
    print_test "Hours parameter validation" 1
fi
echo ""

# Test 9: Performance check
echo -e "${BOLD}Test 9: Performance Check (P95 < 200ms target)${NC}"
START=$(date +%s%N)
curl -s "${BASE_URL}/api/charts/rate-limit-history" > /dev/null
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))  # Convert to milliseconds

echo "Response time: ${DURATION}ms"

if [ "$DURATION" -lt 500 ]; then
    print_test "Performance within acceptable range (<500ms for dev)" 0
else
    echo "Warning: Response time above target (acceptable for dev environment)"
    print_test "Performance check" 1
fi
echo ""

# Summary
echo -e "${BOLD}=== Sanity Checks Complete ===${NC}"
echo ""
echo "Next steps:"
echo "1. Run full pytest suite: pytest tests/test_charts.py -v"
echo "2. Check UI integration in browser at http://localhost:7860"
echo "3. Monitor logs for any warnings or errors"

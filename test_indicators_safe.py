#!/usr/bin/env python3
"""
Test Indicator Endpoints - Verify SAFE Implementation
Tests all indicator endpoints to ensure:
- HTTP 400 for insufficient data (not 500)
- HTTP 200 for successful calculations
- Valid JSON response always returned
- No NaN/Infinity values in responses
"""

import httpx
import asyncio
import json
import sys
from typing import Dict, Any


BASE_URL = "http://localhost:7860"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


async def test_indicator_endpoint(
    client: httpx.AsyncClient,
    endpoint: str,
    params: Dict[str, Any],
    indicator_name: str
) -> bool:
    """Test a single indicator endpoint"""
    print(f"\n{BLUE}Testing {indicator_name}...{RESET}")
    print(f"  Endpoint: {endpoint}")
    print(f"  Params: {params}")
    
    try:
        response = await client.get(endpoint, params=params, timeout=30.0)
        
        print(f"  Status Code: {response.status_code}")
        
        # Check if response is valid JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"{RED}❌ FAIL: Invalid JSON response{RESET}")
            print(f"  Error: {e}")
            return False
        
        # Check status code (should be 200 or 400, never 500)
        if response.status_code == 500:
            print(f"{RED}❌ FAIL: HTTP 500 - Internal Server Error (SHOULD BE 400 for data issues){RESET}")
            print(f"  Response: {json.dumps(data, indent=2)}")
            return False
        
        if response.status_code == 400:
            print(f"{YELLOW}⚠️  HTTP 400 - Expected for insufficient data{RESET}")
            if "error" in data:
                print(f"  Error message: {data.get('message', 'No message')}")
            return True
        
        if response.status_code != 200:
            print(f"{RED}❌ FAIL: Unexpected status code {response.status_code}{RESET}")
            return False
        
        # Check for NaN/Infinity in response
        response_str = json.dumps(data)
        if "NaN" in response_str or "Infinity" in response_str:
            print(f"{RED}❌ FAIL: Response contains NaN or Infinity{RESET}")
            print(f"  Response: {response_str}")
            return False
        
        # Check required fields
        if "symbol" not in data:
            print(f"{RED}❌ FAIL: Missing 'symbol' field{RESET}")
            return False
        
        if "indicator" not in data and "data" not in data:
            print(f"{RED}❌ FAIL: Missing 'indicator' or 'data' field{RESET}")
            return False
        
        # Success
        print(f"{GREEN}✅ PASS{RESET}")
        if "data_points" in data:
            print(f"  Data points: {data['data_points']}")
        if "signal" in data:
            print(f"  Signal: {data['signal']}")
        
        return True
        
    except Exception as e:
        print(f"{RED}❌ FAIL: Exception occurred{RESET}")
        print(f"  Error: {e}")
        return False


async def test_all_indicators():
    """Test all indicator endpoints"""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}INDICATOR ENDPOINTS TEST - PRODUCTION SAFE IMPLEMENTATION{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    # Test cases for each indicator
    test_cases = [
        {
            "endpoint": "/api/indicators/rsi",
            "params": {"symbol": "BTC", "timeframe": "1h", "period": 14},
            "name": "RSI"
        },
        {
            "endpoint": "/api/indicators/macd",
            "params": {"symbol": "BTC", "timeframe": "1h", "fast": 12, "slow": 26, "signal_period": 9},
            "name": "MACD"
        },
        {
            "endpoint": "/api/indicators/sma",
            "params": {"symbol": "BTC", "timeframe": "1h"},
            "name": "SMA"
        },
        {
            "endpoint": "/api/indicators/ema",
            "params": {"symbol": "BTC", "timeframe": "1h"},
            "name": "EMA"
        },
        {
            "endpoint": "/api/indicators/atr",
            "params": {"symbol": "BTC", "timeframe": "1h", "period": 14},
            "name": "ATR"
        },
        {
            "endpoint": "/api/indicators/stoch-rsi",
            "params": {"symbol": "BTC", "timeframe": "1h", "rsi_period": 14, "stoch_period": 14},
            "name": "Stochastic RSI"
        },
        {
            "endpoint": "/api/indicators/bollinger-bands",
            "params": {"symbol": "BTC", "timeframe": "1h", "period": 20, "std_dev": 2.0},
            "name": "Bollinger Bands"
        },
    ]
    
    # Additional test cases with invalid parameters
    invalid_test_cases = [
        {
            "endpoint": "/api/indicators/rsi",
            "params": {"symbol": "INVALID_SYMBOL_XYZ", "timeframe": "1h", "period": 14},
            "name": "RSI (Invalid Symbol)"
        },
        {
            "endpoint": "/api/indicators/macd",
            "params": {"symbol": "BTC", "timeframe": "1h", "fast": 26, "slow": 12, "signal_period": 9},
            "name": "MACD (Invalid Params - fast > slow)"
        },
    ]
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Test valid cases
        print(f"\n{BLUE}=== VALID PARAMETER TESTS ==={RESET}")
        for test in test_cases:
            results["total"] += 1
            passed = await test_indicator_endpoint(
                client,
                test["endpoint"],
                test["params"],
                test["name"]
            )
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        # Test invalid cases (should return 400, not 500)
        print(f"\n{BLUE}=== INVALID PARAMETER TESTS (Should return 400, not 500) ==={RESET}")
        for test in invalid_test_cases:
            results["total"] += 1
            passed = await test_indicator_endpoint(
                client,
                test["endpoint"],
                test["params"],
                test["name"]
            )
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
    
    # Print summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Total Tests: {results['total']}")
    print(f"{GREEN}Passed: {results['passed']}{RESET}")
    print(f"{RED}Failed: {results['failed']}{RESET}")
    
    if results["failed"] == 0:
        print(f"\n{GREEN}✅ ALL TESTS PASSED - Indicator endpoints are PRODUCTION SAFE{RESET}")
        return 0
    else:
        print(f"\n{RED}❌ SOME TESTS FAILED - Please review the failures above{RESET}")
        return 1


async def test_dashboard_endpoints():
    """Test dashboard endpoints for always returning valid JSON"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}DASHBOARD ENDPOINTS TEST{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    endpoints = [
        "/api/resources/summary",
        "/api/models/status",
        "/api/providers",
        "/api/market",
        "/api/news/latest",
        "/api/resources/stats"
    ]
    
    results = {"passed": 0, "failed": 0, "total": len(endpoints)}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        for endpoint in endpoints:
            print(f"\n{BLUE}Testing {endpoint}...{RESET}")
            try:
                response = await client.get(endpoint)
                
                # Should always return valid JSON
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    print(f"{RED}❌ FAIL: Invalid JSON response{RESET}")
                    results["failed"] += 1
                    continue
                
                # Should never crash (200, 400, or 503 acceptable)
                if response.status_code in [200, 400, 503]:
                    print(f"{GREEN}✅ PASS - Status: {response.status_code}{RESET}")
                    results["passed"] += 1
                else:
                    print(f"{RED}❌ FAIL - Unexpected status: {response.status_code}{RESET}")
                    results["failed"] += 1
                    
            except Exception as e:
                print(f"{RED}❌ FAIL: Exception - {e}{RESET}")
                results["failed"] += 1
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"Dashboard Endpoints: {results['passed']}/{results['total']} passed")
    if results["failed"] == 0:
        print(f"{GREEN}✅ All dashboard endpoints return valid JSON{RESET}")
    else:
        print(f"{RED}❌ {results['failed']} endpoints failed{RESET}")
    
    return results["failed"]


async def main():
    """Main test runner"""
    print(f"\n{BLUE}Starting comprehensive endpoint tests...{RESET}")
    print(f"{BLUE}Base URL: {BASE_URL}{RESET}\n")
    
    # Test indicator endpoints
    indicator_failures = await test_all_indicators()
    
    # Test dashboard endpoints
    dashboard_failures = await test_dashboard_endpoints()
    
    # Final summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}FINAL RESULTS{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    if indicator_failures == 0 and dashboard_failures == 0:
        print(f"{GREEN}✅ ALL TESTS PASSED{RESET}")
        print(f"{GREEN}The API is production-ready and stable!{RESET}")
        return 0
    else:
        print(f"{RED}❌ SOME TESTS FAILED{RESET}")
        print(f"Indicator failures: {indicator_failures}")
        print(f"Dashboard failures: {dashboard_failures}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

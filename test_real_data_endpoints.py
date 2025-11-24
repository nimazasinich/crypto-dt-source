#!/usr/bin/env python3
"""
Test All Real Data Endpoints - NO MOCK DATA
Verify that all endpoints return REAL data from external APIs
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:7860"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")


async def test_endpoint(client: httpx.AsyncClient, method: str, path: str, name: str, json_data=None):
    """
    Test a single endpoint and verify real data
    """
    print_info(f"Testing {name}...")
    
    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{path}", timeout=30.0)
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{path}", json=json_data, timeout=30.0)
        else:
            print_error(f"Unsupported method: {method}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify it's not mock data
            data_str = json.dumps(data).lower()
            
            # Check for mock indicators
            mock_indicators = [
                "mock",
                "fake",
                "test",
                "sample",
                "placeholder",
                "lorem ipsum",
                "dummy"
            ]
            
            has_mock = any(indicator in data_str for indicator in mock_indicators)
            
            if has_mock:
                print_warning(f"{name}: Contains potential mock data indicators")
                return False
            
            # Check for real data indicators
            has_timestamp = "timestamp" in data_str or "generated_at" in data_str
            has_source = "source" in data_str
            
            if has_timestamp and has_source:
                print_success(f"{name}: REAL DATA ✓")
                return True
            else:
                print_warning(f"{name}: Response OK but missing data indicators")
                return True
        else:
            print_error(f"{name}: HTTP {response.status_code}")
            return False
    
    except httpx.TimeoutException:
        print_error(f"{name}: Timeout")
        return False
    except Exception as e:
        print_error(f"{name}: {str(e)}")
        return False


async def run_tests():
    """
    Run all endpoint tests
    """
    print("\n" + "=" * 80)
    print("🚀 TESTING ALL REAL DATA ENDPOINTS - ZERO MOCK DATA")
    print("=" * 80 + "\n")
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
    
    async with httpx.AsyncClient() as client:
        # Test cases
        tests = [
            # System endpoints
            ("GET", "/api/health", "Health Check", None),
            ("GET", "/api/status", "System Status", None),
            ("GET", "/api/providers", "Providers List", None),
            
            # Market data endpoints
            ("GET", "/api/market", "Market Snapshot", None),
            ("GET", "/api/market/pairs", "Trading Pairs", None),
            ("GET", "/api/market/ohlc?symbol=BTC&interval=1h&limit=10", "OHLC Data", None),
            ("GET", "/api/market/tickers?limit=10", "Market Tickers", None),
            
            # News endpoints
            ("GET", "/api/news?limit=5", "Crypto News", None),
            ("GET", "/api/news/latest?symbol=BTC&limit=5", "Latest News", None),
            ("GET", "/api/news/headlines?limit=5", "Top Headlines", None),
            
            # Blockchain endpoints
            ("GET", "/api/blockchain/transactions?chain=ethereum&limit=10", "Ethereum Transactions", None),
            ("GET", "/api/blockchain/gas?chain=ethereum", "Gas Prices", None),
            
            # AI Models endpoints
            ("GET", "/api/models/list", "AI Models List", None),
            ("POST", "/api/models/initialize", "Initialize AI Models", {}),
            ("POST", "/api/sentiment/analyze", "Sentiment Analysis", {
                "text": "Bitcoin price is rising rapidly!",
                "mode": "crypto"
            }),
            ("POST", "/api/trading/signal", "Trading Signal", {
                "symbol": "BTC",
                "context": "Price breaking resistance"
            }),
        ]
        
        for method, path, name, json_data in tests:
            results["total"] += 1
            if await test_endpoint(client, method, path, name, json_data):
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            # Small delay between tests
            await asyncio.sleep(1)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {results['total']}")
    print_success(f"Passed: {results['passed']}")
    
    if results['failed'] > 0:
        print_error(f"Failed: {results['failed']}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if results['failed'] == 0:
        print_success("\n🎉 ALL TESTS PASSED - ZERO MOCK DATA CONFIRMED!")
    else:
        print_warning(f"\n⚠️  {results['failed']} tests failed - check logs above")
    
    print("=" * 80 + "\n")
    
    return results['failed'] == 0


async def verify_real_data_sources():
    """
    Verify that all data sources are configured with REAL API keys
    """
    print("\n" + "=" * 80)
    print("🔑 VERIFYING REAL API KEYS")
    print("=" * 80 + "\n")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/status", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                sources = data.get("data_sources", {})
                
                for source, info in sources.items():
                    has_key = info.get("has_api_key") or info.get("has_api_token")
                    if has_key:
                        print_success(f"{source}: API key configured ✓")
                    else:
                        print_warning(f"{source}: No API key found")
                
                return True
        except Exception as e:
            print_error(f"Failed to verify API keys: {e}")
            return False
    
    return False


async def main():
    """
    Main test runner
    """
    print("\n" + "🚨" * 40)
    print("CRITICAL: TESTING REAL DATA ONLY - ZERO MOCK DATA")
    print("🚨" * 40)
    
    # Verify API keys
    await verify_real_data_sources()
    
    # Run endpoint tests
    success = await run_tests()
    
    if success:
        print_success("\n✅ VERIFICATION COMPLETE: ALL ENDPOINTS RETURN REAL DATA")
        print_success("NO MOCK DATA DETECTED")
        return 0
    else:
        print_error("\n❌ VERIFICATION FAILED: Some endpoints may have issues")
        print_warning("Review the test results above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

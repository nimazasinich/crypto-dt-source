"""
Test script for the Crypto Resource Aggregator
Tests all endpoints and resources to ensure they're working correctly
"""

import requests
import json
import time
from typing import Dict, List

# Configuration
BASE_URL = "http://localhost:7860"

# Test results
test_results = {"passed": 0, "failed": 0, "tests": []}


def log_test(name: str, passed: bool, message: str = ""):
    """Log a test result"""
    status = "✓ PASSED" if passed else "✗ FAILED"
    print(f"{status}: {name}")
    if message:
        print(f"  → {message}")

    test_results["tests"].append({"name": name, "passed": passed, "message": message})

    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1


def test_health_check():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Health Check", data.get("status") == "healthy", f"Status: {data.get('status')}"
            )
            return True
        else:
            log_test("Health Check", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False


def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            has_endpoints = "endpoints" in data
            log_test("Root Endpoint", has_endpoints, f"Version: {data.get('version', 'Unknown')}")
            return True
        else:
            log_test("Root Endpoint", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Root Endpoint", False, str(e))
        return False


def test_list_resources():
    """Test listing all resources"""
    try:
        response = requests.get(f"{BASE_URL}/resources", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_categories", 0)
            log_test("List Resources", total > 0, f"Found {total} categories")
            return data
        else:
            log_test("List Resources", False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_test("List Resources", False, str(e))
        return None


def test_get_category(category: str):
    """Test getting resources from a specific category"""
    try:
        response = requests.get(f"{BASE_URL}/resources/{category}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            log_test(f"Get Category: {category}", True, f"Found {count} resources")
            return data
        else:
            log_test(f"Get Category: {category}", False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_test(f"Get Category: {category}", False, str(e))
        return None


def test_query_coingecko():
    """Test querying CoinGecko for Bitcoin price"""
    try:
        payload = {
            "resource_type": "market_data",
            "resource_name": "coingecko",
            "endpoint": "/simple/price",
            "params": {"ids": "bitcoin", "vs_currencies": "usd"},
        }

        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)

            if success and data.get("data"):
                btc_price = data["data"].get("bitcoin", {}).get("usd")
                log_test("Query CoinGecko (Bitcoin Price)", True, f"BTC Price: ${btc_price:,.2f}")
                return True
            else:
                log_test(
                    "Query CoinGecko (Bitcoin Price)", False, data.get("error", "Unknown error")
                )
                return False
        else:
            log_test("Query CoinGecko (Bitcoin Price)", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Query CoinGecko (Bitcoin Price)", False, str(e))
        return False


def test_query_etherscan():
    """Test querying Etherscan for gas prices"""
    try:
        payload = {
            "resource_type": "block_explorers",
            "resource_name": "etherscan",
            "params": {"module": "gastracker", "action": "gasoracle"},
        }

        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)

            if success and data.get("data"):
                result = data["data"].get("result", {})
                safe_gas = result.get("SafeGasPrice", "N/A")
                log_test("Query Etherscan (Gas Oracle)", True, f"Safe Gas Price: {safe_gas} Gwei")
                return True
            else:
                log_test("Query Etherscan (Gas Oracle)", False, data.get("error", "Unknown error"))
                return False
        else:
            log_test("Query Etherscan (Gas Oracle)", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Query Etherscan (Gas Oracle)", False, str(e))
        return False


def test_status_check():
    """Test getting status of all resources"""
    try:
        print("\nChecking resource status (this may take a moment)...")
        response = requests.get(f"{BASE_URL}/status", timeout=60)

        if response.status_code == 200:
            data = response.json()
            total = data.get("total_resources", 0)
            online = data.get("online", 0)
            offline = data.get("offline", 0)

            log_test(
                "Status Check (All Resources)",
                True,
                f"{online}/{total} resources online, {offline} offline",
            )

            # Show details of offline resources
            if offline > 0:
                print("  Offline resources:")
                for resource in data.get("resources", []):
                    if resource["status"] == "offline":
                        print(f"    - {resource['resource']}: {resource.get('error', 'Unknown')}")

            return True
        else:
            log_test("Status Check (All Resources)", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Status Check (All Resources)", False, str(e))
        return False


def test_history():
    """Test getting query history"""
    try:
        response = requests.get(f"{BASE_URL}/history?limit=10", timeout=10)

        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            log_test("Query History", True, f"Retrieved {count} history records")
            return True
        else:
            log_test("Query History", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Query History", False, str(e))
        return False


def test_history_stats():
    """Test getting history statistics"""
    try:
        response = requests.get(f"{BASE_URL}/history/stats", timeout=10)

        if response.status_code == 200:
            data = response.json()
            total_queries = data.get("total_queries", 0)
            success_rate = data.get("success_rate", 0)

            log_test(
                "History Statistics",
                True,
                f"{total_queries} total queries, {success_rate:.1f}% success rate",
            )

            # Show most queried resources
            most_queried = data.get("most_queried_resources", [])
            if most_queried:
                print("  Most queried resources:")
                for resource in most_queried[:3]:
                    print(f"    - {resource['resource']}: {resource['count']} queries")

            return True
        else:
            log_test("History Statistics", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("History Statistics", False, str(e))
        return False


def test_multiple_coins():
    """Test querying multiple cryptocurrencies"""
    try:
        payload = {
            "resource_type": "market_data",
            "resource_name": "coingecko",
            "endpoint": "/simple/price",
            "params": {"ids": "bitcoin,ethereum,tron", "vs_currencies": "usd,eur"},
        }

        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)

            if success and data.get("data"):
                prices = data["data"]
                message = ", ".join(
                    [f"{coin.upper()}: ${prices[coin]['usd']:,.2f}" for coin in prices.keys()]
                )
                log_test("Query Multiple Coins", True, message)
                return True
            else:
                log_test("Query Multiple Coins", False, data.get("error", "Unknown error"))
                return False
        else:
            log_test("Query Multiple Coins", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("Query Multiple Coins", False, str(e))
        return False


def run_all_tests():
    """Run all test cases"""
    print("=" * 70)
    print("CRYPTO RESOURCE AGGREGATOR - TEST SUITE")
    print("=" * 70)
    print()

    # Basic endpoint tests
    print("Testing Basic Endpoints:")
    print("-" * 70)
    test_health_check()
    test_root_endpoint()
    print()

    # Resource listing tests
    print("Testing Resource Management:")
    print("-" * 70)
    resources_data = test_list_resources()

    if resources_data:
        categories = resources_data.get("resources", {})
        # Test a few categories
        for category in list(categories.keys())[:3]:
            test_get_category(category)
    print()

    # Query tests
    print("Testing Resource Queries:")
    print("-" * 70)
    test_query_coingecko()
    test_multiple_coins()
    test_query_etherscan()
    print()

    # Status tests
    print("Testing Status Monitoring:")
    print("-" * 70)
    test_status_check()
    print()

    # History tests
    print("Testing History & Analytics:")
    print("-" * 70)
    test_history()
    test_history_stats()
    print()

    # Print summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {test_results['passed']} ({pass_rate:.1f}%)")
    print(f"Failed:       {test_results['failed']}")
    print("=" * 70)

    if test_results["failed"] == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ {test_results['failed']} test(s) failed")

    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    print("\nDetailed results saved to: test_results.json")


if __name__ == "__main__":
    print("Starting Crypto Resource Aggregator tests...")
    print(f"Target: {BASE_URL}")
    print()

    # Wait for server to be ready
    print("Checking if server is available...")
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✓ Server is ready!")
                print()
                break
        except Exception as e:
            if i < max_retries - 1:
                print(f"Server not ready, retrying in 2 seconds... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"✗ Server is not available after {max_retries} attempts")
                print("Please start the server with: python app.py")
                exit(1)

    # Run all tests
    run_all_tests()

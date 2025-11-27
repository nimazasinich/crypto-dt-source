"""
Comprehensive Smoke Tests for HF Space UI Backend
Tests all required endpoints and acceptance criteria
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
import pytest
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/service"

# Test results storage
test_results = {"passed": 0, "failed": 0, "details": []}

# ====================
# HELPER FUNCTIONS
# ====================


def print_header(title: str):
    """Print formatted section header"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.GREEN}{title}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def print_test_result(name: str, passed: bool, details: str = ""):
    """Print individual test result"""
    if passed:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} {name}")
        test_results["passed"] += 1
    else:
        print(f"{Fore.RED}✗{Style.RESET_ALL} {name}")
        if details:
            print(f"  {Fore.YELLOW}→ {details}{Style.RESET_ALL}")
        test_results["failed"] += 1

    test_results["details"].append({"test": name, "passed": passed, "details": details})


async def make_request(
    method: str,
    endpoint: str,
    params: Dict = None,
    json_data: Dict = None,
    expected_status: int = 200,
) -> tuple[bool, Dict, str]:
    """Make HTTP request and return success status, response data, and error message"""

    url = f"{BASE_URL}{API_PREFIX}{endpoint}"

    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            if method == "GET":
                async with session.get(url, params=params) as response:
                    elapsed_ms = (time.time() - start_time) * 1000
                    data = await response.json()

                    if response.status != expected_status:
                        return False, data, f"Status {response.status}, expected {expected_status}"

                    return True, data, f"{elapsed_ms:.0f}ms"

            elif method == "POST":
                async with session.post(url, json=json_data) as response:
                    elapsed_ms = (time.time() - start_time) * 1000
                    data = await response.json()

                    if response.status != expected_status:
                        return False, data, f"Status {response.status}, expected {expected_status}"

                    return True, data, f"{elapsed_ms:.0f}ms"

    except Exception as e:
        return False, {}, f"Request failed: {str(e)}"


def validate_meta(response: Dict) -> tuple[bool, str]:
    """Validate meta block in response"""

    if "meta" not in response:
        return False, "Missing meta block"

    meta = response["meta"]
    required_fields = ["source", "generated_at", "cache_ttl_seconds"]

    for field in required_fields:
        if field not in meta:
            return False, f"Missing meta.{field}"

    # Check if source is valid
    if not meta["source"]:
        return False, "Invalid meta.source"

    return True, meta["source"]


# ====================
# TEST CATEGORIES
# ====================


async def test_health_and_diagnostics():
    """Test health and diagnostic endpoints"""

    print_header("🏥 HEALTH & DIAGNOSTICS")

    # Health check
    success, data, details = await make_request("GET", "/health")
    print_test_result("Health endpoint", success, details)

    # Diagnostics
    success, data, details = await make_request("GET", "/diagnostics")
    if success and "tests" in data:
        # Check if pair metadata is from HF
        pair_test = data.get("tests", {}).get("pair_metadata", {})
        hf_source = pair_test.get("source") == "hf"
        print_test_result("Diagnostics endpoint", success, details)
        print_test_result(
            "  → Pair metadata HF source", hf_source, pair_test.get("source", "unknown")
        )
    else:
        print_test_result("Diagnostics endpoint", False, "Invalid response structure")


async def test_realtime_data():
    """Test real-time market data endpoints"""

    print_header("📈 REAL-TIME MARKET DATA")

    # Single rate
    success, data, details = await make_request("GET", "/rate", params={"pair": "BTC/USDT"})
    if success:
        has_price = "price" in data and isinstance(data["price"], (int, float))
        meta_valid, source = validate_meta(data)
        print_test_result("GET /rate (BTC/USDT)", success and has_price, details)
        print_test_result("  → Has valid price", has_price)
        print_test_result("  → Has valid meta", meta_valid, source)
    else:
        print_test_result("GET /rate (BTC/USDT)", False, details)

    # Batch rates
    success, data, details = await make_request(
        "GET", "/rate/batch", params={"pairs": "BTC/USDT,ETH/USDT"}
    )
    if success:
        has_rates = "rates" in data and len(data["rates"]) > 0
        print_test_result("GET /rate/batch", success and has_rates, details)
    else:
        print_test_result("GET /rate/batch", False, details)


async def test_pair_metadata():
    """Test pair metadata - MUST be from HF"""

    print_header("🔍 PAIR METADATA (Must be HF)")

    pairs_to_test = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]

    for pair in pairs_to_test:
        success, data, details = await make_request("GET", f"/pair/{pair}")

        if success:
            meta_valid, source = validate_meta(data)
            is_hf = source == "hf"
            has_fields = all(
                field in data for field in ["pair", "base", "quote", "tick_size", "min_qty"]
            )

            print_test_result(f"GET /pair/{pair}", success and is_hf and has_fields, details)
            print_test_result(f"  → Source is HF", is_hf, f"source={source}")
            print_test_result(f"  → Has required fields", has_fields)
        else:
            print_test_result(f"GET /pair/{pair}", False, details)


async def test_historical_data():
    """Test OHLC historical data"""

    print_header("📊 HISTORICAL DATA (OHLC)")

    # Test different intervals
    test_cases = [
        {"symbol": "BTC", "interval": 60, "limit": 10},
        {"symbol": "ETH", "interval": 300, "limit": 50},
    ]

    for params in test_cases:
        success, data, details = await make_request("GET", "/history", params=params)

        if success:
            has_items = "items" in data and len(data["items"]) > 0
            if has_items:
                first_item = data["items"][0]
                has_ohlc = all(
                    field in first_item for field in ["open", "high", "low", "close", "volume"]
                )
            else:
                has_ohlc = False

            test_name = (
                f"GET /history ({params['symbol']}, {params['interval']}s, limit={params['limit']})"
            )
            print_test_result(test_name, success and has_items and has_ohlc, details)
            print_test_result(f"  → Has {len(data.get('items', []))} items", has_items)
            print_test_result(f"  → Has OHLC fields", has_ohlc)
        else:
            print_test_result(f"GET /history ({params['symbol']})", False, details)


async def test_market_overview():
    """Test market overview and top movers"""

    print_header("🌐 MARKET OVERVIEW & TOP MOVERS")

    # Market status
    success, data, details = await make_request("GET", "/market-status")
    if success:
        has_fields = all(
            field in data for field in ["total_market_cap", "btc_dominance", "volume_24h"]
        )
        print_test_result("GET /market-status", success and has_fields, details)
    else:
        print_test_result("GET /market-status", False, details)

    # Top movers
    for n in [10, 50]:
        success, data, details = await make_request("GET", "/top", params={"n": n})

        if success:
            has_movers = "movers" in data and len(data["movers"]) > 0
            print_test_result(f"GET /top (n={n})", success and has_movers, details)
            if has_movers:
                print(f"  → Returned {len(data['movers'])} movers")
        else:
            print_test_result(f"GET /top (n={n})", False, details)


async def test_sentiment_and_news():
    """Test sentiment analysis and news endpoints"""

    print_header("📰 SENTIMENT & NEWS ANALYSIS")

    # Text sentiment
    sentiment_data = {"text": "Bitcoin shows strong bullish signals", "mode": "general"}
    success, data, details = await make_request("POST", "/sentiment", json_data=sentiment_data)

    if success:
        has_fields = all(field in data for field in ["score", "label", "summary"])
        print_test_result("POST /sentiment (text)", success and has_fields, details)
    else:
        print_test_result("POST /sentiment (text)", False, details)

    # Symbol sentiment
    sentiment_data = {"symbol": "BTC", "mode": "news"}
    success, data, details = await make_request("POST", "/sentiment", json_data=sentiment_data)
    print_test_result("POST /sentiment (symbol)", success, details)

    # News
    success, data, details = await make_request("GET", "/news", params={"limit": 10})
    if success:
        has_items = "items" in data and len(data["items"]) > 0
        print_test_result("GET /news", success and has_items, details)
        if has_items:
            print(f"  → Returned {len(data['items'])} news items")
    else:
        print_test_result("GET /news", False, details)


async def test_whale_tracking():
    """Test whale tracking and on-chain data"""

    print_header("🐋 WHALE TRACKING & ON-CHAIN")

    # Whale transactions
    params = {"chain": "ethereum", "min_amount_usd": 100000, "limit": 10}
    success, data, details = await make_request("GET", "/whales", params=params)

    if success:
        has_txs = "transactions" in data
        print_test_result("GET /whales", success and has_txs, details)
        if has_txs:
            tx_count = len(data.get("transactions", []))
            print(f"  → Returned {tx_count} transactions")
    else:
        print_test_result("GET /whales", False, details)

    # On-chain data
    params = {"address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb3", "chain": "ethereum"}
    success, data, details = await make_request("GET", "/onchain", params=params)
    print_test_result("GET /onchain", success, details)


async def test_model_predictions():
    """Test model prediction endpoints"""

    print_header("🤖 MODEL PREDICTIONS")

    # Single model prediction
    predict_data = {"symbol": "BTC", "horizon": "24h"}
    success, data, details = await make_request(
        "POST", "/models/price_lstm/predict", json_data=predict_data
    )

    if success:
        has_fields = all(field in data for field in ["id", "symbol", "score", "model"])
        print_test_result("POST /models/{model}/predict", success and has_fields, details)
    else:
        print_test_result("POST /models/{model}/predict", False, details)

    # Batch predictions
    batch_data = {
        "models": ["price_lstm", "sentiment_rf"],
        "request": {"symbol": "ETH", "horizon": "12h"},
    }
    success, data, details = await make_request(
        "POST", "/models/batch/predict", json_data=batch_data
    )

    if success:
        is_list = isinstance(data, list)
        print_test_result("POST /models/batch/predict", success and is_list, details)
        if is_list:
            print(f"  → Returned {len(data)} predictions")
    else:
        print_test_result("POST /models/batch/predict", False, details)


async def test_generic_query():
    """Test generic query endpoint"""

    print_header("🔧 GENERIC QUERY")

    test_queries = [
        {"type": "rate", "payload": {"pair": "BTC/USDT"}},
        {"type": "history", "payload": {"symbol": "ETH", "interval": 60, "limit": 5}},
        {"type": "sentiment", "payload": {"text": "Bullish market"}},
    ]

    for query in test_queries:
        success, data, details = await make_request("POST", "/query", json_data=query)
        print_test_result(f"POST /query (type={query['type']})", success, details)


async def test_performance():
    """Test response time performance"""

    print_header("⚡ PERFORMANCE TESTS")

    perf_tests = [
        ("Rate endpoint", "GET", "/rate", {"pair": "BTC/USDT"}, 1500),
        ("Pair metadata", "GET", "/pair/BTC-USDT", None, 1500),
        (
            "History (small)",
            "GET",
            "/history",
            {"symbol": "BTC", "interval": 60, "limit": 10},
            4000,
        ),
        ("Market status", "GET", "/market-status", None, 1500),
    ]

    for name, method, endpoint, params, max_ms in perf_tests:
        start = time.time()
        success, data, details = await make_request(method, endpoint, params=params)
        elapsed_ms = (time.time() - start) * 1000

        if success:
            perf_pass = elapsed_ms <= max_ms
            print_test_result(f"{name} (<{max_ms}ms)", perf_pass, f"{elapsed_ms:.0f}ms")
        else:
            print_test_result(f"{name}", False, details)


# ====================
# ACCEPTANCE CRITERIA
# ====================


async def verify_acceptance_criteria():
    """Verify all acceptance criteria from the specification"""

    print_header("✅ ACCEPTANCE CRITERIA VERIFICATION")

    criteria = []

    # 1. Pair metadata must be from HF
    success, data, _ = await make_request("GET", "/pair/BTC-USDT")
    if success:
        meta_valid, source = validate_meta(data)
        criteria.append(
            {"name": "Pair metadata source is HF", "passed": source == "hf", "actual": source}
        )

    # 2. Rate endpoint returns numeric price
    success, data, _ = await make_request("GET", "/rate", params={"pair": "BTC/USDT"})
    if success:
        has_price = "price" in data and isinstance(data["price"], (int, float))
        criteria.append(
            {
                "name": "Rate returns numeric price",
                "passed": has_price,
                "actual": type(data.get("price", None)).__name__,
            }
        )

    # 3. History returns OHLC data
    success, data, _ = await make_request(
        "GET", "/history", params={"symbol": "BTC", "interval": 60, "limit": 5}
    )
    if success:
        has_ohlc = "items" in data and len(data["items"]) > 0
        criteria.append(
            {
                "name": "History returns OHLC items",
                "passed": has_ohlc,
                "actual": len(data.get("items", [])),
            }
        )

    # 4. Top movers returns lists
    success, data, _ = await make_request("GET", "/top", params={"n": 10})
    if success:
        has_movers = "movers" in data and isinstance(data["movers"], list)
        criteria.append(
            {
                "name": "Top movers returns list",
                "passed": has_movers,
                "actual": type(data.get("movers", None)).__name__,
            }
        )

    # 5. Whales endpoint works or returns empty with meta
    success, data, _ = await make_request(
        "GET", "/whales", params={"chain": "ethereum", "min_amount_usd": 100000}
    )
    if success:
        has_meta = "meta" in data
        criteria.append(
            {
                "name": "Whales endpoint returns with meta",
                "passed": has_meta,
                "actual": "meta present" if has_meta else "no meta",
            }
        )

    # 6. Model predict returns output
    predict_data = {"symbol": "BTC", "horizon": "24h"}
    success, data, _ = await make_request(
        "POST", "/models/test_model/predict", json_data=predict_data
    )
    criteria.append(
        {
            "name": "Model predict endpoint works",
            "passed": success,
            "actual": "success" if success else "failed",
        }
    )

    # 7. Generic query endpoint works
    query_data = {"type": "rate", "payload": {"pair": "BTC/USDT"}}
    success, data, _ = await make_request("POST", "/query", json_data=query_data)
    criteria.append(
        {
            "name": "Generic query endpoint works",
            "passed": success,
            "actual": "success" if success else "failed",
        }
    )

    # Print results
    for criterion in criteria:
        if criterion["passed"]:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {criterion['name']}: {criterion['actual']}")
        else:
            print(
                f"{Fore.RED}✗{Style.RESET_ALL} {criterion['name']}: Expected but got {criterion['actual']}"
            )

    # Overall pass/fail
    all_passed = all(c["passed"] for c in criteria)

    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    if all_passed:
        print(f"{Fore.GREEN}✓ ALL ACCEPTANCE CRITERIA PASSED{Style.RESET_ALL}")
    else:
        failed_count = sum(1 for c in criteria if not c["passed"])
        print(f"{Fore.RED}✗ {failed_count}/{len(criteria)} CRITERIA FAILED{Style.RESET_ALL}")

    return all_passed


# ====================
# MAIN TEST RUNNER
# ====================


async def run_all_tests():
    """Run all test suites"""

    print(f"{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.GREEN}HF SPACE UI BACKEND - COMPREHENSIVE SMOKE TESTS")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Run test suites
    await test_health_and_diagnostics()
    await test_realtime_data()
    await test_pair_metadata()
    await test_historical_data()
    await test_market_overview()
    await test_sentiment_and_news()
    await test_whale_tracking()
    await test_model_predictions()
    await test_generic_query()
    await test_performance()

    # Verify acceptance criteria
    acceptance_passed = await verify_acceptance_criteria()

    # Final summary
    print_header("📋 FINAL TEST SUMMARY")

    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Fore.GREEN}{test_results['passed']}{Style.RESET_ALL}")
    print(f"Failed: {Fore.RED}{test_results['failed']}{Style.RESET_ALL}")
    print(f"Pass Rate: {pass_rate:.1f}%")

    # Save results to file
    results_file = "/tmp/hf_ui_test_results.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": test_results["passed"],
                    "failed": test_results["failed"],
                    "pass_rate": pass_rate,
                    "acceptance_criteria_passed": acceptance_passed,
                },
                "details": test_results["details"],
            },
            f,
            indent=2,
        )

    print(f"\nResults saved to: {results_file}")

    # Exit code
    if test_results["failed"] == 0 and acceptance_passed:
        print(f"\n{Fore.GREEN}✓ ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION{Style.RESET_ALL}")
        return 0
    else:
        print(f"\n{Fore.RED}✗ SOME TESTS FAILED - REVIEW REQUIRED{Style.RESET_ALL}")
        return 1


# ====================
# ENTRY POINT
# ====================

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())

#!/usr/bin/env python3
"""
HF Space Complete API Test Script
Tests all endpoints and fallback behavior
"""
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_RESULTS = []


class Colors:
    """ANSI color codes"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def log_test(name: str, status: str, message: str = ""):
    """Log test result"""
    if status == "PASS":
        color = Colors.GREEN
        symbol = "✓"
    elif status == "FAIL":
        color = Colors.RED
        symbol = "✗"
    else:
        color = Colors.YELLOW
        symbol = "⚠"

    result = f"{color}{symbol} {name}{Colors.ENDC}"
    if message:
        result += f" - {message}"

    print(result)
    TEST_RESULTS.append({"name": name, "status": status, "message": message})


async def test_endpoint(
    session: aiohttp.ClientSession, method: str, endpoint: str, **kwargs
) -> tuple:
    """Test an endpoint and return (success, response_data, status_code)"""
    url = f"{BASE_URL}{endpoint}"

    try:
        async with session.request(method, url, **kwargs) as response:
            try:
                data = await response.json()
            except:
                data = await response.text()

            return response.status == 200, data, response.status
    except Exception as e:
        return False, str(e), 0


async def run_tests():
    """Run all API tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}HF SPACE COMPLETE API TEST SUITE{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    async with aiohttp.ClientSession() as session:

        # ====================================================================
        # 1. Market & Pairs Endpoints
        # ====================================================================
        print(f"\n{Colors.BLUE}{Colors.BOLD}[1] Testing Market & Pairs Endpoints{Colors.ENDC}")

        success, data, status = await test_endpoint(session, "GET", "/api/market")
        if success and "items" in data:
            log_test("GET /api/market", "PASS", f"Got {len(data['items'])} market items")
        else:
            log_test("GET /api/market", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(session, "GET", "/api/market/pairs")
        if success and "pairs" in data:
            log_test("GET /api/market/pairs", "PASS", f"Got {len(data['pairs'])} trading pairs")
        else:
            log_test("GET /api/market/pairs", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session,
            "GET",
            "/api/market/ohlc",
            params={"symbol": "BTC", "interval": 60, "limit": 10},
        )
        if success and "data" in data:
            log_test("GET /api/market/ohlc", "PASS", f"Got {len(data['data'])} OHLC candles")
        else:
            log_test("GET /api/market/ohlc", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session, "GET", "/api/market/depth", params={"symbol": "BTC", "limit": 10}
        )
        if success and "bids" in data and "asks" in data:
            log_test(
                "GET /api/market/depth",
                "PASS",
                f"Got orderbook with {len(data['bids'])} bids, {len(data['asks'])} asks",
            )
        else:
            log_test("GET /api/market/depth", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session, "GET", "/api/market/tickers", params={"limit": 10}
        )
        if success and "tickers" in data:
            log_test("GET /api/market/tickers", "PASS", f"Got {len(data['tickers'])} tickers")
        else:
            log_test("GET /api/market/tickers", "FAIL", f"Status: {status}")

        # ====================================================================
        # 2. Signals & Models Endpoints
        # ====================================================================
        print(f"\n{Colors.BLUE}{Colors.BOLD}[2] Testing Signals & Models Endpoints{Colors.ENDC}")

        success, data, status = await test_endpoint(
            session,
            "POST",
            "/api/models/test_model/predict",
            json={"symbol": "BTC", "context": "test", "params": {}},
        )
        signal_id = None
        if success and "id" in data:
            signal_id = data["id"]
            log_test(
                "POST /api/models/{model_key}/predict",
                "PASS",
                f"Generated signal: {data['type']} with score {data['score']}",
            )
        else:
            log_test("POST /api/models/{model_key}/predict", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session, "POST", "/api/models/batch/predict", json={"symbols": ["BTC", "ETH", "BNB"]}
        )
        if success and "predictions" in data:
            log_test(
                "POST /api/models/batch/predict",
                "PASS",
                f"Generated {len(data['predictions'])} predictions",
            )
        else:
            log_test("POST /api/models/batch/predict", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session, "GET", "/api/signals", params={"limit": 10}
        )
        if success and "signals" in data:
            log_test("GET /api/signals", "PASS", f"Retrieved {len(data['signals'])} signals")
        else:
            log_test("GET /api/signals", "FAIL", f"Status: {status}")

        if signal_id:
            success, data, status = await test_endpoint(
                session, "POST", "/api/signals/ack", json={"signal_id": signal_id}
            )
            if success and data.get("status") == "success":
                log_test("POST /api/signals/ack", "PASS", f"Acknowledged signal {signal_id}")
            else:
                log_test("POST /api/signals/ack", "FAIL", f"Status: {status}")

        # ====================================================================
        # 3. News & Sentiment Endpoints
        # ====================================================================
        print(f"\n{Colors.BLUE}{Colors.BOLD}[3] Testing News & Sentiment Endpoints{Colors.ENDC}")

        success, data, status = await test_endpoint(
            session, "GET", "/api/news", params={"limit": 5}
        )
        news_id = None
        if success and "articles" in data:
            if len(data["articles"]) > 0:
                news_id = data["articles"][0]["id"]
            log_test("GET /api/news", "PASS", f"Retrieved {len(data['articles'])} news articles")
        else:
            log_test("GET /api/news", "FAIL", f"Status: {status}")

        if news_id:
            success, data, status = await test_endpoint(session, "GET", f"/api/news/{news_id}")
            if success and "id" in data:
                log_test("GET /api/news/{id}", "PASS", f"Retrieved article {news_id}")
            else:
                log_test("GET /api/news/{id}", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session, "POST", "/api/news/analyze", json={"text": "Bitcoin reaches new all-time high"}
        )
        if success and "sentiment" in data:
            log_test(
                "POST /api/news/analyze", "PASS", f"Sentiment: {data['sentiment'].get('label')}"
            )
        else:
            log_test("POST /api/news/analyze", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session,
            "POST",
            "/api/sentiment/analyze",
            json={"text": "Crypto market is bullish today!", "mode": "crypto"},
        )
        if success and "label" in data:
            log_test(
                "POST /api/sentiment/analyze",
                "PASS",
                f"Label: {data['label']}, Score: {data['score']:.2f}",
            )
        else:
            log_test("POST /api/sentiment/analyze", "FAIL", f"Status: {status}")

        # ====================================================================
        # 4. Whale Tracking Endpoints
        # ====================================================================
        print(f"\n{Colors.BLUE}{Colors.BOLD}[4] Testing Whale Tracking Endpoints{Colors.ENDC}")

        success, data, status = await test_endpoint(
            session,
            "GET",
            "/api/crypto/whales/transactions",
            params={"limit": 10, "min_amount_usd": 100000},
        )
        if success and "transactions" in data:
            log_test(
                "GET /api/crypto/whales/transactions",
                "PASS",
                f"Retrieved {len(data['transactions'])} whale transactions",
            )
        else:
            log_test("GET /api/crypto/whales/transactions", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session, "GET", "/api/crypto/whales/stats", params={"hours": 24}
        )
        if success and "total_transactions" in data:
            log_test(
                "GET /api/crypto/whales/stats",
                "PASS",
                f"Total: {data['total_transactions']}, Volume: ${data['total_volume_usd']:,.0f}",
            )
        else:
            log_test("GET /api/crypto/whales/stats", "FAIL", f"Status: {status}")

        # ====================================================================
        # 5. Blockchain Endpoints
        # ====================================================================
        print(f"\n{Colors.BLUE}{Colors.BOLD}[5] Testing Blockchain Endpoints{Colors.ENDC}")

        success, data, status = await test_endpoint(
            session, "GET", "/api/crypto/blockchain/gas", params={"chain": "ethereum"}
        )
        if success and "gas_prices" in data:
            gas = data["gas_prices"]
            log_test(
                "GET /api/crypto/blockchain/gas",
                "PASS",
                f"Fast: {gas['fast']:.1f}, Standard: {gas['standard']:.1f}, Slow: {gas['slow']:.1f}",
            )
        else:
            log_test("GET /api/crypto/blockchain/gas", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(
            session,
            "GET",
            "/api/crypto/blockchain/stats",
            params={"chain": "ethereum", "hours": 24},
        )
        if success and "blocks_24h" in data:
            log_test(
                "GET /api/crypto/blockchain/stats",
                "PASS",
                f"Blocks: {data['blocks_24h']}, Txs: {data['transactions_24h']}",
            )
        else:
            log_test("GET /api/crypto/blockchain/stats", "FAIL", f"Status: {status}")

        # ====================================================================
        # 6. System Management Endpoints
        # ====================================================================
        print(f"\n{Colors.BLUE}{Colors.BOLD}[6] Testing System Management Endpoints{Colors.ENDC}")

        success, data, status = await test_endpoint(session, "GET", "/api/providers")
        if success and "providers" in data:
            log_test("GET /api/providers", "PASS", f"Found {len(data['providers'])} providers")
        else:
            log_test("GET /api/providers", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(session, "GET", "/api/status")
        if success and "status" in data:
            log_test("GET /api/status", "PASS", f"System status: {data['status']}")
        else:
            log_test("GET /api/status", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(session, "GET", "/api/health")
        if success and "status" in data:
            log_test("GET /api/health", "PASS", f"Health: {data['status']}")
        else:
            log_test("GET /api/health", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(session, "GET", "/api/freshness")
        if success and "market_data" in data:
            log_test("GET /api/freshness", "PASS", f"Got freshness timestamps for all subsystems")
        else:
            log_test("GET /api/freshness", "FAIL", f"Status: {status}")

        # ====================================================================
        # 7. Export & Diagnostics Endpoints
        # ====================================================================
        print(
            f"\n{Colors.BLUE}{Colors.BOLD}[7] Testing Export & Diagnostics Endpoints{Colors.ENDC}"
        )

        success, data, status = await test_endpoint(
            session, "POST", "/api/v2/export/signals", params={"format": "json"}
        )
        if success and "status" in data:
            log_test(
                "POST /api/v2/export/{type}", "PASS", f"Exported {data.get('records', 0)} records"
            )
        else:
            log_test("POST /api/v2/export/{type}", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(session, "POST", "/api/diagnostics/run")
        if success and "summary" in data:
            summary = data["summary"]
            log_test(
                "POST /api/diagnostics/run",
                "PASS",
                f"Passed: {summary['passed']}/{summary['total_tests']} ({summary['success_rate']}%)",
            )
        else:
            log_test("POST /api/diagnostics/run", "FAIL", f"Status: {status}")

        # ====================================================================
        # 8. OpenAPI Documentation
        # ====================================================================
        print(f"\n{Colors.BLUE}{Colors.BOLD}[8] Testing OpenAPI Documentation{Colors.ENDC}")

        success, data, status = await test_endpoint(session, "GET", "/docs")
        if success or status == 200:
            log_test("GET /docs (Swagger UI)", "PASS", "OpenAPI docs accessible")
        else:
            log_test("GET /docs (Swagger UI)", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(session, "GET", "/redoc")
        if success or status == 200:
            log_test("GET /redoc (ReDoc)", "PASS", "ReDoc accessible")
        else:
            log_test("GET /redoc (ReDoc)", "FAIL", f"Status: {status}")

        success, data, status = await test_endpoint(session, "GET", "/openapi.json")
        if success and "openapi" in data:
            log_test("GET /openapi.json", "PASS", f"OpenAPI spec version {data['openapi']}")
        else:
            log_test("GET /openapi.json", "FAIL", f"Status: {status}")


def print_summary():
    """Print test summary"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    passed = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
    warnings = sum(1 for r in TEST_RESULTS if r["status"] == "WARN")

    print(f"Total Tests: {len(TEST_RESULTS)}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {failed}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Warnings: {warnings}{Colors.ENDC}")
    print(f"Success Rate: {(passed/len(TEST_RESULTS)*100):.1f}%")

    print(f"\n{Colors.BOLD}Failed Tests:{Colors.ENDC}")
    for result in TEST_RESULTS:
        if result["status"] == "FAIL":
            print(f"  {Colors.RED}✗{Colors.ENDC} {result['name']}: {result['message']}")

    # Save results to JSON
    with open("data/test_results.json", "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "total": len(TEST_RESULTS),
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "success_rate": round(passed / len(TEST_RESULTS) * 100, 1),
                "results": TEST_RESULTS,
            },
            f,
            indent=2,
        )

    print(f"\n{Colors.BLUE}Results saved to data/test_results.json{Colors.ENDC}")

    return 0 if failed == 0 else 1


async def main():
    """Main function"""
    try:
        await run_tests()
        exit_code = print_summary()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Test suite failed: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure data directory exists
    import os

    os.makedirs("data", exist_ok=True)

    print(f"{Colors.BOLD}Starting HF Space Complete API Test Suite...{Colors.ENDC}")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    asyncio.run(main())

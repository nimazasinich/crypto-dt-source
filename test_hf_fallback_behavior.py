#!/usr/bin/env python3
"""
Test Script for HF-first + Fallback Behavior
اسکریپت تست برای رفتار HF-first و fallback

این اسکریپت:
1. تست می‌کند که HF endpoints به درستی کار می‌کنند
2. Simulate می‌کند که HF down است و fallback‌ها را تست می‌کند
3. بررسی می‌کند که meta fields به درستی تنظیم شده‌اند
4. تست می‌کند که normalization به درستی کار می‌کند
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any, Dict, List

import httpx

# ============================================================================
# Configuration
# ============================================================================

HF_BASE_URL = "https://really-amin-datasourceforcryptocurrency.hf.space"
# برای تست local:
# HF_BASE_URL = "http://localhost:7860"

TEST_ENDPOINTS = [
    # Market Data
    {
        "name": "Market Snapshot",
        "path": "/api/market",
        "method": "GET",
        "params": {"limit": 10, "sort": "volume"},
        "expected_fields": ["items", "last_updated", "meta"],
        "priority": "HF HTTP first",
    },
    {
        "name": "Trading Pairs",
        "path": "/api/market/pairs",
        "method": "GET",
        "params": {"limit": 50, "page": 1},
        "expected_fields": ["pairs", "meta"],
        "priority": "MUST BE HF HTTP",
    },
    {
        "name": "OHLC Data",
        "path": "/api/market/ohlc",
        "method": "GET",
        "params": {"symbol": "BTC", "interval": 60, "limit": 100},
        "expected_fields": ["symbol", "interval", "items", "meta"],
        "priority": "HF HTTP first",
    },
    {
        "name": "Market Depth",
        "path": "/api/market/depth",
        "method": "GET",
        "params": {"symbol": "BTCUSDT", "limit": 50},
        "expected_fields": ["symbol", "bids", "asks", "meta"],
        "priority": "HF HTTP first",
    },
    # News
    {
        "name": "News List",
        "path": "/api/news",
        "method": "GET",
        "params": {"limit": 10},
        "expected_fields": ["articles", "meta"],
        "priority": "HF HTTP first",
    },
    # Whale Tracking
    {
        "name": "Whale Transactions",
        "path": "/api/crypto/whales/transactions",
        "method": "GET",
        "params": {"limit": 20, "chain": "ethereum", "min_amount_usd": 1000000},
        "expected_fields": ["items", "meta"],
        "priority": "HF first, fallback to WhaleAlert/BitQuery",
    },
    # Blockchain
    {
        "name": "Gas Prices",
        "path": "/api/crypto/blockchain/gas",
        "method": "GET",
        "params": {"chain": "ethereum"},
        "expected_fields": ["fast", "standard", "slow", "unit", "meta"],
        "priority": "HF HTTP first",
    },
    # System
    {
        "name": "Providers List",
        "path": "/api/providers",
        "method": "GET",
        "params": {},
        "expected_fields": ["providers", "meta"],
        "priority": "N/A",
    },
    {
        "name": "System Status",
        "path": "/api/status",
        "method": "GET",
        "params": {},
        "expected_fields": ["status", "timestamp", "providers", "hf_status"],
        "priority": "N/A",
    },
    {
        "name": "Health Check",
        "path": "/api/health",
        "method": "GET",
        "params": {},
        "expected_fields": ["status", "timestamp"],
        "priority": "N/A",
    },
]

# ============================================================================
# Test Results Tracker
# ============================================================================


class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def add_pass(self, test_name: str, message: str = ""):
        self.passed.append({"test": test_name, "message": message})
        print(f"  ✓ {test_name}")
        if message:
            print(f"    → {message}")

    def add_fail(self, test_name: str, error: str):
        self.failed.append({"test": test_name, "error": error})
        print(f"  ✗ {test_name}")
        print(f"    → Error: {error}")

    def add_warning(self, test_name: str, warning: str):
        self.warnings.append({"test": test_name, "warning": warning})
        print(f"  ⚠ {test_name}")
        print(f"    → Warning: {warning}")

    def print_summary(self):
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        print("\n" + "=" * 70)
        print("TEST SUMMARY / خلاصه تست‌ها")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"✓ Passed: {len(self.passed)}")
        print(f"✗ Failed: {len(self.failed)}")
        print(f"⚠ Warnings: {len(self.warnings)}")
        print("=" * 70)

        if self.failed:
            print("\nFailed Tests:")
            for fail in self.failed:
                print(f"  • {fail['test']}: {fail['error']}")

        if self.warnings:
            print("\nWarnings:")
            for warn in self.warnings:
                print(f"  • {warn['test']}: {warn['warning']}")

        return len(self.failed) == 0


results = TestResults()

# ============================================================================
# Test Functions
# ============================================================================


async def test_endpoint(client: httpx.AsyncClient, endpoint: Dict[str, Any]) -> None:
    """
    Test a single endpoint
    """
    test_name = endpoint["name"]
    url = f"{HF_BASE_URL}{endpoint['path']}"

    print(f"\n📍 Testing: {test_name}")
    print(f"   URL: {url}")
    print(f"   Priority: {endpoint['priority']}")

    try:
        # Make request
        if endpoint["method"] == "GET":
            response = await client.get(url, params=endpoint["params"])
        elif endpoint["method"] == "POST":
            response = await client.post(url, json=endpoint["params"])

        # Check status code
        if response.status_code != 200:
            results.add_fail(test_name, f"HTTP {response.status_code}: {response.text[:200]}")
            return

        # Parse JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            results.add_fail(test_name, f"Invalid JSON response: {e}")
            return

        # Validate required fields
        missing_fields = []
        for field in endpoint["expected_fields"]:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            results.add_fail(test_name, f"Missing required fields: {', '.join(missing_fields)}")
            return

        # Validate meta fields
        meta_issues = validate_meta_fields(data.get("meta", {}))
        if meta_issues:
            results.add_warning(test_name, f"Meta issues: {', '.join(meta_issues)}")

        # Success
        source = data.get("meta", {}).get("source", "unknown")
        results.add_pass(test_name, f"Source: {source}, Fields: {list(data.keys())}")

    except httpx.RequestError as e:
        results.add_fail(test_name, f"Request error: {e}")
    except Exception as e:
        results.add_fail(test_name, f"Unexpected error: {e}")


def validate_meta_fields(meta: Dict[str, Any]) -> List[str]:
    """
    Validate meta fields

    Required:
    - source: str
    - generated_at: ISO 8601 datetime

    Optional:
    - cache_ttl_seconds: int
    - attempted: list (only on errors)
    """
    issues = []

    # Check required fields
    if "source" not in meta:
        issues.append("missing 'source'")
    elif not isinstance(meta["source"], str):
        issues.append("'source' must be string")

    if "generated_at" not in meta:
        issues.append("missing 'generated_at'")
    else:
        # Validate ISO 8601 format
        try:
            datetime.fromisoformat(meta["generated_at"].replace("Z", "+00:00"))
        except ValueError:
            issues.append("'generated_at' must be ISO 8601 format")

    # Check optional fields
    if "cache_ttl_seconds" in meta:
        if not isinstance(meta["cache_ttl_seconds"], int):
            issues.append("'cache_ttl_seconds' must be integer")

    if "attempted" in meta:
        if not isinstance(meta["attempted"], list):
            issues.append("'attempted' must be array")

    return issues


async def test_fallback_behavior(client: httpx.AsyncClient) -> None:
    """
    Test fallback behavior by simulating HF down

    این تست فرض می‌کند که:
    1. یک endpoint تست وجود دارد که می‌تواند simulate کند HF down است
    2. یا اینکه ما manually HF را خاموش می‌کنیم

    برای تست واقعی، باید:
    - یا یک mock HF endpoint داشته باشیم
    - یا manual تست کنیم
    """
    print("\n📍 Testing: Fallback Behavior")
    print("   این تست نیاز به manual simulation دارد")
    print("   راهنما:")
    print("   1. HF endpoint را موقتاً غیرفعال کنید")
    print("   2. درخواست به /api/market بفرستید")
    print("   3. بررسی کنید که:")
    print("      - meta.source != 'hf'")
    print("      - meta.attempted شامل 'hf' باشد")
    print("      - داده از fallback provider آمده باشد")

    results.add_warning(
        "Fallback Behavior", "Manual test required - simulate HF down and verify fallback works"
    )


async def test_meta_consistency(client: httpx.AsyncClient) -> None:
    """
    Test that all endpoints return consistent meta fields
    """
    print("\n📍 Testing: Meta Field Consistency")

    test_endpoints = ["/api/market", "/api/status", "/api/health"]

    all_valid = True

    for endpoint in test_endpoints:
        try:
            response = await client.get(f"{HF_BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()

                # Check meta exists (except /api/health might be minimal)
                if "meta" in data:
                    issues = validate_meta_fields(data["meta"])
                    if issues:
                        print(f"  ⚠ {endpoint}: {', '.join(issues)}")
                        all_valid = False
                elif endpoint != "/api/health":
                    print(f"  ⚠ {endpoint}: Missing meta field")
                    all_valid = False
        except Exception as e:
            print(f"  ✗ {endpoint}: {e}")
            all_valid = False

    if all_valid:
        results.add_pass("Meta Consistency", "All endpoints have valid meta fields")
    else:
        results.add_fail("Meta Consistency", "Some endpoints have invalid meta fields")


async def test_error_responses(client: httpx.AsyncClient) -> None:
    """
    Test error response format
    """
    print("\n📍 Testing: Error Response Format")

    # Test with invalid parameters
    invalid_requests = [
        {
            "name": "Invalid Symbol",
            "url": "/api/market/ohlc",
            "params": {"symbol": "INVALID_SYMBOL_XXX", "interval": 60},
        },
        {"name": "Invalid Endpoint", "url": "/api/nonexistent", "params": {}},
    ]

    for req in invalid_requests:
        try:
            response = await client.get(f"{HF_BASE_URL}{req['url']}", params=req["params"])

            if response.status_code >= 400:
                try:
                    error_data = response.json()

                    # Check error format
                    if "error" in error_data and "message" in error_data:
                        results.add_pass(
                            f"Error Format: {req['name']}",
                            f"HTTP {response.status_code} with proper error structure",
                        )
                    else:
                        results.add_warning(
                            f"Error Format: {req['name']}",
                            "Error response missing 'error' or 'message' fields",
                        )
                except json.JSONDecodeError:
                    results.add_warning(
                        f"Error Format: {req['name']}", "Error response is not JSON"
                    )
            else:
                results.add_warning(
                    f"Error Format: {req['name']}", f"Expected error but got {response.status_code}"
                )

        except Exception as e:
            results.add_fail(f"Error Format: {req['name']}", str(e))


async def test_cache_ttl(client: httpx.AsyncClient) -> None:
    """
    Test that cache TTL is properly set in meta
    """
    print("\n📍 Testing: Cache TTL in Meta")

    response = await client.get(f"{HF_BASE_URL}/api/market")
    if response.status_code == 200:
        data = response.json()
        meta = data.get("meta", {})

        if "cache_ttl_seconds" in meta:
            ttl = meta["cache_ttl_seconds"]
            if isinstance(ttl, int) and ttl > 0:
                results.add_pass("Cache TTL", f"TTL set to {ttl} seconds")
            else:
                results.add_warning("Cache TTL", f"Invalid TTL value: {ttl}")
        else:
            results.add_warning("Cache TTL", "cache_ttl_seconds not present in meta")
    else:
        results.add_fail("Cache TTL", f"HTTP {response.status_code}")


# ============================================================================
# Main Test Runner
# ============================================================================


async def run_all_tests():
    """Run all tests"""

    print("=" * 70)
    print("HuggingFace Space - API Validation Tests")
    print("تست اعتبارسنجی API فضای HuggingFace")
    print("=" * 70)
    print(f"Base URL: {HF_BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test connection
        print("\n🔌 Testing Connection...")
        try:
            response = await client.get(f"{HF_BASE_URL}/api/health")
            if response.status_code == 200:
                print("  ✓ Connection successful")
            else:
                print(f"  ⚠ Connection returned {response.status_code}")
        except Exception as e:
            print(f"  ✗ Connection failed: {e}")
            print("\n⚠ Cannot reach API. Tests will likely fail.")

        # Test all endpoints
        print("\n" + "=" * 70)
        print("ENDPOINT TESTS / تست endpoint‌ها")
        print("=" * 70)

        for endpoint in TEST_ENDPOINTS:
            await test_endpoint(client, endpoint)

        # Additional tests
        print("\n" + "=" * 70)
        print("ADDITIONAL TESTS / تست‌های اضافی")
        print("=" * 70)

        await test_meta_consistency(client)
        await test_error_responses(client)
        await test_cache_ttl(client)
        await test_fallback_behavior(client)

    # Print summary
    success = results.print_summary()

    return success


def main():
    """Main entry point"""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print(
        """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  HuggingFace Space API Validation Test Script                       ║
║  اسکریپت تست اعتبارسنجی API فضای HuggingFace                         ║
║                                                                      ║
║  این اسکریپت تست می‌کند:                                            ║
║  • تمام endpoint‌های required                                        ║
║  • وجود و صحت meta fields                                           ║
║  • فرمت error responses                                             ║
║  • Cache TTL values                                                  ║
║                                                                      ║
║  استفاده:                                                            ║
║    python test_hf_fallback_behavior.py                               ║
║                                                                      ║
║  برای تست local:                                                     ║
║    در فایل HF_BASE_URL را به localhost تغییر دهید                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    )

    main()

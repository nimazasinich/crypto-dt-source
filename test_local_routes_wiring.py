#!/usr/bin/env python3
"""
Test script to verify local backend routes wiring
Run this after starting api_server_extended.py
"""
import asyncio
import json
import sys
from pathlib import Path

import httpx

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_resources_api():
    """Test /api/resources endpoint"""
    print("\n" + "=" * 60)
    print("TEST 1: /api/resources")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:8000/api/resources")
            data = response.json()

            print(f"✓ Status Code: {response.status_code}")
            print(f"✓ Success: {data.get('success')}")

            if data.get("success"):
                summary = data.get("summary", {})
                print(f"✓ Total Resources: {summary.get('total_resources', 0)}")
                print(f"✓ Local Routes Count: {summary.get('local_routes_count', 0)}")
                print(f"✓ Free Resources: {summary.get('free_resources', 0)}")

                # Check categories
                categories = summary.get("categories", {})
                if "local_backend_routes" in categories:
                    local_cat = categories["local_backend_routes"]
                    print(f"✓ Local Backend Routes Category: {local_cat}")
                    print("  ✅ PASS: Local routes included in categories")
                else:
                    print("  ❌ FAIL: Local routes NOT in categories")
                    return False

            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_resources_apis():
    """Test /api/resources/apis endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: /api/resources/apis")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:8000/api/resources/apis")
            data = response.json()

            print(f"✓ Status Code: {response.status_code}")
            print(f"✓ OK: {data.get('ok')}")

            if data.get("ok"):
                local_routes = data.get("local_routes", {})
                count = local_routes.get("count", 0)
                routes = local_routes.get("routes", [])

                print(f"✓ Local Routes Count: {count}")
                print(f"✓ Routes Returned: {len(routes)}")

                if count > 0 and len(routes) > 0:
                    print("  ✅ PASS: Local routes exposed in API")
                    print(f"  Sample route: {routes[0].get('name', 'N/A')}")
                    print(f"  Sample URL: {routes[0].get('base_url', 'N/A')}")

                    # Check categories
                    categories = data.get("categories", [])
                    if "local" in categories:
                        print("  ✅ PASS: 'local' category present")
                    else:
                        print("  ⚠ WARNING: 'local' category not in list")
                else:
                    print("  ❌ FAIL: No local routes returned")
                    return False

            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_health_summary():
    """Test /api/providers/health-summary endpoint"""
    print("\n" + "=" * 60)
    print("TEST 3: /api/providers/health-summary")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:8000/api/providers/health-summary")
            data = response.json()

            print(f"✓ Status Code: {response.status_code}")
            print(f"✓ OK: {data.get('ok')}")

            if data.get("ok"):
                summary = data.get("summary", {})
                local_routes = summary.get("local_routes", {})

                print(f"✓ Local Routes Total: {local_routes.get('total', 0)}")
                print(f"✓ Local Routes Checked: {local_routes.get('checked', 0)}")
                print(f"✓ Local Routes UP: {local_routes.get('up', 0)}")
                print(f"✓ Local Routes DOWN: {local_routes.get('down', 0)}")

                if local_routes.get("total", 0) > 0:
                    print("  ✅ PASS: Health check includes local routes")

                    # Calculate health percentage
                    checked = local_routes.get("checked", 0)
                    up = local_routes.get("up", 0)
                    if checked > 0:
                        health_pct = (up / checked) * 100
                        print(f"  Health: {health_pct:.1f}%")
                else:
                    print("  ⚠ WARNING: No local routes in health summary")

            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_unified_loader():
    """Test UnifiedConfigLoader programmatically"""
    print("\n" + "=" * 60)
    print("TEST 4: UnifiedConfigLoader")
    print("=" * 60)

    try:
        from backend.services.unified_config_loader import unified_loader

        # Get local routes
        local_routes = unified_loader.get_local_routes()
        print(f"✓ Local Routes Loaded: {len(local_routes)}")

        # Get market data providers (should include local)
        market_providers = unified_loader.get_apis_by_feature("market_data")
        print(f"✓ Market Data Providers: {len(market_providers)}")

        # Check priorities
        if market_providers:
            first_provider = market_providers[0]
            print(f"✓ First Provider: {first_provider.get('name')}")
            print(f"  Priority: {first_provider.get('priority')}")
            print(f"  Is Local: {first_provider.get('is_local', False)}")

            if first_provider.get("is_local") and first_provider.get("priority") == 0:
                print("  ✅ PASS: Local routes have priority 0 and appear first")
            else:
                print("  ⚠ WARNING: Local routes may not be prioritized")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_validation():
    """Test resource validator"""
    print("\n" + "=" * 60)
    print("TEST 5: Resource Validator")
    print("=" * 60)

    try:
        from backend.services.resource_validator import validate_unified_resources

        report = validate_unified_resources(
            "api-resources/crypto_resources_unified_2025-11-11.json"
        )

        print(f"✓ Validation Valid: {report.get('valid')}")
        print(f"✓ Total Categories: {report.get('categories', {}).get('total_categories', 0)}")
        print(f"✓ Total Entries: {report.get('categories', {}).get('total_entries', 0)}")

        local_report = report.get("local_backend_routes", {})
        print(f"✓ Local Routes Count: {local_report.get('routes_count', 0)}")
        print(f"✓ Unique Routes: {local_report.get('unique_routes', 0)}")
        print(f"✓ Duplicates: {local_report.get('duplicate_signatures', 0)}")

        if report.get("valid"):
            print("  ✅ PASS: JSON is valid")
        else:
            print("  ❌ FAIL: Validation errors found")
            return False

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LOCAL BACKEND ROUTES WIRING - TEST SUITE")
    print("=" * 60)
    print("\nMake sure api_server_extended.py is running on port 8000!")
    print("\nStarting tests in 2 seconds...")
    await asyncio.sleep(2)

    results = {}

    # API tests (require server running)
    results["resources_api"] = await test_resources_api()
    results["resources_apis"] = await test_resources_apis()
    results["health_summary"] = await test_health_summary()

    # Programmatic tests (don't require server)
    results["unified_loader"] = await test_unified_loader()
    results["validation"] = await test_validation()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total_tests = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total_tests} tests passed")

    if passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Local routes wiring is complete.")
        return 0
    else:
        print(f"\n⚠ {total_tests - passed} test(s) failed. Check output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

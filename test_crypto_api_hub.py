#!/usr/bin/env python3
"""
Test script for Crypto API Hub implementation
"""

import asyncio
import json
from pathlib import Path


async def test_services_loading():
    """Test loading services from JSON file"""
    print("🧪 Testing services loading...")

    from crypto_api_hub_backend import crypto_hub_service

    services = await crypto_hub_service.get_services()

    print(f"✅ Loaded services successfully")
    print(f"   Total categories: {len(services.get('services', {}))}")

    for category, service_list in services.get('services', {}).items():
        print(f"   - {category}: {len(service_list)} services")

    return True


async def test_get_stats():
    """Test getting service stats"""
    print("\n🧪 Testing service stats...")

    from crypto_api_hub_backend import crypto_hub_service

    stats = await crypto_hub_service.get_service_stats()

    print(f"✅ Stats retrieved successfully")
    print(f"   Total services: {stats.get('total_services')}")
    print(f"   Total endpoints: {stats.get('total_endpoints')}")
    print(f"   Total keys: {stats.get('total_keys')}")

    return True


async def test_search():
    """Test search functionality"""
    print("\n🧪 Testing search...")

    from crypto_api_hub_backend import crypto_hub_service

    # Test searching for "CoinGecko"
    results = await crypto_hub_service.search_services("coingecko")

    print(f"✅ Search completed")
    print(f"   Results for 'coingecko': {len(results)} categories found")

    for category, services in results.items():
        print(f"   - {category}: {len(services)} services")

    return True


async def test_endpoint():
    """Test endpoint testing functionality"""
    print("\n🧪 Testing endpoint proxy...")

    from crypto_api_hub_backend import crypto_hub_service

    # Test with CoinGecko API (free, no key required)
    test_url = "https://api.coingecko.com/api/v3/ping"

    result = await crypto_hub_service.test_endpoint(test_url)

    print(f"✅ Endpoint test completed")
    print(f"   Success: {result.get('success')}")
    print(f"   Status: {result.get('status_code')}")

    if result.get('success'):
        print(f"   Response: {json.dumps(result.get('data'), indent=2)[:200]}...")

    return True


async def test_category_filter():
    """Test category filtering"""
    print("\n🧪 Testing category filtering...")

    from crypto_api_hub_backend import crypto_hub_service

    category = "market"
    services = await crypto_hub_service.get_services_by_category(category)

    print(f"✅ Category filter completed")
    print(f"   Services in '{category}': {len(services)}")

    if services:
        print(f"   First service: {services[0].get('name')}")

    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Crypto API Hub - Backend Tests")
    print("=" * 60)

    tests = [
        test_services_loading,
        test_get_stats,
        test_search,
        test_category_filter,
        test_endpoint
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)

    # Close the service
    from crypto_api_hub_backend import crypto_hub_service
    await crypto_hub_service.close()

    print("\n" + "=" * 60)
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    print("=" * 60)

    if all(results):
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

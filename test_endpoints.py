#!/usr/bin/env python3
"""
Test script for Backend Data Hub endpoints.
Run this after starting the server to verify all endpoints work correctly.

Usage:
    python3 test_endpoints.py
"""

import json
import sys

import requests

BASE_URL = "http://127.0.0.1:7860"
ENDPOINTS = [
    ("GET /api/health", "/api/health", None),
    ("GET /api/status", "/api/status", None),
    ("GET /api/providers", "/api/providers", None),
    ("GET /api/resources", "/api/resources", None),
    ("GET /api/resources?q=coingecko", "/api/resources", {"q": "coingecko"}),
]


def test_endpoint(name, path, params):
    """Test a single endpoint and return result."""
    try:
        url = f"{BASE_URL}{path}"
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return False, f"HTTP {response.status_code}", None

        try:
            data = response.json()
            return True, "OK", data
        except json.JSONDecodeError:
            return False, "Invalid JSON", None

    except requests.exceptions.ConnectionError:
        return False, "Connection refused (server not running?)", None
    except Exception as e:
        return False, str(e), None


def main():
    """Run all endpoint tests."""
    print("=" * 80)
    print("Backend Data Hub - Endpoint Tests")
    print("=" * 80)
    print()

    results = []
    for name, path, params in ENDPOINTS:
        print(f"Testing {name}...")
        success, status, data = test_endpoint(name, path, params)

        if success:
            print(f"  ✅ {status}")

            # Show key metrics
            if "status" in data:
                print(f"     Status: {data['status']}")
            if "total" in data:
                print(f"     Total: {data['total']}")
            if "providers" in data and isinstance(data["providers"], dict):
                print(f"     Providers: {data['providers']}")
            if "resources" in data and isinstance(data["resources"], dict):
                print(f"     Resources: {data['resources'].get('total', 'N/A')}")
            if isinstance(data, list):
                print(f"     Count: {len(data)} items")
        else:
            print(f"  ❌ {status}")

        results.append((name, success))
        print()

    # Summary
    print("=" * 80)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 80)

    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

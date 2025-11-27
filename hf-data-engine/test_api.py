#!/usr/bin/env python3
"""Test script for HuggingFace Crypto Data Engine API"""
import asyncio
import json
from typing import Optional

import httpx

BASE_URL = "http://localhost:8000"


async def test_endpoint(
    client: httpx.AsyncClient, name: str, url: str, params: Optional[dict] = None
) -> bool:
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    if params:
        print(f"Params: {json.dumps(params, indent=2)}")

    try:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()

        data = response.json()
        print(f"✅ SUCCESS - Status: {response.status_code}")
        print(f"Response preview:")
        print(json.dumps(data, indent=2)[:500] + "...")

        return True

    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        return False


async def main():
    """Run all API tests"""
    print("🚀 HuggingFace Crypto Data Engine - API Test Suite")
    print(f"Base URL: {BASE_URL}")

    results = []

    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # Test 1: Root endpoint
        results.append(await test_endpoint(client, "Root Endpoint", "/"))

        # Test 2: Health check
        results.append(await test_endpoint(client, "Health Check", "/api/health"))

        # Test 3: OHLCV - BTC 1h
        results.append(
            await test_endpoint(
                client,
                "OHLCV Data (BTC 1h)",
                "/api/ohlcv",
                {"symbol": "BTC", "interval": "1h", "limit": 10},
            )
        )

        # Test 4: OHLCV - ETH 5m
        results.append(
            await test_endpoint(
                client,
                "OHLCV Data (ETH 5m)",
                "/api/ohlcv",
                {"symbol": "ETH", "interval": "5m", "limit": 20},
            )
        )

        # Test 5: Prices - Single symbol
        results.append(
            await test_endpoint(client, "Prices (BTC)", "/api/prices", {"symbols": "BTC"})
        )

        # Test 6: Prices - Multiple symbols
        results.append(
            await test_endpoint(
                client, "Prices (BTC, ETH, SOL)", "/api/prices", {"symbols": "BTC,ETH,SOL"}
            )
        )

        # Test 7: Prices - All symbols
        results.append(await test_endpoint(client, "Prices (All Symbols)", "/api/prices"))

        # Test 8: Sentiment
        results.append(await test_endpoint(client, "Market Sentiment", "/api/sentiment"))

        # Test 9: Market Overview
        results.append(await test_endpoint(client, "Market Overview", "/api/market/overview"))

        # Test 10: Cache Stats
        results.append(await test_endpoint(client, "Cache Statistics", "/api/cache/stats"))

    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    print(f"Success Rate: {(sum(results) / len(results) * 100):.1f}%")

    if all(results):
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

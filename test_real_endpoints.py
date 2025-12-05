#!/usr/bin/env python3
"""
Test script for real data endpoints
Tests Dashboard and Market page data sources
"""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:7860"  # Default HuggingFace Space port

async def test_endpoint(client: httpx.AsyncClient, endpoint: str, name: str):
    """Test a single endpoint"""
    try:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"Endpoint: {endpoint}")
        print(f"{'='*60}")
        
        response = await client.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ SUCCESS - Status: {response.status_code}")
        print(f"Response keys: {list(data.keys())}")
        
        # Print sample data
        if "coins" in data:
            print(f"Coins count: {len(data['coins'])}")
            if data['coins']:
                print(f"First coin: {data['coins'][0]}")
        elif "history" in data:
            print(f"History points: {len(data['history'])}")
            if data['history']:
                print(f"First point: {data['history'][0]}")
        else:
            print(f"Sample data: {data}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        return False

async def main():
    """Run all tests"""
    print(f"\n{'#'*60}")
    print(f"# Testing Real Data Endpoints")
    print(f"# Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = {}
        
        # Test Dashboard endpoints
        print("\n" + "="*60)
        print("DASHBOARD PAGE ENDPOINTS")
        print("="*60)
        
        results["status"] = await test_endpoint(
            client, "/api/status", "System Status"
        )
        
        results["resources"] = await test_endpoint(
            client, "/api/resources", "Resources Statistics"
        )
        
        results["trending"] = await test_endpoint(
            client, "/api/trending", "Trending Cryptocurrencies"
        )
        
        results["sentiment"] = await test_endpoint(
            client, "/api/sentiment/global", "Global Sentiment (1D)"
        )
        
        results["sentiment_7d"] = await test_endpoint(
            client, "/api/sentiment/global?timeframe=7D", "Global Sentiment (7D)"
        )
        
        # Test Market page endpoints
        print("\n" + "="*60)
        print("MARKET PAGE ENDPOINTS")
        print("="*60)
        
        results["market"] = await test_endpoint(
            client, "/api/market", "Market Overview"
        )
        
        results["top_coins_10"] = await test_endpoint(
            client, "/api/coins/top?limit=10", "Top 10 Coins"
        )
        
        results["top_coins_50"] = await test_endpoint(
            client, "/api/coins/top?limit=50", "Top 50 Coins"
        )
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {name}")
        
        print(f"\n{'='*60}")
        print(f"Results: {passed}/{total} tests passed")
        print(f"{'='*60}\n")
        
        return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)


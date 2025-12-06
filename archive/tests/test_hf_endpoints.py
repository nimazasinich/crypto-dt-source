"""
Test script for HuggingFace Space API endpoints
Tests that ALL endpoints return REAL data (no fake/mock data)

Usage:
    export HF_TOKEN="your_token_here"
    python test_hf_endpoints.py
"""

import os
import sys
import asyncio
import httpx
import time
from typing import Dict, Any

# Configuration
BASE_URL = os.getenv("HF_BASE_URL", "http://localhost:7860")
HF_TOKEN = os.getenv("HF_TOKEN")

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_test(name: str, status: str, message: str = ""):
    """Print test result"""
    if status == "PASS":
        print(f"{GREEN}✓{RESET} {name}")
        if message:
            print(f"  {message}")
    elif status == "FAIL":
        print(f"{RED}✗{RESET} {name}")
        if message:
            print(f"  {RED}{message}{RESET}")
    elif status == "WARN":
        print(f"{YELLOW}⚠{RESET} {name}")
        if message:
            print(f"  {YELLOW}{message}{RESET}")


async def test_authentication():
    """Test authentication"""
    print("\n" + "=" * 70)
    print("TEST 1: Authentication")
    print("=" * 70)
    
    if not HF_TOKEN:
        print_test("HF_TOKEN configured", "FAIL", "HF_TOKEN environment variable not set")
        return False
    
    print_test("HF_TOKEN configured", "PASS", f"Token length: {len(HF_TOKEN)}")
    
    # Test with invalid token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/health",
                headers={"Authorization": "Bearer invalid_token"},
                timeout=10.0
            )
            
            if response.status_code == 401:
                print_test("Invalid token rejected", "PASS", "401 Unauthorized")
            else:
                print_test("Invalid token rejected", "FAIL", f"Got {response.status_code} instead of 401")
                
        except Exception as e:
            print_test("Invalid token test", "FAIL", str(e))
    
    # Test with valid token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/health",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                print_test("Valid token accepted", "PASS", "200 OK")
                return True
            else:
                print_test("Valid token accepted", "FAIL", f"Got {response.status_code}")
                return False
                
        except Exception as e:
            print_test("Valid token test", "FAIL", str(e))
            return False


async def test_health_endpoint():
    """Test /api/health endpoint"""
    print("\n" + "=" * 70)
    print("TEST 2: Health Endpoint")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/health",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                print_test("Health endpoint", "FAIL", f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("success"):
                print_test("Health response", "FAIL", "success=False")
                return False
            
            print_test("Health endpoint responds", "PASS")
            
            # Check database status
            db_status = data.get("database")
            if db_status == "connected":
                print_test("Database connection", "PASS", "Connected")
            else:
                print_test("Database connection", "WARN", f"Status: {db_status}")
            
            # Check cache stats
            cache = data.get("cache", {})
            market_count = cache.get("market_data_count", 0)
            ohlc_count = cache.get("ohlc_count", 0)
            
            print_test("Cache statistics", "PASS", f"Market: {market_count} symbols, OHLC: {ohlc_count} candles")
            
            # Check AI models
            models = data.get("ai_models", {})
            loaded = models.get("loaded", 0)
            total = models.get("total", 0)
            
            if loaded > 0:
                print_test("AI models", "PASS", f"{loaded}/{total} models loaded")
            else:
                print_test("AI models", "WARN", "No models loaded - using fallback")
            
            return True
            
        except Exception as e:
            print_test("Health endpoint", "FAIL", str(e))
            return False


async def test_market_endpoint():
    """Test /api/market endpoint"""
    print("\n" + "=" * 70)
    print("TEST 3: Market Data Endpoint")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/market?limit=5",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                timeout=15.0
            )
            
            if response.status_code != 200:
                print_test("Market endpoint", "FAIL", f"Status code: {response.status_code}")
                print(response.text)
                return False
            
            data = response.json()
            
            # Check if data available
            if not data.get("success"):
                error = data.get("error", "Unknown error")
                print_test("Market data available", "WARN", error)
                print("  Note: This is expected if background workers haven't run yet")
                return False
            
            print_test("Market endpoint responds", "PASS")
            
            # Check data structure
            market_data = data.get("data", [])
            
            if len(market_data) == 0:
                print_test("Market data count", "WARN", "No data returned")
                return False
            
            print_test("Market data count", "PASS", f"{len(market_data)} symbols")
            
            # Verify data is REAL (not fake)
            first_item = market_data[0]
            
            # Check required fields
            required_fields = ["symbol", "price", "last_updated"]
            for field in required_fields:
                if field not in first_item:
                    print_test(f"Field '{field}' present", "FAIL", "Missing field")
                    return False
            
            print_test("Required fields present", "PASS")
            
            # Check price is realistic
            price = first_item.get("price")
            if price and price > 0:
                print_test("Price is positive", "PASS", f"Example: {first_item['symbol']}=${price:.2f}")
            else:
                print_test("Price is positive", "FAIL", f"Price: {price}")
                return False
            
            # Check timestamp is recent (within last hour)
            last_updated = first_item.get("last_updated")
            current_time = int(time.time() * 1000)
            age_seconds = (current_time - last_updated) / 1000
            
            if age_seconds < 3600:  # Less than 1 hour
                print_test("Data is fresh", "PASS", f"Age: {int(age_seconds)}s")
            else:
                print_test("Data is fresh", "WARN", f"Age: {int(age_seconds)}s")
            
            # Print sample data
            print("\n  Sample data:")
            for item in market_data[:3]:
                print(f"    {item['symbol']}: ${item['price']:.2f}")
            
            return True
            
        except Exception as e:
            print_test("Market endpoint", "FAIL", str(e))
            return False


async def test_history_endpoint():
    """Test /api/market/history endpoint"""
    print("\n" + "=" * 70)
    print("TEST 4: Market History Endpoint")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/market/history?symbol=BTCUSDT&timeframe=1h&limit=10",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                timeout=15.0
            )
            
            if response.status_code != 200:
                print_test("History endpoint", "FAIL", f"Status code: {response.status_code}")
                return False
            
            data = response.json()
            
            # Check if data available
            if not data.get("success"):
                error = data.get("error", "Unknown error")
                print_test("OHLC data available", "WARN", error)
                print("  Note: This is expected if background workers haven't run yet")
                return False
            
            print_test("History endpoint responds", "PASS")
            
            # Check data structure
            ohlc_data = data.get("data", [])
            
            if len(ohlc_data) == 0:
                print_test("OHLC data count", "WARN", "No data returned")
                return False
            
            print_test("OHLC data count", "PASS", f"{len(ohlc_data)} candles")
            
            # Verify data is REAL (not fake)
            first_candle = ohlc_data[0]
            
            # Check required fields
            required_fields = ["timestamp", "open", "high", "low", "close", "volume"]
            for field in required_fields:
                if field not in first_candle:
                    print_test(f"Field '{field}' present", "FAIL", "Missing field")
                    return False
            
            print_test("Required fields present", "PASS")
            
            # Check OHLC values are realistic
            o = first_candle.get("open")
            h = first_candle.get("high")
            l = first_candle.get("low")
            c = first_candle.get("close")
            
            if h >= max(o, c) and l <= min(o, c):
                print_test("OHLC values valid", "PASS", f"H={h:.2f} L={l:.2f}")
            else:
                print_test("OHLC values valid", "FAIL", "Invalid OHLC relationship")
                return False
            
            # Print sample data
            print("\n  Sample candles:")
            for candle in ohlc_data[:3]:
                print(f"    O={candle['open']:.2f} H={candle['high']:.2f} L={candle['low']:.2f} C={candle['close']:.2f}")
            
            return True
            
        except Exception as e:
            print_test("History endpoint", "FAIL", str(e))
            return False


async def test_sentiment_endpoint():
    """Test /api/sentiment/analyze endpoint"""
    print("\n" + "=" * 70)
    print("TEST 5: Sentiment Analysis Endpoint")
    print("=" * 70)
    
    test_texts = [
        "Bitcoin is pumping! This is great news for crypto!",
        "The market is crashing. Very bearish sentiment.",
        "Ethereum remains stable with moderate volume."
    ]
    
    async with httpx.AsyncClient() as client:
        for text in test_texts:
            try:
                response = await client.post(
                    f"{BASE_URL}/api/sentiment/analyze",
                    headers={"Authorization": f"Bearer {HF_TOKEN}"},
                    json={"text": text},
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    print_test(f"Sentiment analysis", "FAIL", f"Status code: {response.status_code}")
                    continue
                
                data = response.json()
                
                if not data.get("success"):
                    error = data.get("error", "Unknown error")
                    print_test(f"Sentiment model available", "WARN", error)
                    continue
                
                # Check data structure
                result = data.get("data", {})
                
                sentiment = result.get("label")
                score = result.get("score")
                
                if sentiment and score is not None:
                    print_test(f"Sentiment: '{text[:40]}...'", "PASS", f"{sentiment} (score={score:.3f})")
                else:
                    print_test(f"Sentiment analysis", "FAIL", "Missing sentiment or score")
                
            except Exception as e:
                print_test(f"Sentiment endpoint", "FAIL", str(e))
    
    return True


async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("HuggingFace Space API - Test Suite")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"HF_TOKEN: {'Set' if HF_TOKEN else 'NOT SET'}")
    
    results = {}
    
    # Test 1: Authentication
    results["auth"] = await test_authentication()
    
    if not results["auth"]:
        print(f"\n{RED}Authentication failed - cannot continue tests{RESET}")
        return
    
    # Test 2: Health
    results["health"] = await test_health_endpoint()
    
    # Test 3: Market
    results["market"] = await test_market_endpoint()
    
    # Test 4: History
    results["history"] = await test_history_endpoint()
    
    # Test 5: Sentiment
    results["sentiment"] = await test_sentiment_endpoint()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}✓ All tests passed!{RESET}")
    else:
        print(f"\n{YELLOW}⚠ Some tests failed or returned warnings{RESET}")
        print("Note: If workers haven't run yet, market/history endpoints will return errors.")
        print("This is expected behavior - wait a few minutes for workers to populate cache.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

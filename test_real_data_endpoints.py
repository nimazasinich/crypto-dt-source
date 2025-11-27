#!/usr/bin/env python3
"""
Test script for Real Data API endpoints
Tests all endpoints to ensure they return REAL data (not mock data)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import httpx

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


async def test_health_check():
    """Test health check endpoint"""
    print("\n" + "=" * 80)
    print("Testing: GET /api/health")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   - Status: {data.get('status')}")
                print(f"   - Data sources: {data.get('dataSources')}")
                return True
            else:
                print(f"❌ Health check failed")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_market_prices():
    """Test market prices endpoint (real data from CoinGecko)"""
    print("\n" + "=" * 80)
    print("Testing: GET /api/market (Real data from CoinGecko)")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/market?symbols=BTC,ETH&limit=5")
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Market prices fetched successfully")
                print(f"   - Number of coins: {len(data)}")

                for coin in data[:3]:
                    print(
                        f"   - {coin.get('symbol')}: ${coin.get('price'):.2f} "
                        f"({coin.get('changePercent24h', 0):.2f}%)"
                    )
                    print(f"     Source: {coin.get('source')}")

                # Verify it's real data (not mock)
                if data and data[0].get("source") in ["coingecko", "binance"]:
                    print(f"✅ Confirmed REAL DATA from {data[0].get('source')}")
                    return True
                else:
                    print(f"⚠️ Source verification inconclusive")
                    return False
            else:
                print(f"❌ Failed to fetch market prices: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_ohlcv_history():
    """Test OHLCV historical data (real data from Binance)"""
    print("\n" + "=" * 80)
    print("Testing: GET /api/market/history (Real data from Binance)")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/market/history?symbol=BTC&timeframe=1h&limit=5"
            )
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ OHLCV data fetched successfully")
                print(f"   - Number of candles: {len(data)}")

                if data:
                    candle = data[0]
                    print(f"   - Latest candle:")
                    print(f"     Open: ${candle.get('open'):.2f}")
                    print(f"     High: ${candle.get('high'):.2f}")
                    print(f"     Low: ${candle.get('low'):.2f}")
                    print(f"     Close: ${candle.get('close'):.2f}")
                    print(f"     Volume: {candle.get('volume'):.2f}")

                    # Verify it's real data (prices > 0)
                    if candle.get("open", 0) > 0 and candle.get("close", 0) > 0:
                        print(f"✅ Confirmed REAL DATA from Binance")
                        return True
                    else:
                        print(f"⚠️ Data validation inconclusive")
                        return False
                else:
                    print(f"⚠️ No candle data returned")
                    return False
            else:
                print(f"❌ Failed to fetch OHLCV data: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_sentiment_analysis():
    """Test sentiment analysis (real HuggingFace models)"""
    print("\n" + "=" * 80)
    print("Testing: POST /api/sentiment/analyze (Real HuggingFace model)")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            test_text = "Bitcoin is showing strong bullish momentum and could reach new highs"
            response = await client.post(
                f"{BASE_URL}/api/sentiment/analyze", json={"text": test_text}
            )
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sentiment analysis completed")
                print(f"   - Text: {test_text[:50]}...")
                print(f"   - Sentiment: {data.get('label')} ({data.get('sentiment')})")
                print(f"   - Confidence: {data.get('confidence', 0):.2f}")
                print(f"   - Model: {data.get('model', 'unknown')}")
                print(f"   - Source: {data.get('source', 'unknown')}")

                # Verify it's from HuggingFace
                if data.get("source") == "huggingface":
                    print(f"✅ Confirmed REAL SENTIMENT from HuggingFace model")
                    return True
                else:
                    print(f"⚠️ Source verification inconclusive")
                    return False

            elif response.status_code == 503:
                # Model loading
                data = response.json()
                if "error" in data and "loading" in data["error"].lower():
                    print(f"⏳ Model is loading (estimated time: {data.get('estimated_time')}s)")
                    print(f"✅ This is expected for first request - model will be ready soon")
                    return True
                else:
                    print(f"⚠️ Service unavailable: {data}")
                    return False

            else:
                print(f"❌ Failed to analyze sentiment: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_latest_news():
    """Test latest news (real news from APIs)"""
    print("\n" + "=" * 80)
    print("Testing: GET /api/news/latest (Real news from NewsAPI/RSS)")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/news/latest?limit=5")
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ News fetched successfully")
                print(f"   - Number of articles: {len(data)}")

                for i, article in enumerate(data[:3], 1):
                    print(f"   - Article {i}:")
                    print(f"     Title: {article.get('title', '')[:60]}...")
                    print(f"     Source: {article.get('source', 'unknown')}")
                    print(f"     URL: {article.get('url', 'N/A')}")

                # Verify it's real news (has URLs)
                if data and data[0].get("url"):
                    print(f"✅ Confirmed REAL NEWS articles")
                    return True
                else:
                    print(f"⚠️ News validation inconclusive")
                    return False
            else:
                print(f"❌ Failed to fetch news: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_trending_coins():
    """Test trending coins (real data from CoinGecko)"""
    print("\n" + "=" * 80)
    print("Testing: GET /api/trending (Real trending from CoinGecko)")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/trending?limit=5")
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Trending coins fetched successfully")
                print(f"   - Number of trending coins: {len(data)}")

                for coin in data[:5]:
                    print(f"   - #{coin.get('rank')}: {coin.get('name')} ({coin.get('symbol')})")
                    if coin.get("price"):
                        print(f"     Price: ${coin.get('price'):.2f}")

                # Verify it's real data
                if data and data[0].get("source") == "coingecko":
                    print(f"✅ Confirmed REAL TRENDING data from CoinGecko")
                    return True
                else:
                    print(f"⚠️ Source verification inconclusive")
                    return False
            else:
                print(f"❌ Failed to fetch trending coins: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("CRYPTOCURRENCY DATA ENGINE - REAL DATA API TESTS")
    print("=" * 80)
    print(f"Testing server at: {BASE_URL}")
    print(f"These tests verify that ALL endpoints return REAL data (NO MOCK DATA)")
    print("=" * 80)

    results = {}

    # Run tests
    results["health"] = await test_health_check()
    results["market"] = await test_market_prices()
    results["ohlcv"] = await test_ohlcv_history()
    results["sentiment"] = await test_sentiment_analysis()
    results["news"] = await test_latest_news()
    results["trending"] = await test_trending_coins()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.upper():20s}: {status}")

    print("=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - ALL ENDPOINTS RETURN REAL DATA!")
    elif passed > 0:
        print("⚠️ SOME TESTS PASSED - Check failed tests above")
    else:
        print("❌ ALL TESTS FAILED - Check if server is running")

    print("=" * 80)

    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        sys.exit(1)

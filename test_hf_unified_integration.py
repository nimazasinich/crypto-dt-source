#!/usr/bin/env python3
"""
Test Script for HuggingFace Unified Integration
================================================
تست کامل برای اطمینان از اینکه همه داده‌ها از HuggingFace می‌آیند
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.hf_unified_client import get_hf_client
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_market_prices():
    """Test 1: Market Prices"""
    print("\n" + "=" * 70)
    print("🧪 TEST 1: Market Prices")
    print("=" * 70)

    client = get_hf_client()

    try:
        result = await client.get_market_prices(symbols=["BTC", "ETH", "BNB"], limit=10)

        print(f"✅ Success: {result.get('success')}")
        print(f"📊 Data count: {len(result.get('data', []))}")
        print(f"🔖 Source: {result.get('source')}")
        print(f"⏰ Timestamp: {result.get('timestamp')}")

        if result.get("data"):
            sample = result["data"][0]
            print(f"\n📈 Sample data:")
            print(f"   Symbol: {sample.get('symbol')}")
            print(f"   Price: ${sample.get('price'):,.2f}")
            print(f"   Change 24h: {sample.get('change_24h', 0):.2f}%")

        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_market_history():
    """Test 2: OHLCV History"""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: OHLCV History")
    print("=" * 70)

    client = get_hf_client()

    try:
        result = await client.get_market_history(symbol="BTCUSDT", timeframe="1h", limit=24)

        print(f"✅ Success: {result.get('success')}")
        print(f"📊 Candles count: {len(result.get('data', []))}")
        print(f"🔖 Source: {result.get('source')}")

        if result.get("data"):
            sample = result["data"][0]
            print(f"\n🕯️ Sample candle:")
            print(f"   Timestamp: {sample.get('timestamp')}")
            print(f"   Open: ${sample.get('open'):,.2f}")
            print(f"   High: ${sample.get('high'):,.2f}")
            print(f"   Low: ${sample.get('low'):,.2f}")
            print(f"   Close: ${sample.get('close'):,.2f}")
            print(f"   Volume: {sample.get('volume'):,.2f}")

        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_sentiment_analysis():
    """Test 3: Sentiment Analysis"""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: Sentiment Analysis")
    print("=" * 70)

    client = get_hf_client()

    test_texts = [
        "Bitcoin is rising! Great news for crypto investors!",
        "Market crash incoming. Be careful with your investments.",
        "Ethereum network upgrade completed successfully.",
    ]

    results = []
    for text in test_texts:
        try:
            result = await client.analyze_sentiment(text)

            if result.get("success"):
                data = result.get("data", {})
                sentiment = data.get("sentiment", "unknown")
                confidence = data.get("confidence", 0)

                print(f"\n📝 Text: {text[:50]}...")
                print(f"   Sentiment: {sentiment}")
                print(f"   Confidence: {confidence:.2%}")
                print(f"   Source: {result.get('source')}")

                results.append(True)
            else:
                print(f"❌ Failed: {result.get('error')}")
                results.append(False)
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append(False)

    return all(results)


async def test_news():
    """Test 4: News"""
    print("\n" + "=" * 70)
    print("🧪 TEST 4: News")
    print("=" * 70)

    client = get_hf_client()

    try:
        result = await client.get_news(limit=5)

        articles = result.get("articles", [])
        print(f"📰 Articles count: {len(articles)}")

        if articles:
            for i, article in enumerate(articles[:3], 1):
                print(f"\n📄 Article {i}:")
                print(f"   Title: {article.get('title', 'N/A')}")
                print(f"   Source: {article.get('source', 'N/A')}")
                print(f"   URL: {article.get('url', 'N/A')[:60]}...")

        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_blockchain_gas():
    """Test 5: Blockchain Gas Prices"""
    print("\n" + "=" * 70)
    print("🧪 TEST 5: Blockchain Gas Prices")
    print("=" * 70)

    client = get_hf_client()

    chains = ["ethereum", "bsc", "polygon"]
    results = []

    for chain in chains:
        try:
            result = await client.get_blockchain_gas_prices(chain=chain)

            print(f"\n⛓️ Chain: {chain}")

            gas_prices = result.get("gas_prices", {})
            if gas_prices:
                print(f"   Fast: {gas_prices.get('fast', 0):.2f} {gas_prices.get('unit', 'gwei')}")
                print(
                    f"   Standard: {gas_prices.get('standard', 0):.2f} {gas_prices.get('unit', 'gwei')}"
                )
                print(f"   Slow: {gas_prices.get('slow', 0):.2f} {gas_prices.get('unit', 'gwei')}")

            results.append(True)
        except Exception as e:
            print(f"❌ {chain} FAILED: {e}")
            results.append(False)

    return any(results)  # At least one should work


async def test_health_check():
    """Test 6: Health Check"""
    print("\n" + "=" * 70)
    print("🧪 TEST 6: Health Check")
    print("=" * 70)

    client = get_hf_client()

    try:
        result = await client.health_check()

        print(f"✅ Status: {result.get('status')}")
        print(f"🗄️ Database: {result.get('database')}")

        cache = result.get("cache", {})
        print(f"📦 Cache:")
        print(f"   Market data symbols: {cache.get('market_data_count', 0)}")
        print(f"   OHLC candles: {cache.get('ohlc_count', 0)}")

        ai_models = result.get("ai_models", {})
        print(f"🤖 AI Models:")
        print(f"   Loaded: {ai_models.get('loaded', 0)}")
        print(f"   Failed: {ai_models.get('failed', 0)}")
        print(f"   Total: {ai_models.get('total', 0)}")

        return result.get("success", False)
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "🚀" * 35)
    print("🔬 HuggingFace Unified Integration Test Suite")
    print("🚀" * 35)

    tests = [
        ("Market Prices", test_market_prices),
        ("OHLCV History", test_market_history),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("News", test_news),
        ("Blockchain Gas", test_blockchain_gas),
        ("Health Check", test_health_check),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")

    print(f"\n{'='*70}")
    print(f"📈 Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*70}")

    if passed == total:
        print("\n🎉 All tests passed! HuggingFace integration is working correctly.")
        return 0
    elif passed > 0:
        print(f"\n⚠️ Some tests failed. {passed}/{total} tests passed.")
        return 1
    else:
        print("\n❌ All tests failed. Please check HuggingFace Space configuration.")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

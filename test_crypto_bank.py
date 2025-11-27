#!/usr/bin/env python3
"""
تست کامل بانک اطلاعاتی رمزارز
Complete Crypto Data Bank Test Suite
"""

import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from crypto_data_bank.ai.huggingface_models import get_analyzer
from crypto_data_bank.collectors.free_price_collector import FreePriceCollector
from crypto_data_bank.collectors.rss_news_collector import RSSNewsCollector
from crypto_data_bank.collectors.sentiment_collector import SentimentCollector
from crypto_data_bank.database import get_db
from crypto_data_bank.orchestrator import get_orchestrator


async def test_price_collectors():
    """Test price collectors"""
    print("\n" + "=" * 70)
    print("💰 Testing Price Collectors")
    print("=" * 70)

    collector = FreePriceCollector()

    symbols = ["BTC", "ETH", "SOL"]

    # Test individual sources
    print("\nTesting individual sources...")

    try:
        coincap = await collector.collect_from_coincap(symbols)
        print(f"✅ CoinCap: {len(coincap)} prices")
    except Exception as e:
        print(f"⚠️  CoinCap: {e}")

    try:
        coingecko = await collector.collect_from_coingecko(symbols)
        print(f"✅ CoinGecko: {len(coingecko)} prices")
    except Exception as e:
        print(f"⚠️  CoinGecko: {e}")

    try:
        binance = await collector.collect_from_binance_public(symbols)
        print(f"✅ Binance: {len(binance)} prices")
    except Exception as e:
        print(f"⚠️  Binance: {e}")

    # Test aggregation
    print("\nTesting aggregation...")
    all_prices = await collector.collect_all_free_sources(symbols)
    aggregated = collector.aggregate_prices(all_prices)

    print(f"\n✅ Aggregated {len(aggregated)} prices from multiple sources")

    if aggregated:
        print("\nSample prices:")
        for price in aggregated[:3]:
            print(
                f"  {price['symbol']}: ${price['price']:,.2f} (from {price.get('sources_count', 0)} sources)"
            )

    return len(aggregated) > 0


async def test_news_collectors():
    """Test news collectors"""
    print("\n" + "=" * 70)
    print("📰 Testing News Collectors")
    print("=" * 70)

    collector = RSSNewsCollector()

    print("\nTesting RSS feeds...")

    try:
        cointelegraph = await collector.collect_from_cointelegraph()
        print(f"✅ CoinTelegraph: {len(cointelegraph)} news")
    except Exception as e:
        print(f"⚠️  CoinTelegraph: {e}")

    try:
        coindesk = await collector.collect_from_coindesk()
        print(f"✅ CoinDesk: {len(coindesk)} news")
    except Exception as e:
        print(f"⚠️  CoinDesk: {e}")

    # Test all feeds
    print("\nTesting all RSS feeds...")
    all_news = await collector.collect_all_rss_feeds()
    total = sum(len(v) for v in all_news.values())
    print(f"\n✅ Collected {total} news items from {len(all_news)} sources")

    # Test deduplication
    unique_news = collector.deduplicate_news(all_news)
    print(f"✅ Deduplicated to {len(unique_news)} unique items")

    if unique_news:
        print("\nLatest news:")
        for news in unique_news[:3]:
            print(f"  • {news['title'][:60]}...")
            print(f"    Source: {news['source']}")

    # Test trending coins
    trending = collector.get_trending_coins(unique_news)
    if trending:
        print("\nTrending coins:")
        for coin in trending[:5]:
            print(f"  {coin['coin']}: {coin['mentions']} mentions")

    return len(unique_news) > 0


async def test_sentiment_collectors():
    """Test sentiment collectors"""
    print("\n" + "=" * 70)
    print("😊 Testing Sentiment Collectors")
    print("=" * 70)

    collector = SentimentCollector()

    # Test Fear & Greed
    print("\nTesting Fear & Greed Index...")
    try:
        fg = await collector.collect_fear_greed_index()
        if fg:
            print(
                f"✅ Fear & Greed: {fg['fear_greed_value']}/100 ({fg['fear_greed_classification']})"
            )
        else:
            print("⚠️  Fear & Greed: No data")
    except Exception as e:
        print(f"⚠️  Fear & Greed: {e}")

    # Test all sentiment
    print("\nTesting all sentiment sources...")
    all_sentiment = await collector.collect_all_sentiment_data()

    if all_sentiment.get("overall_sentiment"):
        overall = all_sentiment["overall_sentiment"]
        print(f"\n✅ Overall Sentiment: {overall['overall_sentiment']}")
        print(f"   Score: {overall['sentiment_score']}/100")
        print(f"   Confidence: {overall['confidence']:.2%}")

    return all_sentiment.get("overall_sentiment") is not None


async def test_ai_models():
    """Test AI models"""
    print("\n" + "=" * 70)
    print("🤖 Testing AI Models")
    print("=" * 70)

    analyzer = get_analyzer()

    # Test sentiment analysis
    print("\nTesting sentiment analysis...")
    test_texts = [
        "Bitcoin surges past $50,000 as institutional adoption accelerates",
        "SEC delays crypto ETF decision, causing market uncertainty",
        "Ethereum successfully completes major network upgrade",
    ]

    for i, text in enumerate(test_texts, 1):
        result = await analyzer.analyze_news_sentiment(text)
        print(f"\n{i}. {text[:50]}...")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Confidence: {result.get('confidence', 0):.2%}")

    return True


async def test_database():
    """Test database operations"""
    print("\n" + "=" * 70)
    print("💾 Testing Database")
    print("=" * 70)

    db = get_db()

    # Test saving price
    print("\nTesting price storage...")
    test_price = {
        "price": 50000.0,
        "priceUsd": 50000.0,
        "change24h": 2.5,
        "volume24h": 25000000000,
        "marketCap": 980000000000,
    }

    try:
        db.save_price("BTC", test_price, "test")
        print("✅ Price saved successfully")
    except Exception as e:
        print(f"❌ Failed to save price: {e}")
        return False

    # Test retrieving prices
    print("\nTesting price retrieval...")
    try:
        latest_prices = db.get_latest_prices(["BTC"], 1)
        print(f"✅ Retrieved {len(latest_prices)} prices")
    except Exception as e:
        print(f"❌ Failed to retrieve prices: {e}")
        return False

    # Get statistics
    print("\nDatabase statistics:")
    stats = db.get_statistics()
    print(f"  Prices: {stats.get('prices_count', 0)}")
    print(f"  News: {stats.get('news_count', 0)}")
    print(f"  AI Analysis: {stats.get('ai_analysis_count', 0)}")
    print(f"  Database size: {stats.get('database_size', 0):,} bytes")

    return True


async def test_orchestrator():
    """Test orchestrator"""
    print("\n" + "=" * 70)
    print("🎯 Testing Orchestrator")
    print("=" * 70)

    orchestrator = get_orchestrator()

    # Test single collection cycle
    print("\nTesting single collection cycle...")
    results = await orchestrator.collect_all_data_once()

    print(f"\n✅ Collection Results:")
    if results.get("prices", {}).get("success"):
        print(f"   Prices: {results['prices'].get('prices_saved', 0)} saved")
    else:
        print(f"   Prices: ⚠️  {results.get('prices', {}).get('error', 'Failed')}")

    if results.get("news", {}).get("success"):
        print(f"   News: {results['news'].get('news_saved', 0)} saved")
    else:
        print(f"   News: ⚠️  {results.get('news', {}).get('error', 'Failed')}")

    if results.get("sentiment", {}).get("success"):
        print(f"   Sentiment: ✅ Success")
    else:
        print(f"   Sentiment: ⚠️  Failed")

    # Get status
    status = orchestrator.get_collection_status()
    print(f"\n📊 Collection Status:")
    print(f"   Running: {status['is_running']}")
    print(f"   Last collection: {status.get('last_collection', {})}")

    return results.get("prices", {}).get("success", False)


async def main():
    """Run all tests"""
    print("\n" + "🧪" * 35)
    print("CRYPTO DATA BANK - COMPREHENSIVE TEST SUITE")
    print("تست جامع بانک اطلاعاتی رمزارز")
    print("🧪" * 35)

    results = {}

    # Run all tests
    try:
        results["price_collectors"] = await test_price_collectors()
    except Exception as e:
        print(f"\n❌ Price collectors test failed: {e}")
        results["price_collectors"] = False

    try:
        results["news_collectors"] = await test_news_collectors()
    except Exception as e:
        print(f"\n❌ News collectors test failed: {e}")
        results["news_collectors"] = False

    try:
        results["sentiment_collectors"] = await test_sentiment_collectors()
    except Exception as e:
        print(f"\n❌ Sentiment collectors test failed: {e}")
        results["sentiment_collectors"] = False

    try:
        results["ai_models"] = await test_ai_models()
    except Exception as e:
        print(f"\n❌ AI models test failed: {e}")
        results["ai_models"] = False

    try:
        results["database"] = await test_database()
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        results["database"] = False

    try:
        results["orchestrator"] = await test_orchestrator()
    except Exception as e:
        print(f"\n❌ Orchestrator test failed: {e}")
        results["orchestrator"] = False

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY | خلاصه تست‌ها")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name.replace('_', ' ').title()}")

    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready to use!")
        print("🎉 همه تست‌ها موفق! سیستم آماده استفاده است!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        print(f"⚠️  {total - passed} تست ناموفق. لطفاً خطاها را بررسی کنید.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

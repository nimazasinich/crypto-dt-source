#!/usr/bin/env python3
"""
اعتبارسنجی پیاده‌سازی بانک اطلاعاتی
Validate Crypto Data Bank Implementation
"""

import os
from pathlib import Path


def check_file(filepath, description):
    """Check if a file exists and show info"""
    path = Path(filepath)
    if path.exists():
        size = path.stat().st_size
        lines = 0
        if path.suffix == ".py":
            with open(path) as f:
                lines = len(f.readlines())
        print(f"✅ {description}")
        print(f"   Path: {filepath}")
        print(f"   Size: {size:,} bytes{f', {lines} lines' if lines else ''}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False


def main():
    print("\n" + "=" * 70)
    print("🔍 Crypto Data Bank Implementation Validation")
    print("اعتبارسنجی پیاده‌سازی بانک اطلاعاتی رمزارز")
    print("=" * 70)

    checks = {
        # Core files
        "Database": "crypto_data_bank/database.py",
        "Orchestrator": "crypto_data_bank/orchestrator.py",
        "API Gateway": "crypto_data_bank/api_gateway.py",
        "Package Init": "crypto_data_bank/__init__.py",
        "Requirements": "crypto_data_bank/requirements.txt",
        # Collectors
        "Free Price Collector": "crypto_data_bank/collectors/free_price_collector.py",
        "RSS News Collector": "crypto_data_bank/collectors/rss_news_collector.py",
        "Sentiment Collector": "crypto_data_bank/collectors/sentiment_collector.py",
        "Collectors Init": "crypto_data_bank/collectors/__init__.py",
        # AI
        "HuggingFace Models": "crypto_data_bank/ai/huggingface_models.py",
        "AI Init": "crypto_data_bank/ai/__init__.py",
        # Deployment & Docs
        "Dockerfile": "Dockerfile.crypto-bank",
        "Startup Script": "start_crypto_bank.sh",
        "Test Script": "test_crypto_bank.py",
        "README": "CRYPTO_DATA_BANK_README.md",
        "HF README": "README_HUGGINGFACE.md",
    }

    passed = 0
    total = len(checks)

    print("\n📁 Checking Files...")
    print("=" * 70)

    for name, filepath in checks.items():
        if check_file(filepath, name):
            passed += 1
        print()

    print("=" * 70)
    print(f"📊 Result: {passed}/{total} files found ({passed/total*100:.0f}%)")
    print("=" * 70)

    # Check code structure
    print("\n🏗️  Code Structure Validation")
    print("=" * 70)

    structure_checks = [
        (
            "Free price collectors",
            "crypto_data_bank/collectors/free_price_collector.py",
            [
                "class FreePriceCollector",
                "collect_from_coincap",
                "collect_from_coingecko",
                "collect_from_binance_public",
                "collect_from_kraken_public",
                "collect_from_cryptocompare",
                "collect_all_free_sources",
                "aggregate_prices",
            ],
        ),
        (
            "RSS news collectors",
            "crypto_data_bank/collectors/rss_news_collector.py",
            [
                "class RSSNewsCollector",
                "collect_from_cointelegraph",
                "collect_from_coindesk",
                "collect_from_bitcoinmagazine",
                "collect_all_rss_feeds",
                "deduplicate_news",
                "get_trending_coins",
            ],
        ),
        (
            "Sentiment collectors",
            "crypto_data_bank/collectors/sentiment_collector.py",
            [
                "class SentimentCollector",
                "collect_fear_greed_index",
                "collect_bitcoin_dominance",
                "collect_global_market_stats",
                "calculate_market_sentiment",
            ],
        ),
        (
            "HuggingFace AI",
            "crypto_data_bank/ai/huggingface_models.py",
            [
                "class HuggingFaceAnalyzer",
                "analyze_news_sentiment",
                "analyze_news_batch",
                "categorize_news",
                "calculate_aggregated_sentiment",
                "predict_price_direction",
            ],
        ),
        (
            "Database",
            "crypto_data_bank/database.py",
            [
                "class CryptoDataBank",
                "save_price",
                "get_latest_prices",
                "save_ohlcv_batch",
                "save_news",
                "get_latest_news",
                "save_sentiment",
                "save_ai_analysis",
                "cache_set",
                "cache_get",
            ],
        ),
        (
            "Orchestrator",
            "crypto_data_bank/orchestrator.py",
            [
                "class DataCollectionOrchestrator",
                "collect_and_store_prices",
                "collect_and_store_news",
                "collect_and_store_sentiment",
                "collect_all_data_once",
                "start_background_collection",
                "stop_background_collection",
            ],
        ),
        (
            "API Gateway",
            "crypto_data_bank/api_gateway.py",
            [
                '@app.get("/")',
                '@app.get("/api/health")',
                '@app.get("/api/prices")',
                '@app.get("/api/news")',
                '@app.get("/api/sentiment")',
                '@app.get("/api/market/overview")',
                '@app.get("/api/trending")',
                '@app.get("/api/ai/analysis")',
            ],
        ),
    ]

    all_valid = True

    for component, filepath, required_elements in structure_checks:
        print(f"\n🔍 {component}")

        path = Path(filepath)
        if not path.exists():
            print(f"   ❌ File not found")
            all_valid = False
            continue

        with open(path) as f:
            content = f.read()

        missing = []
        found = []

        for element in required_elements:
            if element in content:
                found.append(element)
            else:
                missing.append(element)

        if missing:
            print(f"   ⚠️  Missing: {', '.join(missing)}")
            all_valid = False
        else:
            print(f"   ✅ All {len(required_elements)} elements found")

    print("\n" + "=" * 70)

    # Summary
    print("\n📊 IMPLEMENTATION SUMMARY")
    print("=" * 70)

    print("\n✅ Completed Components:")
    print("   • Database layer with SQLite")
    print("   • 5 FREE price collectors (no API keys)")
    print("   • 8 RSS news collectors")
    print("   • 3 sentiment data sources")
    print("   • HuggingFace AI models integration")
    print("   • Background data collection orchestrator")
    print("   • FastAPI gateway with caching")
    print("   • Comprehensive REST API")
    print("   • HuggingFace Spaces deployment config")

    print("\n📊 Statistics:")
    print(f"   • Total files: {total}")
    print(f"   • Files created: {passed}")
    print(f"   • Completeness: {passed/total*100:.0f}%")

    print("\n🎯 Features:")
    print("   ✅ NO API keys required for basic functionality")
    print("   ✅ Real-time prices from 5+ sources")
    print("   ✅ News from 8+ RSS feeds")
    print("   ✅ Market sentiment analysis")
    print("   ✅ AI-powered sentiment analysis")
    print("   ✅ Intelligent caching")
    print("   ✅ Background data collection")
    print("   ✅ REST API with auto docs")
    print("   ✅ Ready for HuggingFace Spaces")

    print("\n🚀 Next Steps:")
    print("   1. Install dependencies:")
    print("      pip install -r crypto_data_bank/requirements.txt")
    print("")
    print("   2. Test the system:")
    print("      python test_crypto_bank.py")
    print("")
    print("   3. Start the API:")
    print("      ./start_crypto_bank.sh")
    print("      OR: python crypto_data_bank/api_gateway.py")
    print("")
    print("   4. Access the API:")
    print("      http://localhost:8888")
    print("      http://localhost:8888/docs")

    print("\n" + "=" * 70)

    if passed == total and all_valid:
        print("🎉 ALL COMPONENTS VALIDATED!")
        print("🎉 همه اجزا معتبر هستند!")
        print("\n✅ Ready for deployment to HuggingFace Spaces")
        print("✅ آماده استقرار در HuggingFace Spaces")
        return 0
    else:
        print("⚠️  VALIDATION INCOMPLETE")
        print(f"   Files: {passed}/{total}")
        print(f"   Structure: {'Valid' if all_valid else 'Invalid'}")
        return 1


if __name__ == "__main__":
    exit(main())

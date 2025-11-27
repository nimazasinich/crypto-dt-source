#!/usr/bin/env python3
"""
تست Data Hub Complete
=======================
تست تمام endpoint ها و منابع داده
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any

# Base URL - در Docker
BASE_URL = "http://localhost:7860/api/v2/data-hub"


async def test_market_prices():
    """تست دریافت قیمت‌های بازار"""
    print("\n🧪 تست قیمت‌های بازار...")

    async with httpx.AsyncClient() as client:
        # Test 1: Get top 10 coins
        try:
            response = await client.get(f"{BASE_URL}/market/prices?limit=10")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ دریافت {len(data.get('data', []))} قیمت از {data.get('source')}")
                if data.get("data"):
                    coin = data["data"][0]
                    print(f"   نمونه: {coin.get('symbol')} = ${coin.get('price', 0):,.2f}")
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در دریافت قیمت‌ها: {e}")

        # Test 2: Get specific symbols
        try:
            response = await client.get(f"{BASE_URL}/market/prices?symbols=BTC,ETH,BNB")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ دریافت قیمت برای سمبل‌های خاص")
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا: {e}")


async def test_ohlcv_data():
    """تست دریافت داده‌های OHLCV"""
    print("\n🧪 تست داده‌های OHLCV...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/market/ohlcv?symbol=BTC&interval=1h&limit=24")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ دریافت {len(data.get('data', []))} کندل از {data.get('source')}")
                if data.get("data"):
                    candle = data["data"][-1]
                    print(
                        f"   آخرین کندل: O:{candle.get('open', 0):,.2f} H:{candle.get('high', 0):,.2f} L:{candle.get('low', 0):,.2f} C:{candle.get('close', 0):,.2f}"
                    )
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در دریافت OHLCV: {e}")


async def test_sentiment():
    """تست تحلیل احساسات"""
    print("\n🧪 تست تحلیل احساسات...")

    async with httpx.AsyncClient() as client:
        # Test Fear & Greed Index
        try:
            response = await client.get(f"{BASE_URL}/sentiment/fear-greed")
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("current"):
                    current = data["current"]
                    print(
                        f"✅ Fear & Greed Index: {current.get('value')} ({current.get('value_classification')})"
                    )
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در Fear & Greed: {e}")

        # Test sentiment analysis
        try:
            response = await client.post(
                f"{BASE_URL}/sentiment/analyze",
                json={
                    "text": "Bitcoin price is surging and breaking all resistance levels!",
                    "source": "huggingface",
                },
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    sentiment = data.get("data", {})
                    print(
                        f"✅ تحلیل احساسات: {sentiment.get('label')} (confidence: {sentiment.get('score', 0):.2f})"
                    )
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در تحلیل احساسات: {e}")


async def test_news():
    """تست دریافت اخبار"""
    print("\n🧪 تست اخبار...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/news?query=bitcoin&limit=5")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    articles = data.get("articles", [])
                    print(f"✅ دریافت {len(articles)} خبر از {data.get('sources', ['unknown'])}")
                    if articles:
                        article = articles[0]
                        print(f"   نمونه: {article.get('title', '')[:80]}...")
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در دریافت اخبار: {e}")


async def test_trending():
    """تست ارزهای ترند"""
    print("\n🧪 تست ارزهای ترند...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/trending")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    trending = data.get("trending", [])
                    print(f"✅ دریافت {len(trending)} ارز ترند")
                    if trending:
                        coin = trending[0]
                        print(f"   #1: {coin.get('name')} ({coin.get('symbol')})")
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در دریافت ترندینگ: {e}")


async def test_blockchain():
    """تست داده‌های بلاکچین"""
    print("\n🧪 تست داده‌های بلاکچین...")

    async with httpx.AsyncClient() as client:
        # Test gas prices
        for chain in ["ethereum", "bsc"]:
            try:
                response = await client.get(f"{BASE_URL}/blockchain/{chain}/gas")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        gas = data.get("data", {})
                        if isinstance(gas, dict) and "gas_prices" in gas:
                            prices = gas["gas_prices"]
                            print(
                                f"✅ Gas prices for {chain}: Fast:{prices.get('fast')} Standard:{prices.get('standard')} Slow:{prices.get('slow')}"
                            )
                        elif isinstance(gas, dict):
                            print(f"✅ Gas data for {chain}: {gas}")
                        else:
                            print(f"⚠️ Gas data format unexpected for {chain}")
                else:
                    print(f"⚠️ {chain} gas: {response.status_code}")
            except Exception as e:
                print(f"⚠️ خطا در {chain} gas: {e}")


async def test_whale_activity():
    """تست فعالیت نهنگ‌ها"""
    print("\n🧪 تست فعالیت نهنگ‌ها...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/whales?limit=5&min_value_usd=1000000")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ دریافت داده‌های نهنگ‌ها از {data.get('source')}")
                if data.get("data"):
                    print(
                        f"   تعداد تراکنش‌های بزرگ: {len(data.get('data', {}).get('transactions', []))}"
                    )
            else:
                print(f"⚠️ وضعیت: {response.status_code}")
        except Exception as e:
            print(f"⚠️ خطا در فعالیت نهنگ‌ها: {e}")


async def test_social_media():
    """تست داده‌های شبکه‌های اجتماعی"""
    print("\n🧪 تست شبکه‌های اجتماعی...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/social/reddit?query=bitcoin&limit=5")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    posts = data.get("posts", [])
                    print(f"✅ دریافت {len(posts)} پست از Reddit")
                    if posts:
                        post = posts[0]
                        print(
                            f"   پست برتر: {post.get('title', '')[:60]}... (Score: {post.get('score', 0)})"
                        )
            else:
                print(f"⚠️ وضعیت: {response.status_code}")
        except Exception as e:
            print(f"⚠️ خطا در شبکه‌های اجتماعی: {e}")


async def test_ai_predictions():
    """تست پیش‌بینی‌های AI"""
    print("\n🧪 تست پیش‌بینی‌های AI...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/ai/predict/BTC?model_type=price&timeframe=24h")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ پیش‌بینی AI برای BTC دریافت شد")
                if data.get("prediction"):
                    print(f"   نتیجه: {data.get('prediction')}")
            else:
                print(f"⚠️ وضعیت: {response.status_code}")
        except Exception as e:
            print(f"⚠️ خطا در پیش‌بینی AI: {e}")


async def test_overview():
    """تست نمای کلی سمبل"""
    print("\n🧪 تست نمای کلی...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/overview/BTC")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    overview = data.get("overview", {})
                    print(f"✅ نمای کلی BTC:")
                    if overview.get("market"):
                        market = overview["market"]
                        print(f"   قیمت: ${market.get('price', 0):,.2f}")
                        print(f"   تغییر 24h: {market.get('change_24h', 0):.2f}%")
                    if overview.get("news"):
                        print(f"   اخبار: {len(overview['news'])} مقاله")
                    if overview.get("chart_data"):
                        print(f"   داده‌های نمودار: {len(overview['chart_data'])} کندل")
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در نمای کلی: {e}")


async def test_health():
    """تست سلامت سیستم"""
    print("\n🧪 تست سلامت سیستم...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    status = data.get("status", {})
                    operational = data.get("operational_count", 0)
                    total = data.get("total_sources", 0)
                    print(f"✅ سلامت سیستم: {operational}/{total} منابع فعال")

                    # Show status of each source
                    for source, state in status.items():
                        icon = (
                            "✅" if state == "operational" else "⚠️" if state == "degraded" else "❌"
                        )
                        print(f"   {icon} {source}: {state}")
            else:
                print(f"❌ خطا: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در بررسی سلامت: {e}")


async def main():
    """اجرای تمام تست‌ها"""
    print("=" * 60)
    print("🚀 شروع تست Data Hub Complete")
    print("=" * 60)
    print(f"📍 Base URL: {BASE_URL}")
    print(f"⏰ زمان: {datetime.now().isoformat()}")

    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                print("❌ سرور در دسترس نیست!")
                return
    except Exception as e:
        print(f"❌ سرور در دسترس نیست: {e}")
        print("\n💡 لطفاً ابتدا سرور را اجرا کنید:")
        print("   python api_server_extended.py")
        return

    # Run all tests
    await test_health()
    await asyncio.sleep(1)

    await test_market_prices()
    await asyncio.sleep(1)

    await test_ohlcv_data()
    await asyncio.sleep(1)

    await test_sentiment()
    await asyncio.sleep(1)

    await test_news()
    await asyncio.sleep(1)

    await test_trending()
    await asyncio.sleep(1)

    await test_blockchain()
    await asyncio.sleep(1)

    await test_whale_activity()
    await asyncio.sleep(1)

    await test_social_media()
    await asyncio.sleep(1)

    await test_ai_predictions()
    await asyncio.sleep(1)

    await test_overview()

    print("\n" + "=" * 60)
    print("✅ تست‌ها تکمیل شد!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

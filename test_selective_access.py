#!/usr/bin/env python3
"""
Test Selective Smart Access
تست دسترسی هوشمند انتخابی

فقط APIهایی که نیاز دارن از Proxy/DNS استفاده می‌کنن
بقیه مستقیم می‌رن (سریع‌تر)
"""

import asyncio
import json
from datetime import datetime
from backend.services.smart_access_manager import smart_access_manager
from backend.services.kucoin_client import kucoin_client
from backend.services.binance_client import binance_client
from backend.config.restricted_apis import (
    print_config_summary,
    get_restricted_apis_list,
    get_unrestricted_apis_list,
    should_use_smart_access
)


async def test_kucoin():
    """Test KuCoin (نیاز به Smart Access داره)"""
    print("\n" + "🔥"*30)
    print("TEST 1: KUCOIN (Needs Smart Access)")
    print("🔥"*30)
    
    results = []
    
    # Test 1: Health Check
    print("\n1️⃣ KuCoin Health Check:")
    try:
        is_healthy = await kucoin_client.health_check()
        print(f"   {'✅' if is_healthy else '⚠️'} Health Status: {is_healthy}")
        results.append({"test": "health", "status": "success" if is_healthy else "warning"})
    except Exception as e:
        print(f"   ⚠️ Health check failed: {str(e)[:50]}")
        results.append({"test": "health", "status": "warning"})
    
    # Test 2: Get Ticker
    print("\n2️⃣ KuCoin BTC-USDT Ticker:")
    try:
        ticker = await kucoin_client.get_ticker("BTC-USDT")
        if ticker:
            print(f"   ✅ Price: ${ticker['price']:,.2f}")
            print(f"   📊 24h Change: {ticker['change_24h']:.2f}%")
            print(f"   📈 High: ${ticker['high_24h']:,.2f}")
            print(f"   📉 Low: ${ticker['low_24h']:,.2f}")
            results.append({"test": "ticker", "status": "success", "price": ticker['price']})
        else:
            print(f"   ⚠️ KuCoin may be restricted in your region")
            results.append({"test": "ticker", "status": "restricted"})
    except Exception as e:
        print(f"   ⚠️ Failed: {str(e)[:50]}")
        results.append({"test": "ticker", "status": "failed"})
    
    # Test 3: Get 24h Stats
    print("\n3️⃣ KuCoin 24h Stats:")
    try:
        stats = await kucoin_client.get_24h_stats("ETH-USDT")
        if stats:
            print(f"   ✅ ETH Price: ${stats['price']:,.2f}")
            print(f"   📊 Volume: {stats['volume_24h']:,.0f}")
            results.append({"test": "stats", "status": "success"})
        else:
            print(f"   ⚠️ KuCoin may be restricted in your region")
            results.append({"test": "stats", "status": "restricted"})
    except Exception as e:
        print(f"   ⚠️ Failed: {str(e)[:50]}")
        results.append({"test": "stats", "status": "failed"})
    
    return results


async def test_binance():
    """Test Binance (ممکنه نیاز به Smart Access داشته باشه)"""
    print("\n" + "🔥"*30)
    print("TEST 2: BINANCE (May Need Smart Access)")
    print("🔥"*30)
    
    results = []
    
    # Test 1: Get Ticker
    print("\n1️⃣ Binance BTC/USDT Ticker:")
    ticker = await binance_client.get_24h_ticker("BTCUSDT")
    if ticker:
        price = ticker.get('lastPrice', ticker.get('price', 'N/A'))
        change = ticker.get('priceChangePercent', ticker.get('change', 'N/A'))
        print(f"   ✅ Price: ${price}")
        print(f"   📊 24h Change: {change}%")
        results.append({"test": "ticker", "status": "success", "price": str(price)})
    else:
        print(f"   ❌ Failed to get ticker")
        results.append({"test": "ticker", "status": "failed"})
    
    # Test 2: Get OHLCV
    print("\n2️⃣ Binance OHLCV Data:")
    ohlcv = await binance_client.get_ohlcv("BTCUSDT", "1h", limit=5)
    if ohlcv:
        print(f"   ✅ Got {len(ohlcv)} candles")
        latest = ohlcv[-1]
        print(f"   📊 Latest: O:{latest['open']}, H:{latest['high']}, L:{latest['low']}, C:{latest['close']}")
        results.append({"test": "ohlcv", "status": "success"})
    else:
        print(f"   ❌ Failed to get OHLCV")
        results.append({"test": "ohlcv", "status": "failed"})
    
    return results


async def test_unrestricted_apis():
    """Test APIهایی که مستقیم کار می‌کنن (بدون Smart Access)"""
    print("\n" + "✅"*30)
    print("TEST 3: UNRESTRICTED APIs (Direct Connection)")
    print("✅"*30)
    
    results = []
    
    # Test CoinGecko
    print("\n1️⃣ CoinGecko (Direct):")
    url = "https://api.coingecko.com/api/v3/ping"
    response = await smart_access_manager.smart_fetch(url)
    if response:
        data = response.json()
        print(f"   ✅ {data.get('gecko_says')}")
        results.append({"api": "coingecko", "status": "success"})
    else:
        print(f"   ❌ Failed")
        results.append({"api": "coingecko", "status": "failed"})
    
    # Test CoinPaprika
    print("\n2️⃣ CoinPaprika (Direct):")
    url = "https://api.coinpaprika.com/v1/tickers/btc-bitcoin"
    response = await smart_access_manager.smart_fetch(url)
    if response:
        data = response.json()
        print(f"   ✅ BTC Price: ${data['quotes']['USD']['price']:,.2f}")
        results.append({"api": "coinpaprika", "status": "success"})
    else:
        print(f"   ❌ Failed")
        results.append({"api": "coinpaprika", "status": "failed"})
    
    # Test Alternative.me
    print("\n3️⃣ Alternative.me Fear & Greed (Direct):")
    url = "https://api.alternative.me/fng/"
    response = await smart_access_manager.smart_fetch(url)
    if response:
        data = response.json()
        fng = data['data'][0]
        print(f"   ✅ Fear & Greed Index: {fng['value']} ({fng['value_classification']})")
        results.append({"api": "alternative_me", "status": "success"})
    else:
        print(f"   ❌ Failed")
        results.append({"api": "alternative_me", "status": "failed"})
    
    return results


async def test_access_decision():
    """نمایش تصمیم‌گیری Smart Access برای URLهای مختلف"""
    print("\n" + "🧪"*30)
    print("TEST 4: ACCESS DECISION LOGIC")
    print("🧪"*30)
    
    test_urls = [
        "https://api.kucoin.com/api/v1/market/stats",
        "https://api.binance.com/api/v3/ticker/24hr",
        "https://api.coingecko.com/api/v3/ping",
        "https://api.coinpaprika.com/v1/tickers",
        "https://api.bybit.com/v2/public/time",
        "https://api.alternative.me/fng/",
    ]
    
    print("\n📋 Access Decision for Each URL:\n")
    
    for url in test_urls:
        use_smart = should_use_smart_access(url)
        domain = url.split("://")[1].split("/")[0]
        
        icon = "🔐" if use_smart else "🔓"
        method = "SMART ACCESS" if use_smart else "DIRECT"
        
        print(f"{icon} {domain:40} → {method}")
    
    print("\n" + "─"*60)


async def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🎯 SELECTIVE SMART ACCESS TEST")
    print("تست دسترسی هوشمند انتخابی")
    print("="*60)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Print Configuration
    print("\n" + "📋"*30)
    print_config_summary()
    
    all_results = {
        "test_time": datetime.now().isoformat(),
        "kucoin_tests": [],
        "binance_tests": [],
        "unrestricted_tests": [],
        "statistics": {}
    }
    
    # Test Access Decision Logic
    await test_access_decision()
    
    await asyncio.sleep(1)
    
    # Test KuCoin (Restricted)
    kucoin_results = await test_kucoin()
    all_results["kucoin_tests"] = kucoin_results
    
    await asyncio.sleep(2)
    
    # Test Binance (Restricted)
    binance_results = await test_binance()
    all_results["binance_tests"] = binance_results
    
    await asyncio.sleep(2)
    
    # Test Unrestricted APIs
    unrestricted_results = await test_unrestricted_apis()
    all_results["unrestricted_tests"] = unrestricted_results
    
    # Get Statistics
    stats = smart_access_manager.get_statistics()
    all_results["statistics"] = stats
    
    # Print Summary
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE SUMMARY")
    print("="*60)
    
    # KuCoin
    kucoin_success = sum(1 for r in kucoin_results if r.get("status") == "success")
    print(f"\n🔥 KuCoin (Smart Access):")
    print(f"   Success: {kucoin_success}/{len(kucoin_results)}")
    
    # Binance
    binance_success = sum(1 for r in binance_results if r.get("status") == "success")
    print(f"\n🔥 Binance (Smart Access):")
    print(f"   Success: {binance_success}/{len(binance_results)}")
    
    # Unrestricted
    unrestricted_success = sum(1 for r in unrestricted_results if r.get("status") == "success")
    print(f"\n✅ Unrestricted APIs (Direct):")
    print(f"   Success: {unrestricted_success}/{len(unrestricted_results)}")
    
    # Overall
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Total Success: {stats['total_success']}")
    print(f"   Success Rate: {stats['success_rate']}")
    
    # Method Usage
    print(f"\n📊 Method Usage:")
    for method, data in stats["methods"].items():
        if data["success"] > 0 or data["failed"] > 0:
            print(f"   {method.upper()}:")
            print(f"      Success: {data['success']}, Failed: {data['failed']}")
    
    # Save results
    with open('selective_access_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: selective_access_test_results.json")
    
    # Key Insights
    print(f"\n" + "="*60)
    print("💡 KEY INSIGHTS")
    print("="*60)
    
    print(f"\n✅ Restricted APIs ({len(get_restricted_apis_list())}):")
    for api in get_restricted_apis_list():
        print(f"   🔐 {api} → Uses Smart Access (Proxy/DNS fallback)")
    
    print(f"\n✅ Unrestricted APIs ({len(get_unrestricted_apis_list())}):")
    for api in get_unrestricted_apis_list():
        print(f"   🔓 {api} → Direct connection (faster)")
    
    print(f"\n🎯 BENEFIT:")
    print(f"   ✅ Faster: Unrestricted APIs use direct connection")
    print(f"   ✅ Reliable: Restricted APIs have automatic fallback")
    print(f"   ✅ Efficient: No unnecessary proxy/DNS overhead")
    
    print("\n" + "="*60)
    print("🎉 TEST COMPLETE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())


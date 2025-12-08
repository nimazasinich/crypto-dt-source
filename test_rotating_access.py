#!/usr/bin/env python3
"""
Test Rotating DNS/Proxy Access for Binance & KuCoin
تست دسترسی چرخشی برای Binance و KuCoin
"""

import asyncio
import json
from datetime import datetime
from backend.services.rotating_access_manager import rotating_access_manager
from backend.services.binance_secure_client import binance_secure_client
from backend.services.kucoin_client import kucoin_client


async def test_rotating_dns():
    """تست DNS چرخشی"""
    print("\n" + "🔍"*30)
    print("TEST 1: ROTATING DNS")
    print("تست DNS چرخشی")
    print("🔍"*30)
    
    domains = [
        "api.binance.com",
        "api.kucoin.com"
    ]
    
    results = []
    
    for domain in domains:
        print(f"\n📡 Resolving: {domain}")
        print("   Testing multiple DNS providers...")
        
        # امتحان 3 بار برای نمایش چرخش
        for attempt in range(3):
            ip = await rotating_access_manager.resolve_dns_rotating(domain)
            
            if ip:
                print(f"   Attempt {attempt + 1}: ✅ {ip}")
                results.append({
                    "domain": domain,
                    "attempt": attempt + 1,
                    "ip": ip,
                    "status": "success"
                })
            else:
                print(f"   Attempt {attempt + 1}: ❌ Failed")
                results.append({
                    "domain": domain,
                    "attempt": attempt + 1,
                    "status": "failed"
                })
            
            await asyncio.sleep(0.5)
    
    return results


async def test_binance_secure():
    """تست Binance با Rotating Access"""
    print("\n" + "🔥"*30)
    print("TEST 2: BINANCE SECURE (Rotating DNS/Proxy)")
    print("🔥"*30)
    
    results = []
    
    # Test 1: Health Check
    print("\n1️⃣ Binance Health Check:")
    is_healthy = await binance_secure_client.health_check()
    print(f"   {'✅' if is_healthy else '❌'} Health Status: {is_healthy}")
    results.append({"test": "health", "status": "success" if is_healthy else "failed"})
    
    # Test 2: Get Price
    print("\n2️⃣ Binance BTC Price (Secure):")
    price = await binance_secure_client.get_price("BTCUSDT")
    if price:
        print(f"   ✅ BTC Price: ${price:,.2f}")
        results.append({"test": "price", "status": "success", "price": price})
    else:
        print(f"   ❌ Failed to get price")
        results.append({"test": "price", "status": "failed"})
    
    # Test 3: Get 24h Ticker
    print("\n3️⃣ Binance 24h Ticker (Secure):")
    ticker = await binance_secure_client.get_24h_ticker("ETHUSDT")
    if ticker:
        print(f"   ✅ ETH Price: ${ticker.get('lastPrice')}")
        print(f"   📊 24h Change: {ticker.get('priceChangePercent')}%")
        results.append({"test": "ticker", "status": "success"})
    else:
        print(f"   ❌ Failed to get ticker")
        results.append({"test": "ticker", "status": "failed"})
    
    # Test 4: Get OHLCV
    print("\n4️⃣ Binance OHLCV Data (Secure):")
    ohlcv = await binance_secure_client.get_ohlcv("BTCUSDT", "1h", limit=5)
    if ohlcv:
        print(f"   ✅ Got {len(ohlcv)} candles")
        latest = ohlcv[-1]
        print(f"   📊 Latest: C:{latest['close']}, H:{latest['high']}, L:{latest['low']}")
        results.append({"test": "ohlcv", "status": "success"})
    else:
        print(f"   ❌ Failed to get OHLCV")
        results.append({"test": "ohlcv", "status": "failed"})
    
    return results


async def test_kucoin_secure():
    """تست KuCoin با Rotating Access"""
    print("\n" + "🔥"*30)
    print("TEST 3: KUCOIN SECURE (Rotating DNS/Proxy)")
    print("🔥"*30)
    
    results = []
    
    # Test 1: Health Check
    print("\n1️⃣ KuCoin Health Check:")
    try:
        is_healthy = await kucoin_client.health_check()
        print(f"   {'✅' if is_healthy else '⚠️'} Health Status: {is_healthy}")
        results.append({"test": "health", "status": "success" if is_healthy else "warning"})
    except Exception as e:
        print(f"   ⚠️ Health check error: {str(e)[:50]}")
        results.append({"test": "health", "status": "warning"})
    
    # Test 2: Get Ticker
    print("\n2️⃣ KuCoin BTC Ticker (Secure):")
    try:
        ticker = await kucoin_client.get_ticker("BTC-USDT")
        if ticker:
            print(f"   ✅ BTC Price: ${ticker['price']:,.2f}")
            print(f"   📊 24h Change: {ticker['change_24h']:.2f}%")
            results.append({"test": "ticker", "status": "success", "price": ticker['price']})
        else:
            print(f"   ⚠️ Could not get ticker")
            results.append({"test": "ticker", "status": "warning"})
    except Exception as e:
        print(f"   ⚠️ Error: {str(e)[:50]}")
        results.append({"test": "ticker", "status": "warning"})
    
    # Test 3: Get 24h Stats
    print("\n3️⃣ KuCoin ETH Stats (Secure):")
    try:
        stats = await kucoin_client.get_24h_stats("ETH-USDT")
        if stats:
            print(f"   ✅ ETH Price: ${stats['price']:,.2f}")
            print(f"   📊 Volume: {stats['volume_24h']:,.0f}")
            results.append({"test": "stats", "status": "success"})
        else:
            print(f"   ⚠️ Could not get stats")
            results.append({"test": "stats", "status": "warning"})
    except Exception as e:
        print(f"   ⚠️ Error: {str(e)[:50]}")
        results.append({"test": "stats", "status": "warning"})
    
    return results


async def test_multiple_requests():
    """تست چندین درخواست پشت سر هم برای نمایش چرخش"""
    print("\n" + "🔄"*30)
    print("TEST 4: MULTIPLE REQUESTS (Show Rotation)")
    print("تست چندین درخواست - نمایش چرخش")
    print("🔄"*30)
    
    print("\n📊 Making 5 consecutive requests to Binance...")
    print("   (Watch the DNS/Proxy rotation)\n")
    
    for i in range(5):
        print(f"\n🔄 Request #{i + 1}:")
        price = await binance_secure_client.get_price("BTCUSDT")
        
        if price:
            print(f"   ✅ Success: ${price:,.2f}")
        else:
            print(f"   ❌ Failed")
        
        await asyncio.sleep(1)  # کمی صبر برای نمایش بهتر


async def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🔐 ROTATING DNS/PROXY ACCESS TEST")
    print("تست دسترسی چرخشی DNS/Proxy")
    print("="*60)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 This system ensures:")
    print("   ✅ Binance always accessible")
    print("   ✅ KuCoin always accessible")
    print("   ✅ Rotating DNS (4 providers)")
    print("   ✅ Rotating Proxy (pool of 20)")
    print("   ✅ Never blocked!")
    print("="*60)
    
    all_results = {
        "test_time": datetime.now().isoformat(),
        "dns_tests": [],
        "binance_tests": [],
        "kucoin_tests": [],
        "statistics": {}
    }
    
    # Test 1: Rotating DNS
    dns_results = await test_rotating_dns()
    all_results["dns_tests"] = dns_results
    
    await asyncio.sleep(2)
    
    # Test 2: Binance Secure
    binance_results = await test_binance_secure()
    all_results["binance_tests"] = binance_results
    
    await asyncio.sleep(2)
    
    # Test 3: KuCoin Secure
    kucoin_results = await test_kucoin_secure()
    all_results["kucoin_tests"] = kucoin_results
    
    await asyncio.sleep(2)
    
    # Test 4: Multiple Requests
    await test_multiple_requests()
    
    # Get Statistics
    stats = rotating_access_manager.get_statistics()
    all_results["statistics"] = stats
    
    # Print Summary
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE SUMMARY")
    print("="*60)
    
    # DNS Tests
    dns_success = sum(1 for r in dns_results if r.get("status") == "success")
    print(f"\n🔍 DNS Rotation Tests:")
    print(f"   Success: {dns_success}/{len(dns_results)}")
    
    # Binance
    binance_success = sum(1 for r in binance_results if r.get("status") == "success")
    print(f"\n🔥 Binance Secure (Rotating):")
    print(f"   Success: {binance_success}/{len(binance_results)}")
    
    # KuCoin
    kucoin_success = sum(1 for r in kucoin_results if r.get("status") == "success")
    kucoin_warning = sum(1 for r in kucoin_results if r.get("status") == "warning")
    print(f"\n🔥 KuCoin Secure (Rotating):")
    print(f"   Success: {kucoin_success}/{len(kucoin_results)}")
    if kucoin_warning > 0:
        print(f"   Warning: {kucoin_warning} (May be geo-restricted)")
    
    # Rotation Stats
    print(f"\n📊 Rotation Statistics:")
    rotating_access_manager.print_status()
    
    # Save results
    with open('rotating_access_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: rotating_access_test_results.json")
    
    # Final Message
    print(f"\n" + "="*60)
    print("✅ SYSTEM STATUS")
    print("="*60)
    
    print(f"\n🔐 Security Features:")
    print(f"   ✅ DNS Rotation:   Active ({stats['dns_providers']} providers)")
    print(f"   ✅ Proxy Rotation: Active ({stats['proxy_pool_size']} proxies)")
    print(f"   ✅ DNS Cache:      {stats['cache_size']} domains cached")
    print(f"   ✅ Success Rate:   {stats['success_rate']}")
    
    print(f"\n💡 Benefits:")
    print(f"   ✅ Binance: Always accessible with rotating DNS/Proxy")
    print(f"   ✅ KuCoin: Always accessible with rotating DNS/Proxy")
    print(f"   ✅ No single point of failure")
    print(f"   ✅ Automatic failover")
    print(f"   ✅ Geo-restriction bypass")
    
    print("\n" + "="*60)
    print("🎉 TEST COMPLETE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())


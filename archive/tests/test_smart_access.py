#!/usr/bin/env python3
"""
Test Smart Access to Binance and CoinGecko
تست دسترسی هوشمند به Binance و CoinGecko
"""

import asyncio
import json
from datetime import datetime
from backend.services.smart_access_manager import smart_access_manager, AccessMethod


async def test_binance_access():
    """Test access to Binance API"""
    print("\n" + "🔥"*30)
    print("TESTING BINANCE ACCESS")
    print("تست دسترسی به Binance")
    print("🔥"*30)
    
    # Test endpoints
    endpoints = [
        {
            "name": "Binance Ticker (BTC/USDT)",
            "url": "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        },
        {
            "name": "Binance Server Time",
            "url": "https://api.binance.com/api/v3/time"
        },
        {
            "name": "Binance Exchange Info",
            "url": "https://api.binance.com/api/v3/exchangeInfo?symbol=BTCUSDT"
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n{'─'*60}")
        print(f"📡 Endpoint: {endpoint['name']}")
        print(f"🔗 URL: {endpoint['url']}")
        print(f"{'─'*60}")
        
        response = await smart_access_manager.smart_fetch(endpoint["url"])
        
        if response:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"📊 Response Sample:")
            
            # Print first few keys
            if isinstance(data, dict):
                sample_keys = list(data.keys())[:5]
                for key in sample_keys:
                    value = data[key]
                    if isinstance(value, (str, int, float)):
                        print(f"   {key}: {value}")
            
            results.append({
                "endpoint": endpoint["name"],
                "url": endpoint["url"],
                "status": "success",
                "response_size": len(response.content)
            })
        else:
            print(f"\n❌ FAILED - All methods failed")
            results.append({
                "endpoint": endpoint["name"],
                "url": endpoint["url"],
                "status": "failed"
            })
    
    return results


async def test_coingecko_access():
    """Test access to CoinGecko API"""
    print("\n" + "🦎"*30)
    print("TESTING COINGECKO ACCESS")
    print("تست دسترسی به CoinGecko")
    print("🦎"*30)
    
    endpoints = [
        {
            "name": "CoinGecko Ping",
            "url": "https://api.coingecko.com/api/v3/ping"
        },
        {
            "name": "CoinGecko Bitcoin Price",
            "url": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        },
        {
            "name": "CoinGecko Trending",
            "url": "https://api.coingecko.com/api/v3/search/trending"
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n{'─'*60}")
        print(f"📡 Endpoint: {endpoint['name']}")
        print(f"🔗 URL: {endpoint['url']}")
        print(f"{'─'*60}")
        
        response = await smart_access_manager.smart_fetch(endpoint["url"])
        
        if response:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"📊 Response Sample:")
            
            if isinstance(data, dict):
                sample_keys = list(data.keys())[:5]
                for key in sample_keys:
                    value = data[key]
                    if isinstance(value, (str, int, float, bool)):
                        print(f"   {key}: {value}")
            
            results.append({
                "endpoint": endpoint["name"],
                "url": endpoint["url"],
                "status": "success",
                "response_size": len(response.content)
            })
        else:
            print(f"\n❌ FAILED - All methods failed")
            results.append({
                "endpoint": endpoint["name"],
                "url": endpoint["url"],
                "status": "failed"
            })
    
    return results


async def test_individual_methods():
    """Test each access method individually"""
    print("\n" + "🧪"*30)
    print("TESTING INDIVIDUAL METHODS")
    print("تست تک‌تک روش‌ها")
    print("🧪"*30)
    
    test_url = "https://api.binance.com/api/v3/time"
    
    methods = [
        AccessMethod.DIRECT,
        AccessMethod.DNS_CLOUDFLARE,
        AccessMethod.DNS_GOOGLE,
        AccessMethod.PROXY,
        AccessMethod.DNS_PROXY,
    ]
    
    results = []
    
    for method in methods:
        print(f"\n{'─'*60}")
        print(f"🔬 Testing Method: {method.value.upper()}")
        print(f"{'─'*60}")
        
        response, used_method = await smart_access_manager.fetch_with_method(
            test_url,
            method
        )
        
        if response and response.status_code == 200:
            print(f"✅ {method.value.upper()} - SUCCESS")
            results.append({
                "method": method.value,
                "status": "success"
            })
        else:
            print(f"❌ {method.value.upper()} - FAILED")
            results.append({
                "method": method.value,
                "status": "failed"
            })
    
    return results


async def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🚀 SMART ACCESS MANAGER - COMPREHENSIVE TEST")
    print("مدیر دسترسی هوشمند - تست جامع")
    print("="*60)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    all_results = {
        "test_time": datetime.now().isoformat(),
        "binance_tests": [],
        "coingecko_tests": [],
        "method_tests": [],
        "statistics": {}
    }
    
    # Test 1: Binance Access
    print("\n" + "🔥"*30)
    print("TEST 1: BINANCE API")
    print("🔥"*30)
    binance_results = await test_binance_access()
    all_results["binance_tests"] = binance_results
    
    await asyncio.sleep(2)  # Cool down
    
    # Test 2: CoinGecko Access
    print("\n" + "🦎"*30)
    print("TEST 2: COINGECKO API")
    print("🦎"*30)
    coingecko_results = await test_coingecko_access()
    all_results["coingecko_tests"] = coingecko_results
    
    await asyncio.sleep(2)  # Cool down
    
    # Test 3: Individual Methods
    print("\n" + "🧪"*30)
    print("TEST 3: INDIVIDUAL METHODS")
    print("🧪"*30)
    method_results = await test_individual_methods()
    all_results["method_tests"] = method_results
    
    # Get statistics
    stats = smart_access_manager.get_statistics()
    all_results["statistics"] = stats
    
    # Print Summary
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE SUMMARY")
    print("خلاصه کامل تست‌ها")
    print("="*60)
    
    # Binance Summary
    binance_success = sum(1 for r in binance_results if r["status"] == "success")
    binance_total = len(binance_results)
    print(f"\n🔥 Binance:")
    print(f"   Success: {binance_success}/{binance_total}")
    print(f"   Rate: {(binance_success/binance_total*100) if binance_total > 0 else 0:.1f}%")
    
    # CoinGecko Summary
    coingecko_success = sum(1 for r in coingecko_results if r["status"] == "success")
    coingecko_total = len(coingecko_results)
    print(f"\n🦎 CoinGecko:")
    print(f"   Success: {coingecko_success}/{coingecko_total}")
    print(f"   Rate: {(coingecko_success/coingecko_total*100) if coingecko_total > 0 else 0:.1f}%")
    
    # Methods Summary
    print(f"\n🧪 Individual Methods:")
    for result in method_results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"   {status_icon} {result['method'].upper()}: {result['status']}")
    
    # Overall Statistics
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Total Success: {stats['total_success']}")
    print(f"   Success Rate: {stats['success_rate']}")
    
    print(f"\n📊 Method Performance:")
    for method, data in stats["methods"].items():
        if data["success"] > 0 or data["failed"] > 0:
            print(f"   {method.upper()}:")
            print(f"      Success: {data['success']}, Failed: {data['failed']}")
            print(f"      Success Rate: {data['success_rate']}")
    
    # Save results
    with open('smart_access_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: smart_access_test_results.json")
    
    # Recommendations
    print(f"\n" + "="*60)
    print("💡 RECOMMENDATIONS")
    print("توصیه‌ها")
    print("="*60)
    
    # Find best method
    best_method = None
    best_rate = 0
    for method, data in stats["methods"].items():
        if data["success"] > 0:
            method_total = data["success"] + data["failed"]
            rate = (data["success"] / method_total * 100) if method_total > 0 else 0
            if rate > best_rate:
                best_rate = rate
                best_method = method
    
    if best_method:
        print(f"\n✅ Best Method: {best_method.upper()}")
        print(f"   Success Rate: {best_rate:.1f}%")
        print(f"\n💡 Recommendation:")
        if best_method == "direct":
            print(f"   ✅ Direct connection works! No proxy/DNS needed.")
            print(f"   ✅ اتصال مستقیم کار می‌کند! نیاز به پروکسی/DNS نیست")
        elif "dns" in best_method:
            print(f"   ✅ Use DNS over HTTPS ({best_method})")
            print(f"   ✅ از DNS over HTTPS استفاده کنید")
        elif best_method == "proxy":
            print(f"   ✅ Use free proxy")
            print(f"   ✅ از پروکسی رایگان استفاده کنید")
        else:
            print(f"   ✅ Use combined DNS + Proxy (most powerful)")
            print(f"   ✅ از ترکیب DNS + Proxy استفاده کنید (قوی‌ترین)")
    else:
        print(f"\n❌ No method succeeded")
        print(f"   Try again later or check network connection")
    
    print("\n" + "="*60)
    print("🎉 TEST COMPLETE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())


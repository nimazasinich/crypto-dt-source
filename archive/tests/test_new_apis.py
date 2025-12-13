#!/usr/bin/env python3
"""
Test new APIs found in NewResourceApi folder
تست APIهای جدید پیدا شده
"""

import httpx
import asyncio
import json
from datetime import datetime


async def test_newsapi_new_key():
    """
    Test News API with the new key found in docx
    تست News API با کلید جدید
    """
    print("\n" + "="*60)
    print("🧪 Testing News API (New Key)")
    print("="*60)
    
    api_key = "968a5e25552b4cb5ba3280361d8444ab"
    base_url = "https://newsapi.org/v2"
    
    # Test 1: Everything endpoint
    print("\n1️⃣ Testing /everything endpoint...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/everything",
                params={
                    "q": "cryptocurrency OR bitcoin",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 5,
                    "apiKey": api_key
                }
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Total Results: {data.get('totalResults', 0)}")
                print(f"   Articles Retrieved: {len(data.get('articles', []))}")
                
                if data.get('articles'):
                    print(f"\n   📰 Sample Article:")
                    article = data['articles'][0]
                    print(f"      Title: {article.get('title', 'N/A')[:80]}...")
                    print(f"      Source: {article.get('source', {}).get('name', 'N/A')}")
                    print(f"      Published: {article.get('publishedAt', 'N/A')}")
                
                return {
                    "endpoint": "/everything",
                    "status": "working",
                    "total_results": data.get('totalResults', 0),
                    "rate_limit": response.headers.get('X-RateLimit-Remaining', 'N/A')
                }
            
            elif response.status_code == 401:
                print(f"   ❌ UNAUTHORIZED - Invalid API key")
                return {"endpoint": "/everything", "status": "invalid_key"}
            
            elif response.status_code == 429:
                print(f"   ⚠️ RATE LIMITED")
                return {"endpoint": "/everything", "status": "rate_limited"}
            
            else:
                print(f"   ❌ FAILED - {response.text}")
                return {"endpoint": "/everything", "status": "error"}
    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return {"endpoint": "/everything", "status": "error", "error": str(e)}


async def test_newsapi_top_headlines():
    """Test top headlines endpoint"""
    print("\n2️⃣ Testing /top-headlines endpoint...")
    
    api_key = "968a5e25552b4cb5ba3280361d8444ab"
    base_url = "https://newsapi.org/v2"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/top-headlines",
                params={
                    "category": "business",
                    "language": "en",
                    "pageSize": 5,
                    "apiKey": api_key
                }
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Total Results: {data.get('totalResults', 0)}")
                print(f"   Rate Limit Remaining: {response.headers.get('X-RateLimit-Remaining', 'N/A')}")
                
                return {"endpoint": "/top-headlines", "status": "working"}
            else:
                print(f"   ❌ FAILED")
                return {"endpoint": "/top-headlines", "status": "error"}
    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return {"endpoint": "/top-headlines", "status": "error"}


async def test_coinmarketcap_info_endpoint():
    """
    Test CoinMarketCap info endpoint (new endpoint not in our system)
    تست endpoint جدید CMC
    """
    print("\n" + "="*60)
    print("🧪 Testing CoinMarketCap /info Endpoint")
    print("="*60)
    
    api_key = "04cf4b5b-9868-465c-8ba0-9f2e78c92eb1"
    base_url = "https://pro-api.coinmarketcap.com/v1"
    
    print("\n3️⃣ Testing /cryptocurrency/info endpoint...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{base_url}/cryptocurrency/info",
                params={"symbol": "BTC,ETH"},
                headers={"X-CMC_PRO_API_KEY": api_key}
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                
                if 'data' in data:
                    print(f"\n   💰 Coin Info Retrieved:")
                    for symbol, info in data['data'].items():
                        print(f"      {symbol}:")
                        print(f"         Name: {info.get('name', 'N/A')}")
                        print(f"         Category: {info.get('category', 'N/A')}")
                        print(f"         Description: {info.get('description', 'N/A')[:100]}...")
                        
                        if info.get('urls'):
                            urls = info['urls']
                            print(f"         Website: {urls.get('website', ['N/A'])[0] if urls.get('website') else 'N/A'}")
                
                return {
                    "endpoint": "/cryptocurrency/info",
                    "status": "working",
                    "data_available": True
                }
            
            else:
                print(f"   ❌ FAILED - {response.text[:200]}")
                return {"endpoint": "/cryptocurrency/info", "status": "error"}
    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return {"endpoint": "/cryptocurrency/info", "status": "error"}


async def test_proxy_apis_from_upgrade_doc():
    """
    Test proxy APIs mentioned in UPGRADE_ANALYSIS document
    تست proxy APIs
    """
    print("\n" + "="*60)
    print("🧪 Testing Proxy/DNS APIs from Upgrade Doc")
    print("="*60)
    
    results = []
    
    # Test 1: ProxyScrape API
    print("\n4️⃣ Testing ProxyScrape API...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://api.proxyscrape.com/v2/",
                params={
                    "request": "displayproxies",
                    "protocol": "http",
                    "timeout": "10000",
                    "country": "all",
                    "ssl": "all",
                    "anonymity": "elite",
                    "limit": "5"
                }
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                proxies = response.text.split('\n')
                proxies = [p.strip() for p in proxies if p.strip()]
                print(f"   ✅ SUCCESS!")
                print(f"   Proxies Retrieved: {len(proxies)}")
                if proxies:
                    print(f"   Sample Proxy: {proxies[0]}")
                
                results.append({
                    "api": "ProxyScrape",
                    "status": "working",
                    "proxies_count": len(proxies)
                })
            else:
                print(f"   ❌ FAILED")
                results.append({"api": "ProxyScrape", "status": "error"})
    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append({"api": "ProxyScrape", "status": "error"})
    
    # Test 2: Cloudflare DNS over HTTPS
    print("\n5️⃣ Testing Cloudflare DNS over HTTPS...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://cloudflare-dns.com/dns-query",
                params={"name": "api.binance.com", "type": "A"},
                headers={"accept": "application/dns-json"}
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                if 'Answer' in data:
                    print(f"   Resolved IPs: {[a['data'] for a in data['Answer']]}")
                
                results.append({"api": "Cloudflare DoH", "status": "working"})
            else:
                print(f"   ❌ FAILED")
                results.append({"api": "Cloudflare DoH", "status": "error"})
    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append({"api": "Cloudflare DoH", "status": "error"})
    
    # Test 3: Google DNS over HTTPS
    print("\n6️⃣ Testing Google DNS over HTTPS...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://dns.google/resolve",
                params={"name": "api.coingecko.com", "type": "A"}
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                if 'Answer' in data:
                    print(f"   Resolved IPs: {[a['data'] for a in data['Answer']]}")
                
                results.append({"api": "Google DoH", "status": "working"})
            else:
                print(f"   ❌ FAILED")
                results.append({"api": "Google DoH", "status": "error"})
    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append({"api": "Google DoH", "status": "error"})
    
    return results


async def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("NEW RESOURCE API TESTING")
    print("تست APIهای جدید پیدا شده در NewResourceApi")
    print("🚀"*30)
    print(f"\nTest Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = {
        "test_date": datetime.now().isoformat(),
        "apis_tested": [],
        "working_apis": [],
        "failed_apis": []
    }
    
    # Test 1: News API
    news_result1 = await test_newsapi_new_key()
    all_results["apis_tested"].append("NewsAPI /everything")
    if news_result1.get("status") == "working":
        all_results["working_apis"].append("NewsAPI /everything")
    else:
        all_results["failed_apis"].append("NewsAPI /everything")
    
    # Test 2: News API top headlines
    news_result2 = await test_newsapi_top_headlines()
    all_results["apis_tested"].append("NewsAPI /top-headlines")
    if news_result2.get("status") == "working":
        all_results["working_apis"].append("NewsAPI /top-headlines")
    else:
        all_results["failed_apis"].append("NewsAPI /top-headlines")
    
    # Test 3: CoinMarketCap info
    cmc_result = await test_coinmarketcap_info_endpoint()
    all_results["apis_tested"].append("CoinMarketCap /info")
    if cmc_result.get("status") == "working":
        all_results["working_apis"].append("CoinMarketCap /info")
    else:
        all_results["failed_apis"].append("CoinMarketCap /info")
    
    # Test 4: Proxy/DNS APIs
    proxy_results = await test_proxy_apis_from_upgrade_doc()
    for result in proxy_results:
        api_name = result["api"]
        all_results["apis_tested"].append(api_name)
        if result.get("status") == "working":
            all_results["working_apis"].append(api_name)
        else:
            all_results["failed_apis"].append(api_name)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"\n✅ Working APIs ({len(all_results['working_apis'])}):")
    for api in all_results['working_apis']:
        print(f"   • {api}")
    
    print(f"\n❌ Failed APIs ({len(all_results['failed_apis'])}):")
    for api in all_results['failed_apis']:
        print(f"   • {api}")
    
    print(f"\n📝 Total APIs Tested: {len(all_results['apis_tested'])}")
    print(f"✅ Success Rate: {len(all_results['working_apis'])/len(all_results['apis_tested'])*100:.1f}%")
    
    # Save results
    with open('new_api_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: new_api_test_results.json")
    print("\n" + "🎉"*30 + "\n")
    
    return all_results


if __name__ == "__main__":
    results = asyncio.run(main())

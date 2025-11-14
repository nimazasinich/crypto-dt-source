#!/usr/bin/env python3
"""
Test real providers to verify they actually work
بررسی واقعی پرووایدرها برای اطمینان از عملکرد
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_binance_direct():
    """Test Binance API directly"""
    print("\n" + "="*60)
    print("🧪 Testing Binance Provider")
    print("="*60)

    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": "BTCUSDT",
            "interval": "1h",
            "limit": 5
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)

            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ Response Time: {response.elapsed.total_seconds() * 1000:.0f}ms")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Data Received: {len(data)} candles")
                print(f"✅ First Candle: {data[0][:6]}")  # Show first 6 fields
                return True, "Binance works perfectly!"
            else:
                return False, f"Error: Status {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"


async def test_coingecko_direct():
    """Test CoinGecko API directly"""
    print("\n" + "="*60)
    print("🧪 Testing CoinGecko Provider")
    print("="*60)

    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true"
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)

            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ Response Time: {response.elapsed.total_seconds() * 1000:.0f}ms")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Coins Received: {list(data.keys())}")
                print(f"✅ BTC Price: ${data['bitcoin']['usd']:,.2f}")
                print(f"✅ BTC 24h Change: {data['bitcoin'].get('usd_24h_change', 0):.2f}%")
                return True, "CoinGecko works perfectly!"
            else:
                return False, f"Error: Status {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"


async def test_kraken_direct():
    """Test Kraken API directly"""
    print("\n" + "="*60)
    print("🧪 Testing Kraken Provider")
    print("="*60)

    try:
        url = "https://api.kraken.com/0/public/Ticker"
        params = {
            "pair": "XXBTZUSD"
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)

            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ Response Time: {response.elapsed.total_seconds() * 1000:.0f}ms")

            if response.status_code == 200:
                data = response.json()
                if "error" in data and data["error"]:
                    return False, f"Kraken Error: {data['error']}"

                result = data.get("result", {})
                if result:
                    pair_key = list(result.keys())[0]
                    ticker = result[pair_key]
                    print(f"✅ Pair: {pair_key}")
                    print(f"✅ Last Price: ${float(ticker['c'][0]):,.2f}")
                    print(f"✅ 24h Volume: {float(ticker['v'][1]):,.2f}")
                    return True, "Kraken works perfectly!"
                else:
                    return False, "No data in response"
            else:
                return False, f"Error: Status {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"


async def test_coincap_direct():
    """Test CoinCap API directly"""
    print("\n" + "="*60)
    print("🧪 Testing CoinCap Provider")
    print("="*60)

    try:
        url = "https://api.coincap.io/v2/assets"
        params = {
            "limit": 3
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)

            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ Response Time: {response.elapsed.total_seconds() * 1000:.0f}ms")

            if response.status_code == 200:
                data = response.json()
                assets = data.get("data", [])
                print(f"✅ Assets Received: {len(assets)}")
                for asset in assets[:3]:
                    print(f"   - {asset['symbol']}: ${float(asset['priceUsd']):,.2f}")
                return True, "CoinCap works perfectly!"
            else:
                return False, f"Error: Status {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"


async def test_fear_greed_index():
    """Test Fear & Greed Index"""
    print("\n" + "="*60)
    print("🧪 Testing Fear & Greed Index")
    print("="*60)

    try:
        url = "https://api.alternative.me/fng/"

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)

            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ Response Time: {response.elapsed.total_seconds() * 1000:.0f}ms")

            if response.status_code == 200:
                data = response.json()
                fng = data.get("data", [{}])[0]
                print(f"✅ Value: {fng.get('value')}/100")
                print(f"✅ Classification: {fng.get('value_classification')}")
                print(f"✅ Timestamp: {fng.get('timestamp')}")
                return True, "Fear & Greed Index works!"
            else:
                return False, f"Error: Status {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"


async def test_hf_data_engine():
    """Test HF Data Engine if running"""
    print("\n" + "="*60)
    print("🧪 Testing HF Data Engine")
    print("="*60)

    try:
        base_url = "http://localhost:8000"

        async with httpx.AsyncClient(timeout=30) as client:
            # Test health
            response = await client.get(f"{base_url}/api/health")

            if response.status_code == 200:
                print(f"✅ HF Engine is RUNNING")
                data = response.json()
                print(f"✅ Status: {data.get('status')}")
                print(f"✅ Uptime: {data.get('uptime')}s")
                print(f"✅ Providers: {len(data.get('providers', []))}")

                # Test prices endpoint
                try:
                    prices_response = await client.get(
                        f"{base_url}/api/prices",
                        params={"symbols": "BTC,ETH"}
                    )
                    if prices_response.status_code == 200:
                        prices_data = prices_response.json()
                        print(f"✅ Prices endpoint works: {len(prices_data.get('data', []))} coins")
                    else:
                        print(f"⚠️  Prices endpoint: Status {prices_response.status_code}")
                except:
                    print("⚠️  Prices endpoint not accessible")

                return True, "HF Data Engine works!"
            else:
                return False, f"HF Engine returned status {response.status_code}"

    except httpx.ConnectError:
        return False, "HF Engine is not running (Connection refused)"
    except Exception as e:
        return False, f"Error: {str(e)}"


async def test_fastapi_backend():
    """Test main FastAPI backend"""
    print("\n" + "="*60)
    print("🧪 Testing FastAPI Backend")
    print("="*60)

    try:
        base_url = "http://localhost:7860"

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{base_url}/health")

            if response.status_code == 200:
                print(f"✅ FastAPI Backend is RUNNING")
                print(f"✅ Status Code: {response.status_code}")

                # Test a few endpoints
                endpoints = ["/api/status", "/api/providers"]
                for endpoint in endpoints:
                    try:
                        resp = await client.get(f"{base_url}{endpoint}")
                        status = "✅" if resp.status_code < 400 else "⚠️"
                        print(f"{status} {endpoint}: Status {resp.status_code}")
                    except:
                        print(f"❌ {endpoint}: Failed")

                return True, "FastAPI Backend works!"
            else:
                return False, f"Backend returned status {response.status_code}"

    except httpx.ConnectError:
        return False, "FastAPI Backend is not running"
    except Exception as e:
        return False, f"Error: {str(e)}"


async def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("تست واقعی همه پرووایدرها")
    print("REAL PROVIDER TESTING")
    print("🚀"*30)

    results = {}

    # Test external providers
    print("\n📡 Testing External API Providers...")
    results["Binance"] = await test_binance_direct()
    await asyncio.sleep(1)

    results["CoinGecko"] = await test_coingecko_direct()
    await asyncio.sleep(1)

    results["Kraken"] = await test_kraken_direct()
    await asyncio.sleep(1)

    results["CoinCap"] = await test_coincap_direct()
    await asyncio.sleep(1)

    results["Fear & Greed"] = await test_fear_greed_index()
    await asyncio.sleep(1)

    # Test internal services
    print("\n🏠 Testing Internal Services...")
    results["HF Data Engine"] = await test_hf_data_engine()
    results["FastAPI Backend"] = await test_fastapi_backend()

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY / خلاصه تست")
    print("="*60)

    working = 0
    failed = 0

    for name, (success, message) in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{status} - {name}")
        print(f"   └─ {message}")

        if success:
            working += 1
        else:
            failed += 1

    print("\n" + "="*60)
    print(f"✅ Working: {working}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"📊 Success Rate: {(working/len(results)*100):.1f}%")
    print("="*60)

    # Recommendations
    print("\n💡 توصیه‌ها / RECOMMENDATIONS:")

    if results.get("HF Data Engine", (False, ""))[0]:
        print("✅ HF Data Engine is running - You can use it!")
    else:
        print("⚠️  HF Data Engine is not running. Start it with:")
        print("   cd hf-data-engine && python main.py")

    if results.get("FastAPI Backend", (False, ""))[0]:
        print("✅ FastAPI Backend is running - Dashboard ready!")
    else:
        print("⚠️  FastAPI Backend is not running. Start it with:")
        print("   python app.py")

    external_working = sum(1 for k, v in results.items()
                          if k not in ["HF Data Engine", "FastAPI Backend"] and v[0])

    if external_working >= 3:
        print(f"✅ {external_working} external APIs working - Good coverage!")
    else:
        print(f"⚠️  Only {external_working} external APIs working")
        print("   This might be due to IP restrictions or rate limits")

    print("\n✅ Test Complete!")
    return working, failed


if __name__ == "__main__":
    working, failed = asyncio.run(main())
    exit(0 if failed == 0 else 1)

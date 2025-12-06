#!/usr/bin/env python3
"""
Test all API endpoints to verify fixes
"""
import requests
import json
import sys
from datetime import datetime

API_BASE = "http://localhost:7860"

def test_endpoint(name, url, expected_status=200):
    """Test a single endpoint"""
    try:
        print(f"\n🧪 Testing {name}...")
        print(f"   URL: {url}")
        
        start_time = datetime.now()
        response = requests.get(url, timeout=10)
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        if response.status_code == expected_status:
            print(f"   ✅ SUCCESS ({duration:.0f}ms)")
            try:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    print(f"   📊 Response keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"   📊 Response: {len(data)} items")
            except:
                print(f"   📊 Response: {len(response.text)} chars")
            return True
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:100]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ FAILED: Cannot connect to server")
        print(f"   💡 Make sure Flask server is running: python app.py")
        return False
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("  API Endpoints Test Suite")
    print("=" * 60)
    
    endpoints = [
        ("Health Check", f"{API_BASE}/api/health"),
        ("Exchange Rate (BTC/USDT)", f"{API_BASE}/api/service/rate?pair=BTC/USDT"),
        ("Exchange Rate (ETH/USDT)", f"{API_BASE}/api/service/rate?pair=ETH/USDT"),
        ("Market OHLC", f"{API_BASE}/api/market/ohlc?symbol=BTC&interval=1h&limit=10"),
        ("OHLCV", f"{API_BASE}/api/ohlcv?symbol=BTC&timeframe=1h&limit=10"),
        ("Latest News", f"{API_BASE}/api/news/latest?limit=3"),
    ]
    
    results = []
    for name, url in endpoints:
        success = test_endpoint(name, url)
        results.append((name, success))
    
    print("\n" + "=" * 60)
    print("  Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n📊 Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All endpoints working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} endpoint(s) failed")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure Flask server is running: python app.py")
        print("   2. Restart the server after code changes")
        print("   3. Check server logs for errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())

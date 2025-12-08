#!/usr/bin/env python3
"""
تست جامع API
تست تمام endpoints موجود در سرور
"""
import requests
import json
import sys
from typing import Dict, Any

# پیکربندی
BASE_URL = "http://localhost:7860"


def test_endpoint(name: str, path: str, method: str = "GET", data: Dict = None):
    """تست یک endpoint"""
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"❌ {name}: Method {method} not supported")
            return False
        
        status = "✅" if 200 <= response.status_code < 400 else "❌"
        size = len(response.content)
        
        print(f"{status} {name}")
        print(f"   Path: {path}")
        print(f"   Status: {response.status_code}")
        print(f"   Size: {size} bytes")
        
        # نمایش محتوا برای پاسخ‌های کوچک
        if 200 <= response.status_code < 400 and size < 1000:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        
        print()
        return 200 <= response.status_code < 400
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection error")
        return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False


def main():
    """تابع اصلی"""
    print("=" * 80)
    print("🧪 تست جامع API")
    print("=" * 80)
    print()
    
    # بررسی سرور
    print("🔍 بررسی سرور...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"✅ سرور در حال اجرا است (Status: {response.status_code})")
    except:
        print("❌ سرور در دسترس نیست!")
        print("لطفاً سرور را راه‌اندازی کنید:")
        print("   python3 main.py")
        return 1
    
    print()
    print("=" * 80)
    print("📋 تست Endpoints")
    print("=" * 80)
    print()
    
    tests = [
        # Basic endpoints
        ("Root", "/"),
        ("Health", "/health"),
        ("API Health", "/api/health"),
        ("OpenAPI Schema", "/openapi.json"),
        
        # Resources endpoints
        ("Resources Stats", "/api/resources/stats"),
        ("Resources List", "/api/resources/list"),
        
        # Service endpoints
        ("Service Status", "/api/service/status"),
        ("Service Health", "/api/service/health"),
        
        # Data endpoints
        ("Market Data", "/api/market"),
        ("Trending", "/api/trending"),
        ("News", "/api/news"),
        ("Sentiment", "/api/sentiment"),
        
        # Provider endpoints
        ("Providers List", "/api/providers"),
        ("Providers Health", "/api/providers/health-summary"),
        
        # Status endpoints
        ("System Status", "/api/status"),
        ("API Stats", "/api/stats"),
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test_endpoint(*test):
            passed += 1
        else:
            failed += 1
    
    # نتیجه
    print("=" * 80)
    print("📊 نتایج")
    print("=" * 80)
    print()
    print(f"مجموع تست‌ها: {passed + failed}")
    print(f"✅ موفق: {passed}")
    print(f"❌ ناموفق: {failed}")
    print(f"درصد موفقیت: {(passed/(passed+failed)*100):.1f}%")
    print()
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

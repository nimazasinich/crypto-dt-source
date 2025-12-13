#!/usr/bin/env python3
"""
تست جامع کلاینت-سرور
بررسی هماهنگی کامل Backend و Frontend
"""
import requests
import asyncio
import websockets
import json
from datetime import datetime
from typing import Dict, List

BASE_URL = "http://localhost:7860"
WS_URL = "ws://localhost:7860/ws"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add(self, name: str, passed: bool, details: str = ""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 80)
        print("📊 خلاصه نتایج")
        print("=" * 80)
        print(f"مجموع تست‌ها: {total}")
        print(f"✅ موفق: {self.passed}")
        print(f"❌ ناموفق: {self.failed}")
        print(f"📈 نرخ موفقیت: {(self.passed/total*100):.1f}%")
        
        if self.failed > 0:
            print("\n❌ تست‌های ناموفق:")
            for test in self.tests:
                if not test['passed']:
                    print(f"   • {test['name']}: {test['details']}")

results = TestResults()

def test_http_endpoints():
    """تست تمام HTTP endpoints"""
    print("\n" + "=" * 80)
    print("1️⃣ تست HTTP REST API Endpoints")
    print("=" * 80)
    
    endpoints = [
        ("GET", "/", "صفحه اصلی"),
        ("GET", "/health", "Health Check"),
        ("GET", "/docs", "Swagger Docs"),
        ("GET", "/api/resources/stats", "آمار منابع"),
        ("GET", "/api/categories", "لیست دسته‌ها"),
        ("GET", "/api/resources/list", "لیست منابع"),
        ("GET", "/api/resources/category/block_explorers", "Block Explorers"),
    ]
    
    for method, path, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
            passed = response.status_code == 200
            
            if passed:
                print(f"✅ {name:30} → {response.status_code}")
                results.add(f"HTTP {name}", True)
            else:
                print(f"❌ {name:30} → {response.status_code}")
                results.add(f"HTTP {name}", False, f"Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name:30} → Error: {str(e)[:50]}")
            results.add(f"HTTP {name}", False, str(e)[:50])

def test_data_loading():
    """تست بارگذاری و یکپارچگی داده‌ها"""
    print("\n" + "=" * 80)
    print("2️⃣ تست بارگذاری داده‌ها")
    print("=" * 80)
    
    try:
        # تست آمار
        response = requests.get(f"{BASE_URL}/api/resources/stats")
        data = response.json()
        
        total = data.get('total_resources', 0)
        categories = data.get('total_categories', 0)
        
        print(f"📊 مجموع منابع: {total}")
        print(f"📁 دسته‌بندی‌ها: {categories}")
        
        if total == 281 and categories == 12:
            print("✅ داده‌ها به درستی بارگذاری شدند")
            results.add("Data Loading", True)
        else:
            print(f"⚠️  تعداد داده‌ها انتظار: 281 منبع، 12 دسته")
            results.add("Data Loading", False, f"Got {total} resources, {categories} categories")
        
        # تست هر دسته
        print("\n📂 بررسی دسته‌بندی‌ها:")
        categories_data = data.get('categories', {})
        for cat_name, count in list(categories_data.items())[:5]:
            print(f"   • {cat_name}: {count} مورد")
            results.add(f"Category {cat_name}", True)
            
    except Exception as e:
        print(f"❌ خطا در بارگذاری داده‌ها: {e}")
        results.add("Data Loading", False, str(e))

async def test_websocket():
    """تست WebSocket و Background Services"""
    print("\n" + "=" * 80)
    print("3️⃣ تست WebSocket و Background Services")
    print("=" * 80)
    
    try:
        async with websockets.connect(WS_URL) as ws:
            print("✅ اتصال WebSocket برقرار شد")
            results.add("WebSocket Connect", True)
            
            # پیام اولیه
            msg1 = await asyncio.wait_for(ws.recv(), timeout=5)
            data1 = json.loads(msg1)
            
            if data1.get('type') == 'initial_stats':
                print(f"✅ پیام اولیه: {data1['data']['total_resources']} منبع")
                results.add("WebSocket Initial Message", True)
            else:
                print(f"⚠️  پیام اولیه نامعتبر: {data1.get('type')}")
                results.add("WebSocket Initial Message", False, "Invalid type")
            
            # ارسال و دریافت
            await ws.send("test-ping")
            msg2 = await asyncio.wait_for(ws.recv(), timeout=5)
            data2 = json.loads(msg2)
            
            if data2.get('type') == 'pong':
                print(f"✅ ارسال/دریافت: {data2.get('message')}")
                results.add("WebSocket Send/Receive", True)
            else:
                print(f"⚠️  پاسخ نامعتبر")
                results.add("WebSocket Send/Receive", False)
            
            # Broadcast دوره‌ای
            print("⏳ صبر برای broadcast (10 ثانیه)...")
            msg3 = await asyncio.wait_for(ws.recv(), timeout=12)
            data3 = json.loads(msg3)
            
            if data3.get('type') == 'stats_update':
                print(f"✅ Broadcast دریافت شد: {data3['data']['total_resources']} منبع")
                results.add("WebSocket Broadcast", True)
            else:
                print(f"⚠️  Broadcast نامعتبر")
                results.add("WebSocket Broadcast", False)
                
    except asyncio.TimeoutError:
        print("❌ Timeout در WebSocket")
        results.add("WebSocket", False, "Timeout")
    except Exception as e:
        print(f"❌ خطا در WebSocket: {e}")
        results.add("WebSocket", False, str(e))

def test_specific_resources():
    """تست دسترسی به منابع خاص"""
    print("\n" + "=" * 80)
    print("4️⃣ تست دسترسی به منابع خاص")
    print("=" * 80)
    
    categories_to_test = [
        "block_explorers",
        "market_data_apis",
        "news_apis",
        "rpc_nodes"
    ]
    
    for category in categories_to_test:
        try:
            response = requests.get(
                f"{BASE_URL}/api/resources/category/{category}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                print(f"✅ {category:25} → {total} مورد")
                results.add(f"Resource {category}", True)
                
                # نمایش اولین مورد
                if data.get('resources') and len(data['resources']) > 0:
                    first = data['resources'][0]
                    print(f"   └─ مثال: {first.get('name', 'N/A')}")
            else:
                print(f"❌ {category:25} → Status {response.status_code}")
                results.add(f"Resource {category}", False, f"Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {category:25} → Error")
            results.add(f"Resource {category}", False, str(e)[:30])

def test_ui_compatibility():
    """تست سازگاری UI"""
    print("\n" + "=" * 80)
    print("5️⃣ تست سازگاری UI")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        html = response.text
        
        # بررسی عناصر کلیدی UI
        checks = {
            "HTML Structure": "<!DOCTYPE html>" in html,
            "Title": "<title>" in html,
            "WebSocket JS": "new WebSocket" in html,
            "Stats Display": "totalResources" in html,
            "Categories List": "categoryList" in html,
            "RTL Support": 'dir="rtl"' in html,
            "Responsive": "viewport" in html,
            "Styling": "<style>" in html
        }
        
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name:20}")
                results.add(f"UI {check_name}", True)
            else:
                print(f"❌ {check_name:20}")
                results.add(f"UI {check_name}", False)
                
    except Exception as e:
        print(f"❌ خطا در بررسی UI: {e}")
        results.add("UI Compatibility", False, str(e))

def test_cors():
    """تست CORS"""
    print("\n" + "=" * 80)
    print("6️⃣ تست CORS")
    print("=" * 80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/health",
            headers={"Origin": "http://example.com"}
        )
        
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        
        if cors_header == '*':
            print(f"✅ CORS فعال: {cors_header}")
            results.add("CORS", True)
        else:
            print(f"⚠️  CORS: {cors_header}")
            results.add("CORS", False, f"Header: {cors_header}")
            
    except Exception as e:
        print(f"❌ خطا در تست CORS: {e}")
        results.add("CORS", False, str(e))

def main():
    print("=" * 80)
    print("🧪 تست جامع کلاینت-سرور")
    print("=" * 80)
    print(f"⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend: {BASE_URL}")
    print(f"🔌 WebSocket: {WS_URL}")
    
    # اجرای تست‌ها
    test_http_endpoints()
    test_data_loading()
    asyncio.run(test_websocket())
    test_specific_resources()
    test_ui_compatibility()
    test_cors()
    
    # نمایش خلاصه
    results.summary()
    
    # نتیجه نهایی
    print("\n" + "=" * 80)
    if results.failed == 0:
        print("🎉 تمام تست‌ها با موفقیت پاس شد!")
        print("✅ سیستم آماده استقرار در Hugging Face است")
    else:
        print(f"⚠️  {results.failed} تست ناموفق")
        print("لطفاً مشکلات را برطرف کنید")
    print("=" * 80)

if __name__ == "__main__":
    main()

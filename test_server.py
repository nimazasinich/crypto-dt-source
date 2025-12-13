#!/usr/bin/env python3
"""
اسکریپت تست سرور
راه‌اندازی سرور و تست API endpoints
"""
import requests
import time
import sys
import subprocess
import signal
import json
from typing import Dict, Any, List

# رنگ‌ها برای خروجی
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


class ServerTester:
    """کلاس تست سرور"""
    
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def test_endpoint(self, name: str, path: str, method: str = "GET", 
                     data: Dict = None, expected_status: int = 200) -> bool:
        """تست یک endpoint"""
        url = f"{self.base_url}{path}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=10)
            else:
                print_error(f"Method {method} not supported")
                return False
            
            success = response.status_code == expected_status
            
            result = {
                'name': name,
                'path': path,
                'method': method,
                'status': response.status_code,
                'expected': expected_status,
                'success': success,
                'response_size': len(response.content)
            }
            
            self.test_results.append(result)
            
            if success:
                print_success(f"{name}: {response.status_code} ({len(response.content)} bytes)")
            else:
                print_error(f"{name}: {response.status_code} (expected {expected_status})")
            
            # نمایش محتوای کوچک
            if success and len(response.content) < 500:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    pass
            
            return success
            
        except requests.exceptions.ConnectionError:
            print_error(f"{name}: سرور در دسترس نیست")
            return False
        except requests.exceptions.Timeout:
            print_error(f"{name}: Timeout")
            return False
        except Exception as e:
            print_error(f"{name}: {str(e)}")
            return False
    
    def run_basic_tests(self):
        """تست‌های پایه"""
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}🧪 تست‌های پایه{Colors.ENDC}")
        print("=" * 80 + "\n")
        
        tests = [
            ("Health Check", "/health", "GET"),
            ("Root", "/", "GET"),
            ("API Docs", "/docs", "GET"),
            ("OpenAPI Schema", "/openapi.json", "GET"),
        ]
        
        for test in tests:
            self.test_endpoint(*test)
            time.sleep(0.5)
    
    def run_resource_tests(self):
        """تست منابع"""
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}🧪 تست منابع{Colors.ENDC}")
        print("=" * 80 + "\n")
        
        tests = [
            ("Resources List", "/api/resources/list", "GET"),
            ("Resources Stats", "/api/resources/stats", "GET"),
        ]
        
        for test in tests:
            self.test_endpoint(*test)
            time.sleep(0.5)
    
    def run_data_tests(self):
        """تست داده‌ها"""
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}🧪 تست داده‌های مارکت{Colors.ENDC}")
        print("=" * 80 + "\n")
        
        tests = [
            ("Market Data", "/api/market", "GET"),
            ("Trending", "/api/trending", "GET"),
            ("News", "/api/news", "GET"),
            ("Sentiment", "/api/sentiment", "GET"),
        ]
        
        for test in tests:
            self.test_endpoint(*test)
            time.sleep(0.5)
    
    def run_provider_tests(self):
        """تست providers"""
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}🧪 تست Providers{Colors.ENDC}")
        print("=" * 80 + "\n")
        
        tests = [
            ("Providers List", "/api/providers", "GET"),
            ("Providers Health", "/api/providers/health-summary", "GET"),
        ]
        
        for test in tests:
            self.test_endpoint(*test)
            time.sleep(0.5)
    
    def print_summary(self):
        """خلاصه نتایج"""
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}📊 خلاصه نتایج تست{Colors.ENDC}")
        print("=" * 80 + "\n")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print(f"مجموع تست‌ها: {total}")
        print_success(f"موفق: {passed}")
        if failed > 0:
            print_error(f"ناموفق: {failed}")
        
        print(f"\nدرصد موفقیت: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ تست‌های ناموفق:")
            for r in self.test_results:
                if not r['success']:
                    print(f"   - {r['name']}: {r['status']} (expected {r['expected']})")


def check_server_running(url: str = "http://localhost:7860") -> bool:
    """بررسی اجرا بودن سرور"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """تابع اصلی"""
    print(f"\n{Colors.BOLD}🚀 تست سرور Crypto Intelligence Hub{Colors.ENDC}\n")
    
    # بررسی سرور
    print_info("بررسی وضعیت سرور...")
    
    if not check_server_running():
        print_warning("سرور در حال اجرا نیست.")
        print_info("لطفاً در ترمینال دیگری سرور را اجرا کنید:")
        print(f"   python3 run_server.py")
        print("\nیا:")
        print(f"   python3 main.py")
        
        return 1
    
    print_success("سرور در حال اجرا است!")
    
    # ایجاد tester
    tester = ServerTester()
    
    # اجرای تست‌ها
    tester.run_basic_tests()
    tester.run_resource_tests()
    tester.run_data_tests()
    tester.run_provider_tests()
    
    # نمایش خلاصه
    tester.print_summary()
    
    print(f"\n{Colors.GREEN}✅ تست کامل شد!{Colors.ENDC}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

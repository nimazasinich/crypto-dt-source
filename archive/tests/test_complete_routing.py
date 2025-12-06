#!/usr/bin/env python3
"""
Complete Routing Test
Tests all routing from main app to static pages and API endpoints
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path
from typing import List, Dict

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

# Test configuration
BASE_URL = os.getenv("TEST_URL", "http://localhost:7860")
TIMEOUT = 30.0

class RoutingTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = {
            "passed": [],
            "failed": [],
            "total": 0
        }
    
    async def test_endpoint(self, path: str, method: str = "GET", 
                          description: str = None) -> bool:
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        desc = description or path
        
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                if method == "GET":
                    response = await client.get(url)
                elif method == "POST":
                    response = await client.post(url, json={})
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                success = response.status_code in [200, 301, 302, 307, 308]
                
                if success:
                    self.results["passed"].append({
                        "path": path,
                        "description": desc,
                        "status": response.status_code,
                        "content_length": len(response.content)
                    })
                    print(f"✅ {desc}: {response.status_code}")
                else:
                    self.results["failed"].append({
                        "path": path,
                        "description": desc,
                        "status": response.status_code,
                        "error": response.text[:200]
                    })
                    print(f"❌ {desc}: {response.status_code}")
                
                self.results["total"] += 1
                return success
                
        except Exception as e:
            self.results["failed"].append({
                "path": path,
                "description": desc,
                "error": str(e)
            })
            print(f"❌ {desc}: {e}")
            self.results["total"] += 1
            return False
    
    async def test_all_routes(self):
        """Test all routes in the application"""
        print("=" * 80)
        print("🚀 Testing Complete Application Routing")
        print("=" * 80)
        
        # 1. Test root endpoint
        print("\n📍 Testing Root Endpoint:")
        await self.test_endpoint("/", description="Root (Main UI)")
        
        # 2. Test static file serving
        print("\n📂 Testing Static Files:")
        static_files = [
            "/static/index.html",
            "/static/css/main.css",
            "/static/js/api-config.js",
        ]
        for path in static_files:
            await self.test_endpoint(path)
        
        # 3. Test main UI pages
        print("\n🎨 Testing Main UI Pages:")
        ui_pages = [
            "/static/pages/dashboard/index.html",
            "/static/pages/market/index.html",
            "/static/pages/trading-assistant/index.html",
            "/static/pages/technical-analysis/index.html",
            "/static/pages/news/index.html",
            "/static/pages/sentiment/index.html",
            "/static/pages/models/index.html",
            "/static/pages/api-explorer/index.html",
            "/static/pages/diagnostics/index.html",
            "/static/pages/data-sources/index.html",
            "/static/pages/providers/index.html",
            "/static/pages/settings/index.html",
            "/static/pages/help/index.html",
        ]
        for path in ui_pages:
            await self.test_endpoint(path)
        
        # 4. Test API endpoints (Smart Fallback)
        print("\n🔄 Testing Smart Fallback API:")
        smart_endpoints = [
            "/api/smart/health-report",
            "/api/smart/stats",
            "/api/smart/market?limit=10",
            "/api/smart/news?limit=5",
            "/api/smart/sentiment",
            "/api/smart/blockchain/ethereum",
        ]
        for path in smart_endpoints:
            await self.test_endpoint(path)
        
        # 5. Test original API endpoints
        print("\n📊 Testing Original API Endpoints:")
        api_endpoints = [
            "/api/health",
            "/api/market?limit=10",
            "/api/market/history?symbol=bitcoin&days=7",
        ]
        for path in api_endpoints:
            await self.test_endpoint(path)
        
        # 6. Test Alpha Vantage endpoints
        print("\n📈 Testing Alpha Vantage API:")
        av_endpoints = [
            "/api/alphavantage/health",
            "/api/alphavantage/prices?symbols=BTC",
            "/api/alphavantage/market-status",
        ]
        for path in av_endpoints:
            await self.test_endpoint(path)
        
        # 7. Test Massive.com endpoints
        print("\n📉 Testing Massive.com API:")
        massive_endpoints = [
            "/api/massive/health",
            "/api/massive/market-status",
        ]
        for path in massive_endpoints:
            await self.test_endpoint(path)
        
        # 8. Test documentation
        print("\n📚 Testing Documentation:")
        await self.test_endpoint("/docs", description="FastAPI Swagger Docs")
        await self.test_endpoint("/redoc", description="FastAPI ReDoc")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 Test Summary")
        print("=" * 80)
        
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        total = self.results["total"]
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n✅ Passed: {passed}/{total} ({pass_rate:.1f}%)")
        print(f"❌ Failed: {failed}/{total}")
        
        if self.results["failed"]:
            print("\n❌ Failed Tests:")
            for result in self.results["failed"]:
                print(f"   • {result['description']}")
                print(f"     Path: {result['path']}")
                if 'status' in result:
                    print(f"     Status: {result['status']}")
                if 'error' in result:
                    error = result['error'][:100]
                    print(f"     Error: {error}")
        
        print("\n" + "=" * 80)
        
        if pass_rate >= 80:
            print("✅ Routing Test: PASSED")
        else:
            print("❌ Routing Test: FAILED")
        
        print("=" * 80)


async def main():
    """Main test function"""
    tester = RoutingTester(BASE_URL)
    await tester.test_all_routes()
    
    # Return exit code based on results
    failed = len(tester.results["failed"])
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    print("🔍 Complete Routing Test")
    print(f"🎯 Target: {BASE_URL}")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

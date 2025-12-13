#!/usr/bin/env python3
"""
Test Service Discovery & Health Checking System
Run this to verify the service discovery system works correctly
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def test_service_discovery():
    """Test service discovery functionality"""
    print("\n" + "=" * 70)
    print("🔍 TESTING SERVICE DISCOVERY SYSTEM")
    print("=" * 70)
    
    try:
        from backend.services.service_discovery import ServiceDiscovery
        
        print("\n1️⃣  Initializing service discovery...")
        discovery = ServiceDiscovery()
        
        print("2️⃣  Discovering services...")
        services = discovery.discover_all_services()
        
        print(f"\n✅ Successfully discovered {len(services)} services!")
        
        # Print statistics
        print("\n📊 DISCOVERY STATISTICS:")
        print("-" * 70)
        
        from backend.services.service_discovery import ServiceCategory
        
        for category in ServiceCategory:
            count = len(discovery.get_services_by_category(category))
            if count > 0:
                print(f"   {category.value:30s}: {count:3d} services")
        
        # Show some example services
        print("\n📋 SAMPLE DISCOVERED SERVICES:")
        print("-" * 70)
        
        for service in list(services.values())[:10]:
            print(f"\n   • {service.name}")
            print(f"     Category: {service.category.value}")
            print(f"     URL: {service.base_url}")
            print(f"     Auth Required: {service.requires_auth}")
            if service.features:
                print(f"     Features: {', '.join(service.features[:3])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Service discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_health_checking():
    """Test health checking functionality"""
    print("\n" + "=" * 70)
    print("🏥 TESTING HEALTH CHECKING SYSTEM")
    print("=" * 70)
    
    try:
        from backend.services.health_checker import ServiceHealthChecker
        
        print("\n1️⃣  Initializing health checker...")
        checker = ServiceHealthChecker(timeout=5.0)
        
        print("2️⃣  Testing with known services...")
        
        # Test with a few known services
        test_services = [
            {
                "id": "coingecko",
                "name": "CoinGecko",
                "base_url": "https://api.coingecko.com",
                "endpoints": ["/api/v3/ping"],
                "requires_auth": False
            },
            {
                "id": "alternative_me",
                "name": "Fear & Greed Index",
                "base_url": "https://api.alternative.me",
                "endpoints": ["/fng/"],
                "requires_auth": False
            },
            {
                "id": "defillama",
                "name": "DefiLlama",
                "base_url": "https://api.llama.fi",
                "endpoints": ["/protocols"],
                "requires_auth": False
            }
        ]
        
        print(f"3️⃣  Checking health of {len(test_services)} services...\n")
        
        results = await checker.check_all_services(test_services, max_concurrent=3)
        
        print("\n✅ Health checks completed!")
        
        print("\n📊 HEALTH CHECK RESULTS:")
        print("-" * 70)
        
        for service_id, result in results.items():
            status_icon = "✅" if result.status.value == "online" else "❌"
            print(f"\n   {status_icon} {result.service_name}")
            print(f"      Status: {result.status.value}")
            if result.response_time_ms:
                print(f"      Response Time: {result.response_time_ms:.2f}ms")
            print(f"      Endpoint: {result.endpoint_checked}")
            if result.error_message:
                print(f"      Error: {result.error_message}")
        
        # Print summary
        summary = checker.get_health_summary()
        print("\n📈 SUMMARY:")
        print("-" * 70)
        print(f"   Total Services: {summary['total_services']}")
        print(f"   Average Response Time: {summary['average_response_time_ms']:.2f}ms")
        print("\n   Status Breakdown:")
        for status, count in summary['status_counts'].items():
            print(f"      {status}: {count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Health checking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test API endpoints (requires server to be running)"""
    print("\n" + "=" * 70)
    print("🌐 TESTING API ENDPOINTS")
    print("=" * 70)
    
    try:
        import httpx
        
        base_url = "http://localhost:7860"
        
        print("\n1️⃣  Testing service discovery endpoint...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{base_url}/api/services/discover")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Discovered {data['total_services']} services")
                else:
                    print(f"   ⚠️  Status code: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                print("   💡 Make sure the server is running!")
            
            print("\n2️⃣  Testing health check endpoint...")
            
            try:
                response = await client.get(f"{base_url}/api/services/health?force_check=true")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Health check successful")
                    if 'summary' in data:
                        print(f"   Total: {data['summary']['total_services']}")
                        print(f"   Status: {data['summary']['status_counts']}")
                else:
                    print(f"   ⚠️  Status code: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                print("   💡 Make sure the server is running!")
            
            print("\n3️⃣  Testing categories endpoint...")
            
            try:
                response = await client.get(f"{base_url}/api/services/categories")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Categories endpoint working")
                    print(f"   Categories: {len(data['categories'])}")
                else:
                    print(f"   ⚠️  Status code: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                print("   💡 Make sure the server is running!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API endpoint testing failed: {e}")
        print("\n💡 Make sure the server is running with: python main.py")
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🚀 SERVICE DISCOVERY & HEALTH MONITORING - TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test 1: Service Discovery
    print("\n" + "=" * 70)
    print("TEST 1: Service Discovery")
    print("=" * 70)
    result1 = await test_service_discovery()
    results.append(("Service Discovery", result1))
    
    # Test 2: Health Checking
    print("\n" + "=" * 70)
    print("TEST 2: Health Checking")
    print("=" * 70)
    result2 = await test_health_checking()
    results.append(("Health Checking", result2))
    
    # Test 3: API Endpoints (if server is running)
    print("\n" + "=" * 70)
    print("TEST 3: API Endpoints")
    print("=" * 70)
    result3 = await test_api_endpoints()
    results.append(("API Endpoints", result3))
    
    # Print final summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name:30s}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\n💡 To test API endpoints, make sure the server is running:")
        print("   python main.py")
    
    print("\n" + "=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

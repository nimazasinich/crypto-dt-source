#!/usr/bin/env python3
"""
Backend Stability Test Script
Verifies all new features work correctly
"""

import asyncio
import httpx
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

BASE_URL = "http://localhost:7860"


async def test_endpoints():
    """Test all new API endpoints"""
    print("=" * 70)
    print("🧪 Backend Stability Test Suite")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        tests = [
            ("Source Health Status", f"{BASE_URL}/api/source-health/status"),
            ("Environment Features", f"{BASE_URL}/api/config/features"),
            ("Missing Variables", f"{BASE_URL}/api/config/missing"),
            ("System Status", f"{BASE_URL}/api/status"),
            ("Models Status", f"{BASE_URL}/api/models/status"),
            ("Indicators Services", f"{BASE_URL}/api/indicators/services"),
        ]
        
        passed = 0
        failed = 0
        
        for name, url in tests:
            try:
                response = await client.get(url)
                
                # Check status code
                if response.status_code == 200:
                    # Verify JSON
                    data = response.json()
                    print(f"✅ {name:30} [200 OK] {len(str(data))} bytes")
                    passed += 1
                else:
                    print(f"❌ {name:30} [HTTP {response.status_code}]")
                    failed += 1
            
            except Exception as e:
                print(f"❌ {name:30} [ERROR: {str(e)[:50]}]")
                failed += 1
        
        print("=" * 70)
        print(f"Results: {passed} passed, {failed} failed")
        print("=" * 70)
        
        return failed == 0


def test_imports():
    """Test that all new modules can be imported"""
    print("\n📦 Testing Module Imports...")
    
    try:
        from backend.core.safe_http_client import SafeHTTPClient, health_tracker
        print("✅ backend.core.safe_http_client")
        
        from backend.core.env_config import env_config, is_feature_enabled
        print("✅ backend.core.env_config")
        
        from backend.routers.source_health_api import router as source_health_router
        print("✅ backend.routers.source_health_api")
        
        from backend.routers.env_config_api import router as env_config_router
        print("✅ backend.routers.env_config_api")
        
        print("\n✅ All modules imported successfully!")
        return True
    
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_tracker():
    """Test health tracker functionality"""
    print("\n🏥 Testing Health Tracker...")
    
    try:
        from backend.core.safe_http_client import health_tracker
        
        # Record success
        health_tracker.record_success("test_source", 150.0)
        
        # Record failure
        health_tracker.record_failure("test_source", "timeout", "Test timeout")
        
        # Get status
        status = health_tracker.get_source_health("test_source")
        
        assert status["successes"] == 1
        assert status["failures"] == 1
        assert status["consecutive_failures"] == 1
        
        print(f"✅ Success count: {status['successes']}")
        print(f"✅ Failure count: {status['failures']}")
        print(f"✅ Status: {status['status'].value if hasattr(status['status'], 'value') else status['status']}")
        
        # Reset
        health_tracker.reset_source("test_source")
        print("✅ Reset successful")
        
        return True
    
    except Exception as e:
        print(f"❌ Health tracker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_env_config():
    """Test environment configuration"""
    print("\n⚙️ Testing Environment Configuration...")
    
    try:
        from backend.core.env_config import env_config, is_feature_enabled
        
        # Get all features
        features = env_config.get_all_features()
        print(f"✅ Total features: {len(features)}")
        
        # Check specific features
        has_coingecko = is_feature_enabled("COINGECKO")
        print(f"✅ CoinGecko enabled: {has_coingecko}")
        
        # Get missing variables
        missing = env_config.get_missing_vars()
        print(f"✅ Missing variables: {len(missing)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Env config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n🚀 Starting Backend Stability Tests...")
    print("=" * 70)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed - cannot continue")
        return False
    
    # Test health tracker
    if not test_health_tracker():
        print("\n❌ Health tracker tests failed")
        return False
    
    # Test env config
    if not test_env_config():
        print("\n❌ Environment config tests failed")
        return False
    
    # Test API endpoints (requires server to be running)
    print("\n🌐 Testing API Endpoints (server must be running)...")
    print("   If tests fail, start server with: python run_server.py")
    print("=" * 70)
    
    try:
        success = await test_endpoints()
        
        if success:
            print("\n✅ ALL TESTS PASSED!")
            print("=" * 70)
            print("✨ Backend is stable and ready for production!")
            return True
        else:
            print("\n⚠️ Some endpoint tests failed")
            print("   Make sure the server is running: python run_server.py")
            return False
    
    except Exception as e:
        print(f"\n❌ Endpoint tests failed: {e}")
        print("   Make sure the server is running: python run_server.py")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

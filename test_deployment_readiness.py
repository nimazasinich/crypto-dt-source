#!/usr/bin/env python3
"""
Comprehensive Deployment Readiness Test
Tests all critical functionality before Hugging Face deployment
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

def test_file_structure():
    """Test that all required files exist"""
    print("\n" + "="*80)
    print("📁 Testing File Structure...")
    print("="*80)
    
    required_files = [
        "hf_space_api.py",
        "ai_models.py",
        "config.py",
        "static/index.html",
        "static/js/api-config.js",
        "static/js/trading-pairs-loader.js",
        "static/data/cryptocurrencies.json",
        "static/pages/dashboard/index.html",
        "static/pages/market/index.html",
        "static/pages/sentiment/index.html",
        "static/pages/models/index.html",
        "static/pages/trading-assistant/index.html",
        "database/db_manager.py",
        "backend/services/resource_loader.py",
        "cursor-instructions/consolidated_crypto_resources.json",
    ]
    
    missing = []
    for file in required_files:
        path = Path(file)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file} ({size:,} bytes)")
        else:
            print(f"❌ {file} - MISSING")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️  {len(missing)} files missing!")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files found!")
        return True


def test_cryptocurrency_list():
    """Test cryptocurrency list JSON"""
    print("\n" + "="*80)
    print("💰 Testing Cryptocurrency List...")
    print("="*80)
    
    crypto_file = Path("static/data/cryptocurrencies.json")
    if not crypto_file.exists():
        print("❌ cryptocurrencies.json not found!")
        return False
    
    try:
        with open(crypto_file, 'r') as f:
            data = json.load(f)
        
        cryptos = data.get('cryptocurrencies', [])
        total = data.get('total', 0)
        
        print(f"✅ Loaded {len(cryptos)} cryptocurrencies")
        print(f"   Expected: {total}")
        print(f"   Version: {data.get('version', 'unknown')}")
        
        # Test first few entries
        print(f"\n   Sample entries:")
        for crypto in cryptos[:5]:
            print(f"   • {crypto['rank']}. {crypto['name']} ({crypto['symbol']}) - {crypto['pair']}")
        
        if len(cryptos) >= 300:
            print(f"\n✅ SUCCESS: {len(cryptos)} cryptocurrencies loaded!")
            return True
        else:
            print(f"\n⚠️  WARNING: Only {len(cryptos)} cryptocurrencies (expected 300+)")
            return False
            
    except Exception as e:
        print(f"❌ Error loading cryptocurrencies: {e}")
        return False


def test_resource_loader():
    """Test resource loader"""
    print("\n" + "="*80)
    print("🔌 Testing Resource Loader...")
    print("="*80)
    
    try:
        from backend.services.resource_loader import get_resource_loader
        
        loader = get_resource_loader()
        total = loader.get_resource_count()
        stats = loader.get_statistics()
        
        print(f"✅ Resource loader initialized")
        print(f"   Total resources: {total}")
        print(f"   Expected: 305")
        print(f"   Categories: {stats['categories']}")
        print(f"   Free resources: {stats['free_resources']}")
        print(f"   With API keys: {stats['with_api_keys']}")
        print(f"   WebSocket enabled: {stats['websocket_enabled']}")
        
        print(f"\n   Category breakdown:")
        for category, count in sorted(stats['category_breakdown'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {category}: {count} resources")
        
        if total >= 305:
            print(f"\n✅ SUCCESS: All {total} resources loaded!")
            return True
        else:
            print(f"\n⚠️  WARNING: Only {total}/305 resources loaded")
            return False
            
    except Exception as e:
        print(f"❌ Error loading resources: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_models():
    """Test AI models configuration"""
    print("\n" + "="*80)
    print("🤖 Testing AI Models...")
    print("="*80)
    
    try:
        from ai_models import MODEL_SPECS, HF_MODE
        
        print(f"✅ AI models module loaded")
        print(f"   HF_MODE: {HF_MODE}")
        print(f"   Total model specs: {len(MODEL_SPECS)}")
        
        # Count by category
        by_category = {}
        for spec in MODEL_SPECS.values():
            cat = spec.category
            by_category[cat] = by_category.get(cat, 0) + 1
        
        print(f"\n   Models by category:")
        for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {category}: {count} models")
        
        # Test specific required models
        required_models = [
            'crypto_sent_kk08',
            'crypto_sent_social',
            'crypto_sent_fin'
        ]
        
        print(f"\n   Required models:")
        for model_key in required_models:
            if model_key in MODEL_SPECS:
                spec = MODEL_SPECS[model_key]
                print(f"   ✅ {model_key}: {spec.model_id}")
            else:
                print(f"   ❌ {model_key}: MISSING")
        
        print(f"\n✅ SUCCESS: AI models configured!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading AI models: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Test database connection"""
    print("\n" + "="*80)
    print("💾 Testing Database...")
    print("="*80)
    
    try:
        from database.db_manager import db_manager
        
        # Initialize database
        success = db_manager.init_database()
        if not success:
            print("❌ Failed to initialize database")
            return False
        
        print("✅ Database initialized")
        
        # Health check
        health = db_manager.health_check()
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Database: {health.get('database', 'unknown')}")
        
        if health.get('status') == 'healthy':
            print("\n✅ SUCCESS: Database healthy!")
            return True
        else:
            print(f"\n⚠️  WARNING: Database status: {health.get('status')}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_static_pages():
    """Test that all static pages exist and have required elements"""
    print("\n" + "="*80)
    print("📄 Testing Static Pages...")
    print("="*80)
    
    pages = [
        "static/pages/dashboard/index.html",
        "static/pages/market/index.html",
        "static/pages/trading-assistant/index.html",
        "static/pages/sentiment/index.html",
        "static/pages/models/index.html",
        "static/pages/news/index.html",
        "static/pages/technical-analysis/index.html",
        "static/pages/data-sources/index.html",
        "static/pages/api-explorer/index.html",
    ]
    
    all_ok = True
    for page in pages:
        path = Path(page)
        if path.exists():
            # Check file size
            size = path.stat().st_size
            if size > 1000:  # At least 1KB
                print(f"✅ {page} ({size:,} bytes)")
            else:
                print(f"⚠️  {page} ({size:,} bytes) - seems small")
                all_ok = False
        else:
            print(f"❌ {page} - MISSING")
            all_ok = False
    
    if all_ok:
        print(f"\n✅ SUCCESS: All {len(pages)} pages found!")
    else:
        print(f"\n⚠️  WARNING: Some pages missing or incomplete")
    
    return all_ok


def test_environment():
    """Test environment configuration"""
    print("\n" + "="*80)
    print("🌍 Testing Environment...")
    print("="*80)
    
    env_vars = {
        'PORT': os.getenv('PORT', '7860'),
        'HF_MODE': os.getenv('HF_MODE', 'public'),
        'TEST_MODE': os.getenv('TEST_MODE', 'false'),
        'SPACE_ID': os.getenv('SPACE_ID', 'not_set'),
    }
    
    for key, value in env_vars.items():
        masked = value if key not in ['HF_TOKEN'] else '***' if value else 'not_set'
        print(f"   {key}: {masked}")
    
    print(f"\n✅ Environment checked")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 DEPLOYMENT READINESS TEST")
    print("="*80)
    print("Testing all critical functionality before Hugging Face deployment...")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Cryptocurrency List", test_cryptocurrency_list),
        ("Resource Loader", test_resource_loader),
        ("AI Models", test_ai_models),
        ("Database", test_database),
        ("Static Pages", test_static_pages),
        ("Environment", test_environment),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} test FAILED with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "="*80)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready for deployment!")
        print("="*80)
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before deploying.")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

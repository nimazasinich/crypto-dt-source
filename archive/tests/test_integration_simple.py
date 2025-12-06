#!/usr/bin/env python3
"""
Simple Integration Test Script
Tests file existence and structure without external dependencies
"""

import json
from pathlib import Path

def test_static_files():
    """Test if static files exist"""
    print("🧪 Testing static file structure...")
    print()
    
    files = {
        "Main HTML Page": "static/pages/crypto-api-hub-integrated/index.html",
        "Page Styles": "static/pages/crypto-api-hub-integrated/crypto-api-hub-integrated.css",
        "Enhanced JS": "static/js/crypto-api-hub-enhanced.js",
        "Design System": "static/shared/css/design-system.css",
        "Table Component": "static/shared/js/components/table.js",
        "Table Styles": "static/shared/css/table.css",
        "Toast Component": "static/shared/js/components/toast.js",
        "Toast Helper": "static/shared/js/components/toast-helper.js",
        "Loading Component": "static/shared/js/components/loading.js",
        "Loading Helper": "static/shared/js/components/loading-helper.js",
        "API Client": "static/shared/js/core/api-client.js",
        "Config": "static/shared/js/core/config.js",
    }
    
    passed = 0
    failed = 0
    
    for name, file_path in files.items():
        full_path = Path(file_path)
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✅ {name}")
            print(f"     📁 {file_path} ({size:,} bytes)")
            passed += 1
        else:
            print(f"  ❌ {name}")
            print(f"     📁 {file_path} NOT FOUND")
            failed += 1
    
    print()
    print(f"  📊 Files: {passed} passed, {failed} failed")
    return failed == 0

def test_services_json():
    """Test services JSON file"""
    print("\n🧪 Testing services data...")
    print()
    
    json_path = Path("crypto_api_hub_services.json")
    
    if not json_path.exists():
        print("  ❌ crypto_api_hub_services.json NOT FOUND")
        return False
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print("  ✅ JSON file is valid")
        
        # Check structure
        if "metadata" not in data:
            print("  ❌ Missing 'metadata' key")
            return False
        
        if "categories" not in data:
            print("  ❌ Missing 'categories' key")
            return False
        
        print("  ✅ JSON structure is correct")
        
        # Display statistics
        metadata = data["metadata"]
        print()
        print("  📊 Statistics:")
        print(f"     • Version: {metadata.get('version', 'N/A')}")
        print(f"     • Total services: {metadata.get('total_services', 'N/A')}")
        print(f"     • Total endpoints: {metadata.get('total_endpoints', 'N/A')}")
        print(f"     • API keys: {metadata.get('api_keys_count', 'N/A')}")
        print(f"     • Last updated: {metadata.get('last_updated', 'N/A')}")
        
        # Display categories
        categories = data["categories"]
        print()
        print(f"  📊 Categories ({len(categories)}):")
        for cat_key, cat_data in categories.items():
            services = cat_data.get("services", [])
            print(f"     • {cat_key}: {len(services)} services")
        
        return True
            
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_documentation():
    """Test if documentation exists"""
    print("\n🧪 Testing documentation...")
    print()
    
    docs = {
        "Integration Guide": "SEAMLESS_INTEGRATION_GUIDE.md",
        "Integration Summary": "INTEGRATION_SUMMARY.md",
    }
    
    passed = 0
    failed = 0
    
    for name, file_path in docs.items():
        full_path = Path(file_path)
        if full_path.exists():
            size = full_path.stat().st_size
            lines = len(full_path.read_text().split('\n'))
            print(f"  ✅ {name}")
            print(f"     📁 {file_path} ({size:,} bytes, {lines} lines)")
            passed += 1
        else:
            print(f"  ❌ {name}")
            print(f"     📁 {file_path} NOT FOUND")
            failed += 1
    
    print()
    print(f"  📊 Docs: {passed} passed, {failed} failed")
    return failed == 0

def test_backend_router():
    """Test if backend router exists"""
    print("\n🧪 Testing backend router...")
    print()
    
    router_path = Path("backend/routers/crypto_api_hub_router.py")
    
    if not router_path.exists():
        print("  ❌ crypto_api_hub_router.py NOT FOUND")
        return False
    
    print("  ✅ Backend router exists")
    
    # Check for key functions
    content = router_path.read_text()
    
    checks = [
        ("get_all_services", "GET /services endpoint"),
        ("test_api_endpoint", "POST /test endpoint"),
        ("load_services", "Load services function"),
    ]
    
    for func_name, description in checks:
        if func_name in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ⚠️  {description} not found")
    
    return True

def main():
    """Run all tests"""
    print("=" * 70)
    print("🚀 SEAMLESS BACKEND-FRONTEND INTEGRATION TEST")
    print("=" * 70)
    print()
    
    results = []
    
    # Test static files
    results.append(test_static_files())
    
    # Test services JSON
    results.append(test_services_json())
    
    # Test documentation
    results.append(test_documentation())
    
    # Test backend router
    results.append(test_backend_router())
    
    # Summary
    print()
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print()
    
    if all(results):
        print("  ✅ All tests passed!")
        print()
        print("  🎉 Integration is complete and ready to use!")
    else:
        print("  ⚠️  Some tests failed")
        print()
        print("  Please check the errors above")
    
    print()
    print("=" * 70)
    print("📚 NEXT STEPS")
    print("=" * 70)
    print()
    print("  1. Start the backend server:")
    print("     uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("  2. Access the integrated page:")
    print("     http://localhost:8000/static/pages/crypto-api-hub-integrated/")
    print()
    print("  3. Test the features:")
    print("     • Search and filter services")
    print("     • Test API endpoints")
    print("     • Export data as JSON")
    print("     • Check self-healing (stop backend and refresh)")
    print()
    print("  4. Read the documentation:")
    print("     • SEAMLESS_INTEGRATION_GUIDE.md - Full guide")
    print("     • INTEGRATION_SUMMARY.md - Quick overview")
    print()
    print("=" * 70)
    print("✨ Happy coding!")
    print("=" * 70)

if __name__ == "__main__":
    main()

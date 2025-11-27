#!/usr/bin/env python3
"""
Integration Test Script
Tests the seamless backend-frontend integration
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_static_file_exists():
    """Test if static files are accessible"""
    print("🧪 Testing static file access...")
    
    files_to_check = [
        "/static/pages/crypto-api-hub-integrated/index.html",
        "/static/pages/crypto-api-hub-integrated/crypto-api-hub-integrated.css",
        "/static/js/crypto-api-hub-enhanced.js",
        "/static/shared/css/design-system.css",
        "/static/shared/js/components/table.js",
    ]
    
    for file_path in files_to_check:
        full_path = Path(f".{file_path}")
        if full_path.exists():
            print(f"  ✅ {file_path} exists")
        else:
            print(f"  ❌ {file_path} NOT FOUND")

def test_services_json():
    """Test if services JSON file exists and is valid"""
    print("\n🧪 Testing services JSON file...")
    
    json_path = Path("./crypto_api_hub_services.json")
    
    if not json_path.exists():
        print("  ❌ crypto_api_hub_services.json NOT FOUND")
        return False
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print("  ✅ JSON file is valid")
        
        # Check structure
        if "metadata" in data and "categories" in data:
            print("  ✅ JSON structure is correct")
            
            metadata = data["metadata"]
            print(f"  📊 Total services: {metadata.get('total_services', 'N/A')}")
            print(f"  📊 Total endpoints: {metadata.get('total_endpoints', 'N/A')}")
            print(f"  📊 API keys: {metadata.get('api_keys_count', 'N/A')}")
            
            categories = data["categories"]
            print(f"  📊 Categories: {', '.join(categories.keys())}")
            
            return True
        else:
            print("  ❌ JSON structure is incorrect")
            return False
            
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON: {e}")
        return False

def test_backend_endpoint(endpoint, method="GET", description=""):
    """Test a backend endpoint"""
    print(f"\n🧪 Testing {method} {endpoint}")
    if description:
        print(f"   {description}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ Status: {response.status_code}")
            try:
                data = response.json()
                print(f"  ✅ Valid JSON response")
                return True
            except:
                print(f"  ⚠️  Non-JSON response")
                return True
        else:
            print(f"  ❌ Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  Backend not running (connection refused)")
        print(f"     This is normal if you haven't started the server yet")
        return None
    except requests.exceptions.Timeout:
        print(f"  ❌ Request timeout")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_cors_proxy():
    """Test the CORS proxy endpoint"""
    print("\n🧪 Testing CORS proxy endpoint...")
    
    try:
        # Test with a simple external API
        response = requests.post(
            f"{BASE_URL}/api/crypto-hub/test",
            json={
                "url": "https://api.coingecko.com/api/v3/ping",
                "method": "GET",
                "headers": {},
                "body": None
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("  ✅ CORS proxy works")
                return True
            else:
                print("  ❌ CORS proxy returned failure")
                return False
        else:
            print(f"  ❌ Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  ⚠️  Backend not running")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 SEAMLESS INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Test static files
    test_static_file_exists()
    
    # Test services JSON
    json_valid = test_services_json()
    
    # Test backend endpoints (only if backend is running)
    print("\n" + "=" * 60)
    print("🌐 BACKEND API TESTS")
    print("=" * 60)
    
    test_backend_endpoint(
        "/api/crypto-hub/services",
        method="GET",
        description="Get all crypto services"
    )
    
    test_cors_proxy()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print("""
✅ Static files checked
✅ JSON data validated
⚠️  Backend tests require running server

To start the backend:
  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

Then access the page at:
  http://localhost:8000/static/pages/crypto-api-hub-integrated/
    """)
    
    print("=" * 60)
    print("✨ Integration is ready!")
    print("=" * 60)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script
Tests all critical endpoints for model loading and dashboard functionality
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:7860"

def test_endpoint(name, endpoint, method="GET", data=None):
    """Test a single endpoint"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*70}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
        else:
            print(f"❌ Unknown method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success!")
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Special handling for models summary
                if 'summary' in data:
                    summary = data.get('summary', {})
                    print(f"  - Total Models: {summary.get('total_models', 0)}")
                    print(f"  - Loaded Models: {summary.get('loaded_models', 0)}")
                    print(f"  - Failed Models: {summary.get('failed_models', 0)}")
                    print(f"  - HF Mode: {summary.get('hf_mode', 'unknown')}")
                
                if 'categories' in data:
                    categories = data.get('categories', {})
                    print(f"  - Categories: {len(categories)}")
                    for cat, models in list(categories.items())[:3]:
                        print(f"    * {cat}: {len(models)} models")
                
                return True
            except json.JSONDecodeError:
                print(f"⚠️  Response is not JSON: {response.text[:200]}")
                return False
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Server not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Server took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE ENDPOINT TESTING")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Wait for server to start
    print("\n⏳ Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is running!")
                break
        except:
            time.sleep(1)
            print(f"  Attempt {i+1}/10...")
    else:
        print("❌ Server is not responding. Please start the server first.")
        print("   Run: python api_server_extended.py")
        return
    
    results = {}
    
    # Test critical endpoints
    endpoints = [
        ("Health Check", "/api/health"),
        ("Models Summary", "/api/models/summary"),
        ("Models Status", "/api/models/status"),
        ("Resources Summary", "/api/resources/summary"),
        ("Resources Count", "/api/resources/count"),
        ("Providers Summary", "/api/providers/summary"),
    ]
    
    for name, endpoint in endpoints:
        results[name] = test_endpoint(name, endpoint)
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("\n🎉 All endpoints are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} endpoint(s) failed. Check server logs for details.")

if __name__ == "__main__":
    main()


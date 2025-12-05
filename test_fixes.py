#!/usr/bin/env python3
"""
Test script to verify all fixes are working correctly
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:7860"
RESULTS = []

def log_result(test_name: str, passed: bool, message: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = f"{status} - {test_name}"
    if message:
        result += f": {message}"
    print(result)
    RESULTS.append({"test": test_name, "passed": passed, "message": message})

def test_models_reinitialize():
    """Test 1: Model Reinitialization Endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/api/models/reinitialize", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") or data.get("status") == "ok":
                log_result("Model Reinitialize", True, f"Status: {data.get('status')}")
                return True
            else:
                log_result("Model Reinitialize", False, f"Response: {data}")
                return False
        else:
            log_result("Model Reinitialize", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_result("Model Reinitialize", False, str(e))
        return False

def test_sentiment_analysis():
    """Test 2: Sentiment Analysis with Fallback"""
    test_cases = [
        {"text": "Bitcoin is going to the moon!", "expected": ["bullish", "positive"]},
        {"text": "Market is crashing, sell everything!", "expected": ["bearish", "negative"]},
        {"text": "BTC price is stable today", "expected": ["neutral"]}
    ]
    
    all_passed = True
    for case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/sentiment",
                json={"text": case["text"], "mode": "auto"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                sentiment = data.get("sentiment", "").lower()
                
                # Check if sentiment matches expected
                matches = any(exp in sentiment for exp in case["expected"])
                
                if matches:
                    log_result(
                        f"Sentiment: '{case['text'][:30]}...'",
                        True,
                        f"Got: {sentiment}"
                    )
                else:
                    log_result(
                        f"Sentiment: '{case['text'][:30]}...'",
                        False,
                        f"Expected: {case['expected']}, Got: {sentiment}"
                    )
                    all_passed = False
            else:
                log_result(
                    f"Sentiment: '{case['text'][:30]}...'",
                    False,
                    f"HTTP {response.status_code}"
                )
                all_passed = False
        except Exception as e:
            log_result(
                f"Sentiment: '{case['text'][:30]}...'",
                False,
                str(e)
            )
            all_passed = False
    
    return all_passed

def test_models_status():
    """Test 3: Models Status Endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/models/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models_loaded = data.get("models_loaded", 0)
            log_result("Models Status", True, f"Loaded: {models_loaded} models")
            return True
        else:
            log_result("Models Status", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_result("Models Status", False, str(e))
        return False

def test_health():
    """Test 4: API Health Check"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_result("API Health", True, f"Status: {data.get('status', 'unknown')}")
            return True
        else:
            log_result("API Health", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_result("API Health", False, str(e))
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔧 Testing System Fixes")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Run tests
    tests = [
        ("API Health Check", test_health),
        ("Model Reinitialization", test_models_reinitialize),
        ("Models Status", test_models_status),
        ("Sentiment Analysis", test_sentiment_analysis)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 60)
        test_func()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System fixes verified successfully!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review the output above.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner error: {e}")
        sys.exit(1)

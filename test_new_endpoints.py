#!/usr/bin/env python3
"""
Test script for new model and gap-filling endpoints
Tests with REAL API integrations (no mocks)
"""

import requests
import json
import sys
from datetime import datetime

# Base URL - adjust if needed
BASE_URL = "http://localhost:7860"


def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*60}")


def test_models_list():
    """Test listing all available models"""
    print_test_header("List All AI Models")

    try:
        response = requests.get(f"{BASE_URL}/api/models/list")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Found {data['total']} models")
            print(f"   - Loaded: {data['loaded']}")
            print(f"   - Failed: {data['failed']}")

            # Show first 5 models
            for model in data["models"][:5]:
                print(f"   - {model['key']}: {model['name']} ({model['status']})")

            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_model_info():
    """Test getting model information"""
    print_test_header("Get Model Info")

    model_key = "crypto_sent_0"

    try:
        response = requests.get(f"{BASE_URL}/api/models/{model_key}/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Model info retrieved")
            print(f"   - Name: {data['name']}")
            print(f"   - Task: {data['task']}")
            print(f"   - Category: {data['category']}")
            print(f"   - Loaded: {data['loaded']}")
            print(f"   - Recent predictions: {data['recent_predictions']}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_model_predict():
    """Test model prediction"""
    print_test_header("Model Prediction")

    model_key = "crypto_sent_0"
    payload = {
        "text": "Bitcoin is showing strong bullish momentum with high volume!",
        "symbol": "BTC",
    }

    try:
        response = requests.post(f"{BASE_URL}/api/models/{model_key}/predict", json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Prediction generated")
            print(f"   - Model: {data.get('model')}")
            print(f"   - Symbol: {data.get('symbol')}")
            print(f"   - Type: {data.get('type')}")
            print(f"   - Confidence: {data.get('confidence'):.3f}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_batch_predict():
    """Test batch predictions"""
    print_test_header("Batch Prediction")

    payload = {
        "model_key": "crypto_sent_0",
        "items": [
            {"text": "Bitcoin to the moon!", "symbol": "BTC"},
            {"text": "Ethereum showing weakness", "symbol": "ETH"},
            {"text": "Crypto market is stable", "symbol": "MARKET"},
        ],
    }

    try:
        response = requests.post(f"{BASE_URL}/api/models/batch/predict", json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Batch prediction completed")
            print(f"   - Total items: {data['total_items']}")
            print(f"   - Processed: {data['processed']}")

            for i, result in enumerate(data["results"][:3]):
                print(f"   - Item {i+1}: {result['symbol']} - {result['status']}")

            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_gap_detect():
    """Test gap detection"""
    print_test_header("Gap Detection")

    payload = {
        "data": {
            "symbol": "BTC",
            "prices": [
                {"timestamp": 1000, "open": 50000, "high": 51000, "low": 49000, "close": 50500},
                # Missing data at timestamp 2000
                {"timestamp": 3000, "open": 50500, "high": 51500, "low": 50000, "close": 51000},
            ],
        },
        "required_fields": ["ohlc_data", "volume", "sentiment"],
        "context": {},
    }

    try:
        response = requests.post(f"{BASE_URL}/api/gaps/detect", json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Gap detection completed")
            print(f"   - Gaps detected: {data['gaps_detected']}")

            for i, gap in enumerate(data["gaps"][:3]):
                print(f"   - Gap {i+1}: {gap.get('gap_type')} (severity: {gap.get('severity')})")

            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_gap_fill():
    """Test gap filling"""
    print_test_header("Gap Filling")

    payload = {
        "data": {
            "symbol": "BTC",
            "prices": [
                {"timestamp": 1000, "open": 50000, "high": 51000, "low": 49000, "close": 50500},
                {"timestamp": 3000, "open": 50500, "high": 51500, "low": 50000, "close": 51000},
            ],
        },
        "required_fields": ["prices"],
        "context": {"symbol": "BTC"},
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/gaps/fill", json=payload, timeout=30  # Gap filling might take time
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Gap filling completed")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Gaps detected: {data.get('gaps_detected')}")
            print(f"   - Gaps filled: {data.get('gaps_filled')}")
            print(f"   - Fill rate: {data.get('fill_rate', 0):.2%}")
            print(f"   - Average confidence: {data.get('average_confidence', 0):.3f}")
            print(f"   - Execution time: {data.get('execution_time_ms')}ms")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_gap_statistics():
    """Test gap filling statistics"""
    print_test_header("Gap Fill Statistics")

    try:
        response = requests.get(f"{BASE_URL}/api/gaps/statistics")
        if response.status_code == 200:
            data = response.json()
            stats = data.get("statistics", {})
            print(f"✅ SUCCESS: Statistics retrieved")
            print(f"   - Total attempts: {stats.get('total_attempts', 0)}")
            print(f"   - Successful fills: {stats.get('successful_fills', 0)}")
            print(f"   - Success rate: {stats.get('success_rate', 0):.2%}")
            print(f"   - Average confidence: {stats.get('average_confidence', 0):.3f}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_websocket_stats():
    """Test WebSocket statistics"""
    print_test_header("WebSocket Statistics")

    try:
        response = requests.get(f"{BASE_URL}/api/ws/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: WebSocket stats retrieved")
            print(f"   - Active connections: {data.get('active_connections', 0)}")
            print(f"   - Total subscriptions: {data.get('total_subscriptions', 0)}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_health_check():
    """Test health endpoint"""
    print_test_header("Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Server is healthy")
            print(f"   - Status: {data.get('status')}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 60)
    print("🚀 TESTING NEW ENDPOINTS")
    print("=" * 60)
    print(f"📡 Base URL: {BASE_URL}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Health Check", test_health_check),
        ("List Models", test_models_list),
        ("Model Info", test_model_info),
        ("Model Predict", test_model_predict),
        ("Batch Predict", test_batch_predict),
        ("Gap Detect", test_gap_detect),
        ("Gap Fill", test_gap_fill),
        ("Gap Statistics", test_gap_statistics),
        ("WebSocket Stats", test_websocket_stats),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n📈 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

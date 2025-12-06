#!/usr/bin/env python3
"""
Integration Test Suite
Tests backend-frontend integration
"""

import asyncio
import httpx
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:7860"
API_BASE = f"{BASE_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}Testing: {name}{Colors.END}")

def print_pass(msg: str):
    print(f"  {Colors.GREEN}✓ {msg}{Colors.END}")

def print_fail(msg: str):
    print(f"  {Colors.RED}✗ {msg}{Colors.END}")

def print_warn(msg: str):
    print(f"  {Colors.YELLOW}⚠ {msg}{Colors.END}")

async def test_health():
    """Test health endpoint"""
    print_test("Health Endpoint")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print_pass(f"Backend is {data.get('status', 'unknown')}")
                return True
            else:
                print_fail(f"Health check failed: HTTP {response.status_code}")
                return False
    except Exception as e:
        print_fail(f"Health check failed: {e}")
        return False

async def test_static_files():
    """Test static file serving"""
    print_test("Static Files")
    paths = [
        "/",
        "/static/index.html",
        "/static/pages/dashboard/index.html",
        "/static/shared/js/core/api-client.js",
        "/static/shared/js/core/config.js"
    ]
    
    passed = 0
    async with httpx.AsyncClient() as client:
        for path in paths:
            try:
                response = await client.get(f"{BASE_URL}{path}", timeout=5.0)
                if response.status_code == 200:
                    print_pass(f"{path}")
                    passed += 1
                else:
                    print_fail(f"{path} - HTTP {response.status_code}")
            except Exception as e:
                print_fail(f"{path} - {e}")
    
    return passed == len(paths)

async def test_models_endpoints():
    """Test AI models endpoints"""
    print_test("AI Models Endpoints")
    
    endpoints = [
        "/models/status",
        "/models/list",
        "/models/summary",
        "/hf/health"
    ]
    
    passed = 0
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{API_BASE}{endpoint}", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    print_pass(f"{endpoint} - OK")
                    passed += 1
                else:
                    print_warn(f"{endpoint} - HTTP {response.status_code}")
            except Exception as e:
                print_warn(f"{endpoint} - {e}")
    
    return passed > 0  # At least some endpoints should work

async def test_market_endpoints():
    """Test market data endpoints"""
    print_test("Market Data Endpoints")
    
    endpoints = [
        "/market",
        "/trending",
        "/sentiment",
        "/coins/top?limit=10"
    ]
    
    passed = 0
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{API_BASE}{endpoint}", timeout=10.0)
                if response.status_code == 200:
                    print_pass(f"{endpoint}")
                    passed += 1
                else:
                    print_warn(f"{endpoint} - HTTP {response.status_code}")
            except Exception as e:
                print_warn(f"{endpoint} - {e}")
    
    return passed > 0

async def test_providers_endpoints():
    """Test providers endpoints"""
    print_test("Providers Endpoints")
    
    endpoints = [
        "/providers",
        "/providers/summary",
        "/resources",
        "/resources/count"
    ]
    
    passed = 0
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{API_BASE}{endpoint}", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    print_pass(f"{endpoint}")
                    passed += 1
                else:
                    print_warn(f"{endpoint} - HTTP {response.status_code}")
            except Exception as e:
                print_warn(f"{endpoint} - {e}")
    
    return passed > 0

async def test_sentiment_analysis():
    """Test sentiment analysis"""
    print_test("Sentiment Analysis")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/sentiment/analyze",
                json={
                    "text": "Bitcoin is showing strong bullish momentum!",
                    "mode": "crypto"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                sentiment = data.get("sentiment", {})
                label = sentiment.get("label", "unknown")
                confidence = sentiment.get("confidence", 0)
                print_pass(f"Sentiment: {label} (confidence: {confidence:.2f})")
                return True
            else:
                print_warn(f"Sentiment analysis returned HTTP {response.status_code}")
                return False
    except Exception as e:
        print_warn(f"Sentiment analysis failed: {e}")
        return False

async def test_system_info():
    """Test system info endpoint"""
    print_test("System Information")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/system/info", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                system = data.get("system", {})
                env = data.get("environment", {})
                
                print_pass(f"Platform: {system.get('platform')}")
                print_pass(f"Python: {system.get('python_version')}")
                print_pass(f"Docker: {system.get('is_docker')}")
                print_pass(f"HF Mode: {env.get('hf_mode')}")
                return True
            else:
                print_warn(f"System info returned HTTP {response.status_code}")
                return False
    except Exception as e:
        print_warn(f"System info failed: {e}")
        return False

async def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Crypto Intelligence Hub - Integration Tests{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    tests = [
        ("Health Check", test_health),
        ("Static Files", test_static_files),
        ("AI Models", test_models_endpoints),
        ("Market Data", test_market_endpoints),
        ("Providers", test_providers_endpoints),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("System Info", test_system_info)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            failed += 1
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}✓ All tests passed!{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠ Some tests failed{Colors.END}\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

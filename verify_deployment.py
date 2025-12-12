#!/usr/bin/env python3
"""
Deployment Verification Script
Tests all critical endpoints to ensure HuggingFace Space deployment is working correctly.
"""

import asyncio
import httpx
import sys
from typing import List, Dict, Any
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:7860"
TIMEOUT = 10.0

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Test endpoints
ENDPOINTS = [
    # Health & Status
    {"method": "GET", "path": "/api/health", "category": "Health & Status", "critical": True},
    {"method": "GET", "path": "/api/status", "category": "Health & Status", "critical": True},
    {"method": "GET", "path": "/api/routers", "category": "Health & Status", "critical": True},
    
    # Market Data
    {"method": "GET", "path": "/api/market", "category": "Market Data", "critical": True},
    {"method": "GET", "path": "/api/coins/top?limit=10", "category": "Market Data", "critical": True},
    {"method": "GET", "path": "/api/trending", "category": "Market Data", "critical": False},
    {"method": "GET", "path": "/api/service/rate?pair=BTC/USDT", "category": "Market Data", "critical": False},
    
    # Sentiment & AI
    {"method": "GET", "path": "/api/sentiment/global?timeframe=1D", "category": "Sentiment & AI", "critical": False},
    {"method": "GET", "path": "/api/sentiment/asset/BTC", "category": "Sentiment & AI", "critical": False},
    {"method": "GET", "path": "/api/ai/signals?symbol=BTC", "category": "Sentiment & AI", "critical": False},
    {"method": "POST", "path": "/api/ai/decision", "category": "Sentiment & AI", "critical": False,
     "body": {"symbol": "BTC", "horizon": "swing", "risk_tolerance": "moderate"}},
    
    # News
    {"method": "GET", "path": "/api/news?limit=10", "category": "News", "critical": False},
    {"method": "GET", "path": "/api/news/latest?limit=10", "category": "News", "critical": False},
    
    # Models
    {"method": "GET", "path": "/api/models/list", "category": "AI Models", "critical": False},
    {"method": "GET", "path": "/api/models/status", "category": "AI Models", "critical": False},
    {"method": "GET", "path": "/api/models/summary", "category": "AI Models", "critical": True},
    {"method": "GET", "path": "/api/models/health", "category": "AI Models", "critical": False},
    
    # Resources
    {"method": "GET", "path": "/api/resources", "category": "Resources", "critical": True},
    {"method": "GET", "path": "/api/resources/summary", "category": "Resources", "critical": True},
    {"method": "GET", "path": "/api/resources/categories", "category": "Resources", "critical": False},
    {"method": "GET", "path": "/api/providers", "category": "Resources", "critical": True},
]

async def test_endpoint(client: httpx.AsyncClient, endpoint: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single endpoint"""
    method = endpoint["method"]
    path = endpoint["path"]
    url = f"{BASE_URL}{path}"
    
    result = {
        "endpoint": path,
        "method": method,
        "category": endpoint["category"],
        "critical": endpoint["critical"],
        "status": "pending",
        "status_code": None,
        "response_time": None,
        "error": None
    }
    
    try:
        start_time = datetime.now()
        
        if method == "GET":
            response = await client.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = await client.post(url, json=endpoint.get("body", {}), timeout=TIMEOUT)
        else:
            result["status"] = "error"
            result["error"] = f"Unsupported method: {method}"
            return result
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        result["status_code"] = response.status_code
        result["response_time"] = round(response_time, 2)
        
        if response.status_code == 200:
            result["status"] = "success"
        else:
            result["status"] = "error"
            result["error"] = f"HTTP {response.status_code}"
            
    except httpx.TimeoutException:
        result["status"] = "error"
        result["error"] = "Timeout"
    except httpx.ConnectError:
        result["status"] = "error"
        result["error"] = "Connection refused"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

async def run_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  HuggingFace Space Deployment Verification{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")
    print(f"Base URL: {BASE_URL}")
    print(f"Timeout: {TIMEOUT}s")
    print(f"Total Endpoints: {len(ENDPOINTS)}")
    print()
    
    results = []
    categories = {}
    
    async with httpx.AsyncClient() as client:
        # Test server connectivity first
        print(f"{Colors.YELLOW}Testing server connectivity...{Colors.END}")
        try:
            response = await client.get(f"{BASE_URL}/api/health", timeout=5.0)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✓ Server is responding{Colors.END}\n")
            else:
                print(f"{Colors.RED}✗ Server returned HTTP {response.status_code}{Colors.END}\n")
                return
        except Exception as e:
            print(f"{Colors.RED}✗ Cannot connect to server: {e}{Colors.END}")
            print(f"\n{Colors.YELLOW}Make sure the server is running:{Colors.END}")
            print(f"  python hf_unified_server.py\n")
            sys.exit(1)
        
        # Run tests
        current_category = None
        for endpoint in ENDPOINTS:
            category = endpoint["category"]
            
            # Print category header
            if category != current_category:
                if current_category is not None:
                    print()
                print(f"{Colors.BOLD}{category}{Colors.END}")
                print(f"{'-' * len(category)}")
                current_category = category
            
            # Test endpoint
            result = await test_endpoint(client, endpoint)
            results.append(result)
            
            # Track by category
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0, "failed": 0}
            categories[category]["total"] += 1
            
            # Print result
            status_icon = "✓" if result["status"] == "success" else "✗"
            status_color = Colors.GREEN if result["status"] == "success" else Colors.RED
            
            response_time_str = f"{result['response_time']}ms" if result["response_time"] else "N/A"
            critical_str = " [CRITICAL]" if endpoint["critical"] else ""
            
            print(f"  {status_color}{status_icon}{Colors.END} {endpoint['method']:4} {endpoint['path']:50} {response_time_str:>8}{critical_str}")
            
            if result["status"] == "success":
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
                if result["error"]:
                    print(f"    {Colors.RED}Error: {result['error']}{Colors.END}")
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}Summary{Colors.END}")
    print(f"{'='*80}")
    
    total_tests = len(results)
    total_passed = sum(1 for r in results if r["status"] == "success")
    total_failed = sum(1 for r in results if r["status"] == "error")
    critical_failed = sum(1 for r in results if r["status"] == "error" and r["critical"])
    
    print(f"\nOverall:")
    print(f"  Total Tests: {total_tests}")
    print(f"  {Colors.GREEN}Passed: {total_passed}{Colors.END}")
    print(f"  {Colors.RED}Failed: {total_failed}{Colors.END}")
    if critical_failed > 0:
        print(f"  {Colors.RED}{Colors.BOLD}Critical Failures: {critical_failed}{Colors.END}")
    
    print(f"\nBy Category:")
    for category, stats in categories.items():
        success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        color = Colors.GREEN if success_rate == 100 else Colors.YELLOW if success_rate >= 50 else Colors.RED
        print(f"  {category:20} {color}{stats['passed']}/{stats['total']} passed{Colors.END} ({success_rate:.1f}%)")
    
    # Average response time
    response_times = [r["response_time"] for r in results if r["response_time"] is not None]
    if response_times:
        avg_response = sum(response_times) / len(response_times)
        print(f"\nAverage Response Time: {avg_response:.2f}ms")
    
    # Final verdict
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    if critical_failed > 0:
        print(f"{Colors.RED}{Colors.BOLD}✗ DEPLOYMENT VERIFICATION FAILED{Colors.END}")
        print(f"\n{Colors.RED}Critical endpoints are not responding correctly.{Colors.END}")
        print(f"{Colors.YELLOW}Please check the server logs for errors.{Colors.END}\n")
        sys.exit(1)
    elif total_failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ DEPLOYMENT VERIFICATION PASSED{Colors.END}")
        print(f"\n{Colors.GREEN}All endpoints are working correctly!{Colors.END}")
        print(f"{Colors.GREEN}The system is ready for HuggingFace Space deployment.{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ DEPLOYMENT VERIFICATION PASSED WITH WARNINGS{Colors.END}")
        print(f"\n{Colors.YELLOW}Some non-critical endpoints failed, but the system is functional.{Colors.END}")
        print(f"{Colors.YELLOW}You may proceed with deployment, but consider investigating the failures.{Colors.END}\n")
    
    print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}\n")
        sys.exit(1)

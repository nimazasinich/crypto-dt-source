#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script
Tests all documented endpoints from the HuggingFace Space
"""

import asyncio
import httpx
import sys
from datetime import datetime
from typing import Dict, List, Any

# Base URL - modify this for your deployment
BASE_URL = "http://localhost:7860"

# Documented endpoints to test
ENDPOINTS_TO_TEST = {
    "health_status": [
        {"method": "GET", "path": "/api/health", "description": "Health check"},
        {"method": "GET", "path": "/api/status", "description": "System status"},
        {"method": "GET", "path": "/api/routers", "description": "Router status"},
        {"method": "GET", "path": "/api/endpoints", "description": "List all endpoints"},
    ],
    
    "market_data": [
        {"method": "GET", "path": "/api/market", "description": "Market overview"},
        {"method": "GET", "path": "/api/market/top", "description": "Top coins by market cap"},
        {"method": "GET", "path": "/api/market/trending", "description": "Trending coins"},
        {"method": "GET", "path": "/api/trending", "description": "Trending cryptocurrencies"},
        {"method": "GET", "path": "/api/coins/top?limit=50", "description": "Top 50 coins"},
    ],
    
    "sentiment": [
        {"method": "GET", "path": "/api/sentiment/global?timeframe=1D", "description": "Global sentiment"},
        {"method": "GET", "path": "/api/sentiment/asset/BTC", "description": "BTC sentiment"},
        {"method": "POST", "path": "/api/sentiment/analyze", "description": "Analyze text sentiment",
         "body": {"text": "Bitcoin is going to the moon! 🚀", "mode": "crypto"}},
    ],
    
    "news": [
        {"method": "GET", "path": "/api/news?limit=50", "description": "Latest news"},
        {"method": "GET", "path": "/api/news/latest?limit=10", "description": "Latest news (alias)"},
    ],
    
    "ai_models": [
        {"method": "GET", "path": "/api/models/list", "description": "List available models"},
        {"method": "GET", "path": "/api/models/status", "description": "Models status"},
        {"method": "GET", "path": "/api/models/summary", "description": "Models summary"},
        {"method": "GET", "path": "/api/models/health", "description": "Models health"},
        {"method": "POST", "path": "/api/models/test", "description": "Test model"},
        {"method": "POST", "path": "/api/models/reinitialize", "description": "Reinitialize models"},
    ],
    
    "ai_signals": [
        {"method": "GET", "path": "/api/ai/signals?symbol=BTC", "description": "AI trading signals"},
        {"method": "POST", "path": "/api/ai/decision", "description": "AI trading decision",
         "body": {"symbol": "BTC", "horizon": "swing", "risk_tolerance": "moderate"}},
    ],
    
    "ohlcv": [
        {"method": "GET", "path": "/api/ohlcv/BTC?timeframe=1h&limit=100", "description": "OHLCV data for BTC"},
        {"method": "GET", "path": "/api/ohlcv/multi?symbols=BTC,ETH&timeframe=1h", "description": "Multi OHLCV"},
    ],
    
    "resources": [
        {"method": "GET", "path": "/api/resources", "description": "Resource statistics"},
        {"method": "GET", "path": "/api/resources/summary", "description": "Resources summary"},
        {"method": "GET", "path": "/api/resources/categories", "description": "Resource categories"},
    ],
    
    "providers": [
        {"method": "GET", "path": "/api/providers", "description": "Data providers list"},
    ],
}


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


async def test_endpoint(client: httpx.AsyncClient, method: str, path: str, description: str, body: Dict = None) -> Dict[str, Any]:
    """Test a single endpoint and return results"""
    url = f"{BASE_URL}{path}"
    
    try:
        start_time = datetime.now()
        
        if method == "GET":
            response = await client.get(url, timeout=30.0)
        elif method == "POST":
            response = await client.post(url, json=body or {}, timeout=30.0)
        else:
            return {
                "path": path,
                "method": method,
                "success": False,
                "error": f"Unsupported method: {method}",
                "status_code": None,
                "response_time_ms": 0
            }
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        
        # Try to parse JSON
        try:
            json_data = response.json()
        except:
            json_data = None
        
        return {
            "path": path,
            "method": method,
            "description": description,
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "response_time_ms": round(elapsed, 2),
            "has_json": json_data is not None,
            "error": None if response.status_code < 400 else f"HTTP {response.status_code}"
        }
        
    except Exception as e:
        return {
            "path": path,
            "method": method,
            "description": description,
            "success": False,
            "error": str(e),
            "status_code": None,
            "response_time_ms": 0
        }


async def run_tests():
    """Run all endpoint tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}HuggingFace Space Endpoint Testing{Colors.RESET}")
    print(f"{Colors.BOLD}Base URL: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    all_results = []
    category_stats = {}
    
    async with httpx.AsyncClient() as client:
        for category, endpoints in ENDPOINTS_TO_TEST.items():
            print(f"\n{Colors.BLUE}{Colors.BOLD}Testing {category.replace('_', ' ').title()}:{Colors.RESET}")
            print(f"{'-'*80}")
            
            category_results = []
            
            for endpoint in endpoints:
                result = await test_endpoint(
                    client,
                    endpoint["method"],
                    endpoint["path"],
                    endpoint["description"],
                    endpoint.get("body")
                )
                
                category_results.append(result)
                all_results.append(result)
                
                # Print result
                status_symbol = f"{Colors.GREEN}✓{Colors.RESET}" if result["success"] else f"{Colors.RED}✗{Colors.RESET}"
                status_text = f"{Colors.GREEN}OK{Colors.RESET}" if result["success"] else f"{Colors.RED}FAIL{Colors.RESET}"
                
                print(f"{status_symbol} {endpoint['method']:4s} {endpoint['path']:60s} [{status_text}]")
                
                if not result["success"]:
                    print(f"   {Colors.YELLOW}Error: {result['error']}{Colors.RESET}")
                else:
                    print(f"   {Colors.GREEN}Status: {result['status_code']} | Time: {result['response_time_ms']}ms{Colors.RESET}")
            
            # Category statistics
            success_count = sum(1 for r in category_results if r["success"])
            total_count = len(category_results)
            category_stats[category] = {
                "success": success_count,
                "total": total_count,
                "percentage": (success_count / total_count * 100) if total_count > 0 else 0
            }
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}Test Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    total_success = sum(1 for r in all_results if r["success"])
    total_tests = len(all_results)
    overall_percentage = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{total_success}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{total_tests - total_success}{Colors.RESET}")
    print(f"Success Rate: {Colors.GREEN if overall_percentage >= 80 else Colors.YELLOW if overall_percentage >= 60 else Colors.RED}{overall_percentage:.1f}%{Colors.RESET}\n")
    
    # Category breakdown
    print(f"{Colors.BOLD}Category Breakdown:{Colors.RESET}")
    for category, stats in category_stats.items():
        color = Colors.GREEN if stats["percentage"] >= 80 else Colors.YELLOW if stats["percentage"] >= 60 else Colors.RED
        print(f"  {category.replace('_', ' ').title():20s}: {color}{stats['success']}/{stats['total']} ({stats['percentage']:.0f}%){Colors.RESET}")
    
    # Failed endpoints
    failed = [r for r in all_results if not r["success"]]
    if failed:
        print(f"\n{Colors.BOLD}{Colors.RED}Failed Endpoints:{Colors.RESET}")
        for r in failed:
            print(f"  {r['method']:4s} {r['path']:60s} - {r['error']}")
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    return overall_percentage >= 80


if __name__ == "__main__":
    # Check if custom URL is provided
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip("/")
        print(f"Using custom base URL: {BASE_URL}")
    
    try:
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Testing interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.RESET}")
        sys.exit(1)

#!/usr/bin/env python3
"""
HuggingFace Space Critical Fixes Test Suite
Tests all fixes for HTTP 500 errors, service health monitor, and UI improvements
"""

import asyncio
import httpx
import sys
from datetime import datetime
from typing import Dict, Any, List

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Base URL - adjust as needed
BASE_URL = "http://localhost:7860"

class TestResult:
    def __init__(self, name: str, passed: bool, message: str):
        self.name = name
        self.passed = passed
        self.message = message
        self.timestamp = datetime.utcnow()

class TestRunner:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    def log(self, message: str, color: str = ""):
        print(f"{color}{message}{RESET}")
    
    def log_test(self, name: str, passed: bool, message: str):
        symbol = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        self.log(f"  {symbol} {name}: {message}")
        
        result = TestResult(name, passed, message)
        self.results.append(result)
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    async def test_health_monitor_api(self) -> bool:
        """Test Service Health Monitor API"""
        self.log(f"\n{BOLD}Testing Service Health Monitor API{RESET}", BLUE)
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test health monitor endpoint
                response = await client.get(f"{self.base_url}/api/health/monitor")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify structure
                    required_keys = ["timestamp", "total_services", "online", "offline", "services", "overall_health"]
                    has_all_keys = all(key in data for key in required_keys)
                    
                    if has_all_keys:
                        self.log_test(
                            "Health Monitor API Structure",
                            True,
                            f"Found {data.get('total_services', 0)} services"
                        )
                        
                        # Verify services array
                        services = data.get("services", [])
                        if services:
                            self.log_test(
                                "Services Data",
                                True,
                                f"{len(services)} services with status info"
                            )
                        else:
                            self.log_test(
                                "Services Data",
                                False,
                                "No services found"
                            )
                        
                        return True
                    else:
                        self.log_test(
                            "Health Monitor API Structure",
                            False,
                            f"Missing keys: {[k for k in required_keys if k not in data]}"
                        )
                        return False
                else:
                    self.log_test(
                        "Health Monitor API",
                        False,
                        f"HTTP {response.status_code}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Health Monitor API", False, f"Error: {str(e)}")
            return False
    
    async def test_health_self_endpoint(self) -> bool:
        """Test self health check endpoint"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/health/self")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        self.log_test(
                            "Self Health Check",
                            True,
                            "Service is healthy"
                        )
                        return True
                    else:
                        self.log_test(
                            "Self Health Check",
                            False,
                            f"Status: {data.get('status')}"
                        )
                        return False
                else:
                    self.log_test(
                        "Self Health Check",
                        False,
                        f"HTTP {response.status_code}"
                    )
                    return False
        except Exception as e:
            self.log_test("Self Health Check", False, f"Error: {str(e)}")
            return False
    
    async def test_indicators_comprehensive(self) -> bool:
        """Test indicators comprehensive endpoint (was returning 500)"""
        self.log(f"\n{BOLD}Testing Indicators API (Previously 500 Error){RESET}", BLUE)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/indicators/comprehensive",
                    params={"symbol": "BTC", "timeframe": "1h"}
                )
                
                # Should NOT return 500
                if response.status_code == 500:
                    self.log_test(
                        "Comprehensive Endpoint (No 500)",
                        False,
                        "Still returning 500 error"
                    )
                    return False
                
                # Should return 200 or graceful fallback
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    required = ["symbol", "timeframe", "current_price", "indicators", "signals", "overall_signal"]
                    has_structure = all(key in data for key in required)
                    
                    if has_structure:
                        source = data.get("source", "unknown")
                        self.log_test(
                            "Comprehensive Endpoint",
                            True,
                            f"Returns proper data (source: {source})"
                        )
                        
                        # Check if using fallback
                        if source == "fallback" or source == "error_fallback":
                            self.log_test(
                                "Fallback Mechanism",
                                True,
                                "Gracefully using fallback data"
                            )
                        else:
                            self.log_test(
                                "Real Data",
                                True,
                                "Using real API data"
                            )
                        
                        return True
                    else:
                        self.log_test(
                            "Comprehensive Endpoint Structure",
                            False,
                            f"Missing fields: {[k for k in required if k not in data]}"
                        )
                        return False
                else:
                    self.log_test(
                        "Comprehensive Endpoint",
                        False,
                        f"Unexpected status: {response.status_code}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Comprehensive Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_indicators_services(self) -> bool:
        """Test indicators services list endpoint"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/indicators/services")
                
                if response.status_code == 200:
                    data = response.json()
                    services = data.get("services", [])
                    
                    if len(services) >= 7:  # Should have BB, StochRSI, ATR, SMA, EMA, MACD, RSI, Comprehensive
                        self.log_test(
                            "Indicators Services List",
                            True,
                            f"{len(services)} indicator services available"
                        )
                        return True
                    else:
                        self.log_test(
                            "Indicators Services List",
                            False,
                            f"Only {len(services)} services (expected 8+)"
                        )
                        return False
                else:
                    self.log_test(
                        "Indicators Services List",
                        False,
                        f"HTTP {response.status_code}"
                    )
                    return False
        except Exception as e:
            self.log_test("Indicators Services List", False, f"Error: {str(e)}")
            return False
    
    async def test_ui_pages_exist(self) -> bool:
        """Test that critical UI pages exist and load"""
        self.log(f"\n{BOLD}Testing UI Pages{RESET}", BLUE)
        
        pages = [
            ("/static/pages/service-health/index.html", "Service Health Monitor"),
            ("/static/pages/services/index.html", "Services Page"),
            ("/static/pages/technical-analysis/index.html", "Technical Analysis"),
        ]
        
        all_passed = True
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                for path, name in pages:
                    try:
                        response = await client.get(f"{self.base_url}{path}")
                        
                        if response.status_code == 200:
                            # Check if it contains HTML
                            content = response.text.lower()
                            if "<html" in content and "<body" in content:
                                self.log_test(
                                    f"UI Page: {name}",
                                    True,
                                    "Page loads correctly"
                                )
                            else:
                                self.log_test(
                                    f"UI Page: {name}",
                                    False,
                                    "Not valid HTML"
                                )
                                all_passed = False
                        else:
                            self.log_test(
                                f"UI Page: {name}",
                                False,
                                f"HTTP {response.status_code}"
                            )
                            all_passed = False
                    except Exception as e:
                        self.log_test(f"UI Page: {name}", False, f"Error: {str(e)}")
                        all_passed = False
        except Exception as e:
            self.log_test("UI Pages Test", False, f"Error: {str(e)}")
            return False
        
        return all_passed
    
    async def test_css_files(self) -> bool:
        """Test that critical CSS files exist"""
        self.log(f"\n{BOLD}Testing CSS Files{RESET}", BLUE)
        
        css_files = [
            ("/static/shared/css/animation-fixes.css", "Animation Fixes CSS"),
            ("/static/shared/css/global.css", "Global CSS"),
            ("/static/pages/service-health/service-health.css", "Service Health CSS"),
        ]
        
        all_passed = True
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                for path, name in css_files:
                    try:
                        response = await client.get(f"{self.base_url}{path}")
                        
                        if response.status_code == 200:
                            self.log_test(
                                f"CSS File: {name}",
                                True,
                                "File exists and loads"
                            )
                        else:
                            self.log_test(
                                f"CSS File: {name}",
                                False,
                                f"HTTP {response.status_code}"
                            )
                            all_passed = False
                    except Exception as e:
                        self.log_test(f"CSS File: {name}", False, f"Error: {str(e)}")
                        all_passed = False
        except Exception as e:
            self.log_test("CSS Files Test", False, f"Error: {str(e)}")
            return False
        
        return all_passed
    
    async def run_all_tests(self):
        """Run all tests"""
        self.log(f"\n{BOLD}{'='*70}{RESET}", BLUE)
        self.log(f"{BOLD}HuggingFace Space - Critical Fixes Test Suite{RESET}", BLUE)
        self.log(f"{BOLD}Testing: {self.base_url}{RESET}", BLUE)
        self.log(f"{BOLD}{'='*70}{RESET}\n", BLUE)
        
        # Run all tests
        await self.test_health_monitor_api()
        await self.test_health_self_endpoint()
        await self.test_indicators_comprehensive()
        await self.test_indicators_services()
        await self.test_ui_pages_exist()
        await self.test_css_files()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        self.log(f"\n{BOLD}{'='*70}{RESET}", BLUE)
        self.log(f"{BOLD}Test Summary{RESET}", BLUE)
        self.log(f"{BOLD}{'='*70}{RESET}", BLUE)
        
        self.log(f"\nTotal Tests: {total}")
        self.log(f"✓ Passed: {self.passed}", GREEN)
        self.log(f"✗ Failed: {self.failed}", RED if self.failed > 0 else "")
        self.log(f"Pass Rate: {pass_rate:.1f}%", GREEN if pass_rate >= 80 else YELLOW)
        
        if self.failed == 0:
            self.log(f"\n{BOLD}{GREEN}✓ ALL TESTS PASSED! Space is ready for deployment.{RESET}")
        else:
            self.log(f"\n{BOLD}{RED}✗ Some tests failed. Please review and fix.{RESET}")
            self.log(f"\n{YELLOW}Failed Tests:{RESET}")
            for result in self.results:
                if not result.passed:
                    self.log(f"  - {result.name}: {result.message}", RED)
        
        self.log(f"\n{BOLD}{'='*70}{RESET}\n", BLUE)

async def main():
    """Main entry point"""
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    
    runner = TestRunner(base_url)
    await runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if runner.failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())

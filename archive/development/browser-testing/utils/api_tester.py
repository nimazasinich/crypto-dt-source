"""
API endpoint testing utility.
Tests REST API endpoints for functionality and performance.
"""
import time
import httpx
from typing import List, Dict, Any
from .browser_utils import TestResult


class APITester:
    """
    Tests API endpoints for availability, response time, and correctness.
    """
    
    def __init__(self, base_url: str):
        """
        Initialize API tester.
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url
        self.timeout = 10.0
    
    async def test_endpoint(
        self, 
        endpoint: str, 
        method: str = 'GET',
        expected_status: int = 200
    ) -> TestResult:
        """
        Test a single API endpoint.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            expected_status: Expected HTTP status code
            
        Returns:
            TestResult with test outcome
        """
        start_time = time.time()
        test_name = f"API {method} {endpoint}"
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == 'GET':
                    response = await client.get(url)
                elif method == 'POST':
                    response = await client.post(url)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                duration = time.time() - start_time
                
                if response.status_code == expected_status:
                    # Try to parse JSON
                    try:
                        data = response.json()
                        data_info = f", returned {len(data) if isinstance(data, (list, dict)) else 'data'}"
                    except:
                        data_info = ""
                    
                    return TestResult(
                        test_name=test_name,
                        status='passed',
                        duration=duration,
                        details=f"Status {response.status_code}, {duration:.2f}s{data_info}"
                    )
                else:
                    return TestResult(
                        test_name=test_name,
                        status='failed',
                        duration=duration,
                        details=f"Expected {expected_status}, got {response.status_code}",
                        error=f"HTTP {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details=f"Request timed out after {self.timeout}s",
                error="Timeout"
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details=f"Request failed: {str(e)[:100]}",
                error=str(e)
            )
    
    async def test_all_endpoints(self) -> List[TestResult]:
        """
        Test all critical API endpoints.
        
        Returns:
            List of TestResults
        """
        endpoints = [
            '/health',
            '/api/health',
            '/api/status',
            '/api/providers',
            '/api/resources',
            '/api/trending',
            '/api/sentiment/global',
            '/api/news/latest',
            '/api/models/list',
            '/api/models/status',
        ]
        
        results = []
        print("  Testing API endpoints...")
        
        for endpoint in endpoints:
            result = await self.test_endpoint(endpoint)
            results.append(result)
            
            # Print result
            status_icon = "✓" if result.status == 'passed' else "✗"
            print(f"    {status_icon} {endpoint}: {result.details}")
        
        return results
    
    async def test_endpoint_with_params(
        self,
        endpoint: str,
        params: Dict[str, Any],
        method: str = 'GET'
    ) -> TestResult:
        """
        Test an endpoint with query parameters.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            method: HTTP method
            
        Returns:
            TestResult with test outcome
        """
        start_time = time.time()
        test_name = f"API {method} {endpoint} with params"
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == 'GET':
                    response = await client.get(url, params=params)
                elif method == 'POST':
                    response = await client.post(url, json=params)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    return TestResult(
                        test_name=test_name,
                        status='passed',
                        duration=duration,
                        details=f"Status {response.status_code}, {duration:.2f}s"
                    )
                else:
                    return TestResult(
                        test_name=test_name,
                        status='failed',
                        duration=duration,
                        details=f"HTTP {response.status_code}",
                        error=f"HTTP {response.status_code}"
                    )
                    
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details=f"Request failed: {str(e)[:100]}",
                error=str(e)
            )


#!/usr/bin/env python3
"""
Service Health Checker
Checks health status of all discovered services
"""

import asyncio
import httpx
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service health status"""
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    service_id: str
    service_name: str
    status: ServiceStatus
    response_time_ms: Optional[float]
    status_code: Optional[int]
    error_message: Optional[str]
    checked_at: str
    endpoint_checked: str
    additional_info: Dict[str, Any]


class ServiceHealthChecker:
    """Check health of all services"""
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.health_results: Dict[str, HealthCheckResult] = {}
        
    async def check_service(
        self,
        service_id: str,
        service_name: str,
        base_url: str,
        endpoints: List[str] = None,
        requires_auth: bool = False,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HealthCheckResult:
        """
        Check health of a single service
        
        Args:
            service_id: Unique service identifier
            service_name: Human-readable service name
            base_url: Base URL of the service
            endpoints: List of endpoints to try
            requires_auth: Whether service requires authentication
            api_key: API key if required
            headers: Custom headers
            
        Returns:
            HealthCheckResult
        """
        start_time = time.time()
        
        # Determine which endpoint to check
        check_url = base_url
        if endpoints and len(endpoints) > 0:
            # Try to find a health/ping endpoint first
            health_endpoints = [e for e in endpoints if any(h in e.lower() for h in ['health', 'ping', 'status'])]
            if health_endpoints:
                check_url = base_url.rstrip('/') + '/' + health_endpoints[0].lstrip('/')
            else:
                # Use first endpoint
                check_url = base_url.rstrip('/') + '/' + endpoints[0].lstrip('/')
        
        # Build headers
        request_headers = headers or {}
        if api_key:
            # Try common API key header names
            if 'X-CMC_PRO_API_KEY' not in request_headers and 'coinmarketcap' in base_url.lower():
                request_headers['X-CMC_PRO_API_KEY'] = api_key
            elif 'Authorization' not in request_headers:
                request_headers['Authorization'] = f'Bearer {api_key}'
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(check_url, headers=request_headers)
                
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Determine status
                if response.status_code == 200:
                    status = ServiceStatus.ONLINE
                    error_msg = None
                elif response.status_code == 401 or response.status_code == 403:
                    status = ServiceStatus.UNAUTHORIZED
                    error_msg = "Authentication required or invalid credentials"
                elif response.status_code == 429:
                    status = ServiceStatus.RATE_LIMITED
                    error_msg = "Rate limit exceeded"
                elif 200 <= response.status_code < 300:
                    status = ServiceStatus.ONLINE
                    error_msg = None
                elif 500 <= response.status_code < 600:
                    status = ServiceStatus.OFFLINE
                    error_msg = f"Server error: {response.status_code}"
                else:
                    status = ServiceStatus.DEGRADED
                    error_msg = f"Unexpected status code: {response.status_code}"
                
                # Try to get additional info from response
                additional_info = {}
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        json_data = response.json()
                        if isinstance(json_data, dict):
                            # Extract useful info
                            if 'status' in json_data:
                                additional_info['api_status'] = json_data['status']
                            if 'version' in json_data:
                                additional_info['version'] = json_data['version']
                except:
                    pass
                
                return HealthCheckResult(
                    service_id=service_id,
                    service_name=service_name,
                    status=status,
                    response_time_ms=round(response_time, 2),
                    status_code=response.status_code,
                    error_message=error_msg,
                    checked_at=datetime.utcnow().isoformat(),
                    endpoint_checked=check_url,
                    additional_info=additional_info
                )
        
        except httpx.TimeoutException:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_id=service_id,
                service_name=service_name,
                status=ServiceStatus.OFFLINE,
                response_time_ms=round(response_time, 2),
                status_code=None,
                error_message=f"Timeout after {self.timeout}s",
                checked_at=datetime.utcnow().isoformat(),
                endpoint_checked=check_url,
                additional_info={}
            )
        
        except httpx.ConnectError as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_id=service_id,
                service_name=service_name,
                status=ServiceStatus.OFFLINE,
                response_time_ms=round(response_time, 2),
                status_code=None,
                error_message=f"Connection failed: {str(e)}",
                checked_at=datetime.utcnow().isoformat(),
                endpoint_checked=check_url,
                additional_info={}
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_id=service_id,
                service_name=service_name,
                status=ServiceStatus.UNKNOWN,
                response_time_ms=round(response_time, 2),
                status_code=None,
                error_message=f"Error: {str(e)}",
                checked_at=datetime.utcnow().isoformat(),
                endpoint_checked=check_url,
                additional_info={}
            )
    
    async def check_all_services(
        self,
        services: List[Dict[str, Any]],
        max_concurrent: int = 10
    ) -> Dict[str, HealthCheckResult]:
        """
        Check health of multiple services concurrently
        
        Args:
            services: List of service dictionaries
            max_concurrent: Maximum concurrent checks
            
        Returns:
            Dictionary of service_id -> HealthCheckResult
        """
        logger.info(f"🔍 Checking health of {len(services)} services...")
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_with_semaphore(service: Dict[str, Any]):
            async with semaphore:
                return await self.check_service(
                    service_id=service.get('id', ''),
                    service_name=service.get('name', ''),
                    base_url=service.get('base_url', ''),
                    endpoints=service.get('endpoints', []),
                    requires_auth=service.get('requires_auth', False),
                    api_key=None,  # API keys would need to be loaded from environment
                    headers=service.get('headers', {})
                )
        
        # Check all services concurrently
        tasks = [check_with_semaphore(service) for service in services]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build results dictionary
        health_results = {}
        for result in results:
            if isinstance(result, HealthCheckResult):
                health_results[result.service_id] = result
                self.health_results[result.service_id] = result
            elif isinstance(result, Exception):
                logger.error(f"Health check failed: {result}")
        
        # Log summary
        status_counts = {}
        for result in health_results.values():
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
        
        logger.info(f"✅ Health check complete:")
        for status, count in status_counts.items():
            logger.info(f"   • {status.value}: {count}")
        
        return health_results
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of all health checks"""
        if not self.health_results:
            return {
                "total_services": 0,
                "status_counts": {},
                "average_response_time_ms": 0,
                "last_check": None
            }
        
        status_counts = {}
        response_times = []
        
        for result in self.health_results.values():
            status_counts[result.status.value] = status_counts.get(result.status.value, 0) + 1
            if result.response_time_ms is not None:
                response_times.append(result.response_time_ms)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Get most recent check time
        check_times = [result.checked_at for result in self.health_results.values()]
        last_check = max(check_times) if check_times else None
        
        return {
            "total_services": len(self.health_results),
            "status_counts": status_counts,
            "average_response_time_ms": round(avg_response_time, 2),
            "fastest_service": min(
                [(r.service_name, r.response_time_ms) for r in self.health_results.values() if r.response_time_ms],
                key=lambda x: x[1]
            )[0] if any(r.response_time_ms for r in self.health_results.values()) else None,
            "slowest_service": max(
                [(r.service_name, r.response_time_ms) for r in self.health_results.values() if r.response_time_ms],
                key=lambda x: x[1]
            )[0] if any(r.response_time_ms for r in self.health_results.values()) else None,
            "last_check": last_check
        }
    
    def get_services_by_status(self, status: ServiceStatus) -> List[HealthCheckResult]:
        """Get all services with a specific status"""
        return [r for r in self.health_results.values() if r.status == status]
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export health check results to dictionary"""
        return {
            "summary": self.get_health_summary(),
            "services": [asdict(result) for result in self.health_results.values()]
        }


# Singleton instance
_health_checker_instance: Optional[ServiceHealthChecker] = None


def get_health_checker() -> ServiceHealthChecker:
    """Get or create singleton health checker instance"""
    global _health_checker_instance
    if _health_checker_instance is None:
        _health_checker_instance = ServiceHealthChecker()
    return _health_checker_instance


async def perform_health_check() -> Dict[str, Any]:
    """
    Perform a complete health check of all services
    
    Returns:
        Dictionary with health check results
    """
    from backend.services.service_discovery import get_service_discovery
    
    # Get discovered services
    discovery = get_service_discovery()
    services = [asdict(s) for s in discovery.get_all_services()]
    
    # Add internal services
    from backend.services.service_discovery import INTERNAL_SERVICES
    services.extend(INTERNAL_SERVICES)
    
    # Check health
    checker = get_health_checker()
    results = await checker.check_all_services(services)
    
    return checker.export_to_dict()


if __name__ == "__main__":
    # Test health checker
    import sys
    sys.path.insert(0, '/workspace')
    
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        # Test with a few known services
        test_services = [
            {
                "id": "coingecko",
                "name": "CoinGecko",
                "base_url": "https://api.coingecko.com",
                "endpoints": ["/api/v3/ping"],
                "requires_auth": False
            },
            {
                "id": "alternative_me",
                "name": "Fear & Greed Index",
                "base_url": "https://api.alternative.me",
                "endpoints": ["/fng/"],
                "requires_auth": False
            },
            {
                "id": "defillama",
                "name": "DefiLlama",
                "base_url": "https://api.llama.fi",
                "endpoints": ["/protocols"],
                "requires_auth": False
            }
        ]
        
        checker = ServiceHealthChecker()
        results = await checker.check_all_services(test_services)
        
        print("\n" + "=" * 70)
        print("HEALTH CHECK RESULTS")
        print("=" * 70)
        
        for service_id, result in results.items():
            status_emoji = "✅" if result.status == ServiceStatus.ONLINE else "❌"
            print(f"\n{status_emoji} {result.service_name}")
            print(f"   Status: {result.status.value}")
            print(f"   Response Time: {result.response_time_ms}ms")
            print(f"   Endpoint: {result.endpoint_checked}")
            if result.error_message:
                print(f"   Error: {result.error_message}")
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        summary = checker.get_health_summary()
        print(f"Total Services: {summary['total_services']}")
        print(f"Average Response Time: {summary['average_response_time_ms']}ms")
        print("\nStatus Breakdown:")
        for status, count in summary['status_counts'].items():
            print(f"   • {status}: {count}")
    
    asyncio.run(test())

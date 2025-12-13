#!/usr/bin/env python3
"""
Binance DNS Connector with Multi-Endpoint Failover
Handles Binance API connections with automatic DNS-based failover across multiple mirror endpoints
"""

import httpx
from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class BinanceDNSConnector:
    """
    Binance API connector with DNS-based failover support
    
    Features:
    - Multiple DNS endpoints for Binance global distribution
    - Automatic failover on connection errors
    - Health tracking per endpoint
    - Round-robin with health-based selection
    - Exponential backoff for failed endpoints
    """
    
    # Multiple DNS entries for Binance (global distribution)
    BINANCE_GLOBAL_ENDPOINTS = [
        "https://api.binance.com",      # Primary (Global)
        "https://api1.binance.com",     # Mirror 1
        "https://api2.binance.com",     # Mirror 2
        "https://api3.binance.com",     # Mirror 3
        "https://api4.binance.com",     # Mirror 4 (if available)
    ]
    
    BINANCE_US_ENDPOINTS = [
        "https://api.binance.us",       # US users
    ]
    
    def __init__(self, use_us: bool = False, timeout: float = 10.0):
        """
        Initialize Binance DNS connector
        
        Args:
            use_us: If True, use Binance US endpoints
            timeout: Request timeout in seconds
        """
        self.endpoints = self.BINANCE_US_ENDPOINTS if use_us else self.BINANCE_GLOBAL_ENDPOINTS
        self.timeout = timeout
        self.use_us = use_us
        
        # Health tracking for each endpoint
        self.endpoint_health: Dict[str, Dict[str, Any]] = {
            endpoint: {
                "available": True,
                "consecutive_failures": 0,
                "last_success": None,
                "last_failure": None,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0,
                "backoff_until": 0.0
            }
            for endpoint in self.endpoints
        }
        
        self.current_endpoint_index = 0
        
        logger.info(f"🌐 Binance DNS Connector initialized: {len(self.endpoints)} endpoints available")
    
    def _get_next_healthy_endpoint(self) -> Optional[str]:
        """
        Get next healthy endpoint using intelligent selection
        
        Strategy:
        1. Filter endpoints not in backoff
        2. Prefer endpoints with recent success
        3. Round-robin among healthy endpoints
        
        Returns:
            Next healthy endpoint URL or None if all down
        """
        now = time.time()
        
        # Get available endpoints (not in backoff)
        available = [
            endpoint for endpoint in self.endpoints
            if self.endpoint_health[endpoint]["backoff_until"] <= now
        ]
        
        if not available:
            # All endpoints in backoff - return least recently failed
            logger.warning("🚨 All Binance endpoints in backoff! Using least recently failed.")
            return min(
                self.endpoints,
                key=lambda e: self.endpoint_health[e]["backoff_until"]
            )
        
        # Sort by success rate and recent activity
        def score_endpoint(endpoint: str) -> float:
            health = self.endpoint_health[endpoint]
            total = health["total_requests"]
            
            if total == 0:
                return 0  # New endpoint - high priority
            
            success_rate = health["successful_requests"] / total
            score = (1 - success_rate) * 100  # Lower is better
            
            # Add penalty for consecutive failures
            score += health["consecutive_failures"] * 10
            
            return score
        
        # Get best endpoint
        best_endpoint = min(available, key=score_endpoint)
        
        return best_endpoint
    
    def _record_success(self, endpoint: str, response_time: float):
        """Record successful request"""
        health = self.endpoint_health[endpoint]
        health["consecutive_failures"] = 0
        health["last_success"] = datetime.now().isoformat()
        health["total_requests"] += 1
        health["successful_requests"] += 1
        health["backoff_until"] = 0.0
        
        # Update average response time
        if health["avg_response_time"] == 0:
            health["avg_response_time"] = response_time
        else:
            # Exponential moving average
            health["avg_response_time"] = 0.7 * health["avg_response_time"] + 0.3 * response_time
    
    def _record_failure(self, endpoint: str, error: str):
        """Record failed request with exponential backoff"""
        health = self.endpoint_health[endpoint]
        health["consecutive_failures"] += 1
        health["last_failure"] = datetime.now().isoformat()
        health["total_requests"] += 1
        health["failed_requests"] += 1
        
        # Exponential backoff: 2^failures seconds (max 300s = 5 min)
        backoff_duration = min(2 ** health["consecutive_failures"], 300)
        health["backoff_until"] = time.time() + backoff_duration
        
        logger.warning(
            f"❌ Binance endpoint failed: {endpoint} - {error} "
            f"(failures: {health['consecutive_failures']}, backoff: {backoff_duration}s)"
        )
    
    async def get(
        self,
        path: str,
        params: Optional[Dict] = None,
        max_retries: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make GET request with automatic DNS failover
        
        Args:
            path: API endpoint path (e.g., "/api/v3/ticker/price")
            params: Query parameters
            max_retries: Maximum retry attempts (default: number of endpoints)
        
        Returns:
            JSON response or None if all endpoints failed
        """
        if max_retries is None:
            max_retries = len(self.endpoints)
        
        last_error = None
        
        for attempt in range(max_retries):
            endpoint = self._get_next_healthy_endpoint()
            
            if not endpoint:
                logger.error("🚨 No Binance endpoints available!")
                break
            
            url = f"{endpoint}{path}"
            start_time = time.time()
            
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    
                    response_time = time.time() - start_time
                    self._record_success(endpoint, response_time)
                    
                    logger.info(
                        f"✅ Binance {path} - {endpoint} - {response_time*1000:.0f}ms"
                    )
                    
                    return response.json()
            
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}"
                self._record_failure(endpoint, last_error)
                
                # If rate limited, try next endpoint immediately
                if e.response.status_code == 429:
                    logger.warning(f"⚠️ Binance rate limit hit on {endpoint}, trying next...")
                    continue
                
                # For other HTTP errors, might still retry
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.3)
            
            except httpx.TimeoutException:
                last_error = "Timeout"
                self._record_failure(endpoint, last_error)
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.3)
            
            except Exception as e:
                last_error = str(e)
                self._record_failure(endpoint, last_error)
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.3)
        
        logger.error(f"❌ All Binance endpoints failed for {path}: {last_error}")
        return None
    
    async def post(
        self,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        max_retries: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make POST request with automatic DNS failover
        
        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            max_retries: Maximum retry attempts
        
        Returns:
            JSON response or None if all endpoints failed
        """
        if max_retries is None:
            max_retries = len(self.endpoints)
        
        last_error = None
        
        for attempt in range(max_retries):
            endpoint = self._get_next_healthy_endpoint()
            
            if not endpoint:
                logger.error("🚨 No Binance endpoints available!")
                break
            
            url = f"{endpoint}{path}"
            start_time = time.time()
            
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=data, params=params)
                    response.raise_for_status()
                    
                    response_time = time.time() - start_time
                    self._record_success(endpoint, response_time)
                    
                    logger.info(
                        f"✅ Binance POST {path} - {endpoint} - {response_time*1000:.0f}ms"
                    )
                    
                    return response.json()
            
            except Exception as e:
                last_error = str(e)
                self._record_failure(endpoint, last_error)
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.3)
        
        logger.error(f"❌ All Binance endpoints failed for POST {path}: {last_error}")
        return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all Binance endpoints
        
        Returns:
            Dict with health information for each endpoint
        """
        now = time.time()
        
        return {
            "connector_type": "Binance US" if self.use_us else "Binance Global",
            "total_endpoints": len(self.endpoints),
            "endpoints": [
                {
                    "url": endpoint,
                    "available": health["backoff_until"] <= now,
                    "consecutive_failures": health["consecutive_failures"],
                    "success_rate": (
                        100 * health["successful_requests"] / health["total_requests"]
                        if health["total_requests"] > 0 else 0
                    ),
                    "total_requests": health["total_requests"],
                    "avg_response_time_ms": health["avg_response_time"] * 1000,
                    "last_success": health["last_success"],
                    "last_failure": health["last_failure"],
                    "backoff_until": (
                        datetime.fromtimestamp(health["backoff_until"]).isoformat()
                        if health["backoff_until"] > now else None
                    )
                }
                for endpoint, health in self.endpoint_health.items()
            ]
        }
    
    def reset_health(self, endpoint: Optional[str] = None):
        """
        Reset health tracking for endpoint(s)
        
        Args:
            endpoint: Specific endpoint to reset, or None to reset all
        """
        if endpoint:
            if endpoint in self.endpoint_health:
                self.endpoint_health[endpoint]["consecutive_failures"] = 0
                self.endpoint_health[endpoint]["backoff_until"] = 0.0
                logger.info(f"🔄 Reset health for {endpoint}")
        else:
            for ep in self.endpoint_health:
                self.endpoint_health[ep]["consecutive_failures"] = 0
                self.endpoint_health[ep]["backoff_until"] = 0.0
            logger.info("🔄 Reset health for all endpoints")


# ===== GLOBAL INSTANCES =====

_binance_global_connector: Optional[BinanceDNSConnector] = None
_binance_us_connector: Optional[BinanceDNSConnector] = None


def get_binance_connector(use_us: bool = False) -> BinanceDNSConnector:
    """
    Get singleton Binance connector instance
    
    Args:
        use_us: If True, return US connector, else global connector
    
    Returns:
        BinanceDNSConnector instance
    """
    global _binance_global_connector, _binance_us_connector
    
    if use_us:
        if _binance_us_connector is None:
            _binance_us_connector = BinanceDNSConnector(use_us=True)
        return _binance_us_connector
    else:
        if _binance_global_connector is None:
            _binance_global_connector = BinanceDNSConnector(use_us=False)
        return _binance_global_connector


# ===== CONVENIENCE FUNCTIONS =====

async def binance_get(path: str, params: Optional[Dict] = None, use_us: bool = False) -> Optional[Dict]:
    """
    Convenience function for Binance GET requests with failover
    
    Args:
        path: API path (e.g., "/api/v3/ticker/price")
        params: Query parameters
        use_us: Use Binance US endpoints
    
    Returns:
        JSON response or None
    """
    connector = get_binance_connector(use_us=use_us)
    return await connector.get(path, params=params)


async def binance_post(
    path: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    use_us: bool = False
) -> Optional[Dict]:
    """
    Convenience function for Binance POST requests with failover
    
    Args:
        path: API path
        data: Request body
        params: Query parameters
        use_us: Use Binance US endpoints
    
    Returns:
        JSON response or None
    """
    connector = get_binance_connector(use_us=use_us)
    return await connector.post(path, data=data, params=params)


# ===== TEST =====

if __name__ == "__main__":
    async def test():
        print("=" * 70)
        print("Testing Binance DNS Connector")
        print("=" * 70)
        
        connector = get_binance_connector(use_us=False)
        
        # Test 1: Get BTC price
        print("\n1. Testing BTC price fetch:")
        result = await connector.get("/api/v3/ticker/price", params={"symbol": "BTCUSDT"})
        if result:
            print(f"   ✅ BTC Price: ${float(result.get('price', 0)):,.2f}")
        else:
            print("   ❌ Failed to fetch BTC price")
        
        # Test 2: Get multiple prices
        print("\n2. Testing multiple price fetch:")
        result = await connector.get("/api/v3/ticker/price")
        if result:
            print(f"   ✅ Fetched {len(result)} prices")
        else:
            print("   ❌ Failed to fetch prices")
        
        # Test 3: Health status
        print("\n3. Health Status:")
        health = connector.get_health_status()
        print(f"   Total endpoints: {health['total_endpoints']}")
        for ep in health['endpoints']:
            status = "✅" if ep['available'] else "❌"
            print(f"   {status} {ep['url']}: {ep['success_rate']:.1f}% success, {ep['total_requests']} requests")
        
        print("\n" + "=" * 70)
        print("Test completed!")
    
    asyncio.run(test())

"""
Crypto API Hub Monitoring Service

Provides continuous monitoring, health checks, and automatic recovery
for crypto API endpoints and services.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import httpx
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class CryptoHubMonitor:
    """
    Monitoring service for Crypto API Hub with self-healing capabilities
    """
    
    def __init__(
        self,
        check_interval: int = 60,
        timeout: int = 10,
        max_retries: int = 3,
        alert_threshold: int = 5
    ):
        """
        Initialize the monitoring service
        
        Args:
            check_interval: Seconds between health checks
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            alert_threshold: Number of failures before alerting
        """
        self.check_interval = check_interval
        self.timeout = timeout
        self.max_retries = max_retries
        self.alert_threshold = alert_threshold
        
        # Monitoring data
        self.endpoints: Set[str] = set()
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.last_check: Dict[str, datetime] = {}
        self.recovery_attempts: Dict[str, int] = defaultdict(int)
        
        # Monitoring state
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "recoveries": 0,
            "start_time": None
        }
        
        logger.info("Crypto Hub Monitor initialized")
    
    def register_endpoint(self, url: str, metadata: Optional[Dict] = None):
        """
        Register an endpoint for monitoring
        
        Args:
            url: Endpoint URL to monitor
            metadata: Optional metadata about the endpoint
        """
        self.endpoints.add(url)
        
        if url not in self.health_status:
            self.health_status[url] = {
                "status": "unknown",
                "last_check": None,
                "response_time": None,
                "error": None,
                "metadata": metadata or {}
            }
        
        logger.info(f"Registered endpoint for monitoring: {url}")
    
    def unregister_endpoint(self, url: str):
        """
        Unregister an endpoint from monitoring
        
        Args:
            url: Endpoint URL to unregister
        """
        self.endpoints.discard(url)
        self.health_status.pop(url, None)
        self.failure_counts.pop(url, None)
        self.response_times.pop(url, None)
        self.last_check.pop(url, None)
        self.recovery_attempts.pop(url, None)
        
        logger.info(f"Unregistered endpoint: {url}")
    
    async def start(self):
        """
        Start the monitoring service
        """
        if self.is_running:
            logger.warning("Monitoring service is already running")
            return
        
        self.is_running = True
        self.stats["start_time"] = datetime.utcnow()
        
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Crypto Hub Monitoring started")
    
    async def stop(self):
        """
        Stop the monitoring service
        """
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Crypto Hub Monitoring stopped")
    
    async def _monitoring_loop(self):
        """
        Main monitoring loop
        """
        while self.is_running:
            try:
                await self._perform_health_checks()
                await self._analyze_and_recover()
                await self._cleanup_old_data()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)
    
    async def _perform_health_checks(self):
        """
        Perform health checks on all registered endpoints
        """
        if not self.endpoints:
            return
        
        tasks = [
            self._check_endpoint(endpoint)
            for endpoint in self.endpoints
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for endpoint, result in zip(self.endpoints, results):
            if isinstance(result, Exception):
                logger.error(f"Health check error for {endpoint}: {result}")
    
    async def _check_endpoint(self, url: str) -> Dict[str, Any]:
        """
        Check health of a specific endpoint
        
        Args:
            url: Endpoint URL to check
            
        Returns:
            Health check result
        """
        self.stats["total_checks"] += 1
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use HEAD request for efficiency
                response = await client.head(url)
                
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                is_healthy = response.status_code < 400
                
                # Update status
                self.health_status[url] = {
                    "status": "healthy" if is_healthy else "degraded",
                    "status_code": response.status_code,
                    "last_check": start_time.isoformat(),
                    "response_time": response_time,
                    "error": None,
                    "metadata": self.health_status.get(url, {}).get("metadata", {})
                }
                
                # Track response times
                self.response_times[url].append(response_time)
                if len(self.response_times[url]) > 100:
                    self.response_times[url] = self.response_times[url][-100:]
                
                self.last_check[url] = start_time
                
                if is_healthy:
                    self.stats["successful_checks"] += 1
                    
                    # Reset failure count on success
                    if self.failure_counts[url] > 0:
                        logger.info(f"Endpoint recovered: {url}")
                        self.stats["recoveries"] += 1
                    
                    self.failure_counts[url] = 0
                    self.recovery_attempts[url] = 0
                else:
                    self.stats["failed_checks"] += 1
                    self.failure_counts[url] += 1
                
                return self.health_status[url]
        
        except httpx.TimeoutException:
            return await self._handle_check_failure(url, "Request timeout", start_time)
        except httpx.RequestError as e:
            return await self._handle_check_failure(url, f"Request error: {str(e)}", start_time)
        except Exception as e:
            return await self._handle_check_failure(url, f"Unexpected error: {str(e)}", start_time)
    
    async def _handle_check_failure(
        self,
        url: str,
        error_message: str,
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Handle health check failure
        
        Args:
            url: Failed endpoint URL
            error_message: Error message
            start_time: Check start time
            
        Returns:
            Updated health status
        """
        self.stats["failed_checks"] += 1
        self.failure_counts[url] += 1
        
        self.health_status[url] = {
            "status": "unhealthy",
            "last_check": start_time.isoformat(),
            "response_time": None,
            "error": error_message,
            "failure_count": self.failure_counts[url],
            "metadata": self.health_status.get(url, {}).get("metadata", {})
        }
        
        self.last_check[url] = start_time
        
        # Alert if threshold exceeded
        if self.failure_counts[url] >= self.alert_threshold:
            logger.error(
                f"ALERT: Endpoint {url} has failed {self.failure_counts[url]} times. "
                f"Error: {error_message}"
            )
        
        return self.health_status[url]
    
    async def _analyze_and_recover(self):
        """
        Analyze unhealthy endpoints and attempt recovery
        """
        unhealthy_endpoints = [
            url for url, status in self.health_status.items()
            if status.get("status") == "unhealthy"
        ]
        
        for url in unhealthy_endpoints:
            # Check if recovery should be attempted
            if self.recovery_attempts[url] < self.max_retries:
                await self._attempt_recovery(url)
    
    async def _attempt_recovery(self, url: str):
        """
        Attempt to recover an unhealthy endpoint
        
        Args:
            url: Endpoint URL to recover
        """
        self.recovery_attempts[url] += 1
        
        logger.info(
            f"Attempting recovery for {url} "
            f"(attempt {self.recovery_attempts[url]}/{self.max_retries})"
        )
        
        # Try different recovery strategies
        strategies = [
            self._recovery_simple_retry,
            self._recovery_with_headers,
            self._recovery_get_request,
        ]
        
        for strategy in strategies:
            try:
                success = await strategy(url)
                if success:
                    logger.info(f"Recovery successful for {url} using {strategy.__name__}")
                    self.recovery_attempts[url] = 0
                    return True
            except Exception as e:
                logger.debug(f"Recovery strategy {strategy.__name__} failed: {e}")
        
        return False
    
    async def _recovery_simple_retry(self, url: str) -> bool:
        """Simple retry strategy"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.head(url)
                return response.status_code < 400
        except Exception:
            return False
    
    async def _recovery_with_headers(self, url: str) -> bool:
        """Retry with modified headers"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; CryptoHubMonitor/1.0)",
                "Accept": "*/*"
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.head(url, headers=headers)
                return response.status_code < 400
        except Exception:
            return False
    
    async def _recovery_get_request(self, url: str) -> bool:
        """Retry with GET instead of HEAD"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                return response.status_code < 400
        except Exception:
            return False
    
    async def _cleanup_old_data(self):
        """
        Clean up old monitoring data
        """
        current_time = datetime.utcnow()
        max_age = timedelta(hours=24)
        
        # Clean up old response times
        for url in list(self.response_times.keys()):
            if url not in self.endpoints:
                del self.response_times[url]
        
        # Reset failure counts for recovered endpoints
        for url in list(self.failure_counts.keys()):
            if url not in self.endpoints:
                del self.failure_counts[url]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get overall health summary
        
        Returns:
            Health summary
        """
        total = len(self.health_status)
        healthy = sum(
            1 for s in self.health_status.values()
            if s.get("status") == "healthy"
        )
        degraded = sum(
            1 for s in self.health_status.values()
            if s.get("status") == "degraded"
        )
        unhealthy = sum(
            1 for s in self.health_status.values()
            if s.get("status") == "unhealthy"
        )
        
        # Calculate average response time
        all_response_times = [
            rt for times in self.response_times.values()
            for rt in times
        ]
        avg_response_time = (
            sum(all_response_times) / len(all_response_times)
            if all_response_times else 0
        )
        
        uptime = None
        if self.stats["start_time"]:
            uptime = (datetime.utcnow() - self.stats["start_time"]).total_seconds()
        
        return {
            "total_endpoints": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "health_percentage": round((healthy / total * 100)) if total > 0 else 0,
            "average_response_time": round(avg_response_time, 3),
            "statistics": {
                **self.stats,
                "uptime_seconds": uptime
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_endpoint_details(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific endpoint
        
        Args:
            url: Endpoint URL
            
        Returns:
            Endpoint details or None if not found
        """
        if url not in self.health_status:
            return None
        
        status = self.health_status[url]
        
        # Calculate statistics
        response_times = self.response_times.get(url, [])
        
        return {
            **status,
            "failure_count": self.failure_counts.get(url, 0),
            "recovery_attempts": self.recovery_attempts.get(url, 0),
            "response_time_stats": {
                "min": min(response_times) if response_times else None,
                "max": max(response_times) if response_times else None,
                "avg": sum(response_times) / len(response_times) if response_times else None,
                "samples": len(response_times)
            }
        }
    
    def export_report(self, filepath: Optional[Path] = None) -> str:
        """
        Export monitoring report
        
        Args:
            filepath: Optional path to save report
            
        Returns:
            Report as JSON string
        """
        report = {
            "summary": self.get_health_summary(),
            "endpoints": {
                url: self.get_endpoint_details(url)
                for url in self.endpoints
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        report_json = json.dumps(report, indent=2)
        
        if filepath:
            filepath.write_text(report_json)
            logger.info(f"Report exported to {filepath}")
        
        return report_json


# Global monitor instance
_monitor: Optional[CryptoHubMonitor] = None


def get_monitor() -> CryptoHubMonitor:
    """
    Get the global monitor instance
    
    Returns:
        CryptoHubMonitor instance
    """
    global _monitor
    if _monitor is None:
        _monitor = CryptoHubMonitor()
    return _monitor


async def start_monitoring():
    """
    Start the global monitoring service
    """
    monitor = get_monitor()
    await monitor.start()


async def stop_monitoring():
    """
    Stop the global monitoring service
    """
    monitor = get_monitor()
    await monitor.stop()

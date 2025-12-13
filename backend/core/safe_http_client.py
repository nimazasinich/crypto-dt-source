#!/usr/bin/env python3
"""
Safe HTTP Client with Smart Routing & Health Tracking
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES:
- ONLY HTTP 200 is considered valid
- Reject HTTP 206 (Partial Content)
- Reject empty responses
- Validate content-type before parsing JSON
- Track source health in memory
- Smart routing based on health
- Never retry same failing source repeatedly
"""

import httpx
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import os

logger = logging.getLogger(__name__)


class SourceHealth(Enum):
    """Source health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class SourceHealthTracker:
    """
    In-memory health tracker for data sources
    Tracks failures, successes, and automatically switches sources
    """
    
    def __init__(self):
        self._sources: Dict[str, Dict[str, Any]] = {}
        self._max_failures = 3
        self._degraded_threshold = 0.5  # 50% success rate
        self._recovery_time = timedelta(minutes=5)
    
    def get_source_health(self, source_name: str) -> Dict[str, Any]:
        """Get health status for a source"""
        if source_name not in self._sources:
            self._sources[source_name] = {
                "successes": 0,
                "failures": 0,
                "consecutive_failures": 0,
                "last_success": None,
                "last_failure": None,
                "status": SourceHealth.UNKNOWN,
                "created_at": datetime.utcnow()
            }
        return self._sources[source_name]
    
    def record_success(self, source_name: str, response_time_ms: float):
        """Record successful request"""
        source = self.get_source_health(source_name)
        source["successes"] += 1
        source["consecutive_failures"] = 0
        source["last_success"] = datetime.utcnow()
        source["last_response_time_ms"] = response_time_ms
        
        # Update status
        self._update_status(source_name)
        
        logger.info(f"✅ {source_name}: Success (response_time={response_time_ms:.0f}ms)")
    
    def record_failure(self, source_name: str, error_type: str, error_message: str):
        """Record failed request"""
        source = self.get_source_health(source_name)
        source["failures"] += 1
        source["consecutive_failures"] += 1
        source["last_failure"] = datetime.utcnow()
        source["last_error"] = {
            "type": error_type,
            "message": error_message,
            "timestamp": datetime.utcnow()
        }
        
        # Update status
        self._update_status(source_name)
        
        logger.warning(
            f"❌ {source_name}: Failure #{source['consecutive_failures']} "
            f"(type={error_type}, msg={error_message[:100]})"
        )
    
    def _update_status(self, source_name: str):
        """Update source health status based on metrics"""
        source = self.get_source_health(source_name)
        
        # Check consecutive failures
        if source["consecutive_failures"] >= self._max_failures:
            source["status"] = SourceHealth.OFFLINE
            logger.error(f"🔴 {source_name}: Marked OFFLINE (consecutive failures: {source['consecutive_failures']})")
            return
        
        # Check if recovering from offline
        if source["status"] == SourceHealth.OFFLINE:
            if source["last_success"] and \
               (datetime.utcnow() - source["last_success"]) < self._recovery_time:
                source["status"] = SourceHealth.DEGRADED
                logger.info(f"🟡 {source_name}: Recovering to DEGRADED")
            return
        
        # Calculate success rate
        total = source["successes"] + source["failures"]
        if total > 0:
            success_rate = source["successes"] / total
            
            if success_rate >= self._degraded_threshold:
                source["status"] = SourceHealth.HEALTHY
            else:
                source["status"] = SourceHealth.DEGRADED
                logger.warning(f"🟡 {source_name}: Marked DEGRADED (success_rate={success_rate:.1%})")
        else:
            source["status"] = SourceHealth.UNKNOWN
    
    def should_use_source(self, source_name: str) -> tuple[bool, str]:
        """
        Determine if source should be used
        Returns: (should_use, reason)
        """
        source = self.get_source_health(source_name)
        status = source["status"]
        
        if status == SourceHealth.OFFLINE:
            # Check if enough time passed for recovery attempt
            if source["last_failure"]:
                time_since_failure = datetime.utcnow() - source["last_failure"]
                if time_since_failure < self._recovery_time:
                    reason = f"Source offline, waiting {self._recovery_time - time_since_failure} for recovery"
                    return False, reason
                else:
                    reason = "Source offline but recovery time elapsed, retrying"
                    return True, reason
            return False, "Source offline"
        
        if status == SourceHealth.DEGRADED:
            reason = f"Source degraded but usable (success_rate={source['successes']/(source['successes']+source['failures']):.1%})"
            return True, reason
        
        if status == SourceHealth.HEALTHY:
            return True, "Source healthy"
        
        # UNKNOWN - allow usage
        return True, "Source status unknown, attempting"
    
    def get_all_sources(self) -> Dict[str, Dict[str, Any]]:
        """Get all tracked sources"""
        return {
            name: {
                **info,
                "status": info["status"].value if isinstance(info["status"], SourceHealth) else info["status"]
            }
            for name, info in self._sources.items()
        }
    
    def reset_source(self, source_name: str):
        """Reset source health (useful for manual recovery)"""
        if source_name in self._sources:
            del self._sources[source_name]
            logger.info(f"🔄 {source_name}: Health data reset")


# Global health tracker
health_tracker = SourceHealthTracker()


class SafeHTTPClient:
    """
    Safe HTTP client with comprehensive validation and health tracking
    
    SAFETY RULES:
    - Only HTTP 200 is valid
    - Reject 206 Partial Content
    - Reject empty responses
    - Validate Content-Type before JSON parsing
    - Track all requests for health monitoring
    """
    
    def __init__(
        self,
        source_name: str,
        base_url: str,
        timeout: float = 15.0,
        headers: Optional[Dict[str, str]] = None
    ):
        self.source_name = source_name
        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = headers or {}
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Safe GET request with comprehensive validation
        
        Returns:
            Validated JSON response
        
        Raises:
            Exception with detailed error message
        """
        # Check if source should be used
        should_use, reason = health_tracker.should_use_source(self.source_name)
        if not should_use:
            logger.warning(f"⚠️ {self.source_name}: Skipping request - {reason}")
            raise Exception(f"Source {self.source_name} unavailable: {reason}")
        
        logger.info(f"🌐 {self.source_name}: GET {endpoint} (reason: {reason})")
        
        start_time = datetime.utcnow()
        
        try:
            # Merge headers
            request_headers = {**self.default_headers, **(headers or {})}
            
            # Build full URL
            url = f"{self.base_url}{endpoint}" if not endpoint.startswith("http") else endpoint
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=request_headers,
                    **kwargs
                )
                
                # Calculate response time
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # RULE 1: Only HTTP 200 is valid
                if response.status_code != 200:
                    error_msg = f"Invalid HTTP status: {response.status_code} (only 200 accepted)"
                    
                    # Special handling for 206 Partial Content
                    if response.status_code == 206:
                        error_msg = "HTTP 206 Partial Content rejected - incomplete data"
                    
                    logger.error(f"❌ {self.source_name}: {error_msg}")
                    health_tracker.record_failure(
                        self.source_name,
                        f"http_{response.status_code}",
                        error_msg
                    )
                    raise Exception(error_msg)
                
                # RULE 2: Reject empty responses
                if not response.content or len(response.content) == 0:
                    error_msg = "Empty response body"
                    logger.error(f"❌ {self.source_name}: {error_msg}")
                    health_tracker.record_failure(
                        self.source_name,
                        "empty_response",
                        error_msg
                    )
                    raise Exception(error_msg)
                
                # RULE 3: Validate Content-Type before parsing JSON
                content_type = response.headers.get("content-type", "").lower()
                if "application/json" not in content_type:
                    # Try to parse anyway but log warning
                    logger.warning(
                        f"⚠️ {self.source_name}: Unexpected Content-Type: {content_type} "
                        f"(expected application/json)"
                    )
                
                # Parse JSON safely
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON response: {str(e)}"
                    logger.error(f"❌ {self.source_name}: {error_msg}")
                    health_tracker.record_failure(
                        self.source_name,
                        "invalid_json",
                        error_msg
                    )
                    raise Exception(error_msg)
                
                # SUCCESS - record metrics
                health_tracker.record_success(self.source_name, response_time)
                
                logger.info(
                    f"✅ {self.source_name}: Success "
                    f"(status=200, time={response_time:.0f}ms, size={len(response.content)} bytes)"
                )
                
                return data
        
        except httpx.TimeoutException as e:
            error_msg = f"Request timeout after {self.timeout}s"
            logger.error(f"❌ {self.source_name}: {error_msg}")
            health_tracker.record_failure(
                self.source_name,
                "timeout",
                error_msg
            )
            raise Exception(error_msg) from e
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error: {e.response.status_code}"
            logger.error(f"❌ {self.source_name}: {error_msg}")
            health_tracker.record_failure(
                self.source_name,
                f"http_error_{e.response.status_code}",
                error_msg
            )
            raise Exception(error_msg) from e
        
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(f"❌ {self.source_name}: {error_msg}")
            health_tracker.record_failure(
                self.source_name,
                "request_error",
                error_msg
            )
            raise Exception(error_msg) from e
        
        except Exception as e:
            # Don't re-record if already recorded above
            if "Invalid HTTP status" not in str(e) and "Empty response" not in str(e):
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"❌ {self.source_name}: {error_msg}")
                health_tracker.record_failure(
                    self.source_name,
                    "unexpected_error",
                    error_msg
                )
            raise


# Export for easy import
__all__ = [
    "SafeHTTPClient",
    "SourceHealth",
    "SourceHealthTracker",
    "health_tracker"
]

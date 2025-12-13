"""
System Metrics API - Real-time system monitoring with actual metrics
Provides CPU, memory, uptime, request rate, response time, and error rate
All metrics are REAL and measured, no fake data.
"""
import logging
import time
import psutil
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Global metrics tracker
class MetricsTracker:
    """Track request metrics for real-time monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.max_response_times = 100  # Keep last 100 response times
        self.last_minute_requests = []
        self.last_minute_errors = []
        
    def record_request(self, response_time_ms: float, is_error: bool = False):
        """Record a request with its response time"""
        current_time = time.time()
        
        self.request_count += 1
        if is_error:
            self.error_count += 1
        
        # Track response time
        self.response_times.append(response_time_ms)
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)
        
        # Track requests per minute
        self.last_minute_requests.append(current_time)
        self.last_minute_requests = [t for t in self.last_minute_requests if current_time - t < 60]
        
        # Track errors per minute
        if is_error:
            self.last_minute_errors.append(current_time)
            self.last_minute_errors = [t for t in self.last_minute_errors if current_time - t < 60]
    
    def get_requests_per_minute(self) -> int:
        """Get number of requests in the last minute"""
        return len(self.last_minute_requests)
    
    def get_average_response_time(self) -> float:
        """Get average response time in milliseconds"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_error_rate(self) -> float:
        """Get error rate as a percentage"""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100
    
    def get_uptime(self) -> int:
        """Get uptime in seconds"""
        return int(time.time() - self.start_time)


# Global metrics tracker instance
_metrics_tracker: Optional[MetricsTracker] = None


def get_metrics_tracker() -> MetricsTracker:
    """Get or create the global metrics tracker"""
    global _metrics_tracker
    if _metrics_tracker is None:
        _metrics_tracker = MetricsTracker()
    return _metrics_tracker


# Response models
class SystemMetricsResponse(BaseModel):
    """System metrics response model"""
    cpu: float
    memory: Dict[str, float]
    uptime: int
    requests_per_min: int
    avg_response_ms: float
    error_rate: float
    timestamp: int
    status: str = "ok"


@router.get("/api/system/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Get real-time system metrics
    
    Returns:
        - cpu: CPU usage percentage (0-100)
        - memory: Memory usage (used and total in MB)
        - uptime: Process uptime in seconds
        - requests_per_min: Number of requests in the last minute
        - avg_response_ms: Average response time in milliseconds
        - error_rate: Error rate as percentage
        - timestamp: Current Unix timestamp
    
    All metrics are REAL and measured, no fake data.
    """
    try:
        tracker = get_metrics_tracker()
        
        # Get CPU usage (real)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage (real)
        memory = psutil.virtual_memory()
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # Get uptime (real)
        uptime = tracker.get_uptime()
        
        # Get request metrics (real)
        requests_per_min = tracker.get_requests_per_minute()
        avg_response_ms = tracker.get_average_response_time()
        error_rate = tracker.get_error_rate()
        
        # Current timestamp
        timestamp = int(time.time())
        
        return SystemMetricsResponse(
            cpu=round(cpu_percent, 2),
            memory={
                "used": round(memory_used_mb, 2),
                "total": round(memory_total_mb, 2),
                "percent": round(memory.percent, 2)
            },
            uptime=uptime,
            requests_per_min=requests_per_min,
            avg_response_ms=round(avg_response_ms, 2),
            error_rate=round(error_rate, 2),
            timestamp=timestamp,
            status="ok"
        )
    
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        # Return fallback values instead of failing
        return SystemMetricsResponse(
            cpu=0.0,
            memory={"used": 0.0, "total": 0.0, "percent": 0.0},
            uptime=0,
            requests_per_min=0,
            avg_response_ms=0.0,
            error_rate=0.0,
            timestamp=int(time.time()),
            status="degraded"
        )


@router.get("/api/system/health")
async def get_system_health():
    """
    Get system health status
    
    Returns basic health information for monitoring
    """
    try:
        tracker = get_metrics_tracker()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Determine health status
        status = "healthy"
        issues = []
        
        if cpu_percent > 90:
            status = "warning"
            issues.append("High CPU usage")
        
        if memory.percent > 90:
            status = "warning"
            issues.append("High memory usage")
        
        if tracker.get_error_rate() > 10:
            status = "warning"
            issues.append("High error rate")
        
        return {
            "status": status,
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory.percent, 2),
            "uptime": tracker.get_uptime(),
            "issues": issues,
            "timestamp": int(time.time())
        }
    
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": int(time.time())
        }


@router.get("/api/system/info")
async def get_system_info():
    """
    Get static system information
    
    Returns system configuration and details
    """
    try:
        import platform
        
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "timestamp": int(time.time())
        }
    
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {
            "error": str(e),
            "timestamp": int(time.time())
        }

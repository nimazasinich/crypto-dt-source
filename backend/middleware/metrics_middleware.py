"""
Metrics Middleware - Automatically track request metrics
Records request count, response times, and error rates
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track HTTP request metrics
    
    Tracks:
    - Request count
    - Response times
    - Error rates
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request and track metrics"""
        # Skip tracking for static files and the metrics endpoint itself
        if (request.url.path.startswith("/static/") or 
            request.url.path == "/api/system/metrics" or
            request.url.path == "/api/system/health"):
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Check if it's an error response
            is_error = response.status_code >= 400
            
            # Record metrics
            try:
                from backend.routers.system_metrics_api import get_metrics_tracker
                tracker = get_metrics_tracker()
                tracker.record_request(response_time_ms, is_error)
            except Exception as e:
                logger.debug(f"Failed to record metrics: {e}")
            
            return response
        
        except Exception as e:
            # Record error
            response_time_ms = (time.time() - start_time) * 1000
            
            try:
                from backend.routers.system_metrics_api import get_metrics_tracker
                tracker = get_metrics_tracker()
                tracker.record_request(response_time_ms, is_error=True)
            except Exception as track_error:
                logger.debug(f"Failed to record error metrics: {track_error}")
            
            # Re-raise the exception
            raise e

#!/usr/bin/env python3
"""
Simple Rate Limiter for API Endpoints
"""

import logging
import time
from collections import defaultdict
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class SimpleRateLimiter:
    """
    Simple in-memory rate limiter
    """

    def __init__(self):
        # Store: {client_id: [(timestamp, count)]}
        self.requests: Dict[str, list] = defaultdict(list)

        # Rate limit configurations (requests per minute)
        self.limits = {
            "default": 60,  # 60 requests per minute
            "sentiment": 30,  # 30 sentiment requests per minute
            "model_loading": 5,  # 5 model loads per minute
            "dataset_loading": 5,  # 5 dataset loads per minute
            "external_api": 100,  # 100 external API calls per minute
        }

        # Time windows in seconds
        self.window = 60  # 1 minute

    def is_allowed(self, client_id: str, endpoint_type: str = "default") -> Tuple[bool, Dict]:
        """
        Check if request is allowed based on rate limit

        Args:
            client_id: Client identifier (IP, API key, etc.)
            endpoint_type: Type of endpoint (default, sentiment, model_loading, etc.)

        Returns:
            Tuple of (is_allowed, info_dict)
        """
        current_time = time.time()
        limit = self.limits.get(endpoint_type, self.limits["default"])

        # Clean old requests outside the window
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] if current_time - ts < self.window
        ]

        # Count requests in current window
        request_count = len(self.requests[client_id])

        # Check if allowed
        if request_count < limit:
            # Allow request and record it
            self.requests[client_id].append(current_time)

            return True, {
                "allowed": True,
                "requests_remaining": limit - request_count - 1,
                "limit": limit,
                "window_seconds": self.window,
                "reset_at": current_time + self.window,
            }
        else:
            # Deny request
            oldest_request = min(self.requests[client_id])
            reset_at = oldest_request + self.window

            return False, {
                "allowed": False,
                "requests_remaining": 0,
                "limit": limit,
                "window_seconds": self.window,
                "reset_at": reset_at,
                "retry_after": reset_at - current_time,
            }

    def reset_client(self, client_id: str):
        """Reset rate limit for a specific client"""
        if client_id in self.requests:
            del self.requests[client_id]
            logger.info(f"Rate limit reset for client: {client_id}")

    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        current_time = time.time()

        active_clients = 0
        total_requests = 0

        for client_id, timestamps in self.requests.items():
            # Count only recent requests
            recent_requests = [ts for ts in timestamps if current_time - ts < self.window]
            if recent_requests:
                active_clients += 1
                total_requests += len(recent_requests)

        return {
            "active_clients": active_clients,
            "total_recent_requests": total_requests,
            "window_seconds": self.window,
            "limits": self.limits,
        }


# Global instance
rate_limiter = SimpleRateLimiter()


# Export
__all__ = ["SimpleRateLimiter", "rate_limiter"]

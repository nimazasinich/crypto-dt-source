"""
Enhanced Rate Limiting System
Implements token bucket and sliding window algorithms for API rate limiting
"""

import time
import threading
from typing import Dict, Optional, Tuple
from collections import deque
from dataclasses import dataclass
import logging
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int = 30
    requests_per_hour: int = 1000
    burst_size: int = 10  # Allow burst requests


class TokenBucket:
    """
    Token bucket algorithm for rate limiting
    Allows burst traffic while maintaining average rate
    """

    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket

        Args:
            rate: Tokens per second
            capacity: Maximum bucket capacity (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if successful, False if insufficient tokens
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Add tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            # Try to consume
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time to wait before tokens are available

        Args:
            tokens: Number of tokens needed

        Returns:
            Wait time in seconds
        """
        with self.lock:
            if self.tokens >= tokens:
                return 0.0

            tokens_needed = tokens - self.tokens
            return tokens_needed / self.rate


class SlidingWindowCounter:
    """
    Sliding window algorithm for rate limiting
    Provides accurate rate limiting over time windows
    """

    def __init__(self, window_seconds: int, max_requests: int):
        """
        Initialize sliding window counter

        Args:
            window_seconds: Window size in seconds
            max_requests: Maximum requests in window
        """
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.requests: deque = deque()
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        """
        Check if request is allowed

        Returns:
            True if allowed, False if rate limit exceeded
        """
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds

            # Remove old requests outside window
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()

            # Check limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True

            return False

    def get_remaining(self) -> int:
        """Get remaining requests in current window"""
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds

            # Remove old requests
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()

            return max(0, self.max_requests - len(self.requests))


class RateLimiter:
    """
    Comprehensive rate limiter combining multiple algorithms
    Supports per-IP, per-user, and per-API-key limits
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter

        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()

        # Per-client limiters (keyed by IP/user/API key)
        self.minute_limiters: Dict[str, SlidingWindowCounter] = {}
        self.hour_limiters: Dict[str, SlidingWindowCounter] = {}
        self.burst_limiters: Dict[str, TokenBucket] = {}

        self.lock = threading.Lock()

        logger.info(
            f"Rate limiter initialized: "
            f"{self.config.requests_per_minute}/min, "
            f"{self.config.requests_per_hour}/hour, "
            f"burst={self.config.burst_size}"
        )

    def check_rate_limit(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is within rate limits

        Args:
            client_id: Client identifier (IP, user, or API key)

        Returns:
            Tuple of (allowed: bool, error_message: Optional[str])
        """
        with self.lock:
            # Get or create limiters for this client
            if client_id not in self.minute_limiters:
                self._create_limiters(client_id)

            # Check burst limit (token bucket)
            if not self.burst_limiters[client_id].consume():
                wait_time = self.burst_limiters[client_id].get_wait_time()
                return False, f"Rate limit exceeded. Retry after {wait_time:.1f}s"

            # Check minute limit
            if not self.minute_limiters[client_id].allow_request():
                return False, f"Rate limit: {self.config.requests_per_minute} requests/minute exceeded"

            # Check hour limit
            if not self.hour_limiters[client_id].allow_request():
                return False, f"Rate limit: {self.config.requests_per_hour} requests/hour exceeded"

            return True, None

    def _create_limiters(self, client_id: str):
        """Create limiters for new client"""
        self.minute_limiters[client_id] = SlidingWindowCounter(
            window_seconds=60,
            max_requests=self.config.requests_per_minute
        )
        self.hour_limiters[client_id] = SlidingWindowCounter(
            window_seconds=3600,
            max_requests=self.config.requests_per_hour
        )
        self.burst_limiters[client_id] = TokenBucket(
            rate=self.config.requests_per_minute / 60.0,  # per second
            capacity=self.config.burst_size
        )

    def get_limits_info(self, client_id: str) -> Dict[str, any]:
        """
        Get current limits info for client

        Args:
            client_id: Client identifier

        Returns:
            Dictionary with limit information
        """
        with self.lock:
            if client_id not in self.minute_limiters:
                return {
                    'minute_remaining': self.config.requests_per_minute,
                    'hour_remaining': self.config.requests_per_hour,
                    'burst_available': self.config.burst_size
                }

            return {
                'minute_remaining': self.minute_limiters[client_id].get_remaining(),
                'hour_remaining': self.hour_limiters[client_id].get_remaining(),
                'minute_limit': self.config.requests_per_minute,
                'hour_limit': self.config.requests_per_hour
            }

    def reset_client(self, client_id: str):
        """Reset rate limits for a client"""
        with self.lock:
            self.minute_limiters.pop(client_id, None)
            self.hour_limiters.pop(client_id, None)
            self.burst_limiters.pop(client_id, None)
            logger.info(f"Reset rate limits for client: {client_id}")


# Global rate limiter instance
global_rate_limiter = RateLimiter()


# ==================== DECORATORS ====================


def rate_limit(
    requests_per_minute: int = 30,
    requests_per_hour: int = 1000,
    get_client_id=lambda: "default"
):
    """
    Decorator for rate limiting endpoints

    Args:
        requests_per_minute: Max requests per minute
        requests_per_hour: Max requests per hour
        get_client_id: Function to extract client ID from request

    Usage:
        @rate_limit(requests_per_minute=60)
        async def my_endpoint():
            ...
    """
    config = RateLimitConfig(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour
    )
    limiter = RateLimiter(config)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client_id = get_client_id()

            allowed, error_msg = limiter.check_rate_limit(client_id)

            if not allowed:
                # Return HTTP 429 Too Many Requests
                # Actual implementation depends on framework
                raise Exception(f"Rate limit exceeded: {error_msg}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ==================== HELPER FUNCTIONS ====================


def check_rate_limit(client_id: str) -> Tuple[bool, Optional[str]]:
    """
    Check rate limit using global limiter

    Args:
        client_id: Client identifier

    Returns:
        Tuple of (allowed, error_message)
    """
    return global_rate_limiter.check_rate_limit(client_id)


def get_rate_limit_info(client_id: str) -> Dict[str, any]:
    """
    Get rate limit info for client

    Args:
        client_id: Client identifier

    Returns:
        Rate limit information dictionary
    """
    return global_rate_limiter.get_limits_info(client_id)

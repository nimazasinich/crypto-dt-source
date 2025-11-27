"""
Rate Limit Tracking Module
Manages rate limits per provider with in-memory tracking
"""

import time
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, Optional, Tuple

from utils.logger import setup_logger

logger = setup_logger("rate_limiter")


class RateLimiter:
    """
    Rate limiter with per-provider tracking
    """

    def __init__(self):
        """Initialize rate limiter"""
        self.limits: Dict[str, Dict] = {}
        self.lock = Lock()

    def configure_limit(self, provider: str, limit_type: str, limit_value: int):
        """
        Configure rate limit for a provider

        Args:
            provider: Provider name
            limit_type: Type of limit (per_minute, per_hour, per_day, per_second)
            limit_value: Maximum requests allowed
        """
        with self.lock:
            # Calculate reset time based on limit type
            now = datetime.now()
            if limit_type == "per_second":
                reset_time = now + timedelta(seconds=1)
            elif limit_type == "per_minute":
                reset_time = now + timedelta(minutes=1)
            elif limit_type == "per_hour":
                reset_time = now + timedelta(hours=1)
            elif limit_type == "per_day":
                reset_time = now + timedelta(days=1)
            else:
                logger.warning(f"Unknown limit type {limit_type} for {provider}")
                reset_time = now + timedelta(minutes=1)

            self.limits[provider] = {
                "limit_type": limit_type,
                "limit_value": limit_value,
                "current_usage": 0,
                "reset_time": reset_time,
                "last_request_time": None,
            }

            logger.info(f"Configured rate limit for {provider}: {limit_value} {limit_type}")

    def can_make_request(self, provider: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request can be made without exceeding rate limit

        Args:
            provider: Provider name

        Returns:
            Tuple of (can_proceed, reason_if_blocked)
        """
        with self.lock:
            if provider not in self.limits:
                # No limit configured, allow request
                return True, None

            limit_info = self.limits[provider]
            now = datetime.now()

            # Check if we need to reset the counter
            if now >= limit_info["reset_time"]:
                self._reset_limit(provider)
                limit_info = self.limits[provider]

            # Check if under limit
            if limit_info["current_usage"] < limit_info["limit_value"]:
                return True, None
            else:
                seconds_until_reset = (limit_info["reset_time"] - now).total_seconds()
                return False, f"Rate limit reached. Reset in {int(seconds_until_reset)}s"

    def record_request(self, provider: str):
        """
        Record a request against the rate limit

        Args:
            provider: Provider name
        """
        with self.lock:
            if provider not in self.limits:
                logger.warning(f"Recording request for unconfigured provider: {provider}")
                return

            limit_info = self.limits[provider]
            now = datetime.now()

            # Check if we need to reset first
            if now >= limit_info["reset_time"]:
                self._reset_limit(provider)
                limit_info = self.limits[provider]

            # Increment usage
            limit_info["current_usage"] += 1
            limit_info["last_request_time"] = now

            # Log warning if approaching limit
            percentage = (limit_info["current_usage"] / limit_info["limit_value"]) * 100
            if percentage >= 80:
                logger.warning(
                    f"Rate limit warning for {provider}: {percentage:.1f}% used "
                    f"({limit_info['current_usage']}/{limit_info['limit_value']})"
                )

    def _reset_limit(self, provider: str):
        """
        Reset rate limit counter

        Args:
            provider: Provider name
        """
        if provider not in self.limits:
            return

        limit_info = self.limits[provider]
        limit_type = limit_info["limit_type"]
        now = datetime.now()

        # Calculate new reset time
        if limit_type == "per_second":
            reset_time = now + timedelta(seconds=1)
        elif limit_type == "per_minute":
            reset_time = now + timedelta(minutes=1)
        elif limit_type == "per_hour":
            reset_time = now + timedelta(hours=1)
        elif limit_type == "per_day":
            reset_time = now + timedelta(days=1)
        else:
            reset_time = now + timedelta(minutes=1)

        limit_info["current_usage"] = 0
        limit_info["reset_time"] = reset_time

        logger.debug(f"Reset rate limit for {provider}. Next reset: {reset_time}")

    def get_status(self, provider: str) -> Optional[Dict]:
        """
        Get current rate limit status for provider

        Args:
            provider: Provider name

        Returns:
            Dict with limit info or None if not configured
        """
        with self.lock:
            if provider not in self.limits:
                return None

            limit_info = self.limits[provider]
            now = datetime.now()

            # Check if needs reset
            if now >= limit_info["reset_time"]:
                self._reset_limit(provider)
                limit_info = self.limits[provider]

            percentage = (
                (limit_info["current_usage"] / limit_info["limit_value"]) * 100
                if limit_info["limit_value"] > 0
                else 0
            )
            seconds_until_reset = max(0, (limit_info["reset_time"] - now).total_seconds())

            status = "ok"
            if percentage >= 100:
                status = "blocked"
            elif percentage >= 80:
                status = "warning"

            return {
                "provider": provider,
                "limit_type": limit_info["limit_type"],
                "limit_value": limit_info["limit_value"],
                "current_usage": limit_info["current_usage"],
                "percentage": round(percentage, 1),
                "reset_time": limit_info["reset_time"].isoformat(),
                "reset_in_seconds": int(seconds_until_reset),
                "status": status,
                "last_request_time": (
                    limit_info["last_request_time"].isoformat()
                    if limit_info["last_request_time"]
                    else None
                ),
            }

    def get_all_statuses(self) -> Dict[str, Dict]:
        """
        Get rate limit status for all providers

        Returns:
            Dict mapping provider names to their rate limit status
        """
        with self.lock:
            return {provider: self.get_status(provider) for provider in self.limits.keys()}

    def remove_limit(self, provider: str):
        """
        Remove rate limit configuration for provider

        Args:
            provider: Provider name
        """
        with self.lock:
            if provider in self.limits:
                del self.limits[provider]
                logger.info(f"Removed rate limit for {provider}")


# Global rate limiter instance
rate_limiter = RateLimiter()

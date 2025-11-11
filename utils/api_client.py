"""
HTTP API Client with Retry Logic and Timeout Handling
Provides robust HTTP client for API requests
"""

import aiohttp
import asyncio
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
import time
from utils.logger import setup_logger

logger = setup_logger("api_client")


class APIClientError(Exception):
    """Base exception for API client errors"""
    pass


class TimeoutError(APIClientError):
    """Timeout exception"""
    pass


class RateLimitError(APIClientError):
    """Rate limit exception"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class AuthenticationError(APIClientError):
    """Authentication exception"""
    pass


class ServerError(APIClientError):
    """Server error exception"""
    pass


class APIClient:
    """
    HTTP client with retry logic, timeout handling, and connection pooling
    """

    def __init__(
        self,
        default_timeout: int = 10,
        max_connections: int = 100,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize API client

        Args:
            default_timeout: Default timeout in seconds
            max_connections: Maximum concurrent connections
            retry_attempts: Maximum number of retry attempts
            retry_delay: Initial retry delay in seconds (exponential backoff)
        """
        self.default_timeout = default_timeout
        self.max_connections = max_connections
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

        # Connection pool configuration
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=10,
            ttl_dns_cache=300,
            enable_cleanup_closed=True
        )

        # Default headers
        self.default_headers = {
            "User-Agent": "CryptoAPIMonitor/1.0",
            "Accept": "application/json"
        }

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Tuple[int, Any, float, Optional[str]]:
        """
        Make HTTP request with error handling

        Returns:
            Tuple of (status_code, response_data, response_time_ms, error_message)
        """
        merged_headers = {**self.default_headers}
        if headers:
            merged_headers.update(headers)

        timeout_seconds = timeout or self.default_timeout
        timeout_config = aiohttp.ClientTimeout(total=timeout_seconds)

        start_time = time.time()
        error_message = None

        try:
            async with aiohttp.ClientSession(
                connector=self.connector,
                timeout=timeout_config
            ) as session:
                async with session.request(
                    method,
                    url,
                    headers=merged_headers,
                    params=params,
                    ssl=True,  # Enable SSL verification
                    **kwargs
                ) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    status_code = response.status

                    # Try to parse JSON response
                    try:
                        data = await response.json()
                    except:
                        # If not JSON, get text
                        data = await response.text()

                    return status_code, data, response_time_ms, error_message

        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            error_message = f"Request timeout after {timeout_seconds}s"
            return 0, None, response_time_ms, error_message

        except aiohttp.ClientError as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_message = f"Client error: {str(e)}"
            return 0, None, response_time_ms, error_message

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_message = f"Unexpected error: {str(e)}"
            return 0, None, response_time_ms, error_message

    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: Optional[int] = None,
        retry: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Optional headers
            params: Optional query parameters
            timeout: Optional timeout override
            retry: Enable retry logic

        Returns:
            Dict with keys: success, status_code, data, response_time_ms, error_type, error_message
        """
        attempt = 0
        last_error = None
        current_timeout = timeout or self.default_timeout

        while attempt < (self.retry_attempts if retry else 1):
            attempt += 1

            status_code, data, response_time_ms, error_message = await self._make_request(
                method, url, headers, params, current_timeout, **kwargs
            )

            # Success
            if status_code == 200:
                return {
                    "success": True,
                    "status_code": status_code,
                    "data": data,
                    "response_time_ms": response_time_ms,
                    "error_type": None,
                    "error_message": None,
                    "retry_count": attempt - 1
                }

            # Rate limit - extract Retry-After header
            elif status_code == 429:
                last_error = "rate_limit"
                # Try to get retry-after from response
                retry_after = 60  # Default to 60 seconds

                if not retry or attempt >= self.retry_attempts:
                    return {
                        "success": False,
                        "status_code": status_code,
                        "data": None,
                        "response_time_ms": response_time_ms,
                        "error_type": "rate_limit",
                        "error_message": f"Rate limit exceeded. Retry after {retry_after}s",
                        "retry_count": attempt - 1,
                        "retry_after": retry_after
                    }

                # Wait and retry
                await asyncio.sleep(retry_after + 10)  # Add 10s buffer
                continue

            # Authentication error - don't retry
            elif status_code in [401, 403]:
                return {
                    "success": False,
                    "status_code": status_code,
                    "data": None,
                    "response_time_ms": response_time_ms,
                    "error_type": "authentication",
                    "error_message": f"Authentication failed: HTTP {status_code}",
                    "retry_count": attempt - 1
                }

            # Server error - retry with exponential backoff
            elif status_code >= 500:
                last_error = "server_error"

                if not retry or attempt >= self.retry_attempts:
                    return {
                        "success": False,
                        "status_code": status_code,
                        "data": None,
                        "response_time_ms": response_time_ms,
                        "error_type": "server_error",
                        "error_message": f"Server error: HTTP {status_code}",
                        "retry_count": attempt - 1
                    }

                # Exponential backoff: 1min, 2min, 4min
                delay = self.retry_delay * 60 * (2 ** (attempt - 1))
                await asyncio.sleep(min(delay, 240))  # Max 4 minutes
                continue

            # Timeout - retry with increased timeout
            elif error_message and "timeout" in error_message.lower():
                last_error = "timeout"

                if not retry or attempt >= self.retry_attempts:
                    return {
                        "success": False,
                        "status_code": 0,
                        "data": None,
                        "response_time_ms": response_time_ms,
                        "error_type": "timeout",
                        "error_message": error_message,
                        "retry_count": attempt - 1
                    }

                # Increase timeout by 50%
                current_timeout = int(current_timeout * 1.5)
                await asyncio.sleep(self.retry_delay)
                continue

            # Other errors
            else:
                return {
                    "success": False,
                    "status_code": status_code or 0,
                    "data": data,
                    "response_time_ms": response_time_ms,
                    "error_type": "network_error" if status_code == 0 else "http_error",
                    "error_message": error_message or f"HTTP {status_code}",
                    "retry_count": attempt - 1
                }

        # All retries exhausted
        return {
            "success": False,
            "status_code": 0,
            "data": None,
            "response_time_ms": 0,
            "error_type": last_error or "unknown",
            "error_message": "All retry attempts exhausted",
            "retry_count": self.retry_attempts
        }

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return await self.request("POST", url, **kwargs)

    async def close(self):
        """Close connector"""
        if self.connector:
            await self.connector.close()


# Global client instance
_client = None


def get_client() -> APIClient:
    """Get global API client instance"""
    global _client
    if _client is None:
        _client = APIClient()
    return _client

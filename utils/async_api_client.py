"""
Unified Async API Client - Replace mixed sync/async HTTP calls
Implements retry logic, error handling, and logging consistently
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import traceback

import config

logger = logging.getLogger(__name__)


class AsyncAPIClient:
    """
    Unified async HTTP client with retry logic and error handling
    Replaces mixed requests/aiohttp calls throughout the codebase
    """

    def __init__(
        self,
        timeout: int = config.REQUEST_TIMEOUT,
        max_retries: int = config.MAX_RETRIES,
        retry_delay: float = 2.0
    ):
        """
        Initialize async API client

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make async GET request with retry logic

        Args:
            url: Request URL
            params: Query parameters
            headers: HTTP headers

        Returns:
            JSON response as dictionary or None on failure
        """
        if not self._session:
            raise RuntimeError("Client must be used as async context manager")

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"GET {url} (attempt {attempt + 1}/{self.max_retries})")

                async with self._session.get(url, params=params, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    logger.debug(f"GET {url} successful")
                    return data

            except aiohttp.ClientResponseError as e:
                logger.warning(f"HTTP {e.status} error on {url}: {e.message}")
                if e.status in (404, 400, 401, 403):
                    # Don't retry client errors
                    return None
                # Retry on server errors (5xx)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                return None

            except aiohttp.ClientConnectionError as e:
                logger.warning(f"Connection error on {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                return None

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on {url} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                return None

            except Exception as e:
                logger.error(f"Unexpected error on {url}: {e}\n{traceback.format_exc()}")
                return None

        return None

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make async POST request with retry logic

        Args:
            url: Request URL
            data: Form data
            json: JSON payload
            headers: HTTP headers

        Returns:
            JSON response as dictionary or None on failure
        """
        if not self._session:
            raise RuntimeError("Client must be used as async context manager")

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"POST {url} (attempt {attempt + 1}/{self.max_retries})")

                async with self._session.post(
                    url, data=data, json=json, headers=headers
                ) as response:
                    response.raise_for_status()
                    response_data = await response.json()
                    logger.debug(f"POST {url} successful")
                    return response_data

            except aiohttp.ClientResponseError as e:
                logger.warning(f"HTTP {e.status} error on {url}: {e.message}")
                if e.status in (404, 400, 401, 403):
                    return None
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                return None

            except Exception as e:
                logger.error(f"Error on POST {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                return None

        return None

    async def gather_requests(
        self,
        urls: List[str],
        params_list: Optional[List[Optional[Dict[str, Any]]]] = None
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Make multiple async GET requests in parallel

        Args:
            urls: List of URLs to fetch
            params_list: Optional list of params for each URL

        Returns:
            List of responses (None for failed requests)
        """
        if params_list is None:
            params_list = [None] * len(urls)

        tasks = [
            self.get(url, params=params)
            for url, params in zip(urls, params_list)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to None
        return [
            result if not isinstance(result, Exception) else None
            for result in results
        ]


# ==================== CONVENIENCE FUNCTIONS ====================


async def safe_api_call(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = config.REQUEST_TIMEOUT
) -> Optional[Dict[str, Any]]:
    """
    Convenience function for single async API call

    Args:
        url: Request URL
        params: Query parameters
        headers: HTTP headers
        timeout: Request timeout

    Returns:
        JSON response or None on failure
    """
    async with AsyncAPIClient(timeout=timeout) as client:
        return await client.get(url, params=params, headers=headers)


async def parallel_api_calls(
    urls: List[str],
    params_list: Optional[List[Optional[Dict[str, Any]]]] = None,
    timeout: int = config.REQUEST_TIMEOUT
) -> List[Optional[Dict[str, Any]]]:
    """
    Convenience function for parallel async API calls

    Args:
        urls: List of URLs
        params_list: Optional params for each URL
        timeout: Request timeout

    Returns:
        List of responses (None for failures)
    """
    async with AsyncAPIClient(timeout=timeout) as client:
        return await client.gather_requests(urls, params_list)

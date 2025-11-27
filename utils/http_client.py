"""
Async HTTP Client with Retry Logic
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get(
        self,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """Make GET request with retry logic"""
        start_time = datetime.utcnow()

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

                # Try to parse JSON response
                try:
                    data = await response.json()
                except:
                    data = await response.text()

                return {
                    "success": response.status == 200,
                    "status_code": response.status,
                    "data": data,
                    "response_time_ms": elapsed_ms,
                    "error": (
                        None
                        if response.status == 200
                        else {"type": "http_error", "message": f"HTTP {response.status}"}
                    ),
                }

        except asyncio.TimeoutError:
            elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            if retry_count < self.max_retries:
                logger.warning(
                    f"Timeout for {url}, retrying ({retry_count + 1}/{self.max_retries})"
                )
                await asyncio.sleep(2**retry_count)  # Exponential backoff
                return await self.get(url, headers, params, retry_count + 1)

            return {
                "success": False,
                "status_code": 0,
                "data": None,
                "response_time_ms": elapsed_ms,
                "error": {"type": "timeout", "message": "Request timeout"},
            }

        except aiohttp.ClientError as e:
            elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return {
                "success": False,
                "status_code": 0,
                "data": None,
                "response_time_ms": elapsed_ms,
                "error": {"type": "client_error", "message": str(e)},
            }

        except Exception as e:
            elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            logger.error(f"Unexpected error for {url}: {e}")

            return {
                "success": False,
                "status_code": 0,
                "data": None,
                "response_time_ms": elapsed_ms,
                "error": {"type": "unknown", "message": str(e)},
            }

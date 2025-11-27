"""
API Health Monitoring Engine
Async health checks with retry logic, caching, and metrics tracking
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""

    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check"""

    provider_name: str
    category: str
    status: HealthStatus
    response_time: float  # in milliseconds
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: float = None
    endpoint_tested: str = ""

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        d = asdict(self)
        d["status"] = self.status.value
        d["timestamp_human"] = datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return d

    def get_badge(self) -> str:
        """Get emoji badge for status"""
        badges = {
            HealthStatus.ONLINE: "🟢",
            HealthStatus.DEGRADED: "🟡",
            HealthStatus.OFFLINE: "🔴",
            HealthStatus.UNKNOWN: "⚪",
        }
        return badges.get(self.status, "⚪")


class APIMonitor:
    """Asynchronous API health monitor"""

    def __init__(self, config, timeout: int = 10, max_concurrent: int = 10):
        self.config = config
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 60  # 1 minute cache
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.results_history = []  # Store recent results

    async def check_endpoint(
        self, resource: Dict, use_proxy: bool = False, proxy_index: int = 0
    ) -> HealthCheckResult:
        """Check a single endpoint health"""
        provider_name = resource.get("name", "Unknown")
        category = resource.get("category", "Other")

        # Check cache first
        cache_key = f"{provider_name}:{category}"
        if cache_key in self.cache:
            cached_result, cache_time = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                logger.debug(f"Cache hit for {provider_name}")
                return cached_result

        # Construct URL
        url = resource.get("url", "")
        endpoint = resource.get("endpoint", "")
        test_url = f"{url}{endpoint}" if endpoint else url

        # Add API key if available
        api_key = resource.get("key", "")
        if not api_key:
            # Try to get from config
            key_name = provider_name.lower().replace(" ", "").replace("(", "").replace(")", "")
            api_key = self.config.get_api_key(key_name)

        # Apply proxy if needed
        if use_proxy:
            proxy_url = self.config.get_cors_proxy(proxy_index)
            if "allorigins" in proxy_url:
                test_url = f"{proxy_url}{test_url}"
            else:
                test_url = f"{proxy_url}{test_url}"

        start_time = time.time()

        try:
            async with self.semaphore:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as session:
                    headers = {}

                    # Add API key to headers if available
                    if api_key:
                        if "coinmarketcap" in provider_name.lower():
                            headers["X-CMC_PRO_API_KEY"] = api_key
                        elif (
                            "etherscan" in provider_name.lower()
                            or "bscscan" in provider_name.lower()
                        ):
                            # Add as query parameter instead
                            separator = "&" if "?" in test_url else "?"
                            test_url = f"{test_url}{separator}apikey={api_key}"

                    async with session.get(test_url, headers=headers, ssl=False) as response:
                        response_time = (time.time() - start_time) * 1000  # Convert to ms
                        status_code = response.status

                        # Determine health status
                        if status_code == 200:
                            # Try to parse JSON to ensure valid response
                            try:
                                data = await response.json()
                                if data:
                                    status = HealthStatus.ONLINE
                                else:
                                    status = HealthStatus.DEGRADED
                            except:
                                status = HealthStatus.DEGRADED
                        elif 200 < status_code < 300:
                            status = HealthStatus.ONLINE
                        elif 400 <= status_code < 500:
                            status = HealthStatus.DEGRADED
                        else:
                            status = HealthStatus.OFFLINE

                        result = HealthCheckResult(
                            provider_name=provider_name,
                            category=category,
                            status=status,
                            response_time=response_time,
                            status_code=status_code,
                            endpoint_tested=test_url[:100],  # Truncate long URLs
                        )

        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                provider_name=provider_name,
                category=category,
                status=HealthStatus.OFFLINE,
                response_time=response_time,
                error_message="Timeout",
                endpoint_tested=test_url[:100],
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                provider_name=provider_name,
                category=category,
                status=HealthStatus.OFFLINE,
                response_time=response_time,
                error_message=str(e)[:200],  # Truncate long errors
                endpoint_tested=test_url[:100],
            )
            logger.error(f"Error checking {provider_name}: {e}")

        # Cache the result
        self.cache[cache_key] = (result, time.time())

        # Add to history
        self.results_history.append(result)
        # Keep only last 1000 results
        if len(self.results_history) > 1000:
            self.results_history = self.results_history[-1000:]

        return result

    async def check_all(
        self, resources: Optional[List[Dict]] = None, use_proxy: bool = False
    ) -> List[HealthCheckResult]:
        """Check all endpoints"""
        if resources is None:
            resources = self.config.get_all_resources()

        logger.info(f"Checking {len(resources)} endpoints...")

        # Create tasks with stagger to avoid overwhelming APIs
        tasks = []
        for i, resource in enumerate(resources):
            # Stagger requests by 0.1 seconds each
            await asyncio.sleep(0.1)
            task = asyncio.create_task(self.check_endpoint(resource, use_proxy))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, HealthCheckResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Task failed with exception: {result}")

        logger.info(f"Completed {len(valid_results)} checks")
        return valid_results

    async def check_by_category(
        self, category: str, use_proxy: bool = False
    ) -> List[HealthCheckResult]:
        """Check all endpoints in a category"""
        resources = self.config.get_by_category(category)
        return await self.check_all(resources, use_proxy)

    async def check_single(
        self, provider_name: str, use_proxy: bool = False
    ) -> Optional[HealthCheckResult]:
        """Check a single provider by name"""
        resources = self.config.get_all_resources()
        resource = next((r for r in resources if r.get("name") == provider_name), None)

        if resource:
            return await self.check_endpoint(resource, use_proxy)
        return None

    def get_summary_stats(self, results: List[HealthCheckResult]) -> Dict:
        """Calculate summary statistics from results"""
        if not results:
            return {
                "total": 0,
                "online": 0,
                "degraded": 0,
                "offline": 0,
                "unknown": 0,
                "online_percentage": 0,
                "avg_response_time": 0,
                "critical_issues": 0,
            }

        online = sum(1 for r in results if r.status == HealthStatus.ONLINE)
        degraded = sum(1 for r in results if r.status == HealthStatus.DEGRADED)
        offline = sum(1 for r in results if r.status == HealthStatus.OFFLINE)
        unknown = sum(1 for r in results if r.status == HealthStatus.UNKNOWN)

        response_times = [r.response_time for r in results if r.response_time]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Critical issues: Tier 1 APIs that are offline
        critical_issues = sum(
            1
            for r in results
            if r.status == HealthStatus.OFFLINE and self._is_tier1(r.provider_name)
        )

        return {
            "total": len(results),
            "online": online,
            "degraded": degraded,
            "offline": offline,
            "unknown": unknown,
            "online_percentage": round((online / len(results)) * 100, 2) if results else 0,
            "avg_response_time": round(avg_response_time, 2),
            "critical_issues": critical_issues,
        }

    def _is_tier1(self, provider_name: str) -> bool:
        """Check if provider is Tier 1"""
        resources = self.config.get_all_resources()
        resource = next((r for r in resources if r.get("name") == provider_name), None)
        return resource.get("tier", 3) == 1 if resource else False

    def get_category_stats(self, results: List[HealthCheckResult]) -> Dict[str, Dict]:
        """Get statistics grouped by category"""
        category_results = {}

        for result in results:
            category = result.category
            if category not in category_results:
                category_results[category] = []
            category_results[category].append(result)

        return {
            category: self.get_summary_stats(cat_results)
            for category, cat_results in category_results.items()
        }

    def get_recent_history(self, hours: int = 24) -> List[HealthCheckResult]:
        """Get recent history within specified hours"""
        cutoff_time = time.time() - (hours * 3600)
        return [r for r in self.results_history if r.timestamp >= cutoff_time]

    def clear_cache(self):
        """Clear the results cache"""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_uptime_percentage(self, provider_name: str, hours: int = 24) -> float:
        """Calculate uptime percentage for a provider"""
        recent = self.get_recent_history(hours)
        provider_results = [r for r in recent if r.provider_name == provider_name]

        if not provider_results:
            return 0.0

        online_count = sum(1 for r in provider_results if r.status == HealthStatus.ONLINE)
        return round((online_count / len(provider_results)) * 100, 2)


# Convenience function for synchronous usage
def check_all_sync(config, use_proxy: bool = False) -> List[HealthCheckResult]:
    """Synchronous wrapper for checking all endpoints"""
    monitor = APIMonitor(config)
    return asyncio.run(monitor.check_all(use_proxy=use_proxy))

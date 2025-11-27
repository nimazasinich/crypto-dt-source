"""
Real-time API Health Monitoring Module
Implements comprehensive health checks with rate limiting, failure tracking, and database persistence
"""

import asyncio
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config import config
from database import Database
from monitor import HealthCheckResult, HealthStatus
from monitoring.rate_limiter import rate_limiter

# Import required modules
from utils.api_client import APIClient
from utils.logger import log_api_request, log_error, setup_logger

# Setup logger
logger = setup_logger("health_checker")


class HealthChecker:
    """
    Real-time API health monitoring with rate limiting and failure tracking
    """

    def __init__(self, db_path: str = "data/health_metrics.db"):
        """
        Initialize health checker

        Args:
            db_path: Path to SQLite database
        """
        self.api_client = APIClient(
            default_timeout=10,
            max_connections=50,
            retry_attempts=1,  # We'll handle retries ourselves
            retry_delay=1.0,
        )
        self.db = Database(db_path)
        self.consecutive_failures: Dict[str, int] = defaultdict(int)

        # Initialize rate limiters for all providers
        self._initialize_rate_limiters()

        logger.info("HealthChecker initialized")

    def _initialize_rate_limiters(self):
        """Configure rate limiters for all providers"""
        for provider in config.get_all_providers():
            if provider.rate_limit_type and provider.rate_limit_value:
                rate_limiter.configure_limit(
                    provider=provider.name,
                    limit_type=provider.rate_limit_type,
                    limit_value=provider.rate_limit_value,
                )
                logger.info(
                    f"Configured rate limit for {provider.name}: "
                    f"{provider.rate_limit_value} {provider.rate_limit_type}"
                )

    async def check_provider(self, provider_name: str) -> Optional[HealthCheckResult]:
        """
        Check single provider health

        Args:
            provider_name: Name of the provider to check

        Returns:
            HealthCheckResult object or None if provider not found
        """
        provider = config.get_provider(provider_name)
        if not provider:
            logger.error(f"Provider not found: {provider_name}")
            return None

        # Check rate limit before making request
        can_proceed, reason = rate_limiter.can_make_request(provider.name)
        if not can_proceed:
            logger.warning(f"Rate limit blocked request to {provider.name}: {reason}")

            # Return a degraded status for rate-limited provider
            result = HealthCheckResult(
                provider_name=provider.name,
                category=provider.category,
                status=HealthStatus.DEGRADED,
                response_time=0,
                status_code=None,
                error_message=f"Rate limited: {reason}",
                timestamp=time.time(),
                endpoint_tested=provider.health_check_endpoint,
            )

            # Save to database
            self.db.save_health_check(result)
            return result

        # Perform health check
        result = await self._perform_health_check(provider)

        # Record request against rate limit
        rate_limiter.record_request(provider.name)

        # Update consecutive failure tracking
        if result.status == HealthStatus.OFFLINE:
            self.consecutive_failures[provider.name] += 1
            logger.warning(
                f"{provider.name} offline - consecutive failures: "
                f"{self.consecutive_failures[provider.name]}"
            )
        else:
            self.consecutive_failures[provider.name] = 0

        # Re-evaluate status based on consecutive failures
        if self.consecutive_failures[provider.name] >= 3:
            result = HealthCheckResult(
                provider_name=result.provider_name,
                category=result.category,
                status=HealthStatus.OFFLINE,
                response_time=result.response_time,
                status_code=result.status_code,
                error_message=f"3+ consecutive failures (count: {self.consecutive_failures[provider.name]})",
                timestamp=result.timestamp,
                endpoint_tested=result.endpoint_tested,
            )

        # Save to database
        self.db.save_health_check(result)

        # Log the check
        log_api_request(
            logger=logger,
            provider=provider.name,
            endpoint=provider.health_check_endpoint,
            duration_ms=result.response_time,
            status=result.status.value,
            http_code=result.status_code,
            level="INFO" if result.status == HealthStatus.ONLINE else "WARNING",
        )

        return result

    async def check_all_providers(self) -> List[HealthCheckResult]:
        """
        Check all configured providers

        Returns:
            List of HealthCheckResult objects
        """
        providers = config.get_all_providers()
        logger.info(f"Starting health check for {len(providers)} providers")

        # Create tasks for all providers with staggered start
        tasks = []
        for i, provider in enumerate(providers):
            # Stagger requests by 100ms to avoid overwhelming the system
            await asyncio.sleep(0.1)
            task = asyncio.create_task(self.check_provider(provider.name))
            tasks.append(task)

        # Wait for all checks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and None values
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, HealthCheckResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Health check failed with exception: {result}", exc_info=True)
                # Create a failed result
                provider = providers[i]
                failed_result = HealthCheckResult(
                    provider_name=provider.name,
                    category=provider.category,
                    status=HealthStatus.OFFLINE,
                    response_time=0,
                    status_code=None,
                    error_message=f"Exception: {str(result)[:200]}",
                    timestamp=time.time(),
                    endpoint_tested=provider.health_check_endpoint,
                )
                self.db.save_health_check(failed_result)
                valid_results.append(failed_result)
            elif result is None:
                # Provider not found or other issue
                continue

        logger.info(f"Completed health check: {len(valid_results)} results")

        # Log summary statistics
        self._log_summary_stats(valid_results)

        return valid_results

    async def check_category(self, category: str) -> List[HealthCheckResult]:
        """
        Check providers in a specific category

        Args:
            category: Category name (e.g., 'market_data', 'blockchain_explorers')

        Returns:
            List of HealthCheckResult objects
        """
        providers = config.get_providers_by_category(category)

        if not providers:
            logger.warning(f"No providers found for category: {category}")
            return []

        logger.info(f"Starting health check for category '{category}': {len(providers)} providers")

        # Create tasks for all providers in category
        tasks = []
        for i, provider in enumerate(providers):
            # Stagger requests
            await asyncio.sleep(0.1)
            task = asyncio.create_task(self.check_provider(provider.name))
            tasks.append(task)

        # Wait for all checks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter valid results
        valid_results = []
        for result in results:
            if isinstance(result, HealthCheckResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Category check failed with exception: {result}", exc_info=True)

        logger.info(f"Completed category '{category}' check: {len(valid_results)} results")

        return valid_results

    async def _perform_health_check(self, provider) -> HealthCheckResult:
        """
        Perform the actual health check HTTP request

        Args:
            provider: ProviderConfig object

        Returns:
            HealthCheckResult object
        """
        endpoint = provider.health_check_endpoint

        # Build headers
        headers = {}
        params = {}

        # Add API key to headers or query params based on provider
        if provider.requires_key and provider.api_key:
            if "coinmarketcap" in provider.name.lower():
                headers["X-CMC_PRO_API_KEY"] = provider.api_key
            elif "cryptocompare" in provider.name.lower():
                headers["authorization"] = f"Apikey {provider.api_key}"
            elif "newsapi" in provider.name.lower() or "newsdata" in endpoint.lower():
                params["apikey"] = provider.api_key
            elif "etherscan" in provider.name.lower() or "bscscan" in provider.name.lower():
                params["apikey"] = provider.api_key
            elif "tronscan" in provider.name.lower():
                headers["TRON-PRO-API-KEY"] = provider.api_key
            else:
                # Generic API key in query param
                params["apikey"] = provider.api_key

        # Calculate timeout in seconds (convert from ms if needed)
        timeout = (provider.timeout_ms or 10000) / 1000.0

        # Make the HTTP request
        start_time = time.time()
        response = await self.api_client.request(
            method="GET",
            url=endpoint,
            headers=headers if headers else None,
            params=params if params else None,
            timeout=int(timeout),
            retry=False,  # We handle retries at a higher level
        )

        # Extract response data
        success = response.get("success", False)
        status_code = response.get("status_code", 0)
        response_time_ms = response.get("response_time_ms", 0)
        error_type = response.get("error_type")
        error_message = response.get("error_message")

        # Determine health status based on response
        status = self._determine_health_status(
            success=success,
            status_code=status_code,
            response_time_ms=response_time_ms,
            error_type=error_type,
        )

        # Build error message if applicable
        final_error_message = None
        if not success:
            if error_message:
                final_error_message = error_message
            elif error_type:
                final_error_message = (
                    f"{error_type}: HTTP {status_code}" if status_code else error_type
                )
            else:
                final_error_message = f"Request failed with status {status_code}"

        # Create result object
        result = HealthCheckResult(
            provider_name=provider.name,
            category=provider.category,
            status=status,
            response_time=response_time_ms,
            status_code=status_code if status_code > 0 else None,
            error_message=final_error_message,
            timestamp=time.time(),
            endpoint_tested=endpoint,
        )

        return result

    def _determine_health_status(
        self, success: bool, status_code: int, response_time_ms: float, error_type: Optional[str]
    ) -> HealthStatus:
        """
        Determine health status based on response metrics

        Rules:
        - ONLINE: status 200, response < 2000ms
        - DEGRADED: response 2000-5000ms OR status 4xx/5xx
        - OFFLINE: timeout OR status 0 (network error)

        Args:
            success: Whether request was successful
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            error_type: Type of error if any

        Returns:
            HealthStatus enum value
        """
        # Offline conditions
        if error_type == "timeout":
            return HealthStatus.OFFLINE

        if status_code == 0:  # Network error, connection failed
            return HealthStatus.OFFLINE

        # Degraded conditions
        if status_code >= 400:  # 4xx or 5xx errors
            return HealthStatus.DEGRADED

        if response_time_ms >= 2000 and response_time_ms < 5000:
            return HealthStatus.DEGRADED

        if response_time_ms >= 5000:
            return HealthStatus.OFFLINE

        # Online conditions
        if status_code == 200 and response_time_ms < 2000:
            return HealthStatus.ONLINE

        # Success with other 2xx codes and good response time
        if success and 200 <= status_code < 300 and response_time_ms < 2000:
            return HealthStatus.ONLINE

        # Default to degraded for edge cases
        return HealthStatus.DEGRADED

    def _log_summary_stats(self, results: List[HealthCheckResult]):
        """
        Log summary statistics for health check results

        Args:
            results: List of HealthCheckResult objects
        """
        if not results:
            return

        total = len(results)
        online = sum(1 for r in results if r.status == HealthStatus.ONLINE)
        degraded = sum(1 for r in results if r.status == HealthStatus.DEGRADED)
        offline = sum(1 for r in results if r.status == HealthStatus.OFFLINE)

        avg_response_time = sum(r.response_time for r in results) / total if total > 0 else 0

        logger.info(
            f"Health Check Summary - Total: {total}, "
            f"Online: {online} ({online/total*100:.1f}%), "
            f"Degraded: {degraded} ({degraded/total*100:.1f}%), "
            f"Offline: {offline} ({offline/total*100:.1f}%), "
            f"Avg Response Time: {avg_response_time:.2f}ms"
        )

    def get_consecutive_failures(self, provider_name: str) -> int:
        """
        Get consecutive failure count for a provider

        Args:
            provider_name: Provider name

        Returns:
            Number of consecutive failures
        """
        return self.consecutive_failures.get(provider_name, 0)

    def reset_consecutive_failures(self, provider_name: str):
        """
        Reset consecutive failure count for a provider

        Args:
            provider_name: Provider name
        """
        if provider_name in self.consecutive_failures:
            self.consecutive_failures[provider_name] = 0
            logger.info(f"Reset consecutive failures for {provider_name}")

    def get_all_consecutive_failures(self) -> Dict[str, int]:
        """
        Get all consecutive failure counts

        Returns:
            Dictionary mapping provider names to failure counts
        """
        return dict(self.consecutive_failures)

    async def close(self):
        """Close resources"""
        await self.api_client.close()
        logger.info("HealthChecker closed")


# Convenience functions for synchronous usage
def check_provider_sync(provider_name: str) -> Optional[HealthCheckResult]:
    """
    Synchronous wrapper for checking a single provider

    Args:
        provider_name: Provider name

    Returns:
        HealthCheckResult object or None
    """
    checker = HealthChecker()
    result = asyncio.run(checker.check_provider(provider_name))
    asyncio.run(checker.close())
    return result


def check_all_providers_sync() -> List[HealthCheckResult]:
    """
    Synchronous wrapper for checking all providers

    Returns:
        List of HealthCheckResult objects
    """
    checker = HealthChecker()
    results = asyncio.run(checker.check_all_providers())
    asyncio.run(checker.close())
    return results


def check_category_sync(category: str) -> List[HealthCheckResult]:
    """
    Synchronous wrapper for checking a category

    Args:
        category: Category name

    Returns:
        List of HealthCheckResult objects
    """
    checker = HealthChecker()
    results = asyncio.run(checker.check_category(category))
    asyncio.run(checker.close())
    return results


# Example usage
if __name__ == "__main__":

    async def main():
        """Example usage of HealthChecker"""
        checker = HealthChecker()

        # Check single provider
        print("\n=== Checking single provider: CoinGecko ===")
        result = await checker.check_provider("CoinGecko")
        if result:
            print(f"Status: {result.status.value}")
            print(f"Response Time: {result.response_time:.2f}ms")
            print(f"HTTP Code: {result.status_code}")
            print(f"Error: {result.error_message}")

        # Check all providers
        print("\n=== Checking all providers ===")
        results = await checker.check_all_providers()
        for r in results:
            print(f"{r.provider_name}: {r.status.value} ({r.response_time:.2f}ms)")

        # Check by category
        print("\n=== Checking market_data category ===")
        market_results = await checker.check_category("market_data")
        for r in market_results:
            print(f"{r.provider_name}: {r.status.value} ({r.response_time:.2f}ms)")

        await checker.close()

    asyncio.run(main())

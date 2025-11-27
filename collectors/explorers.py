"""
Blockchain Explorer Data Collectors
Fetches data from Etherscan, BscScan, and TronScan
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config import config
from utils.api_client import get_client
from utils.logger import log_api_request, log_error, setup_logger

logger = setup_logger("explorers_collector")


def calculate_staleness_minutes(data_timestamp: Optional[datetime]) -> Optional[float]:
    """
    Calculate staleness in minutes from data timestamp to now

    Args:
        data_timestamp: Timestamp of the data

    Returns:
        Staleness in minutes or None if timestamp not available
    """
    if not data_timestamp:
        return None

    now = datetime.now(timezone.utc)
    if data_timestamp.tzinfo is None:
        data_timestamp = data_timestamp.replace(tzinfo=timezone.utc)

    delta = now - data_timestamp
    return delta.total_seconds() / 60.0


async def get_etherscan_gas_price() -> Dict[str, Any]:
    """
    Get current Ethereum gas price from Etherscan

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "Etherscan"
    category = "blockchain_explorers"
    endpoint = "/api?module=gastracker&action=gasoracle"

    logger.info(f"Fetching gas price from {provider}")

    try:
        client = get_client()
        provider_config = config.get_provider(provider)

        if not provider_config:
            error_msg = f"Provider {provider} not configured"
            log_error(logger, provider, "config_error", error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
            }

        # Check if API key is available
        if provider_config.requires_key and not provider_config.api_key:
            error_msg = f"API key required but not configured for {provider}"
            log_error(logger, provider, "auth_error", error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
                "error_type": "missing_api_key",
            }

        # Build request URL
        url = provider_config.endpoint_url
        params = {"module": "gastracker", "action": "gasoracle", "apikey": provider_config.api_key}

        # Make request
        response = await client.get(url, params=params, timeout=provider_config.timeout_ms // 1000)

        # Log request
        log_api_request(
            logger,
            provider,
            endpoint,
            response.get("response_time_ms", 0),
            "success" if response["success"] else "error",
            response.get("status_code"),
        )

        if not response["success"]:
            error_msg = response.get("error_message", "Unknown error")
            log_error(logger, provider, response.get("error_type", "unknown"), error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
                "error_type": response.get("error_type"),
            }

        # Extract data
        data = response["data"]

        # Etherscan returns real-time data, so staleness is minimal
        data_timestamp = datetime.now(timezone.utc)
        staleness = 0.0

        # Check API response status
        if isinstance(data, dict):
            api_status = data.get("status")
            if api_status == "0":
                error_msg = data.get("message", "API returned error status")
                log_error(logger, provider, "api_error", error_msg, endpoint)
                return {
                    "provider": provider,
                    "category": category,
                    "data": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "staleness_minutes": None,
                    "success": False,
                    "error": error_msg,
                    "error_type": "api_error",
                }

        logger.info(f"{provider} - {endpoint} - Gas price retrieved, staleness: {staleness:.2f}m")

        return {
            "provider": provider,
            "category": category,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_timestamp": data_timestamp.isoformat(),
            "staleness_minutes": staleness,
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0),
        }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(logger, provider, "exception", error_msg, endpoint, exc_info=True)
        return {
            "provider": provider,
            "category": category,
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "staleness_minutes": None,
            "success": False,
            "error": error_msg,
            "error_type": "exception",
        }


async def get_bscscan_bnb_price() -> Dict[str, Any]:
    """
    Get BNB price from BscScan

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "BscScan"
    category = "blockchain_explorers"
    endpoint = "/api?module=stats&action=bnbprice"

    logger.info(f"Fetching BNB price from {provider}")

    try:
        client = get_client()
        provider_config = config.get_provider(provider)

        if not provider_config:
            error_msg = f"Provider {provider} not configured"
            log_error(logger, provider, "config_error", error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
            }

        # Check if API key is available
        if provider_config.requires_key and not provider_config.api_key:
            error_msg = f"API key required but not configured for {provider}"
            log_error(logger, provider, "auth_error", error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
                "error_type": "missing_api_key",
            }

        # Build request URL
        url = provider_config.endpoint_url
        params = {"module": "stats", "action": "bnbprice", "apikey": provider_config.api_key}

        # Make request
        response = await client.get(url, params=params, timeout=provider_config.timeout_ms // 1000)

        # Log request
        log_api_request(
            logger,
            provider,
            endpoint,
            response.get("response_time_ms", 0),
            "success" if response["success"] else "error",
            response.get("status_code"),
        )

        if not response["success"]:
            error_msg = response.get("error_message", "Unknown error")
            log_error(logger, provider, response.get("error_type", "unknown"), error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
                "error_type": response.get("error_type"),
            }

        # Extract data
        data = response["data"]

        # BscScan returns real-time data
        data_timestamp = datetime.now(timezone.utc)
        staleness = 0.0

        # Check API response status
        if isinstance(data, dict):
            api_status = data.get("status")
            if api_status == "0":
                error_msg = data.get("message", "API returned error status")
                log_error(logger, provider, "api_error", error_msg, endpoint)
                return {
                    "provider": provider,
                    "category": category,
                    "data": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "staleness_minutes": None,
                    "success": False,
                    "error": error_msg,
                    "error_type": "api_error",
                }

            # Extract timestamp if available
            if "result" in data and isinstance(data["result"], dict):
                if "ethusd_timestamp" in data["result"]:
                    try:
                        data_timestamp = datetime.fromtimestamp(
                            int(data["result"]["ethusd_timestamp"]), tz=timezone.utc
                        )
                        staleness = calculate_staleness_minutes(data_timestamp)
                    except:
                        pass

        logger.info(f"{provider} - {endpoint} - BNB price retrieved, staleness: {staleness:.2f}m")

        return {
            "provider": provider,
            "category": category,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_timestamp": data_timestamp.isoformat(),
            "staleness_minutes": staleness,
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0),
        }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(logger, provider, "exception", error_msg, endpoint, exc_info=True)
        return {
            "provider": provider,
            "category": category,
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "staleness_minutes": None,
            "success": False,
            "error": error_msg,
            "error_type": "exception",
        }


async def get_tronscan_stats() -> Dict[str, Any]:
    """
    Get TRX network statistics from TronScan

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "TronScan"
    category = "blockchain_explorers"
    endpoint = "/system/status"

    logger.info(f"Fetching network stats from {provider}")

    try:
        client = get_client()
        provider_config = config.get_provider(provider)

        if not provider_config:
            error_msg = f"Provider {provider} not configured"
            log_error(logger, provider, "config_error", error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
            }

        # Build request URL
        url = f"{provider_config.endpoint_url}{endpoint}"
        headers = {}

        # Add API key if available
        if provider_config.requires_key and provider_config.api_key:
            headers["TRON-PRO-API-KEY"] = provider_config.api_key

        # Make request
        response = await client.get(
            url, headers=headers if headers else None, timeout=provider_config.timeout_ms // 1000
        )

        # Log request
        log_api_request(
            logger,
            provider,
            endpoint,
            response.get("response_time_ms", 0),
            "success" if response["success"] else "error",
            response.get("status_code"),
        )

        if not response["success"]:
            error_msg = response.get("error_message", "Unknown error")
            log_error(logger, provider, response.get("error_type", "unknown"), error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
                "error_type": response.get("error_type"),
            }

        # Extract data
        data = response["data"]

        # TronScan returns real-time data
        data_timestamp = datetime.now(timezone.utc)
        staleness = 0.0

        # Parse timestamp if available in response
        if isinstance(data, dict):
            # TronScan may include timestamp in various fields
            if "timestamp" in data:
                try:
                    data_timestamp = datetime.fromtimestamp(
                        int(data["timestamp"]) / 1000, tz=timezone.utc  # TronScan uses milliseconds
                    )
                    staleness = calculate_staleness_minutes(data_timestamp)
                except:
                    pass

        logger.info(
            f"{provider} - {endpoint} - Network stats retrieved, staleness: {staleness:.2f}m"
        )

        return {
            "provider": provider,
            "category": category,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_timestamp": data_timestamp.isoformat(),
            "staleness_minutes": staleness,
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0),
        }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(logger, provider, "exception", error_msg, endpoint, exc_info=True)
        return {
            "provider": provider,
            "category": category,
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "staleness_minutes": None,
            "success": False,
            "error": error_msg,
            "error_type": "exception",
        }


async def collect_explorer_data() -> List[Dict[str, Any]]:
    """
    Main function to collect blockchain explorer data from all sources

    Returns:
        List of results from all explorer data collectors
    """
    logger.info("Starting blockchain explorer data collection from all sources")

    # Run all collectors concurrently
    results = await asyncio.gather(
        get_etherscan_gas_price(),
        get_bscscan_bnb_price(),
        get_tronscan_stats(),
        return_exceptions=True,
    )

    # Process results
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Collector failed with exception: {str(result)}")
            processed_results.append(
                {
                    "provider": "Unknown",
                    "category": "blockchain_explorers",
                    "data": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "staleness_minutes": None,
                    "success": False,
                    "error": str(result),
                    "error_type": "exception",
                }
            )
        else:
            processed_results.append(result)

    # Log summary
    successful = sum(1 for r in processed_results if r.get("success", False))
    logger.info(
        f"Explorer data collection complete: {successful}/{len(processed_results)} successful"
    )

    return processed_results


class ExplorerDataCollector:
    """
    Explorer Data Collector class for WebSocket streaming interface
    Wraps the standalone explorer data collection functions
    """

    def __init__(self, config: Any = None):
        """
        Initialize the explorer data collector

        Args:
            config: Configuration object (optional, for compatibility)
        """
        self.config = config
        self.logger = logger

    async def collect(self) -> Dict[str, Any]:
        """
        Collect blockchain explorer data from all sources

        Returns:
            Dict with aggregated explorer data
        """
        results = await collect_explorer_data()

        # Aggregate data for WebSocket streaming
        aggregated = {
            "latest_block": None,
            "network_hashrate": None,
            "difficulty": None,
            "mempool_size": None,
            "transactions_count": None,
            "gas_prices": {},
            "sources": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for result in results:
            if result.get("success") and result.get("data"):
                provider = result.get("provider", "unknown")
                aggregated["sources"].append(provider)

                data = result["data"]

                # Parse gas price data
                if "result" in data and isinstance(data["result"], dict):
                    gas_data = data["result"]
                    if provider == "Etherscan":
                        aggregated["gas_prices"]["ethereum"] = {
                            "safe": gas_data.get("SafeGasPrice"),
                            "propose": gas_data.get("ProposeGasPrice"),
                            "fast": gas_data.get("FastGasPrice"),
                        }
                    elif provider == "BscScan":
                        aggregated["gas_prices"]["bsc"] = gas_data.get("result")

                # Parse network stats
                if provider == "TronScan" and "data" in data:
                    stats = data["data"]
                    aggregated["latest_block"] = stats.get("latestBlock")
                    aggregated["transactions_count"] = stats.get("totalTransaction")

        return aggregated


# Example usage
if __name__ == "__main__":

    async def main():
        results = await collect_explorer_data()

        print("\n=== Blockchain Explorer Data Collection Results ===")
        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Success: {result['success']}")
            print(f"Staleness: {result.get('staleness_minutes', 'N/A')} minutes")
            if result["success"]:
                print(f"Response Time: {result.get('response_time_ms', 0):.2f}ms")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

    asyncio.run(main())

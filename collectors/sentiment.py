"""
Sentiment Data Collectors
Fetches cryptocurrency sentiment data from Alternative.me Fear & Greed Index
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from utils.api_client import get_client
from utils.logger import setup_logger, log_api_request, log_error
from config import config

logger = setup_logger("sentiment_collector")


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


async def get_fear_greed_index() -> Dict[str, Any]:
    """
    Fetch current Fear & Greed Index from Alternative.me

    The Fear & Greed Index is a sentiment indicator for the cryptocurrency market.
    - 0-24: Extreme Fear
    - 25-49: Fear
    - 50-74: Greed
    - 75-100: Extreme Greed

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "AlternativeMe"
    category = "sentiment"
    endpoint = "/fng/"

    logger.info(f"Fetching Fear & Greed Index from {provider}")

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
                "error": error_msg
            }

        # Build request URL
        url = f"{provider_config.endpoint_url}{endpoint}"
        params = {
            "limit": "1",  # Get only the latest index
            "format": "json"
        }

        # Make request
        response = await client.get(url, params=params, timeout=provider_config.timeout_ms // 1000)

        # Log request
        log_api_request(
            logger,
            provider,
            endpoint,
            response.get("response_time_ms", 0),
            "success" if response["success"] else "error",
            response.get("status_code")
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
                "error_type": response.get("error_type")
            }

        # Extract data
        data = response["data"]

        # Parse timestamp from response
        data_timestamp = None
        if isinstance(data, dict) and "data" in data:
            data_list = data["data"]
            if isinstance(data_list, list) and len(data_list) > 0:
                index_data = data_list[0]
                if isinstance(index_data, dict) and "timestamp" in index_data:
                    try:
                        # Alternative.me returns Unix timestamp
                        data_timestamp = datetime.fromtimestamp(
                            int(index_data["timestamp"]),
                            tz=timezone.utc
                        )
                    except:
                        pass

        staleness = calculate_staleness_minutes(data_timestamp)

        # Extract index value and classification
        index_value = None
        index_classification = None
        if isinstance(data, dict) and "data" in data:
            data_list = data["data"]
            if isinstance(data_list, list) and len(data_list) > 0:
                index_data = data_list[0]
                if isinstance(index_data, dict):
                    index_value = index_data.get("value")
                    index_classification = index_data.get("value_classification")

        logger.info(
            f"{provider} - {endpoint} - Fear & Greed Index: {index_value} ({index_classification}), "
            f"staleness: {staleness:.2f}m" if staleness else "staleness: N/A"
        )

        return {
            "provider": provider,
            "category": category,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_timestamp": data_timestamp.isoformat() if data_timestamp else None,
            "staleness_minutes": staleness,
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0),
            "index_value": index_value,
            "index_classification": index_classification
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
            "error_type": "exception"
        }


async def collect_sentiment_data() -> List[Dict[str, Any]]:
    """
    Main function to collect sentiment data from all sources

    Currently collects from:
    - Alternative.me Fear & Greed Index

    Returns:
        List of results from all sentiment collectors
    """
    logger.info("Starting sentiment data collection from all sources")

    # Run all collectors concurrently
    results = await asyncio.gather(
        get_fear_greed_index(),
        return_exceptions=True
    )

    # Process results
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Collector failed with exception: {str(result)}")
            processed_results.append({
                "provider": "Unknown",
                "category": "sentiment",
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "staleness_minutes": None,
                "success": False,
                "error": str(result),
                "error_type": "exception"
            })
        else:
            processed_results.append(result)

    # Log summary
    successful = sum(1 for r in processed_results if r.get("success", False))
    logger.info(f"Sentiment data collection complete: {successful}/{len(processed_results)} successful")

    return processed_results


# Example usage
if __name__ == "__main__":
    async def main():
        results = await collect_sentiment_data()

        print("\n=== Sentiment Data Collection Results ===")
        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Success: {result['success']}")
            print(f"Staleness: {result.get('staleness_minutes', 'N/A')} minutes")
            if result['success']:
                print(f"Response Time: {result.get('response_time_ms', 0):.2f}ms")
                if result.get('index_value'):
                    print(f"Fear & Greed Index: {result['index_value']} ({result['index_classification']})")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

    asyncio.run(main())

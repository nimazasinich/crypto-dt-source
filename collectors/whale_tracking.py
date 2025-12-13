"""
Whale Tracking Collectors
Fetches whale transaction data from WhaleAlert, Arkham Intelligence, and other sources
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from utils.api_client import get_client
from utils.logger import setup_logger, log_api_request, log_error

logger = setup_logger("whale_tracking_collector")


async def get_whalealert_transactions(api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch recent large crypto transactions from WhaleAlert

    Args:
        api_key: WhaleAlert API key

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "WhaleAlert"
    category = "whale_tracking"
    endpoint = "/transactions"

    logger.info(f"Fetching whale transactions from {provider}")

    try:
        if not api_key:
            error_msg = f"API key required for {provider}"
            log_error(logger, provider, "missing_api_key", error_msg, endpoint)
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": error_msg,
                "error_type": "missing_api_key"
            }

        client = get_client()

        # WhaleAlert API endpoint
        url = "https://api.whale-alert.io/v1/transactions"

        # Get transactions from last hour
        now = int(datetime.now(timezone.utc).timestamp())
        start_time = now - 3600  # 1 hour ago

        params = {
            "api_key": api_key,
            "start": start_time,
            "limit": 100  # Max 100 transactions
        }

        # Make request
        response = await client.get(url, params=params, timeout=15)

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
                "success": False,
                "error": error_msg,
                "error_type": response.get("error_type")
            }

        # Extract data
        data = response["data"]

        # Process transactions
        whale_data = None
        if isinstance(data, dict) and "transactions" in data:
            transactions = data["transactions"]

            # Aggregate statistics
            total_value_usd = sum(tx.get("amount_usd", 0) for tx in transactions)
            symbols = set(tx.get("symbol", "unknown") for tx in transactions)

            whale_data = {
                "transaction_count": len(transactions),
                "total_value_usd": round(total_value_usd, 2),
                "unique_symbols": list(symbols),
                "time_range_hours": 1,
                "largest_tx": max(transactions, key=lambda x: x.get("amount_usd", 0)) if transactions else None,
                "transactions": transactions[:10]  # Keep only top 10 for brevity
            }

        logger.info(
            f"{provider} - {endpoint} - Retrieved {whale_data.get('transaction_count', 0)} transactions, "
            f"Total value: ${whale_data.get('total_value_usd', 0):,.0f}" if whale_data else "No data"
        )

        return {
            "provider": provider,
            "category": category,
            "data": whale_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0)
        }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(logger, provider, "exception", error_msg, endpoint, exc_info=True)
        return {
            "provider": provider,
            "category": category,
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": error_msg,
            "error_type": "exception"
        }


async def get_arkham_intel() -> Dict[str, Any]:
    """
    Fetch blockchain intelligence data from Arkham Intelligence

    Note: Arkham requires authentication and may not have a public API.
    This is a placeholder implementation that should be extended with proper API access.

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "Arkham"
    category = "whale_tracking"
    endpoint = "/intelligence"

    logger.info(f"Fetching intelligence data from {provider} (placeholder)")

    try:
        # Placeholder implementation
        # Arkham Intelligence may require special access or partnership
        # They provide wallet labeling, entity tracking, and transaction analysis

        placeholder_data = {
            "status": "placeholder",
            "message": "Arkham Intelligence API not yet implemented",
            "planned_features": [
                "Wallet address labeling",
                "Entity tracking and attribution",
                "Transaction flow analysis",
                "Dark web marketplace monitoring",
                "Exchange flow tracking"
            ],
            "note": "Requires Arkham API access or partnership"
        }

        logger.info(f"{provider} - {endpoint} - Placeholder data returned")

        return {
            "provider": provider,
            "category": category,
            "data": placeholder_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "error": None,
            "is_placeholder": True
        }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(logger, provider, "exception", error_msg, endpoint, exc_info=True)
        return {
            "provider": provider,
            "category": category,
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": error_msg,
            "error_type": "exception"
        }


async def get_clankapp_whales() -> Dict[str, Any]:
    """
    Fetch whale tracking data from ClankApp

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "ClankApp"
    category = "whale_tracking"
    endpoint = "/whales"

    logger.info(f"Fetching whale data from {provider}")

    try:
        client = get_client()

        # ClankApp public API (if available)
        # Note: This may require API key or may not have public endpoints
        url = "https://clankapp.com/api/v1/whales"

        # Make request
        response = await client.get(url, timeout=10)

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
            # If API is not available, return placeholder
            logger.warning(f"{provider} - API not available, returning placeholder")
            return {
                "provider": provider,
                "category": category,
                "data": {
                    "status": "placeholder",
                    "message": "ClankApp API not accessible or requires authentication",
                    "planned_features": [
                        "Whale wallet tracking",
                        "Large transaction alerts",
                        "Portfolio tracking"
                    ]
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": True,
                "error": None,
                "is_placeholder": True
            }

        # Extract data
        data = response["data"]

        logger.info(f"{provider} - {endpoint} - Data retrieved successfully")

        return {
            "provider": provider,
            "category": category,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0)
        }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(logger, provider, "exception", error_msg, endpoint, exc_info=True)
        return {
            "provider": provider,
            "category": category,
            "data": {
                "status": "placeholder",
                "message": f"ClankApp integration error: {str(e)}"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "error": None,
            "is_placeholder": True
        }


async def get_bitquery_whale_transactions() -> Dict[str, Any]:
    """
    Fetch large transactions using BitQuery GraphQL API

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "BitQuery"
    category = "whale_tracking"
    endpoint = "/graphql"

    logger.info(f"Fetching whale transactions from {provider}")

    try:
        client = get_client()

        # BitQuery GraphQL endpoint
        url = "https://graphql.bitquery.io"

        # GraphQL query for large transactions (>$100k)
        query = """
        {
          ethereum(network: ethereum) {
            transfers(
              amount: {gt: 100000}
              options: {limit: 10, desc: "amount"}
            ) {
              transaction {
                hash
              }
              amount
              currency {
                symbol
                name
              }
              sender {
                address
              }
              receiver {
                address
              }
              block {
                timestamp {
                  iso8601
                }
              }
            }
          }
        }
        """

        payload = {"query": query}
        headers = {"Content-Type": "application/json"}

        # Make request
        response = await client.post(url, json=payload, headers=headers, timeout=15)

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
            # Return placeholder if API fails
            logger.warning(f"{provider} - API request failed, returning placeholder")
            return {
                "provider": provider,
                "category": category,
                "data": {
                    "status": "placeholder",
                    "message": "BitQuery API requires authentication",
                    "planned_features": [
                        "Large transaction tracking via GraphQL",
                        "Multi-chain whale monitoring",
                        "Token transfer analytics"
                    ]
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": True,
                "error": None,
                "is_placeholder": True
            }

        # Extract data
        data = response["data"]

        whale_data = None
        if isinstance(data, dict) and "data" in data:
            transfers = data.get("data", {}).get("ethereum", {}).get("transfers", [])

            if transfers:
                total_value = sum(t.get("amount", 0) for t in transfers)

                whale_data = {
                    "transaction_count": len(transfers),
                    "total_value": round(total_value, 2),
                    "largest_transfers": transfers[:5]
                }

        logger.info(
            f"{provider} - {endpoint} - Retrieved {whale_data.get('transaction_count', 0)} large transactions"
            if whale_data else f"{provider} - {endpoint} - No data"
        )

        return {
            "provider": provider,
            "category": category,
            "data": whale_data or {"status": "no_data", "message": "No large transactions found"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0)
        }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(logger, provider, "exception", error_msg, endpoint, exc_info=True)
        return {
            "provider": provider,
            "category": category,
            "data": {
                "status": "placeholder",
                "message": f"BitQuery integration error: {str(e)}"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "error": None,
            "is_placeholder": True
        }


async def collect_whale_tracking_data(whalealert_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Main function to collect whale tracking data from all sources

    Args:
        whalealert_key: WhaleAlert API key

    Returns:
        List of results from all whale tracking collectors
    """
    logger.info("Starting whale tracking data collection from all sources")

    # Run all collectors concurrently
    results = await asyncio.gather(
        get_whalealert_transactions(whalealert_key),
        get_arkham_intel(),
        get_clankapp_whales(),
        get_bitquery_whale_transactions(),
        return_exceptions=True
    )

    # Process results
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Collector failed with exception: {str(result)}")
            processed_results.append({
                "provider": "Unknown",
                "category": "whale_tracking",
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(result),
                "error_type": "exception"
            })
        else:
            processed_results.append(result)

    # Log summary
    successful = sum(1 for r in processed_results if r.get("success", False))
    placeholder_count = sum(1 for r in processed_results if r.get("is_placeholder", False))

    logger.info(
        f"Whale tracking collection complete: {successful}/{len(processed_results)} successful "
        f"({placeholder_count} placeholders)"
    )

    return processed_results


class WhaleTrackingCollector:
    """
    Whale Tracking Collector class for WebSocket streaming interface
    Wraps the standalone whale tracking collection functions
    """

    def __init__(self, config: Any = None):
        """
        Initialize the whale tracking collector

        Args:
            config: Configuration object (optional, for compatibility)
        """
        self.config = config
        self.logger = logger

    async def collect(self) -> Dict[str, Any]:
        """
        Collect whale tracking data from all sources

        Returns:
            Dict with aggregated whale tracking data
        """
        import os
        whalealert_key = os.getenv("WHALEALERT_API_KEY")
        results = await collect_whale_tracking_data(whalealert_key)

        # Aggregate data for WebSocket streaming
        aggregated = {
            "large_transactions": [],
            "whale_wallets": [],
            "total_volume": 0,
            "alert_threshold": 1000000,  # $1M default threshold
            "alerts": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        for result in results:
            if result.get("success") and result.get("data"):
                provider = result.get("provider", "unknown")
                data = result["data"]

                # Skip placeholders
                if isinstance(data, dict) and data.get("status") == "placeholder":
                    continue

                # Parse WhaleAlert transactions
                if provider == "WhaleAlert" and isinstance(data, dict):
                    transactions = data.get("transactions", [])
                    for tx in transactions:
                        aggregated["large_transactions"].append({
                            "amount": tx.get("amount", 0),
                            "amount_usd": tx.get("amount_usd", 0),
                            "symbol": tx.get("symbol", "unknown"),
                            "from": tx.get("from", {}).get("owner", "unknown"),
                            "to": tx.get("to", {}).get("owner", "unknown"),
                            "timestamp": tx.get("timestamp"),
                            "source": provider
                        })
                    aggregated["total_volume"] += data.get("total_value_usd", 0)

                # Parse other sources
                elif isinstance(data, dict):
                    tx_count = data.get("transaction_count", 0)
                    total_value = data.get("total_value_usd", data.get("total_value", 0))
                    aggregated["total_volume"] += total_value

        return aggregated


# Example usage
if __name__ == "__main__":
    async def main():
        import os

        whalealert_key = os.getenv("WHALEALERT_API_KEY")

        results = await collect_whale_tracking_data(whalealert_key)

        print("\n=== Whale Tracking Data Collection Results ===")
        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Success: {result['success']}")
            print(f"Is Placeholder: {result.get('is_placeholder', False)}")

            if result['success']:
                data = result.get('data', {})
                if isinstance(data, dict):
                    if data.get('status') == 'placeholder':
                        print(f"Status: {data.get('message', 'N/A')}")
                    else:
                        print(f"Transaction Count: {data.get('transaction_count', 'N/A')}")
                        print(f"Total Value: ${data.get('total_value_usd', data.get('total_value', 0)):,.0f}")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

    asyncio.run(main())

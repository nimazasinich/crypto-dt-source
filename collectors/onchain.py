"""
On-Chain Analytics Collectors
Placeholder implementations for The Graph and Blockchair data collection

These collectors are designed to be extended with actual implementations
when on-chain data sources are integrated.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from utils.api_client import get_client
from utils.logger import setup_logger, log_api_request, log_error

logger = setup_logger("onchain_collector")


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


async def get_the_graph_data() -> Dict[str, Any]:
    """
    Fetch on-chain data from The Graph protocol - Uniswap V3 subgraph

    The Graph is a decentralized protocol for indexing and querying blockchain data.
    This implementation queries the Uniswap V3 subgraph for DEX metrics.

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "TheGraph"
    category = "onchain_analytics"
    endpoint = "/subgraphs/uniswap-v3"

    logger.info(f"Fetching on-chain data from {provider}")

    try:
        client = get_client()

        # Uniswap V3 subgraph endpoint
        url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

        # GraphQL query to get top pools and overall stats
        query = """
        {
          factories(first: 1) {
            totalVolumeUSD
            totalValueLockedUSD
            txCount
          }
          pools(first: 10, orderBy: totalValueLockedUSD, orderDirection: desc) {
            id
            token0 {
              symbol
            }
            token1 {
              symbol
            }
            totalValueLockedUSD
            volumeUSD
            txCount
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
        raw_data = response["data"]

        graph_data = None
        if isinstance(raw_data, dict) and "data" in raw_data:
            data = raw_data["data"]
            factories = data.get("factories", [])
            pools = data.get("pools", [])

            if factories:
                factory = factories[0]
                graph_data = {
                    "protocol": "Uniswap V3",
                    "total_volume_usd": float(factory.get("totalVolumeUSD", 0)),
                    "total_tvl_usd": float(factory.get("totalValueLockedUSD", 0)),
                    "total_transactions": int(factory.get("txCount", 0)),
                    "top_pools": [
                        {
                            "pair": f"{pool.get('token0', {}).get('symbol', '?')}/{pool.get('token1', {}).get('symbol', '?')}",
                            "tvl_usd": float(pool.get("totalValueLockedUSD", 0)),
                            "volume_usd": float(pool.get("volumeUSD", 0)),
                            "tx_count": int(pool.get("txCount", 0)),
                        }
                        for pool in pools
                    ],
                }

        data_timestamp = datetime.now(timezone.utc)
        staleness = calculate_staleness_minutes(data_timestamp)

        logger.info(
            f"{provider} - {endpoint} - TVL: ${graph_data.get('total_tvl_usd', 0):,.0f}"
            if graph_data
            else f"{provider} - {endpoint} - No data"
        )

        return {
            "provider": provider,
            "category": category,
            "data": graph_data,
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


async def get_blockchair_data() -> Dict[str, Any]:
    """
    Fetch blockchain statistics from Blockchair

    Blockchair is a blockchain explorer and analytics platform.
    This implementation fetches Bitcoin and Ethereum network statistics.

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "Blockchair"
    category = "onchain_analytics"
    endpoint = "/stats"

    logger.info(f"Fetching blockchain stats from {provider}")

    try:
        client = get_client()

        # Fetch stats for BTC and ETH
        btc_url = "https://api.blockchair.com/bitcoin/stats"
        eth_url = "https://api.blockchair.com/ethereum/stats"

        # Make concurrent requests
        btc_response, eth_response = await asyncio.gather(
            client.get(btc_url, timeout=10), client.get(eth_url, timeout=10), return_exceptions=True
        )

        # Log requests
        if not isinstance(btc_response, Exception):
            log_api_request(
                logger,
                provider,
                f"{endpoint}/bitcoin",
                btc_response.get("response_time_ms", 0),
                "success" if btc_response["success"] else "error",
                btc_response.get("status_code"),
            )

        if not isinstance(eth_response, Exception):
            log_api_request(
                logger,
                provider,
                f"{endpoint}/ethereum",
                eth_response.get("response_time_ms", 0),
                "success" if eth_response["success"] else "error",
                eth_response.get("status_code"),
            )

        # Process Bitcoin data
        btc_data = None
        if not isinstance(btc_response, Exception) and btc_response.get("success"):
            raw_btc = btc_response.get("data", {})
            if isinstance(raw_btc, dict) and "data" in raw_btc:
                btc_stats = raw_btc["data"]
                btc_data = {
                    "blocks": btc_stats.get("blocks"),
                    "transactions": btc_stats.get("transactions"),
                    "market_price_usd": btc_stats.get("market_price_usd"),
                    "hashrate_24h": btc_stats.get("hashrate_24h"),
                    "difficulty": btc_stats.get("difficulty"),
                    "mempool_size": btc_stats.get("mempool_size"),
                    "mempool_transactions": btc_stats.get("mempool_transactions"),
                }

        # Process Ethereum data
        eth_data = None
        if not isinstance(eth_response, Exception) and eth_response.get("success"):
            raw_eth = eth_response.get("data", {})
            if isinstance(raw_eth, dict) and "data" in raw_eth:
                eth_stats = raw_eth["data"]
                eth_data = {
                    "blocks": eth_stats.get("blocks"),
                    "transactions": eth_stats.get("transactions"),
                    "market_price_usd": eth_stats.get("market_price_usd"),
                    "hashrate_24h": eth_stats.get("hashrate_24h"),
                    "difficulty": eth_stats.get("difficulty"),
                    "mempool_size": eth_stats.get("mempool_tps"),
                }

        blockchair_data = {"bitcoin": btc_data, "ethereum": eth_data}

        data_timestamp = datetime.now(timezone.utc)
        staleness = calculate_staleness_minutes(data_timestamp)

        logger.info(
            f"{provider} - {endpoint} - BTC blocks: {btc_data.get('blocks', 'N/A') if btc_data else 'N/A'}, "
            f"ETH blocks: {eth_data.get('blocks', 'N/A') if eth_data else 'N/A'}"
        )

        return {
            "provider": provider,
            "category": category,
            "data": blockchair_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_timestamp": data_timestamp.isoformat(),
            "staleness_minutes": staleness,
            "success": True,
            "error": None,
            "response_time_ms": (
                btc_response.get("response_time_ms", 0)
                if not isinstance(btc_response, Exception)
                else 0
            ),
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


async def get_glassnode_metrics() -> Dict[str, Any]:
    """
    Fetch advanced on-chain metrics from Glassnode (placeholder)

    Glassnode provides advanced on-chain analytics and metrics.
    This is a placeholder implementation that should be extended with:
    - NUPL (Net Unrealized Profit/Loss)
    - SOPR (Spent Output Profit Ratio)
    - Exchange flows
    - Whale transactions
    - Active addresses
    - Realized cap

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "Glassnode"
    category = "onchain_analytics"
    endpoint = "/metrics"

    logger.info(f"Fetching on-chain metrics from {provider} (placeholder)")

    try:
        # Placeholder implementation
        # Glassnode API requires API key and has extensive metrics
        # Example metrics: NUPL, SOPR, Exchange Flows, Miner Revenue, etc.

        placeholder_data = {
            "status": "placeholder",
            "message": "Glassnode integration not yet implemented",
            "planned_metrics": [
                "NUPL - Net Unrealized Profit/Loss",
                "SOPR - Spent Output Profit Ratio",
                "Exchange Net Flows",
                "Whale Transaction Count",
                "Active Addresses",
                "Realized Cap",
                "MVRV Ratio",
                "Supply in Profit",
                "Long/Short Term Holder Supply",
            ],
            "note": "Requires Glassnode API key for access",
        }

        data_timestamp = datetime.now(timezone.utc)
        staleness = 0.0

        logger.info(f"{provider} - {endpoint} - Placeholder data returned")

        return {
            "provider": provider,
            "category": category,
            "data": placeholder_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_timestamp": data_timestamp.isoformat(),
            "staleness_minutes": staleness,
            "success": True,
            "error": None,
            "is_placeholder": True,
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


async def collect_onchain_data() -> List[Dict[str, Any]]:
    """
    Main function to collect on-chain analytics data from all sources

    Currently returns placeholder implementations for:
    - The Graph (GraphQL-based blockchain data)
    - Blockchair (blockchain explorer and stats)
    - Glassnode (advanced on-chain metrics)

    Returns:
        List of results from all on-chain collectors
    """
    logger.info("Starting on-chain data collection from all sources (placeholder)")

    # Run all collectors concurrently
    results = await asyncio.gather(
        get_the_graph_data(), get_blockchair_data(), get_glassnode_metrics(), return_exceptions=True
    )

    # Process results
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Collector failed with exception: {str(result)}")
            processed_results.append(
                {
                    "provider": "Unknown",
                    "category": "onchain_analytics",
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
    placeholder_count = sum(1 for r in processed_results if r.get("is_placeholder", False))

    logger.info(
        f"On-chain data collection complete: {successful}/{len(processed_results)} successful "
        f"({placeholder_count} placeholders)"
    )

    return processed_results


class OnChainCollector:
    """
    On-Chain Analytics Collector class for WebSocket streaming interface
    Wraps the standalone on-chain data collection functions
    """

    def __init__(self, config: Any = None):
        """
        Initialize the on-chain collector

        Args:
            config: Configuration object (optional, for compatibility)
        """
        self.config = config
        self.logger = logger

    async def collect(self) -> Dict[str, Any]:
        """
        Collect on-chain analytics data from all sources

        Returns:
            Dict with aggregated on-chain data
        """
        results = await collect_onchain_data()

        # Aggregate data for WebSocket streaming
        aggregated = {
            "active_addresses": None,
            "transaction_count": None,
            "total_fees": None,
            "gas_price": None,
            "network_utilization": None,
            "contract_events": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for result in results:
            if result.get("success") and result.get("data"):
                provider = result.get("provider", "unknown")
                data = result["data"]

                # Skip placeholders but still return basic structure
                if isinstance(data, dict) and data.get("status") == "placeholder":
                    continue

                # Parse data from various providers (when implemented)
                # Currently all are placeholders, so this will be empty
                pass

        return aggregated


# Example usage
if __name__ == "__main__":

    async def main():
        results = await collect_onchain_data()

        print("\n=== On-Chain Data Collection Results ===")
        print("Note: These are placeholder implementations")
        print()

        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Success: {result['success']}")
            print(f"Is Placeholder: {result.get('is_placeholder', False)}")
            if result["success"]:
                data = result.get("data", {})
                if isinstance(data, dict):
                    print(f"Status: {data.get('status', 'N/A')}")
                    print(f"Message: {data.get('message', 'N/A')}")
                    if "planned_features" in data:
                        print(f"Planned Features: {len(data['planned_features'])}")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

        print("\n" + "=" * 50)
        print("To implement these collectors:")
        print("1. The Graph: Add GraphQL queries for specific subgraphs")
        print("2. Blockchair: Add API key and implement endpoint calls")
        print("3. Glassnode: Add API key and implement metrics fetching")
        print("=" * 50)

    asyncio.run(main())

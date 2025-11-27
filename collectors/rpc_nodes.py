"""
RPC Node Collectors
Fetches blockchain data from RPC endpoints (Infura, Alchemy, Ankr, etc.)
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from utils.api_client import get_client
from utils.logger import log_api_request, log_error, setup_logger

logger = setup_logger("rpc_collector")


async def get_eth_block_number(
    provider: str, rpc_url: str, api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch latest Ethereum block number from RPC endpoint

    Args:
        provider: Provider name (e.g., "Infura", "Alchemy")
        rpc_url: RPC endpoint URL
        api_key: Optional API key to append to URL

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    category = "rpc_nodes"
    endpoint = "eth_blockNumber"

    logger.info(f"Fetching block number from {provider}")

    try:
        client = get_client()

        # Build URL with API key if provided
        url = f"{rpc_url}/{api_key}" if api_key else rpc_url

        # JSON-RPC request payload
        payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}

        headers = {"Content-Type": "application/json"}

        # Make request
        response = await client.post(url, json=payload, headers=headers, timeout=10)

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
                "success": False,
                "error": error_msg,
                "error_type": response.get("error_type"),
            }

        # Extract data
        data = response["data"]

        # Parse hex block number
        block_data = None
        if isinstance(data, dict) and "result" in data:
            hex_block = data["result"]
            block_number = int(hex_block, 16) if hex_block else 0
            block_data = {"block_number": block_number, "hex": hex_block, "chain": "ethereum"}

        logger.info(f"{provider} - {endpoint} - Block: {block_data.get('block_number', 'N/A')}")

        return {
            "provider": provider,
            "category": category,
            "data": block_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "success": False,
            "error": error_msg,
            "error_type": "exception",
        }


async def get_eth_gas_price(
    provider: str, rpc_url: str, api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch current gas price from RPC endpoint

    Args:
        provider: Provider name
        rpc_url: RPC endpoint URL
        api_key: Optional API key

    Returns:
        Dict with gas price data
    """
    category = "rpc_nodes"
    endpoint = "eth_gasPrice"

    logger.info(f"Fetching gas price from {provider}")

    try:
        client = get_client()
        url = f"{rpc_url}/{api_key}" if api_key else rpc_url

        payload = {"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1}

        headers = {"Content-Type": "application/json"}
        response = await client.post(url, json=payload, headers=headers, timeout=10)

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
                "success": False,
                "error": error_msg,
                "error_type": response.get("error_type"),
            }

        data = response["data"]
        gas_data = None

        if isinstance(data, dict) and "result" in data:
            hex_gas = data["result"]
            gas_wei = int(hex_gas, 16) if hex_gas else 0
            gas_gwei = gas_wei / 1e9

            gas_data = {
                "gas_price_wei": gas_wei,
                "gas_price_gwei": round(gas_gwei, 2),
                "hex": hex_gas,
                "chain": "ethereum",
            }

        logger.info(f"{provider} - {endpoint} - Gas: {gas_data.get('gas_price_gwei', 'N/A')} Gwei")

        return {
            "provider": provider,
            "category": category,
            "data": gas_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "success": False,
            "error": error_msg,
            "error_type": "exception",
        }


async def get_eth_chain_id(
    provider: str, rpc_url: str, api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch chain ID from RPC endpoint

    Args:
        provider: Provider name
        rpc_url: RPC endpoint URL
        api_key: Optional API key

    Returns:
        Dict with chain ID data
    """
    category = "rpc_nodes"
    endpoint = "eth_chainId"

    try:
        client = get_client()
        url = f"{rpc_url}/{api_key}" if api_key else rpc_url

        payload = {"jsonrpc": "2.0", "method": "eth_chainId", "params": [], "id": 1}

        headers = {"Content-Type": "application/json"}
        response = await client.post(url, json=payload, headers=headers, timeout=10)

        if not response["success"]:
            error_msg = response.get("error_message", "Unknown error")
            return {
                "provider": provider,
                "category": category,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": error_msg,
            }

        data = response["data"]
        chain_data = None

        if isinstance(data, dict) and "result" in data:
            hex_chain = data["result"]
            chain_id = int(hex_chain, 16) if hex_chain else 0

            # Map chain IDs to names
            chain_names = {
                1: "Ethereum Mainnet",
                3: "Ropsten",
                4: "Rinkeby",
                5: "Goerli",
                11155111: "Sepolia",
                56: "BSC Mainnet",
                97: "BSC Testnet",
                137: "Polygon Mainnet",
                80001: "Mumbai Testnet",
            }

            chain_data = {
                "chain_id": chain_id,
                "chain_name": chain_names.get(chain_id, f"Unknown (ID: {chain_id})"),
                "hex": hex_chain,
            }

        return {
            "provider": provider,
            "category": category,
            "data": chain_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0),
        }

    except Exception as e:
        return {
            "provider": provider,
            "category": category,
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": str(e),
            "error_type": "exception",
        }


async def collect_infura_data(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Collect data from Infura RPC endpoints

    Args:
        api_key: Infura project ID

    Returns:
        List of results from Infura endpoints
    """
    provider = "Infura"
    rpc_url = "https://mainnet.infura.io/v3"

    if not api_key:
        logger.warning(f"{provider} - No API key provided, skipping")
        return [
            {
                "provider": provider,
                "category": "rpc_nodes",
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": "API key required",
                "error_type": "missing_api_key",
            }
        ]

    logger.info(f"Starting {provider} data collection")

    results = await asyncio.gather(
        get_eth_block_number(provider, rpc_url, api_key),
        get_eth_gas_price(provider, rpc_url, api_key),
        get_eth_chain_id(provider, rpc_url, api_key),
        return_exceptions=True,
    )

    processed = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"{provider} - Collector failed: {str(result)}")
            processed.append(
                {
                    "provider": provider,
                    "category": "rpc_nodes",
                    "data": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": False,
                    "error": str(result),
                    "error_type": "exception",
                }
            )
        else:
            processed.append(result)

    successful = sum(1 for r in processed if r.get("success", False))
    logger.info(f"{provider} - Collection complete: {successful}/{len(processed)} successful")

    return processed


async def collect_alchemy_data(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Collect data from Alchemy RPC endpoints

    Args:
        api_key: Alchemy API key

    Returns:
        List of results from Alchemy endpoints
    """
    provider = "Alchemy"
    rpc_url = "https://eth-mainnet.g.alchemy.com/v2"

    if not api_key:
        logger.warning(f"{provider} - No API key provided, using free tier")
        # Alchemy has a public demo endpoint
        api_key = "demo"

    logger.info(f"Starting {provider} data collection")

    results = await asyncio.gather(
        get_eth_block_number(provider, rpc_url, api_key),
        get_eth_gas_price(provider, rpc_url, api_key),
        get_eth_chain_id(provider, rpc_url, api_key),
        return_exceptions=True,
    )

    processed = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"{provider} - Collector failed: {str(result)}")
            processed.append(
                {
                    "provider": provider,
                    "category": "rpc_nodes",
                    "data": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": False,
                    "error": str(result),
                    "error_type": "exception",
                }
            )
        else:
            processed.append(result)

    successful = sum(1 for r in processed if r.get("success", False))
    logger.info(f"{provider} - Collection complete: {successful}/{len(processed)} successful")

    return processed


async def collect_ankr_data() -> List[Dict[str, Any]]:
    """
    Collect data from Ankr public RPC endpoints (no key required)

    Returns:
        List of results from Ankr endpoints
    """
    provider = "Ankr"
    rpc_url = "https://rpc.ankr.com/eth"

    logger.info(f"Starting {provider} data collection")

    results = await asyncio.gather(
        get_eth_block_number(provider, rpc_url),
        get_eth_gas_price(provider, rpc_url),
        get_eth_chain_id(provider, rpc_url),
        return_exceptions=True,
    )

    processed = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"{provider} - Collector failed: {str(result)}")
            processed.append(
                {
                    "provider": provider,
                    "category": "rpc_nodes",
                    "data": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": False,
                    "error": str(result),
                    "error_type": "exception",
                }
            )
        else:
            processed.append(result)

    successful = sum(1 for r in processed if r.get("success", False))
    logger.info(f"{provider} - Collection complete: {successful}/{len(processed)} successful")

    return processed


async def collect_public_rpc_data() -> List[Dict[str, Any]]:
    """
    Collect data from free public RPC endpoints

    Returns:
        List of results from public endpoints
    """
    logger.info("Starting public RPC data collection")

    public_rpcs = [
        ("Cloudflare", "https://cloudflare-eth.com"),
        ("PublicNode", "https://ethereum.publicnode.com"),
        ("LlamaNodes", "https://eth.llamarpc.com"),
    ]

    all_results = []

    for provider, rpc_url in public_rpcs:
        results = await asyncio.gather(
            get_eth_block_number(provider, rpc_url),
            get_eth_gas_price(provider, rpc_url),
            return_exceptions=True,
        )

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"{provider} - Collector failed: {str(result)}")
                all_results.append(
                    {
                        "provider": provider,
                        "category": "rpc_nodes",
                        "data": None,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "success": False,
                        "error": str(result),
                        "error_type": "exception",
                    }
                )
            else:
                all_results.append(result)

    successful = sum(1 for r in all_results if r.get("success", False))
    logger.info(f"Public RPC collection complete: {successful}/{len(all_results)} successful")

    return all_results


async def collect_rpc_data(
    infura_key: Optional[str] = None, alchemy_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Main function to collect RPC data from all sources

    Args:
        infura_key: Infura project ID
        alchemy_key: Alchemy API key

    Returns:
        List of results from all RPC collectors
    """
    logger.info("Starting RPC data collection from all sources")

    # Collect from all providers
    all_results = []

    # Infura (requires key)
    if infura_key:
        infura_results = await collect_infura_data(infura_key)
        all_results.extend(infura_results)

    # Alchemy (has free tier)
    alchemy_results = await collect_alchemy_data(alchemy_key)
    all_results.extend(alchemy_results)

    # Ankr (free, no key needed)
    ankr_results = await collect_ankr_data()
    all_results.extend(ankr_results)

    # Public RPCs (free)
    public_results = await collect_public_rpc_data()
    all_results.extend(public_results)

    # Log summary
    successful = sum(1 for r in all_results if r.get("success", False))
    logger.info(f"RPC data collection complete: {successful}/{len(all_results)} successful")

    return all_results


class RPCNodeCollector:
    """
    RPC Node Collector class for WebSocket streaming interface
    Wraps the standalone RPC node collection functions
    """

    def __init__(self, config: Any = None):
        """
        Initialize the RPC node collector

        Args:
            config: Configuration object (optional, for compatibility)
        """
        self.config = config
        self.logger = logger

    async def collect(self) -> Dict[str, Any]:
        """
        Collect RPC node data from all sources

        Returns:
            Dict with aggregated RPC node data
        """
        import os

        infura_key = os.getenv("INFURA_API_KEY")
        alchemy_key = os.getenv("ALCHEMY_API_KEY")
        results = await collect_rpc_data(infura_key, alchemy_key)

        # Aggregate data for WebSocket streaming
        aggregated = {
            "nodes": [],
            "active_nodes": 0,
            "total_nodes": 0,
            "average_latency": 0,
            "events": [],
            "block_number": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        total_latency = 0
        latency_count = 0

        for result in results:
            aggregated["total_nodes"] += 1

            if result.get("success"):
                aggregated["active_nodes"] += 1
                provider = result.get("provider", "unknown")
                response_time = result.get("response_time_ms", 0)
                data = result.get("data", {})

                # Track latency
                if response_time:
                    total_latency += response_time
                    latency_count += 1

                # Add node info
                node_info = {
                    "provider": provider,
                    "response_time_ms": response_time,
                    "status": "active",
                    "data": data,
                }

                # Extract block number
                if "result" in data and isinstance(data["result"], str):
                    try:
                        block_number = int(data["result"], 16)
                        node_info["block_number"] = block_number
                        if (
                            aggregated["block_number"] is None
                            or block_number > aggregated["block_number"]
                        ):
                            aggregated["block_number"] = block_number
                    except:
                        pass

                aggregated["nodes"].append(node_info)

        # Calculate average latency
        if latency_count > 0:
            aggregated["average_latency"] = total_latency / latency_count

        return aggregated


# Example usage
if __name__ == "__main__":

    async def main():
        import os

        infura_key = os.getenv("INFURA_API_KEY")
        alchemy_key = os.getenv("ALCHEMY_API_KEY")

        results = await collect_rpc_data(infura_key, alchemy_key)

        print("\n=== RPC Data Collection Results ===")
        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Success: {result['success']}")
            if result["success"]:
                print(f"Response Time: {result.get('response_time_ms', 0):.2f}ms")
                data = result.get("data", {})
                if data:
                    print(f"Data: {data}")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

    asyncio.run(main())

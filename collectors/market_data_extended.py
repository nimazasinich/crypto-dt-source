"""
Extended Market Data Collectors
Fetches data from Coinpaprika, DefiLlama, Messari, CoinCap, and other market data sources
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from utils.api_client import get_client
from utils.logger import setup_logger, log_api_request, log_error

logger = setup_logger("market_data_extended_collector")


async def get_coinpaprika_tickers() -> Dict[str, Any]:
    """
    Fetch ticker data from Coinpaprika (free, no key required)

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "Coinpaprika"
    category = "market_data"
    endpoint = "/tickers"

    logger.info(f"Fetching tickers from {provider}")

    try:
        client = get_client()

        # Coinpaprika API (free, no key needed)
        url = "https://api.coinpaprika.com/v1/tickers"

        params = {
            "quotes": "USD",
            "limit": 100
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

        # Process top coins
        market_data = None
        if isinstance(data, list):
            top_10 = data[:10]
            total_market_cap = sum(coin.get("quotes", {}).get("USD", {}).get("market_cap", 0) for coin in top_10)

            market_data = {
                "total_coins": len(data),
                "top_10_market_cap": round(total_market_cap, 2),
                "top_10_coins": [
                    {
                        "symbol": coin.get("symbol"),
                        "name": coin.get("name"),
                        "price": coin.get("quotes", {}).get("USD", {}).get("price"),
                        "market_cap": coin.get("quotes", {}).get("USD", {}).get("market_cap"),
                        "volume_24h": coin.get("quotes", {}).get("USD", {}).get("volume_24h"),
                        "percent_change_24h": coin.get("quotes", {}).get("USD", {}).get("percent_change_24h")
                    }
                    for coin in top_10
                ]
            }

        logger.info(f"{provider} - {endpoint} - Retrieved {len(data) if isinstance(data, list) else 0} tickers")

        return {
            "provider": provider,
            "category": category,
            "data": market_data,
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


async def get_defillama_tvl() -> Dict[str, Any]:
    """
    Fetch DeFi Total Value Locked from DefiLlama (free, no key required)

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "DefiLlama"
    category = "defi_data"
    endpoint = "/tvl"

    logger.info(f"Fetching TVL data from {provider}")

    try:
        client = get_client()

        # DefiLlama API (free, no key needed)
        url = "https://api.llama.fi/v2/protocols"

        # Make request
        response = await client.get(url, timeout=15)

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

        # Process protocols
        tvl_data = None
        if isinstance(data, list):
            # Sort by TVL
            sorted_protocols = sorted(data, key=lambda x: x.get("tvl", 0), reverse=True)
            top_20 = sorted_protocols[:20]

            total_tvl = sum(p.get("tvl", 0) for p in data)

            tvl_data = {
                "total_protocols": len(data),
                "total_tvl": round(total_tvl, 2),
                "top_20_protocols": [
                    {
                        "name": p.get("name"),
                        "symbol": p.get("symbol"),
                        "tvl": round(p.get("tvl", 0), 2),
                        "change_1d": p.get("change_1d"),
                        "change_7d": p.get("change_7d"),
                        "chains": p.get("chains", [])[:3]  # Top 3 chains
                    }
                    for p in top_20
                ]
            }

        logger.info(
            f"{provider} - {endpoint} - Total TVL: ${tvl_data.get('total_tvl', 0):,.0f}"
            if tvl_data else f"{provider} - {endpoint} - No data"
        )

        return {
            "provider": provider,
            "category": category,
            "data": tvl_data,
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


async def get_coincap_assets() -> Dict[str, Any]:
    """
    Fetch asset data from CoinCap (free, no key required)

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "CoinCap"
    category = "market_data"
    endpoint = "/assets"

    logger.info(f"Fetching assets from {provider}")

    try:
        client = get_client()

        # CoinCap API (free, no key needed)
        url = "https://api.coincap.io/v2/assets"

        params = {"limit": 50}

        # Make request
        response = await client.get(url, params=params, timeout=10)

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
        raw_data = response["data"]

        # Process assets
        asset_data = None
        if isinstance(raw_data, dict) and "data" in raw_data:
            assets = raw_data["data"]

            top_10 = assets[:10] if isinstance(assets, list) else []

            asset_data = {
                "total_assets": len(assets) if isinstance(assets, list) else 0,
                "top_10_assets": [
                    {
                        "symbol": asset.get("symbol"),
                        "name": asset.get("name"),
                        "price_usd": float(asset.get("priceUsd", 0)),
                        "market_cap_usd": float(asset.get("marketCapUsd", 0)),
                        "volume_24h_usd": float(asset.get("volumeUsd24Hr", 0)),
                        "change_percent_24h": float(asset.get("changePercent24Hr", 0))
                    }
                    for asset in top_10
                ]
            }

        logger.info(f"{provider} - {endpoint} - Retrieved {asset_data.get('total_assets', 0)} assets")

        return {
            "provider": provider,
            "category": category,
            "data": asset_data,
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


async def get_messari_assets(api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch asset data from Messari

    Args:
        api_key: Messari API key (optional, has free tier)

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "Messari"
    category = "market_data"
    endpoint = "/assets"

    logger.info(f"Fetching assets from {provider}")

    try:
        client = get_client()

        # Messari API
        url = "https://data.messari.io/api/v1/assets"

        params = {"limit": 20}

        headers = {}
        if api_key:
            headers["x-messari-api-key"] = api_key

        # Make request
        response = await client.get(url, params=params, headers=headers, timeout=15)

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
        raw_data = response["data"]

        # Process assets
        asset_data = None
        if isinstance(raw_data, dict) and "data" in raw_data:
            assets = raw_data["data"]

            asset_data = {
                "total_assets": len(assets) if isinstance(assets, list) else 0,
                "assets": [
                    {
                        "symbol": asset.get("symbol"),
                        "name": asset.get("name"),
                        "slug": asset.get("slug"),
                        "metrics": {
                            "market_cap": asset.get("metrics", {}).get("marketcap", {}).get("current_marketcap_usd"),
                            "volume_24h": asset.get("metrics", {}).get("market_data", {}).get("volume_last_24_hours"),
                            "price": asset.get("metrics", {}).get("market_data", {}).get("price_usd")
                        }
                    }
                    for asset in assets[:10]
                ] if isinstance(assets, list) else []
            }

        logger.info(f"{provider} - {endpoint} - Retrieved {asset_data.get('total_assets', 0)} assets")

        return {
            "provider": provider,
            "category": category,
            "data": asset_data,
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


async def get_cryptocompare_toplist() -> Dict[str, Any]:
    """
    Fetch top cryptocurrencies from CryptoCompare (free tier available)

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "CryptoCompare"
    category = "market_data"
    endpoint = "/top/totalvolfull"

    logger.info(f"Fetching top list from {provider}")

    try:
        client = get_client()

        # CryptoCompare API
        url = "https://min-api.cryptocompare.com/data/top/totalvolfull"

        params = {
            "limit": 20,
            "tsym": "USD"
        }

        # Make request
        response = await client.get(url, params=params, timeout=10)

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
        raw_data = response["data"]

        # Process data
        toplist_data = None
        if isinstance(raw_data, dict) and "Data" in raw_data:
            coins = raw_data["Data"]

            toplist_data = {
                "total_coins": len(coins) if isinstance(coins, list) else 0,
                "top_coins": [
                    {
                        "symbol": coin.get("CoinInfo", {}).get("Name"),
                        "name": coin.get("CoinInfo", {}).get("FullName"),
                        "price": coin.get("RAW", {}).get("USD", {}).get("PRICE"),
                        "market_cap": coin.get("RAW", {}).get("USD", {}).get("MKTCAP"),
                        "volume_24h": coin.get("RAW", {}).get("USD", {}).get("VOLUME24HOUR"),
                        "change_24h": coin.get("RAW", {}).get("USD", {}).get("CHANGEPCT24HOUR")
                    }
                    for coin in (coins[:10] if isinstance(coins, list) else [])
                ]
            }

        logger.info(f"{provider} - {endpoint} - Retrieved {toplist_data.get('total_coins', 0)} coins")

        return {
            "provider": provider,
            "category": category,
            "data": toplist_data,
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


async def collect_extended_market_data(messari_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Main function to collect extended market data from all sources

    Args:
        messari_key: Optional Messari API key

    Returns:
        List of results from all extended market data collectors
    """
    logger.info("Starting extended market data collection from all sources")

    # Run all collectors concurrently
    results = await asyncio.gather(
        get_coinpaprika_tickers(),
        get_defillama_tvl(),
        get_coincap_assets(),
        get_messari_assets(messari_key),
        get_cryptocompare_toplist(),
        return_exceptions=True
    )

    # Process results
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Collector failed with exception: {str(result)}")
            processed_results.append({
                "provider": "Unknown",
                "category": "market_data",
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
    logger.info(f"Extended market data collection complete: {successful}/{len(processed_results)} successful")

    return processed_results


# Example usage
if __name__ == "__main__":
    async def main():
        import os

        messari_key = os.getenv("MESSARI_API_KEY")

        results = await collect_extended_market_data(messari_key)

        print("\n=== Extended Market Data Collection Results ===")
        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Category: {result['category']}")
            print(f"Success: {result['success']}")

            if result['success']:
                print(f"Response Time: {result.get('response_time_ms', 0):.2f}ms")
                data = result.get('data', {})
                if data:
                    if 'total_tvl' in data:
                        print(f"Total TVL: ${data['total_tvl']:,.0f}")
                    elif 'total_assets' in data:
                        print(f"Total Assets: {data['total_assets']}")
                    elif 'total_coins' in data:
                        print(f"Total Coins: {data['total_coins']}")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

    asyncio.run(main())

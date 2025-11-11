"""
Market Data Collectors
Fetches cryptocurrency market data from CoinGecko, CoinMarketCap, and Binance
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from utils.api_client import get_client
from utils.logger import setup_logger, log_api_request, log_error
from config import config

logger = setup_logger("market_data_collector")


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


async def get_coingecko_simple_price() -> Dict[str, Any]:
    """
    Fetch BTC, ETH, BNB prices from CoinGecko simple/price endpoint

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "CoinGecko"
    category = "market_data"
    endpoint = "/simple/price"

    logger.info(f"Fetching simple price from {provider}")

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
            "ids": "bitcoin,ethereum,binancecoin",
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_last_updated_at": "true"
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

        # Parse timestamps from response
        data_timestamp = None
        if isinstance(data, dict):
            # CoinGecko returns last_updated_at as Unix timestamp
            for coin_data in data.values():
                if isinstance(coin_data, dict) and "last_updated_at" in coin_data:
                    data_timestamp = datetime.fromtimestamp(
                        coin_data["last_updated_at"],
                        tz=timezone.utc
                    )
                    break

        staleness = calculate_staleness_minutes(data_timestamp)

        logger.info(
            f"{provider} - {endpoint} - Retrieved {len(data) if isinstance(data, dict) else 0} coins, "
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
            "staleness_minutes": None,
            "success": False,
            "error": error_msg,
            "error_type": "exception"
        }


async def get_coinmarketcap_quotes() -> Dict[str, Any]:
    """
    Fetch BTC, ETH, BNB market data from CoinMarketCap quotes endpoint

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "CoinMarketCap"
    category = "market_data"
    endpoint = "/cryptocurrency/quotes/latest"

    logger.info(f"Fetching quotes from {provider}")

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
                "error_type": "missing_api_key"
            }

        # Build request
        url = f"{provider_config.endpoint_url}{endpoint}"
        headers = {
            "X-CMC_PRO_API_KEY": provider_config.api_key,
            "Accept": "application/json"
        }
        params = {
            "symbol": "BTC,ETH,BNB",
            "convert": "USD"
        }

        # Make request
        response = await client.get(
            url,
            headers=headers,
            params=params,
            timeout=provider_config.timeout_ms // 1000
        )

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
            # CoinMarketCap response structure
            for coin_data in data["data"].values():
                if isinstance(coin_data, dict) and "quote" in coin_data:
                    quote = coin_data.get("quote", {}).get("USD", {})
                    if "last_updated" in quote:
                        try:
                            data_timestamp = datetime.fromisoformat(
                                quote["last_updated"].replace("Z", "+00:00")
                            )
                            break
                        except:
                            pass

        staleness = calculate_staleness_minutes(data_timestamp)

        coin_count = len(data.get("data", {})) if isinstance(data, dict) else 0
        logger.info(
            f"{provider} - {endpoint} - Retrieved {coin_count} coins, "
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
            "staleness_minutes": None,
            "success": False,
            "error": error_msg,
            "error_type": "exception"
        }


async def get_binance_ticker() -> Dict[str, Any]:
    """
    Fetch ticker data from Binance public API (24hr ticker)

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "Binance"
    category = "market_data"
    endpoint = "/api/v3/ticker/24hr"

    logger.info(f"Fetching 24hr ticker from {provider}")

    try:
        client = get_client()

        # Binance API base URL
        url = f"https://api.binance.com{endpoint}"
        params = {
            "symbols": '["BTCUSDT","ETHUSDT","BNBUSDT"]'
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
                "staleness_minutes": None,
                "success": False,
                "error": error_msg,
                "error_type": response.get("error_type")
            }

        # Extract data
        data = response["data"]

        # Parse timestamp from response
        # Binance returns closeTime as Unix timestamp in milliseconds
        data_timestamp = None
        if isinstance(data, list) and len(data) > 0:
            first_ticker = data[0]
            if isinstance(first_ticker, dict) and "closeTime" in first_ticker:
                try:
                    data_timestamp = datetime.fromtimestamp(
                        first_ticker["closeTime"] / 1000,
                        tz=timezone.utc
                    )
                except:
                    pass

        staleness = calculate_staleness_minutes(data_timestamp)

        ticker_count = len(data) if isinstance(data, list) else 0
        logger.info(
            f"{provider} - {endpoint} - Retrieved {ticker_count} tickers, "
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
            "staleness_minutes": None,
            "success": False,
            "error": error_msg,
            "error_type": "exception"
        }


async def collect_market_data() -> List[Dict[str, Any]]:
    """
    Main function to collect market data from all sources

    Returns:
        List of results from all market data collectors
    """
    logger.info("Starting market data collection from all sources")

    # Run all collectors concurrently
    results = await asyncio.gather(
        get_coingecko_simple_price(),
        get_coinmarketcap_quotes(),
        get_binance_ticker(),
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
                "staleness_minutes": None,
                "success": False,
                "error": str(result),
                "error_type": "exception"
            })
        else:
            processed_results.append(result)

    # Log summary
    successful = sum(1 for r in processed_results if r.get("success", False))
    logger.info(f"Market data collection complete: {successful}/{len(processed_results)} successful")

    return processed_results


# Example usage
if __name__ == "__main__":
    async def main():
        results = await collect_market_data()

        print("\n=== Market Data Collection Results ===")
        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Success: {result['success']}")
            print(f"Staleness: {result.get('staleness_minutes', 'N/A')} minutes")
            if result['success']:
                print(f"Response Time: {result.get('response_time_ms', 0):.2f}ms")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

    asyncio.run(main())

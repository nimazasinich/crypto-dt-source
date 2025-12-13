"""
News Data Collectors
Fetches cryptocurrency news from CryptoPanic and NewsAPI
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from utils.api_client import get_client
from utils.logger import setup_logger, log_api_request, log_error
from config import config

logger = setup_logger("news_collector")


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


def parse_iso_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse ISO timestamp string to datetime

    Args:
        timestamp_str: ISO format timestamp string

    Returns:
        datetime object or None if parsing fails
    """
    try:
        # Handle various ISO formats
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str.replace('Z', '+00:00')
        return datetime.fromisoformat(timestamp_str)
    except:
        return None


async def get_cryptopanic_posts() -> Dict[str, Any]:
    """
    Fetch latest cryptocurrency news posts from CryptoPanic

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "CryptoPanic"
    category = "news"
    endpoint = "/posts/"

    logger.info(f"Fetching posts from {provider}")

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
            "auth_token": "free",  # CryptoPanic offers free tier
            "public": "true",
            "kind": "news",  # Get news posts
            "filter": "rising"  # Get rising news
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

        # Parse timestamp from most recent post
        data_timestamp = None
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
            if isinstance(results, list) and len(results) > 0:
                # Get the most recent post's timestamp
                first_post = results[0]
                if isinstance(first_post, dict) and "created_at" in first_post:
                    data_timestamp = parse_iso_timestamp(first_post["created_at"])

        staleness = calculate_staleness_minutes(data_timestamp)

        # Count posts
        post_count = 0
        if isinstance(data, dict) and "results" in data:
            post_count = len(data["results"])

        logger.info(
            f"{provider} - {endpoint} - Retrieved {post_count} posts, "
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
            "post_count": post_count
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


async def get_newsapi_headlines() -> Dict[str, Any]:
    """
    Fetch cryptocurrency headlines from NewsAPI (newsdata.io)

    Returns:
        Dict with provider, category, data, timestamp, staleness, success, error
    """
    provider = "NewsAPI"
    category = "news"
    endpoint = "/news"

    logger.info(f"Fetching headlines from {provider}")

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

        # Build request URL
        url = f"{provider_config.endpoint_url}{endpoint}"
        params = {
            "apikey": provider_config.api_key,
            "q": "cryptocurrency OR bitcoin OR ethereum",
            "language": "en",
            "category": "business,technology"
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

        # Parse timestamp from most recent article
        data_timestamp = None
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
            if isinstance(results, list) and len(results) > 0:
                # Get the most recent article's timestamp
                first_article = results[0]
                if isinstance(first_article, dict):
                    # Try different timestamp fields
                    timestamp_field = first_article.get("pubDate") or first_article.get("publishedAt")
                    if timestamp_field:
                        data_timestamp = parse_iso_timestamp(timestamp_field)

        staleness = calculate_staleness_minutes(data_timestamp)

        # Count articles
        article_count = 0
        if isinstance(data, dict) and "results" in data:
            article_count = len(data["results"])

        logger.info(
            f"{provider} - {endpoint} - Retrieved {article_count} articles, "
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
            "article_count": article_count
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


async def collect_news_data() -> List[Dict[str, Any]]:
    """
    Main function to collect news data from all sources

    Returns:
        List of results from all news collectors
    """
    logger.info("Starting news data collection from all sources")

    # Run all collectors concurrently
    results = await asyncio.gather(
        get_cryptopanic_posts(),
        get_newsapi_headlines(),
        return_exceptions=True
    )

    # Process results
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Collector failed with exception: {str(result)}")
            processed_results.append({
                "provider": "Unknown",
                "category": "news",
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
    total_items = sum(
        r.get("post_count", 0) + r.get("article_count", 0)
        for r in processed_results if r.get("success", False)
    )

    logger.info(
        f"News data collection complete: {successful}/{len(processed_results)} successful, "
        f"{total_items} total items"
    )

    return processed_results


# Alias for backward compatibility
collect_news = collect_news_data


class NewsCollector:
    """
    News Collector class for WebSocket streaming interface
    Wraps the standalone news collection functions
    """

    def __init__(self, config: Any = None):
        """
        Initialize the news collector

        Args:
            config: Configuration object (optional, for compatibility)
        """
        self.config = config
        self.logger = logger

    async def collect(self) -> Dict[str, Any]:
        """
        Collect news data from all sources

        Returns:
            Dict with aggregated news data
        """
        results = await collect_news_data()

        # Aggregate data for WebSocket streaming
        aggregated = {
            "articles": [],
            "sources": [],
            "categories": [],
            "breaking": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        for result in results:
            if result.get("success") and result.get("data"):
                provider = result.get("provider", "unknown")
                aggregated["sources"].append(provider)

                data = result["data"]

                # Parse CryptoPanic posts
                if provider == "CryptoPanic" and "results" in data:
                    for post in data["results"][:10]:  # Take top 10
                        aggregated["articles"].append({
                            "title": post.get("title"),
                            "url": post.get("url"),
                            "source": post.get("source", {}).get("title"),
                            "published_at": post.get("published_at"),
                            "kind": post.get("kind"),
                            "votes": post.get("votes", {})
                        })

                # Parse NewsAPI articles
                elif provider == "NewsAPI" and "articles" in data:
                    for article in data["articles"][:10]:  # Take top 10
                        aggregated["articles"].append({
                            "title": article.get("title"),
                            "url": article.get("url"),
                            "source": article.get("source", {}).get("name"),
                            "published_at": article.get("publishedAt"),
                            "description": article.get("description")
                        })

        return aggregated


# Example usage
if __name__ == "__main__":
    async def main():
        results = await collect_news_data()

        print("\n=== News Data Collection Results ===")
        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Success: {result['success']}")
            print(f"Staleness: {result.get('staleness_minutes', 'N/A')} minutes")
            if result['success']:
                print(f"Response Time: {result.get('response_time_ms', 0):.2f}ms")
                print(f"Items: {result.get('post_count', 0) + result.get('article_count', 0)}")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

    asyncio.run(main())

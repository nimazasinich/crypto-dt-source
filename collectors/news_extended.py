"""
Extended News Collectors
Fetches news from RSS feeds, CoinDesk, CoinTelegraph, and other crypto news sources
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import feedparser

from utils.api_client import get_client
from utils.logger import log_api_request, log_error, setup_logger

logger = setup_logger("news_extended_collector")


async def get_rss_feed(provider: str, feed_url: str) -> Dict[str, Any]:
    """
    Fetch and parse RSS feed from a news source

    Args:
        provider: Provider name
        feed_url: RSS feed URL

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    category = "news"
    endpoint = "/rss"

    logger.info(f"Fetching RSS feed from {provider}")

    try:
        client = get_client()

        # Fetch RSS feed
        response = await client.get(feed_url, timeout=15)

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

        # Parse RSS feed
        raw_data = response.get("raw_content", "")
        if not raw_data:
            raw_data = str(response.get("data", ""))

        # Use feedparser to parse RSS
        feed = feedparser.parse(raw_data)

        news_data = None
        if feed and hasattr(feed, "entries"):
            entries = feed.entries[:10]  # Get top 10 articles

            articles = []
            for entry in entries:
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")[:200] if "summary" in entry else None,
                }
                articles.append(article)

            news_data = {
                "feed_title": (
                    feed.feed.get("title", provider) if hasattr(feed, "feed") else provider
                ),
                "total_entries": len(feed.entries),
                "articles": articles,
            }

        logger.info(
            f"{provider} - {endpoint} - Retrieved {len(feed.entries) if feed else 0} articles"
        )

        return {
            "provider": provider,
            "category": category,
            "data": news_data,
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


async def get_coindesk_news() -> Dict[str, Any]:
    """
    Fetch news from CoinDesk RSS feed

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/")


async def get_cointelegraph_news() -> Dict[str, Any]:
    """
    Fetch news from CoinTelegraph RSS feed

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("CoinTelegraph", "https://cointelegraph.com/rss")


async def get_decrypt_news() -> Dict[str, Any]:
    """
    Fetch news from Decrypt RSS feed

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("Decrypt", "https://decrypt.co/feed")


async def get_bitcoinmagazine_news() -> Dict[str, Any]:
    """
    Fetch news from Bitcoin Magazine RSS feed

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("BitcoinMagazine", "https://bitcoinmagazine.com/.rss/full/")


async def get_theblock_news() -> Dict[str, Any]:
    """
    Fetch news from The Block

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("TheBlock", "https://www.theblock.co/rss.xml")


async def get_cryptoslate_news() -> Dict[str, Any]:
    """
    Fetch news from CryptoSlate

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    provider = "CryptoSlate"
    category = "news"
    endpoint = "/newslist"

    logger.info(f"Fetching news from {provider}")

    try:
        client = get_client()

        # CryptoSlate API endpoint (if available)
        url = "https://cryptoslate.com/wp-json/cs/v1/posts"

        params = {"per_page": 10, "orderby": "date"}

        # Make request
        response = await client.get(url, params=params, timeout=10)

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
            # Fallback to RSS feed
            logger.info(f"{provider} - API failed, trying RSS feed")
            return await get_rss_feed(provider, "https://cryptoslate.com/feed/")

        # Extract data
        data = response["data"]

        news_data = None
        if isinstance(data, list):
            articles = [
                {
                    "title": article.get("title", {}).get("rendered", ""),
                    "link": article.get("link", ""),
                    "published": article.get("date", ""),
                    "excerpt": article.get("excerpt", {}).get("rendered", "")[:200],
                }
                for article in data
            ]

            news_data = {"total_entries": len(articles), "articles": articles}

        logger.info(
            f"{provider} - {endpoint} - Retrieved {len(data) if isinstance(data, list) else 0} articles"
        )

        return {
            "provider": provider,
            "category": category,
            "data": news_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "error": None,
            "response_time_ms": response.get("response_time_ms", 0),
        }

    except Exception as e:
        # Fallback to RSS feed on error
        logger.info(f"{provider} - Exception occurred, trying RSS feed")
        return await get_rss_feed(provider, "https://cryptoslate.com/feed/")


async def get_cryptonews_feed() -> Dict[str, Any]:
    """
    Fetch news from Crypto.news RSS feed

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("CryptoNews", "https://crypto.news/feed/")


async def get_coinjournal_news() -> Dict[str, Any]:
    """
    Fetch news from CoinJournal RSS feed

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("CoinJournal", "https://coinjournal.net/feed/")


async def get_beincrypto_news() -> Dict[str, Any]:
    """
    Fetch news from BeInCrypto RSS feed

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("BeInCrypto", "https://beincrypto.com/feed/")


async def get_cryptobriefing_news() -> Dict[str, Any]:
    """
    Fetch news from CryptoBriefing

    Returns:
        Dict with provider, category, data, timestamp, success, error
    """
    return await get_rss_feed("CryptoBriefing", "https://cryptobriefing.com/feed/")


async def collect_extended_news() -> List[Dict[str, Any]]:
    """
    Main function to collect news from all extended sources

    Returns:
        List of results from all news collectors
    """
    logger.info("Starting extended news collection from all sources")

    # Run all collectors concurrently
    results = await asyncio.gather(
        get_coindesk_news(),
        get_cointelegraph_news(),
        get_decrypt_news(),
        get_bitcoinmagazine_news(),
        get_theblock_news(),
        get_cryptoslate_news(),
        get_cryptonews_feed(),
        get_coinjournal_news(),
        get_beincrypto_news(),
        get_cryptobriefing_news(),
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
                    "category": "news",
                    "data": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": False,
                    "error": str(result),
                    "error_type": "exception",
                }
            )
        else:
            processed_results.append(result)

    # Log summary
    successful = sum(1 for r in processed_results if r.get("success", False))
    total_articles = sum(
        r.get("data", {}).get("total_entries", 0)
        for r in processed_results
        if r.get("success", False) and r.get("data")
    )

    logger.info(
        f"Extended news collection complete: {successful}/{len(processed_results)} sources successful, "
        f"{total_articles} total articles"
    )

    return processed_results


# Example usage
if __name__ == "__main__":

    async def main():
        results = await collect_extended_news()

        print("\n=== Extended News Collection Results ===")
        for result in results:
            print(f"\nProvider: {result['provider']}")
            print(f"Success: {result['success']}")

            if result["success"]:
                data = result.get("data", {})
                if data:
                    print(f"Total Articles: {data.get('total_entries', 'N/A')}")
                    articles = data.get("articles", [])
                    if articles:
                        print(f"Latest: {articles[0].get('title', 'N/A')[:60]}...")
            else:
                print(f"Error: {result.get('error', 'Unknown')}")

    asyncio.run(main())

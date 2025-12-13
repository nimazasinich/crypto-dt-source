#!/usr/bin/env python3
"""
Data Collection Module for Crypto Data Aggregator
Collects price data, news, and sentiment from various sources
"""

import requests
import aiohttp
import asyncio
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re

# Try to import optional dependencies
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    logging.warning("feedparser not installed. RSS feed parsing will be limited.")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logging.warning("beautifulsoup4 not installed. HTML parsing will be limited.")

# Import local modules
import config
import database

# Setup logging using config settings
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get database instance
db = database.get_database()

# Collection state tracking
_collection_timers = []
_is_collecting = False


# ==================== AI MODEL STUB FUNCTIONS ====================
# These provide fallback functionality when ai_models.py is not available

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Simple sentiment analysis based on keyword matching
    Returns sentiment score and label

    Args:
        text: Text to analyze

    Returns:
        Dict with 'score' and 'label'
    """
    if not text:
        return {'score': 0.0, 'label': 'neutral'}

    text_lower = text.lower()

    # Positive keywords
    positive_words = [
        'bullish', 'moon', 'rally', 'surge', 'gain', 'profit', 'up', 'green',
        'buy', 'long', 'growth', 'rise', 'pump', 'ATH', 'breakthrough',
        'adoption', 'positive', 'optimistic', 'upgrade', 'partnership'
    ]

    # Negative keywords
    negative_words = [
        'bearish', 'crash', 'dump', 'drop', 'loss', 'down', 'red', 'sell',
        'short', 'decline', 'fall', 'fear', 'scam', 'hack', 'vulnerability',
        'negative', 'pessimistic', 'concern', 'warning', 'risk'
    ]

    # Count occurrences
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    # Calculate score (-1 to 1)
    total = positive_count + negative_count
    if total == 0:
        score = 0.0
        label = 'neutral'
    else:
        score = (positive_count - negative_count) / total

        # Determine label
        if score <= -0.6:
            label = 'very_negative'
        elif score <= -0.2:
            label = 'negative'
        elif score <= 0.2:
            label = 'neutral'
        elif score <= 0.6:
            label = 'positive'
        else:
            label = 'very_positive'

    return {'score': score, 'label': label}


def summarize_text(text: str, max_length: int = 150) -> str:
    """
    Simple text summarization - takes first sentences up to max_length

    Args:
        text: Text to summarize
        max_length: Maximum length of summary

    Returns:
        Summarized text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = ' '.join(text.split())

    # If already short enough, return as is
    if len(text) <= max_length:
        return text

    # Try to break at sentence boundary
    sentences = re.split(r'[.!?]+', text)
    summary = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(summary) + len(sentence) + 2 <= max_length:
            summary += sentence + ". "
        else:
            break

    # If no complete sentences fit, truncate
    if not summary:
        summary = text[:max_length-3] + "..."

    return summary.strip()


# Try to import AI models if available
try:
    import ai_models
    # Override stub functions with real AI models if available
    analyze_sentiment = ai_models.analyze_sentiment
    summarize_text = ai_models.summarize_text
    logger.info("Using AI models for sentiment analysis and summarization")
except ImportError:
    logger.info("AI models not available, using simple keyword-based analysis")


# ==================== HELPER FUNCTIONS ====================

def safe_api_call(url: str, timeout: int = 10, headers: Optional[Dict] = None) -> Optional[Dict]:
    """
    Make HTTP GET request with error handling and retry logic

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        headers: Optional request headers

    Returns:
        Response JSON or None on failure
    """
    if headers is None:
        headers = {'User-Agent': config.USER_AGENT}

    for attempt in range(config.MAX_RETRIES):
        try:
            logger.debug(f"API call attempt {attempt + 1}/{config.MAX_RETRIES}: {url}")
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
            if response.status_code == 429:  # Rate limit
                wait_time = (attempt + 1) * 5
                logger.info(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            elif response.status_code >= 500:  # Server error
                time.sleep(attempt + 1)
            else:
                break  # Don't retry on 4xx errors
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}")
            time.sleep(attempt + 1)
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error on attempt {attempt + 1}: {e}")
            time.sleep(attempt + 1)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            break

    logger.error(f"All retry attempts failed for {url}")
    return None


def extract_mentioned_coins(text: str) -> List[str]:
    """
    Extract cryptocurrency symbols/names mentioned in text

    Args:
        text: Text to search for coin mentions

    Returns:
        List of coin symbols mentioned
    """
    if not text:
        return []

    text_upper = text.upper()
    mentioned = []

    # Check for common symbols
    common_symbols = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
        'XRP': 'ripple', 'ADA': 'cardano', 'SOL': 'solana',
        'DOT': 'polkadot', 'DOGE': 'dogecoin', 'AVAX': 'avalanche-2',
        'MATIC': 'polygon', 'LINK': 'chainlink', 'UNI': 'uniswap',
        'LTC': 'litecoin', 'ATOM': 'cosmos', 'ALGO': 'algorand'
    }

    # Check coin symbols
    for symbol, coin_id in common_symbols.items():
        # Look for symbol as whole word or with $ prefix
        pattern = r'\b' + symbol + r'\b|\$' + symbol + r'\b'
        if re.search(pattern, text_upper):
            mentioned.append(symbol)

    # Check for full coin names (case insensitive)
    coin_names = {
        'bitcoin': 'BTC', 'ethereum': 'ETH', 'binance': 'BNB',
        'ripple': 'XRP', 'cardano': 'ADA', 'solana': 'SOL',
        'polkadot': 'DOT', 'dogecoin': 'DOGE'
    }

    text_lower = text.lower()
    for name, symbol in coin_names.items():
        if name in text_lower and symbol not in mentioned:
            mentioned.append(symbol)

    return list(set(mentioned))  # Remove duplicates


# ==================== PRICE DATA COLLECTION ====================

def collect_price_data() -> Tuple[bool, int]:
    """
    Fetch price data from CoinGecko API, fallback to CoinCap if needed

    Returns:
        Tuple of (success: bool, count: int)
    """
    logger.info("Starting price data collection...")

    try:
        # Try CoinGecko first
        url = f"{config.COINGECKO_BASE_URL}{config.COINGECKO_ENDPOINTS['coins_markets']}"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': config.TOP_COINS_LIMIT,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '1h,24h,7d'
        }

        # Add params to URL
        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_str}"

        data = safe_api_call(full_url, timeout=config.REQUEST_TIMEOUT)

        if data is None:
            logger.warning("CoinGecko API failed, trying CoinCap backup...")
            return collect_price_data_coincap()

        # Parse and validate data
        prices = []
        for item in data:
            try:
                price = item.get('current_price', 0)

                # Validate price
                if not config.MIN_PRICE <= price <= config.MAX_PRICE:
                    logger.warning(f"Invalid price for {item.get('symbol')}: {price}")
                    continue

                price_data = {
                    'symbol': item.get('symbol', '').upper(),
                    'name': item.get('name', ''),
                    'price_usd': price,
                    'volume_24h': item.get('total_volume', 0),
                    'market_cap': item.get('market_cap', 0),
                    'percent_change_1h': item.get('price_change_percentage_1h_in_currency'),
                    'percent_change_24h': item.get('price_change_percentage_24h'),
                    'percent_change_7d': item.get('price_change_percentage_7d'),
                    'rank': item.get('market_cap_rank', 999)
                }

                # Validate market cap and volume
                if price_data['market_cap'] and price_data['market_cap'] < config.MIN_MARKET_CAP:
                    continue
                if price_data['volume_24h'] and price_data['volume_24h'] < config.MIN_VOLUME:
                    continue

                prices.append(price_data)

            except Exception as e:
                logger.error(f"Error parsing price data item: {e}")
                continue

        # Save to database
        if prices:
            count = db.save_prices_batch(prices)
            logger.info(f"Successfully collected and saved {count} price records from CoinGecko")
            return True, count
        else:
            logger.warning("No valid price data to save")
            return False, 0

    except Exception as e:
        logger.error(f"Error in collect_price_data: {e}")
        return False, 0


def collect_price_data_coincap() -> Tuple[bool, int]:
    """
    Backup function using CoinCap API

    Returns:
        Tuple of (success: bool, count: int)
    """
    logger.info("Starting CoinCap price data collection...")

    try:
        url = f"{config.COINCAP_BASE_URL}{config.COINCAP_ENDPOINTS['assets']}"
        params = {
            'limit': config.TOP_COINS_LIMIT
        }

        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_str}"

        response = safe_api_call(full_url, timeout=config.REQUEST_TIMEOUT)

        if response is None or 'data' not in response:
            logger.error("CoinCap API failed")
            return False, 0

        data = response['data']

        # Parse and validate data
        prices = []
        for idx, item in enumerate(data):
            try:
                price = float(item.get('priceUsd', 0))

                # Validate price
                if not config.MIN_PRICE <= price <= config.MAX_PRICE:
                    logger.warning(f"Invalid price for {item.get('symbol')}: {price}")
                    continue

                price_data = {
                    'symbol': item.get('symbol', '').upper(),
                    'name': item.get('name', ''),
                    'price_usd': price,
                    'volume_24h': float(item.get('volumeUsd24Hr', 0)) if item.get('volumeUsd24Hr') else None,
                    'market_cap': float(item.get('marketCapUsd', 0)) if item.get('marketCapUsd') else None,
                    'percent_change_1h': None,  # CoinCap doesn't provide 1h change
                    'percent_change_24h': float(item.get('changePercent24Hr', 0)) if item.get('changePercent24Hr') else None,
                    'percent_change_7d': None,  # CoinCap doesn't provide 7d change
                    'rank': int(item.get('rank', idx + 1))
                }

                # Validate market cap and volume
                if price_data['market_cap'] and price_data['market_cap'] < config.MIN_MARKET_CAP:
                    continue
                if price_data['volume_24h'] and price_data['volume_24h'] < config.MIN_VOLUME:
                    continue

                prices.append(price_data)

            except Exception as e:
                logger.error(f"Error parsing CoinCap data item: {e}")
                continue

        # Save to database
        if prices:
            count = db.save_prices_batch(prices)
            logger.info(f"Successfully collected and saved {count} price records from CoinCap")
            return True, count
        else:
            logger.warning("No valid price data to save from CoinCap")
            return False, 0

    except Exception as e:
        logger.error(f"Error in collect_price_data_coincap: {e}")
        return False, 0


# ==================== NEWS DATA COLLECTION ====================

def collect_news_data() -> int:
    """
    Parse RSS feeds and Reddit posts, analyze sentiment and save to database

    Returns:
        Count of articles collected
    """
    logger.info("Starting news data collection...")
    articles_collected = 0

    # Collect from RSS feeds
    if FEEDPARSER_AVAILABLE:
        articles_collected += _collect_rss_feeds()
    else:
        logger.warning("Feedparser not available, skipping RSS feeds")

    # Collect from Reddit
    articles_collected += _collect_reddit_posts()

    logger.info(f"News collection completed. Total articles: {articles_collected}")
    return articles_collected


def _collect_rss_feeds() -> int:
    """Collect articles from RSS feeds"""
    count = 0

    for source_name, feed_url in config.RSS_FEEDS.items():
        try:
            logger.debug(f"Parsing RSS feed: {source_name}")
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:  # Limit to 20 most recent per feed
                try:
                    # Extract article data
                    title = entry.get('title', '')
                    url = entry.get('link', '')

                    # Skip if no URL
                    if not url:
                        continue

                    # Get published date
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            published_date = datetime(*entry.published_parsed[:6]).isoformat()
                        except:
                            pass

                    # Get summary/description
                    summary = entry.get('summary', '') or entry.get('description', '')
                    if summary and BS4_AVAILABLE:
                        # Strip HTML tags
                        soup = BeautifulSoup(summary, 'html.parser')
                        summary = soup.get_text()

                    # Combine title and summary for analysis
                    full_text = f"{title} {summary}"

                    # Extract mentioned coins
                    related_coins = extract_mentioned_coins(full_text)

                    # Analyze sentiment
                    sentiment_result = analyze_sentiment(full_text)

                    # Summarize text
                    summary_text = summarize_text(summary or title, max_length=200)

                    # Prepare news data
                    news_data = {
                        'title': title,
                        'summary': summary_text,
                        'url': url,
                        'source': source_name,
                        'sentiment_score': sentiment_result['score'],
                        'sentiment_label': sentiment_result['label'],
                        'related_coins': related_coins,
                        'published_date': published_date
                    }

                    # Save to database
                    if db.save_news(news_data):
                        count += 1

                except Exception as e:
                    logger.error(f"Error processing RSS entry from {source_name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing RSS feed {source_name}: {e}")
            continue

    logger.info(f"Collected {count} articles from RSS feeds")
    return count


def _collect_reddit_posts() -> int:
    """Collect posts from Reddit"""
    count = 0

    for subreddit_name, endpoint_url in config.REDDIT_ENDPOINTS.items():
        try:
            logger.debug(f"Fetching Reddit posts from r/{subreddit_name}")

            # Reddit API requires .json extension
            if not endpoint_url.endswith('.json'):
                endpoint_url = endpoint_url.rstrip('/') + '.json'

            headers = {'User-Agent': config.USER_AGENT}
            data = safe_api_call(endpoint_url, headers=headers)

            if not data or 'data' not in data or 'children' not in data['data']:
                logger.warning(f"Invalid response from Reddit: {subreddit_name}")
                continue

            posts = data['data']['children']

            for post_data in posts[:15]:  # Limit to 15 posts per subreddit
                try:
                    post = post_data.get('data', {})

                    # Extract post data
                    title = post.get('title', '')
                    url = post.get('url', '')
                    permalink = f"https://reddit.com{post.get('permalink', '')}"
                    selftext = post.get('selftext', '')

                    # Skip if no title
                    if not title:
                        continue

                    # Use permalink as primary URL (actual Reddit post)
                    article_url = permalink

                    # Get timestamp
                    created_utc = post.get('created_utc')
                    published_date = None
                    if created_utc:
                        try:
                            published_date = datetime.fromtimestamp(created_utc).isoformat()
                        except:
                            pass

                    # Combine title and text for analysis
                    full_text = f"{title} {selftext}"

                    # Extract mentioned coins
                    related_coins = extract_mentioned_coins(full_text)

                    # Analyze sentiment
                    sentiment_result = analyze_sentiment(full_text)

                    # Summarize text
                    summary_text = summarize_text(selftext or title, max_length=200)

                    # Prepare news data
                    news_data = {
                        'title': title,
                        'summary': summary_text,
                        'url': article_url,
                        'source': f"reddit_{subreddit_name}",
                        'sentiment_score': sentiment_result['score'],
                        'sentiment_label': sentiment_result['label'],
                        'related_coins': related_coins,
                        'published_date': published_date
                    }

                    # Save to database
                    if db.save_news(news_data):
                        count += 1

                except Exception as e:
                    logger.error(f"Error processing Reddit post from {subreddit_name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching Reddit posts from {subreddit_name}: {e}")
            continue

    logger.info(f"Collected {count} posts from Reddit")
    return count


# ==================== SENTIMENT DATA COLLECTION ====================

def collect_sentiment_data() -> Optional[Dict[str, Any]]:
    """
    Fetch Fear & Greed Index from Alternative.me

    Returns:
        Sentiment data or None on failure
    """
    logger.info("Starting sentiment data collection...")

    try:
        # Fetch Fear & Greed Index
        data = safe_api_call(config.ALTERNATIVE_ME_URL, timeout=config.REQUEST_TIMEOUT)

        if data is None or 'data' not in data:
            logger.error("Failed to fetch Fear & Greed Index")
            return None

        # Parse response
        fng_data = data['data'][0] if data['data'] else {}

        value = fng_data.get('value')
        classification = fng_data.get('value_classification', 'Unknown')
        timestamp = fng_data.get('timestamp')

        if value is None:
            logger.warning("No value in Fear & Greed response")
            return None

        # Convert to sentiment score (-1 to 1)
        # Fear & Greed is 0-100, convert to -1 to 1
        sentiment_score = (int(value) - 50) / 50.0

        # Determine label
        if int(value) <= 25:
            sentiment_label = 'extreme_fear'
        elif int(value) <= 45:
            sentiment_label = 'fear'
        elif int(value) <= 55:
            sentiment_label = 'neutral'
        elif int(value) <= 75:
            sentiment_label = 'greed'
        else:
            sentiment_label = 'extreme_greed'

        sentiment_data = {
            'value': int(value),
            'classification': classification,
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'timestamp': timestamp
        }

        # Save to news table as market-wide sentiment
        news_data = {
            'title': f"Market Sentiment: {classification}",
            'summary': f"Fear & Greed Index: {value}/100 - {classification}",
            'url': config.ALTERNATIVE_ME_URL,
            'source': 'alternative_me',
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'related_coins': ['BTC', 'ETH'],  # Market-wide
            'published_date': datetime.now().isoformat()
        }

        db.save_news(news_data)

        logger.info(f"Sentiment collected: {classification} ({value}/100)")
        return sentiment_data

    except Exception as e:
        logger.error(f"Error in collect_sentiment_data: {e}")
        return None


# ==================== SCHEDULING ====================

def schedule_data_collection():
    """
    Schedule periodic data collection using threading.Timer
    Runs collection tasks in background at configured intervals
    """
    global _is_collecting

    if _is_collecting:
        logger.warning("Data collection already running")
        return

    _is_collecting = True
    logger.info("Starting scheduled data collection...")

    def run_price_collection():
        """Wrapper for price collection with rescheduling"""
        try:
            collect_price_data()
        except Exception as e:
            logger.error(f"Error in scheduled price collection: {e}")
        finally:
            # Reschedule
            if _is_collecting:
                timer = threading.Timer(
                    config.COLLECTION_INTERVALS['price_data'],
                    run_price_collection
                )
                timer.daemon = True
                timer.start()
                _collection_timers.append(timer)

    def run_news_collection():
        """Wrapper for news collection with rescheduling"""
        try:
            collect_news_data()
        except Exception as e:
            logger.error(f"Error in scheduled news collection: {e}")
        finally:
            # Reschedule
            if _is_collecting:
                timer = threading.Timer(
                    config.COLLECTION_INTERVALS['news_data'],
                    run_news_collection
                )
                timer.daemon = True
                timer.start()
                _collection_timers.append(timer)

    def run_sentiment_collection():
        """Wrapper for sentiment collection with rescheduling"""
        try:
            collect_sentiment_data()
        except Exception as e:
            logger.error(f"Error in scheduled sentiment collection: {e}")
        finally:
            # Reschedule
            if _is_collecting:
                timer = threading.Timer(
                    config.COLLECTION_INTERVALS['sentiment_data'],
                    run_sentiment_collection
                )
                timer.daemon = True
                timer.start()
                _collection_timers.append(timer)

    # Initial run immediately
    logger.info("Running initial data collection...")

    # Run initial collections in separate threads
    threading.Thread(target=run_price_collection, daemon=True).start()
    time.sleep(2)  # Stagger starts
    threading.Thread(target=run_news_collection, daemon=True).start()
    time.sleep(2)
    threading.Thread(target=run_sentiment_collection, daemon=True).start()

    logger.info("Scheduled data collection started successfully")
    logger.info(f"Price data: every {config.COLLECTION_INTERVALS['price_data']}s")
    logger.info(f"News data: every {config.COLLECTION_INTERVALS['news_data']}s")
    logger.info(f"Sentiment data: every {config.COLLECTION_INTERVALS['sentiment_data']}s")


def stop_scheduled_collection():
    """Stop all scheduled collection tasks"""
    global _is_collecting

    logger.info("Stopping scheduled data collection...")
    _is_collecting = False

    # Cancel all timers
    for timer in _collection_timers:
        try:
            timer.cancel()
        except:
            pass

    _collection_timers.clear()
    logger.info("Scheduled data collection stopped")


# ==================== ASYNC COLLECTION (BONUS) ====================

async def collect_price_data_async() -> Tuple[bool, int]:
    """
    Async version of price data collection using aiohttp

    Returns:
        Tuple of (success: bool, count: int)
    """
    logger.info("Starting async price data collection...")

    try:
        url = f"{config.COINGECKO_BASE_URL}{config.COINGECKO_ENDPOINTS['coins_markets']}"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': config.TOP_COINS_LIMIT,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '1h,24h,7d'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=config.REQUEST_TIMEOUT) as response:
                if response.status != 200:
                    logger.error(f"API returned status {response.status}")
                    return False, 0

                data = await response.json()

        # Parse and validate data (same as sync version)
        prices = []
        for item in data:
            try:
                price = item.get('current_price', 0)

                if not config.MIN_PRICE <= price <= config.MAX_PRICE:
                    continue

                price_data = {
                    'symbol': item.get('symbol', '').upper(),
                    'name': item.get('name', ''),
                    'price_usd': price,
                    'volume_24h': item.get('total_volume', 0),
                    'market_cap': item.get('market_cap', 0),
                    'percent_change_1h': item.get('price_change_percentage_1h_in_currency'),
                    'percent_change_24h': item.get('price_change_percentage_24h'),
                    'percent_change_7d': item.get('price_change_percentage_7d'),
                    'rank': item.get('market_cap_rank', 999)
                }

                if price_data['market_cap'] and price_data['market_cap'] < config.MIN_MARKET_CAP:
                    continue
                if price_data['volume_24h'] and price_data['volume_24h'] < config.MIN_VOLUME:
                    continue

                prices.append(price_data)

            except Exception as e:
                logger.error(f"Error parsing price data item: {e}")
                continue

        # Save to database
        if prices:
            count = db.save_prices_batch(prices)
            logger.info(f"Async collected and saved {count} price records")
            return True, count
        else:
            return False, 0

    except Exception as e:
        logger.error(f"Error in collect_price_data_async: {e}")
        return False, 0


# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Crypto Data Collector - Manual Test Run")
    logger.info("=" * 60)

    # Test price collection
    logger.info("\n--- Testing Price Collection ---")
    success, count = collect_price_data()
    print(f"Price collection: {'SUCCESS' if success else 'FAILED'} - {count} records")

    # Test news collection
    logger.info("\n--- Testing News Collection ---")
    news_count = collect_news_data()
    print(f"News collection: {news_count} articles collected")

    # Test sentiment collection
    logger.info("\n--- Testing Sentiment Collection ---")
    sentiment = collect_sentiment_data()
    if sentiment:
        print(f"Sentiment: {sentiment['classification']} ({sentiment['value']}/100)")
    else:
        print("Sentiment collection: FAILED")

    logger.info("\n" + "=" * 60)
    logger.info("Manual test run completed")
    logger.info("=" * 60)

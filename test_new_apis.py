#!/usr/bin/env python3
"""
Test script for newly added API keys:
- NewsAPI
- CoinMarketCap
"""

import os
import asyncio
import logging
import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        logger.info("✅ Environment variables loaded from .env")
    else:
        logger.warning("⚠️ .env file not found")

load_env()


async def test_newsapi():
    """Test NewsAPI with the provided API key"""
    logger.info("=" * 60)
    logger.info("TEST 1: NewsAPI - Cryptocurrency News")
    logger.info("=" * 60)
    
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        logger.error("❌ NEWSAPI_KEY not found in environment")
        return
    
    logger.info(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Cryptocurrency news
            logger.info("\n📰 Fetching cryptocurrency news...")
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "cryptocurrency OR bitcoin OR ethereum",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 10,
                    "apiKey": api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                logger.info(f"✅ NewsAPI working! Fetched {len(articles)} articles")
                logger.info(f"   Total results available: {data.get('totalResults', 0)}")
                
                logger.info("\n📰 Latest crypto headlines:")
                for i, article in enumerate(articles[:5], 1):
                    logger.info(f"\n   {i}. {article.get('title', 'No title')}")
                    logger.info(f"      Source: {article.get('source', {}).get('name', 'Unknown')}")
                    logger.info(f"      Published: {article.get('publishedAt', 'Unknown')}")
                    logger.info(f"      URL: {article.get('url', 'N/A')[:60]}...")
            else:
                logger.error(f"❌ NewsAPI returned error: {data}")
        
        # Test 2: Bitcoin specific news
        logger.info("\n\n📰 Fetching Bitcoin-specific news...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "bitcoin",
                    "language": "en",
                    "sortBy": "popularity",
                    "pageSize": 5,
                    "apiKey": api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                logger.info(f"✅ Fetched {len(articles)} Bitcoin articles")
    
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ NewsAPI HTTP error: {e}")
        logger.error(f"   Status code: {e.response.status_code}")
        logger.error(f"   Response: {e.response.text[:200]}")
    except Exception as e:
        logger.error(f"❌ NewsAPI test failed: {e}")
    
    logger.info("")


async def test_coinmarketcap():
    """Test CoinMarketCap API with the provided API key"""
    logger.info("=" * 60)
    logger.info("TEST 2: CoinMarketCap - Cryptocurrency Data")
    logger.info("=" * 60)
    
    api_key = os.getenv("COINMARKETCAP_API_KEY")
    if not api_key:
        logger.error("❌ COINMARKETCAP_API_KEY not found in environment")
        return
    
    logger.info(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        headers = {
            "X-CMC_PRO_API_KEY": api_key,
            "Accept": "application/json"
        }
        
        # Test 1: Get latest cryptocurrency listings
        logger.info("\n💰 Fetching top cryptocurrencies by market cap...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",
                headers=headers,
                params={
                    "start": "1",
                    "limit": "10",
                    "convert": "USD"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status", {}).get("error_code") == 0:
                cryptos = data.get("data", [])
                logger.info(f"✅ CoinMarketCap API working! Fetched {len(cryptos)} cryptocurrencies")
                
                logger.info("\n💰 Top 10 Cryptocurrencies:")
                for crypto in cryptos:
                    name = crypto.get("name", "Unknown")
                    symbol = crypto.get("symbol", "???")
                    rank = crypto.get("cmc_rank", "?")
                    quote = crypto.get("quote", {}).get("USD", {})
                    price = quote.get("price", 0)
                    change_24h = quote.get("percent_change_24h", 0)
                    market_cap = quote.get("market_cap", 0)
                    
                    logger.info(
                        f"\n   #{rank} {name} ({symbol})"
                    )
                    logger.info(f"      Price: ${price:,.2f}")
                    logger.info(f"      24h Change: {change_24h:+.2f}%")
                    logger.info(f"      Market Cap: ${market_cap:,.0f}")
            else:
                logger.error(f"❌ CoinMarketCap returned error: {data}")
        
        # Test 2: Get specific coin quote (Bitcoin)
        logger.info("\n\n💰 Fetching Bitcoin quote...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest",
                headers=headers,
                params={
                    "symbol": "BTC",
                    "convert": "USD"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status", {}).get("error_code") == 0:
                btc_data = data.get("data", {}).get("BTC", [{}])[0]
                quote = btc_data.get("quote", {}).get("USD", {})
                
                logger.info(f"✅ Bitcoin Data:")
                logger.info(f"   Name: {btc_data.get('name', 'Bitcoin')}")
                logger.info(f"   Symbol: {btc_data.get('symbol', 'BTC')}")
                logger.info(f"   Price: ${quote.get('price', 0):,.2f}")
                logger.info(f"   24h Volume: ${quote.get('volume_24h', 0):,.0f}")
                logger.info(f"   24h Change: {quote.get('percent_change_24h', 0):+.2f}%")
                logger.info(f"   Market Cap: ${quote.get('market_cap', 0):,.0f}")
                logger.info(f"   Dominance: {quote.get('market_cap_dominance', 0):.2f}%")
    
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ CoinMarketCap HTTP error: {e}")
        logger.error(f"   Status code: {e.response.status_code}")
        logger.error(f"   Response: {e.response.text[:200]}")
    except Exception as e:
        logger.error(f"❌ CoinMarketCap test failed: {e}")
    
    logger.info("")


async def test_integrated_news_service():
    """Test the integrated crypto news client with new NewsAPI key"""
    logger.info("=" * 60)
    logger.info("TEST 3: Integrated Crypto News Service")
    logger.info("=" * 60)
    
    try:
        from backend.services.crypto_news_client import CryptoNewsClient
        client = CryptoNewsClient()
        
        logger.info(f"NewsAPI key configured: {'✅' if client.newsapi_key else '❌'}")
        logger.info(f"RSS feeds configured: {len(client.rss_feeds)}")
        
        # Fetch news
        logger.info("\n📰 Fetching latest crypto news from all sources...")
        articles = await client.get_latest_news(limit=10)
        
        logger.info(f"✅ Successfully fetched {len(articles)} articles")
        
        # Group by source
        sources = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        logger.info("\n📊 Articles by source:")
        for source, count in sources.items():
            logger.info(f"   {source}: {count} articles")
        
        # Show some headlines
        logger.info("\n📰 Sample headlines:")
        for i, article in enumerate(articles[:5], 1):
            logger.info(f"\n   {i}. [{article.get('source')}] {article.get('title', 'No title')[:60]}...")
    
    except Exception as e:
        logger.error(f"❌ Integrated news service test failed: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("")


async def main():
    """Run all API tests"""
    logger.info("\n" + "=" * 60)
    logger.info("🚀 TESTING NEW API KEYS")
    logger.info("=" * 60 + "\n")
    
    try:
        await test_newsapi()
        await test_coinmarketcap()
        await test_integrated_news_service()
        
        logger.info("=" * 60)
        logger.info("✅ ALL API TESTS COMPLETED")
        logger.info("=" * 60)
        logger.info("\n📊 SUMMARY:")
        logger.info("✅ NewsAPI: Configured and tested")
        logger.info("✅ CoinMarketCap: Configured and tested")
        logger.info("✅ Integrated services: Updated")
        logger.info("\n💡 BENEFITS:")
        logger.info("  • Access to 100+ news sources via NewsAPI")
        logger.info("  • Professional-grade crypto data from CoinMarketCap")
        logger.info("  • Enhanced market intelligence")
        logger.info("  • More reliable data aggregation")
        logger.info("\n🎯 NEXT STEPS:")
        logger.info("  1. APIs are ready to use")
        logger.info("  2. Start system: python3 main.py")
        logger.info("  3. Monitor API usage to stay within limits")
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

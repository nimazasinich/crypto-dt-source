#!/usr/bin/env python3
"""
جمع‌آوری اخبار از RSS فیدهای رایگان
RSS News Collectors - FREE RSS Feeds
"""

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

import feedparser
import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSNewsCollector:
    """جمع‌آوری اخبار رمزارز از RSS فیدهای رایگان"""

    def __init__(self):
        self.timeout = httpx.Timeout(20.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/xml, text/xml, application/rss+xml",
        }

        # Free RSS feeds - NO API KEY NEEDED
        self.rss_feeds = {
            "cointelegraph": "https://cointelegraph.com/rss",
            "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "bitcoinmagazine": "https://bitcoinmagazine.com/.rss/full/",
            "decrypt": "https://decrypt.co/feed",
            "theblock": "https://www.theblock.co/rss.xml",
            "cryptopotato": "https://cryptopotato.com/feed/",
            "newsbtc": "https://www.newsbtc.com/feed/",
            "bitcoinist": "https://bitcoinist.com/feed/",
            "cryptocompare": "https://www.cryptocompare.com/api/data/news/?feeds=cointelegraph,coindesk,cryptocompare",
        }

    def clean_html(self, html_text: str) -> str:
        """حذف HTML تگ‌ها و تمیز کردن متن"""
        if not html_text:
            return ""

        # Remove HTML tags
        soup = BeautifulSoup(html_text, "html.parser")
        text = soup.get_text()

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def extract_coins_from_text(self, text: str) -> List[str]:
        """استخراج نام رمزارزها از متن"""
        if not text:
            return []

        text_upper = text.upper()
        coins = []

        # Common crypto symbols
        crypto_symbols = [
            "BTC",
            "BITCOIN",
            "ETH",
            "ETHEREUM",
            "SOL",
            "SOLANA",
            "BNB",
            "BINANCE",
            "XRP",
            "RIPPLE",
            "ADA",
            "CARDANO",
            "DOGE",
            "DOGECOIN",
            "MATIC",
            "POLYGON",
            "DOT",
            "POLKADOT",
            "AVAX",
            "AVALANCHE",
            "LINK",
            "CHAINLINK",
            "UNI",
            "UNISWAP",
            "ATOM",
            "COSMOS",
            "LTC",
            "LITECOIN",
            "BCH",
            "BITCOIN CASH",
        ]

        for symbol in crypto_symbols:
            if symbol in text_upper:
                # Add the short symbol form
                short_symbol = symbol.split()[0] if " " in symbol else symbol
                if short_symbol not in coins and len(short_symbol) <= 5:
                    coins.append(short_symbol)

        return list(set(coins))

    async def fetch_rss_feed(self, url: str, source_name: str) -> List[Dict]:
        """دریافت و پارس یک RSS فید"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)

                if response.status_code != 200:
                    logger.warning(f"⚠️ {source_name} returned status {response.status_code}")
                    return []

                # Parse RSS feed
                feed = feedparser.parse(response.text)

                if not feed.entries:
                    logger.warning(f"⚠️ {source_name} has no entries")
                    return []

                news_items = []
                for entry in feed.entries[:20]:  # Limit to 20 most recent
                    # Extract published date
                    published_at = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])
                    else:
                        published_at = datetime.now()

                    # Get description
                    description = ""
                    if hasattr(entry, "summary"):
                        description = self.clean_html(entry.summary)
                    elif hasattr(entry, "description"):
                        description = self.clean_html(entry.description)

                    # Combine title and description for coin extraction
                    full_text = f"{entry.title} {description}"
                    coins = self.extract_coins_from_text(full_text)

                    news_items.append(
                        {
                            "title": entry.title,
                            "description": description[:500],  # Limit description length
                            "url": entry.link,
                            "source": source_name,
                            "published_at": published_at.isoformat(),
                            "coins": coins,
                            "category": "news",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                logger.info(f"✅ {source_name}: Collected {len(news_items)} news items")
                return news_items

        except Exception as e:
            logger.error(f"❌ Error fetching {source_name}: {e}")
            return []

    async def collect_from_cointelegraph(self) -> List[Dict]:
        """CoinTelegraph RSS Feed"""
        return await self.fetch_rss_feed(self.rss_feeds["cointelegraph"], "CoinTelegraph")

    async def collect_from_coindesk(self) -> List[Dict]:
        """CoinDesk RSS Feed"""
        return await self.fetch_rss_feed(self.rss_feeds["coindesk"], "CoinDesk")

    async def collect_from_bitcoinmagazine(self) -> List[Dict]:
        """Bitcoin Magazine RSS Feed"""
        return await self.fetch_rss_feed(self.rss_feeds["bitcoinmagazine"], "Bitcoin Magazine")

    async def collect_from_decrypt(self) -> List[Dict]:
        """Decrypt RSS Feed"""
        return await self.fetch_rss_feed(self.rss_feeds["decrypt"], "Decrypt")

    async def collect_from_theblock(self) -> List[Dict]:
        """The Block RSS Feed"""
        return await self.fetch_rss_feed(self.rss_feeds["theblock"], "The Block")

    async def collect_from_cryptopotato(self) -> List[Dict]:
        """CryptoPotato RSS Feed"""
        return await self.fetch_rss_feed(self.rss_feeds["cryptopotato"], "CryptoPotato")

    async def collect_from_newsbtc(self) -> List[Dict]:
        """NewsBTC RSS Feed"""
        return await self.fetch_rss_feed(self.rss_feeds["newsbtc"], "NewsBTC")

    async def collect_from_bitcoinist(self) -> List[Dict]:
        """Bitcoinist RSS Feed"""
        return await self.fetch_rss_feed(self.rss_feeds["bitcoinist"], "Bitcoinist")

    async def collect_all_rss_feeds(self) -> Dict[str, List[Dict]]:
        """
        جمع‌آوری از همه RSS فیدها به صورت همزمان
        Collect from ALL RSS feeds simultaneously
        """
        logger.info("🚀 Starting collection from ALL RSS feeds...")

        tasks = [
            self.collect_from_cointelegraph(),
            self.collect_from_coindesk(),
            self.collect_from_bitcoinmagazine(),
            self.collect_from_decrypt(),
            self.collect_from_theblock(),
            self.collect_from_cryptopotato(),
            self.collect_from_newsbtc(),
            self.collect_from_bitcoinist(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "cointelegraph": results[0] if not isinstance(results[0], Exception) else [],
            "coindesk": results[1] if not isinstance(results[1], Exception) else [],
            "bitcoinmagazine": results[2] if not isinstance(results[2], Exception) else [],
            "decrypt": results[3] if not isinstance(results[3], Exception) else [],
            "theblock": results[4] if not isinstance(results[4], Exception) else [],
            "cryptopotato": results[5] if not isinstance(results[5], Exception) else [],
            "newsbtc": results[6] if not isinstance(results[6], Exception) else [],
            "bitcoinist": results[7] if not isinstance(results[7], Exception) else [],
        }

    def deduplicate_news(self, all_news: Dict[str, List[Dict]]) -> List[Dict]:
        """
        حذف اخبار تکراری
        Remove duplicate news based on URL
        """
        seen_urls = set()
        unique_news = []

        for source, news_list in all_news.items():
            for news_item in news_list:
                url = news_item["url"]

                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_news.append(news_item)

        # Sort by published date (most recent first)
        unique_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)

        logger.info(f"📰 Deduplicated to {len(unique_news)} unique news items")
        return unique_news

    def filter_by_coins(self, news: List[Dict], coins: List[str]) -> List[Dict]:
        """فیلتر اخبار بر اساس رمزارز خاص"""
        coins_upper = [c.upper() for c in coins]

        filtered = [
            item
            for item in news
            if any(coin.upper() in coins_upper for coin in item.get("coins", []))
        ]

        return filtered

    def get_trending_coins(self, news: List[Dict]) -> List[Dict[str, int]]:
        """
        پیدا کردن رمزارزهای ترند (بیشترین ذکر در اخبار)
        Find trending coins (most mentioned in news)
        """
        coin_counts = {}

        for item in news:
            for coin in item.get("coins", []):
                coin_counts[coin] = coin_counts.get(coin, 0) + 1

        # Sort by count
        trending = [
            {"coin": coin, "mentions": count}
            for coin, count in sorted(coin_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return trending[:20]  # Top 20


async def main():
    """Test the RSS collectors"""
    collector = RSSNewsCollector()

    print("\n" + "=" * 70)
    print("🧪 Testing FREE RSS News Collectors")
    print("=" * 70)

    # Test individual feeds
    print("\n1️⃣ Testing CoinTelegraph RSS...")
    ct_news = await collector.collect_from_cointelegraph()
    print(f"   Got {len(ct_news)} news items")
    if ct_news:
        print(f"   Latest: {ct_news[0]['title'][:60]}...")

    print("\n2️⃣ Testing CoinDesk RSS...")
    cd_news = await collector.collect_from_coindesk()
    print(f"   Got {len(cd_news)} news items")
    if cd_news:
        print(f"   Latest: {cd_news[0]['title'][:60]}...")

    print("\n3️⃣ Testing Bitcoin Magazine RSS...")
    bm_news = await collector.collect_from_bitcoinmagazine()
    print(f"   Got {len(bm_news)} news items")

    # Test all feeds at once
    print("\n\n" + "=" * 70)
    print("🚀 Testing ALL RSS Feeds Simultaneously")
    print("=" * 70)

    all_news = await collector.collect_all_rss_feeds()

    total = sum(len(v) for v in all_news.values())
    print(f"\n✅ Total news collected: {total}")
    for source, news in all_news.items():
        print(f"   {source}: {len(news)} items")

    # Test deduplication
    print("\n" + "=" * 70)
    print("🔄 Testing Deduplication")
    print("=" * 70)

    unique_news = collector.deduplicate_news(all_news)
    print(f"\n✅ Deduplicated to {len(unique_news)} unique items")

    # Show latest news
    print("\n📰 Latest 5 News Items:")
    for i, news in enumerate(unique_news[:5], 1):
        print(f"\n{i}. {news['title']}")
        print(f"   Source: {news['source']}")
        print(f"   Published: {news['published_at']}")
        if news.get("coins"):
            print(f"   Coins: {', '.join(news['coins'])}")

    # Test trending coins
    print("\n" + "=" * 70)
    print("🔥 Trending Coins (Most Mentioned)")
    print("=" * 70)

    trending = collector.get_trending_coins(unique_news)
    print(f"\n✅ Top 10 Trending Coins:")
    for i, item in enumerate(trending[:10], 1):
        print(f"   {i}. {item['coin']}: {item['mentions']} mentions")


if __name__ == "__main__":
    asyncio.run(main())

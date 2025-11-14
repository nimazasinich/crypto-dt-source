#!/usr/bin/env python3
"""
هماهنگ‌کننده جمع‌آوری داده
Data Collection Orchestrator - Manages all collectors
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto_data_bank.database import get_db
from crypto_data_bank.collectors.free_price_collector import FreePriceCollector
from crypto_data_bank.collectors.rss_news_collector import RSSNewsCollector
from crypto_data_bank.collectors.sentiment_collector import SentimentCollector
from crypto_data_bank.ai.huggingface_models import get_analyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCollectionOrchestrator:
    """
    هماهنگ‌کننده اصلی جمع‌آوری داده
    Main orchestrator for data collection from all FREE sources
    """

    def __init__(self):
        self.db = get_db()
        self.price_collector = FreePriceCollector()
        self.news_collector = RSSNewsCollector()
        self.sentiment_collector = SentimentCollector()
        self.ai_analyzer = get_analyzer()

        self.collection_tasks = []
        self.is_running = False

        # Collection intervals (in seconds)
        self.intervals = {
            'prices': 60,  # Every 1 minute
            'news': 300,  # Every 5 minutes
            'sentiment': 180,  # Every 3 minutes
        }

        self.last_collection = {
            'prices': None,
            'news': None,
            'sentiment': None,
        }

    async def collect_and_store_prices(self):
        """جمع‌آوری و ذخیره قیمت‌ها"""
        try:
            logger.info("💰 Collecting prices from FREE sources...")

            # Collect from all free sources
            all_prices = await self.price_collector.collect_all_free_sources()

            # Aggregate prices
            aggregated = self.price_collector.aggregate_prices(all_prices)

            # Save to database
            saved_count = 0
            for price_data in aggregated:
                try:
                    self.db.save_price(
                        symbol=price_data['symbol'],
                        price_data=price_data,
                        source='free_aggregated'
                    )
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Error saving price for {price_data.get('symbol')}: {e}")

            self.last_collection['prices'] = datetime.now()

            logger.info(f"✅ Saved {saved_count}/{len(aggregated)} prices to database")

            return {
                "success": True,
                "prices_collected": len(aggregated),
                "prices_saved": saved_count,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error collecting prices: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def collect_and_store_news(self):
        """جمع‌آوری و ذخیره اخبار"""
        try:
            logger.info("📰 Collecting news from FREE RSS feeds...")

            # Collect from all RSS feeds
            all_news = await self.news_collector.collect_all_rss_feeds()

            # Deduplicate
            unique_news = self.news_collector.deduplicate_news(all_news)

            # Analyze with AI (if available)
            if hasattr(self.ai_analyzer, 'analyze_news_batch'):
                logger.info("🤖 Analyzing news with AI...")
                analyzed_news = await self.ai_analyzer.analyze_news_batch(unique_news[:50])
            else:
                analyzed_news = unique_news

            # Save to database
            saved_count = 0
            for news_item in analyzed_news:
                try:
                    # Add AI sentiment if available
                    if 'ai_sentiment' in news_item:
                        news_item['sentiment'] = news_item['ai_confidence']

                    self.db.save_news(news_item)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Error saving news: {e}")

            self.last_collection['news'] = datetime.now()

            logger.info(f"✅ Saved {saved_count}/{len(analyzed_news)} news items to database")

            # Store AI analysis if available
            if analyzed_news and 'ai_sentiment' in analyzed_news[0]:
                try:
                    # Get trending coins from news
                    trending = self.news_collector.get_trending_coins(analyzed_news)

                    # Save AI analysis for trending coins
                    for trend in trending[:10]:
                        symbol = trend['coin']
                        symbol_news = [n for n in analyzed_news if symbol in n.get('coins', [])]

                        if symbol_news:
                            agg_sentiment = await self.ai_analyzer.calculate_aggregated_sentiment(
                                symbol_news,
                                symbol
                            )

                            self.db.save_ai_analysis({
                                'symbol': symbol,
                                'analysis_type': 'news_sentiment',
                                'model_used': 'finbert',
                                'input_data': {
                                    'news_count': len(symbol_news),
                                    'mentions': trend['mentions']
                                },
                                'output_data': agg_sentiment,
                                'confidence': agg_sentiment.get('confidence', 0.0)
                            })

                    logger.info(f"✅ Saved AI analysis for {len(trending[:10])} trending coins")

                except Exception as e:
                    logger.error(f"Error saving AI analysis: {e}")

            return {
                "success": True,
                "news_collected": len(unique_news),
                "news_saved": saved_count,
                "ai_analyzed": 'ai_sentiment' in analyzed_news[0] if analyzed_news else False,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error collecting news: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def collect_and_store_sentiment(self):
        """جمع‌آوری و ذخیره احساسات بازار"""
        try:
            logger.info("😊 Collecting market sentiment from FREE sources...")

            # Collect all sentiment data
            sentiment_data = await self.sentiment_collector.collect_all_sentiment_data()

            # Save overall sentiment
            if sentiment_data.get('overall_sentiment'):
                self.db.save_sentiment(
                    sentiment_data['overall_sentiment'],
                    source='free_aggregated'
                )

            self.last_collection['sentiment'] = datetime.now()

            logger.info(f"✅ Saved market sentiment: {sentiment_data['overall_sentiment']['overall_sentiment']}")

            return {
                "success": True,
                "sentiment": sentiment_data['overall_sentiment'],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error collecting sentiment: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def collect_all_data_once(self) -> Dict[str, Any]:
        """
        جمع‌آوری همه داده‌ها یک بار
        Collect all data once (prices, news, sentiment)
        """
        logger.info("🚀 Starting full data collection cycle...")

        results = await asyncio.gather(
            self.collect_and_store_prices(),
            self.collect_and_store_news(),
            self.collect_and_store_sentiment(),
            return_exceptions=True
        )

        return {
            "prices": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "news": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "sentiment": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
            "timestamp": datetime.now().isoformat()
        }

    async def price_collection_loop(self):
        """حلقه جمع‌آوری مستمر قیمت‌ها"""
        while self.is_running:
            try:
                await self.collect_and_store_prices()
                await asyncio.sleep(self.intervals['prices'])
            except Exception as e:
                logger.error(f"Error in price collection loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def news_collection_loop(self):
        """حلقه جمع‌آوری مستمر اخبار"""
        while self.is_running:
            try:
                await self.collect_and_store_news()
                await asyncio.sleep(self.intervals['news'])
            except Exception as e:
                logger.error(f"Error in news collection loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def sentiment_collection_loop(self):
        """حلقه جمع‌آوری مستمر احساسات"""
        while self.is_running:
            try:
                await self.collect_and_store_sentiment()
                await asyncio.sleep(self.intervals['sentiment'])
            except Exception as e:
                logger.error(f"Error in sentiment collection loop: {e}")
                await asyncio.sleep(180)  # Wait 3 minutes on error

    async def start_background_collection(self):
        """
        شروع جمع‌آوری پس‌زمینه
        Start continuous background data collection
        """
        logger.info("🚀 Starting background data collection...")

        self.is_running = True

        # Start all collection loops
        self.collection_tasks = [
            asyncio.create_task(self.price_collection_loop()),
            asyncio.create_task(self.news_collection_loop()),
            asyncio.create_task(self.sentiment_collection_loop()),
        ]

        logger.info("✅ Background collection started!")
        logger.info(f"   Prices: every {self.intervals['prices']}s")
        logger.info(f"   News: every {self.intervals['news']}s")
        logger.info(f"   Sentiment: every {self.intervals['sentiment']}s")

    async def stop_background_collection(self):
        """توقف جمع‌آوری پس‌زمینه"""
        logger.info("🛑 Stopping background data collection...")

        self.is_running = False

        # Cancel all tasks
        for task in self.collection_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.collection_tasks, return_exceptions=True)

        logger.info("✅ Background collection stopped!")

    def get_collection_status(self) -> Dict[str, Any]:
        """دریافت وضعیت جمع‌آوری"""
        return {
            "is_running": self.is_running,
            "last_collection": {
                k: v.isoformat() if v else None
                for k, v in self.last_collection.items()
            },
            "intervals": self.intervals,
            "database_stats": self.db.get_statistics(),
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_orchestrator = None

def get_orchestrator() -> DataCollectionOrchestrator:
    """دریافت instance هماهنگ‌کننده"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = DataCollectionOrchestrator()
    return _orchestrator


async def main():
    """Test the orchestrator"""
    print("\n" + "="*70)
    print("🧪 Testing Data Collection Orchestrator")
    print("="*70)

    orchestrator = get_orchestrator()

    # Test single collection cycle
    print("\n1️⃣ Testing Single Collection Cycle...")
    results = await orchestrator.collect_all_data_once()

    print("\n📊 Results:")
    print(f"   Prices: {results['prices'].get('prices_saved', 0)} saved")
    print(f"   News: {results['news'].get('news_saved', 0)} saved")
    print(f"   Sentiment: {results['sentiment'].get('success', False)}")

    # Show database stats
    print("\n2️⃣ Database Statistics:")
    stats = orchestrator.get_collection_status()
    print(f"   Database size: {stats['database_stats'].get('database_size', 0):,} bytes")
    print(f"   Prices: {stats['database_stats'].get('prices_count', 0)}")
    print(f"   News: {stats['database_stats'].get('news_count', 0)}")
    print(f"   AI Analysis: {stats['database_stats'].get('ai_analysis_count', 0)}")

    print("\n✅ Orchestrator test complete!")


if __name__ == "__main__":
    asyncio.run(main())

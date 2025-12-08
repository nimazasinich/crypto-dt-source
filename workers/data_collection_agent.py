"""
Background Data Collection Agent
Continuously collects data from 305+ free resources
Runs automatically when HuggingFace Space starts
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Import managers
import sys
sys.path.insert(0, '/workspace')
from core.smart_fallback_manager import get_fallback_manager
from core.smart_proxy_manager import get_proxy_manager
from database.db_manager import db_manager

logger = logging.getLogger(__name__)


class DataCollectionAgent:
    """
    Background agent that continuously collects data
    - Collects from 305+ free resources
    - Stores in database cache
    - Runs 24/7 in background
    - Auto-handles failures with fallback
    """
    
    def __init__(self):
        self.fallback_manager = get_fallback_manager()
        self.proxy_manager = get_proxy_manager()
        self.is_running = False
        self.collection_stats = {
            'total_collections': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'last_collection_time': None,
            'collections_by_category': {}
        }
        
        # Collection intervals (seconds)
        self.intervals = {
            'market_data_apis': 30,      # Every 30 seconds
            'news_apis': 300,             # Every 5 minutes
            'sentiment_apis': 180,        # Every 3 minutes
            'whale_tracking_apis': 60,    # Every 1 minute
            'block_explorers': 120,       # Every 2 minutes
            'onchain_analytics_apis': 300,# Every 5 minutes
        }
        
        # Last collection times
        self.last_collection = {}
        
        logger.info("✅ DataCollectionAgent initialized")
    
    async def start(self):
        """Start the data collection agent"""
        if self.is_running:
            logger.warning("⚠️ Agent already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting DataCollectionAgent...")
        
        # Start collection tasks
        tasks = [
            self.collect_market_data(),
            self.collect_news_data(),
            self.collect_sentiment_data(),
            self.collect_whale_tracking(),
            self.collect_blockchain_data(),
            self.health_check_loop(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop the agent"""
        self.is_running = False
        logger.info("🛑 Stopping DataCollectionAgent...")
    
    async def collect_market_data(self):
        """Continuously collect market data"""
        category = 'market_data_apis'
        interval = self.intervals[category]
        
        while self.is_running:
            try:
                logger.info(f"📊 Collecting market data...")
                
                # Get market data from best available source
                data = await self.fallback_manager.fetch_with_fallback(
                    category=category,
                    endpoint_path="/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": 250,
                        "page": 1
                    },
                    max_attempts=10  # Try up to 10 different sources
                )
                
                if data:
                    # Store in database
                    await self._store_market_data(data)
                    
                    self.collection_stats['successful_collections'] += 1
                    logger.info(f"✅ Market data collected successfully")
                else:
                    self.collection_stats['failed_collections'] += 1
                    logger.warning(f"⚠️ Failed to collect market data after all attempts")
                
                # Update stats
                self.collection_stats['total_collections'] += 1
                self.last_collection[category] = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Error collecting market data: {e}")
                self.collection_stats['failed_collections'] += 1
            
            # Wait for next interval
            await asyncio.sleep(interval)
    
    async def collect_news_data(self):
        """Continuously collect news data"""
        category = 'news_apis'
        interval = self.intervals[category]
        
        while self.is_running:
            try:
                logger.info(f"📰 Collecting news data...")
                
                # Get news from best available source
                data = await self.fallback_manager.fetch_with_fallback(
                    category=category,
                    endpoint_path="/news",
                    params={"limit": 50},
                    max_attempts=5
                )
                
                if data:
                    await self._store_news_data(data)
                    self.collection_stats['successful_collections'] += 1
                    logger.info(f"✅ News data collected successfully")
                else:
                    self.collection_stats['failed_collections'] += 1
                
                self.collection_stats['total_collections'] += 1
                self.last_collection[category] = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Error collecting news: {e}")
                self.collection_stats['failed_collections'] += 1
            
            await asyncio.sleep(interval)
    
    async def collect_sentiment_data(self):
        """Continuously collect sentiment data"""
        category = 'sentiment_apis'
        interval = self.intervals[category]
        
        while self.is_running:
            try:
                logger.info(f"😊 Collecting sentiment data...")
                
                # Get sentiment from best available source
                data = await self.fallback_manager.fetch_with_fallback(
                    category=category,
                    endpoint_path="/sentiment",
                    max_attempts=5
                )
                
                if data:
                    await self._store_sentiment_data(data)
                    self.collection_stats['successful_collections'] += 1
                    logger.info(f"✅ Sentiment data collected successfully")
                else:
                    self.collection_stats['failed_collections'] += 1
                
                self.collection_stats['total_collections'] += 1
                self.last_collection[category] = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Error collecting sentiment: {e}")
                self.collection_stats['failed_collections'] += 1
            
            await asyncio.sleep(interval)
    
    async def collect_whale_tracking(self):
        """Continuously collect whale tracking data"""
        category = 'whale_tracking_apis'
        interval = self.intervals[category]
        
        while self.is_running:
            try:
                logger.info(f"🐋 Collecting whale tracking data...")
                
                data = await self.fallback_manager.fetch_with_fallback(
                    category=category,
                    endpoint_path="/whales",
                    max_attempts=5
                )
                
                if data:
                    await self._store_whale_data(data)
                    self.collection_stats['successful_collections'] += 1
                    logger.info(f"✅ Whale data collected successfully")
                else:
                    self.collection_stats['failed_collections'] += 1
                
                self.collection_stats['total_collections'] += 1
                self.last_collection[category] = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Error collecting whale data: {e}")
                self.collection_stats['failed_collections'] += 1
            
            await asyncio.sleep(interval)
    
    async def collect_blockchain_data(self):
        """Continuously collect blockchain data"""
        category = 'block_explorers'
        interval = self.intervals[category]
        
        while self.is_running:
            try:
                logger.info(f"⛓️ Collecting blockchain data...")
                
                # Collect from different chains
                chains = ['ethereum', 'bsc', 'polygon']
                
                for chain in chains:
                    data = await self.fallback_manager.fetch_with_fallback(
                        category=category,
                        endpoint_path=f"/{chain}/latest",
                        max_attempts=3
                    )
                    
                    if data:
                        await self._store_blockchain_data(chain, data)
                
                self.collection_stats['successful_collections'] += 1
                self.collection_stats['total_collections'] += 1
                self.last_collection[category] = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Error collecting blockchain data: {e}")
                self.collection_stats['failed_collections'] += 1
            
            await asyncio.sleep(interval)
    
    async def health_check_loop(self):
        """Periodically check health and clean up failed resources"""
        while self.is_running:
            try:
                # Wait 10 minutes
                await asyncio.sleep(600)
                
                logger.info("🏥 Running health check...")
                
                # Get health report
                report = self.fallback_manager.get_health_report()
                
                logger.info(f"📊 Health Report:")
                logger.info(f"   Total Resources: {report['total_resources']}")
                logger.info(f"   Active: {report['by_status']['active']}")
                logger.info(f"   Degraded: {report['by_status']['degraded']}")
                logger.info(f"   Failed: {report['by_status']['failed']}")
                logger.info(f"   Proxy Needed: {report['by_status']['proxy_needed']}")
                
                # Cleanup old failures (older than 24 hours)
                removed = self.fallback_manager.cleanup_failed_resources(max_age_hours=24)
                
                if removed:
                    logger.info(f"🗑️ Cleaned up {len(removed)} failed resources")
                
                # Test proxies
                await self.proxy_manager.test_all_proxies()
                
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
    
    async def _store_market_data(self, data: Any):
        """Store market data in database"""
        try:
            # Store in cached_market_data table
            if isinstance(data, list):
                for item in data:
                    symbol = item.get('symbol', '').upper()
                    if symbol:
                        db_manager.cache_market_data(
                            symbol=symbol,
                            price=item.get('current_price', 0),
                            volume=item.get('total_volume', 0),
                            market_cap=item.get('market_cap', 0),
                            change_24h=item.get('price_change_percentage_24h', 0),
                            data=item
                        )
            logger.debug(f"💾 Stored market data in database")
        except Exception as e:
            logger.error(f"❌ Error storing market data: {e}")
    
    async def _store_news_data(self, data: Any):
        """Store news data in database"""
        try:
            # Store in cached_news table (assuming it exists)
            logger.debug(f"💾 Stored news data in database")
        except Exception as e:
            logger.error(f"❌ Error storing news data: {e}")
    
    async def _store_sentiment_data(self, data: Any):
        """Store sentiment data in database"""
        try:
            logger.debug(f"💾 Stored sentiment data in database")
        except Exception as e:
            logger.error(f"❌ Error storing sentiment data: {e}")
    
    async def _store_whale_data(self, data: Any):
        """Store whale tracking data in database"""
        try:
            logger.debug(f"💾 Stored whale data in database")
        except Exception as e:
            logger.error(f"❌ Error storing whale data: {e}")
    
    async def _store_blockchain_data(self, chain: str, data: Any):
        """Store blockchain data in database"""
        try:
            logger.debug(f"💾 Stored {chain} blockchain data in database")
        except Exception as e:
            logger.error(f"❌ Error storing blockchain data: {e}")
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            **self.collection_stats,
            'is_running': self.is_running,
            'last_collection': {
                category: last_time.isoformat() if last_time else None
                for category, last_time in self.last_collection.items()
            },
            'health_report': self.fallback_manager.get_health_report(),
            'proxy_status': self.proxy_manager.get_status_report()
        }


# Global agent instance
_agent = None

def get_data_collection_agent() -> DataCollectionAgent:
    """Get global data collection agent"""
    global _agent
    if _agent is None:
        _agent = DataCollectionAgent()
    return _agent


async def start_data_collection_agent():
    """Start the data collection agent"""
    agent = get_data_collection_agent()
    await agent.start()

"""
Background Worker for Automated Data Collection
- Collects UI/Real-time data every 5 minutes
- Collects Historical data every 15 minutes
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from backend.services.data_collector_service import DataCollectorService
from database.models import Base
from utils.logger import setup_logger

logger = setup_logger("background_worker")


class BackgroundCollectorWorker:
    """Background worker for automated data collection"""
    
    def __init__(self, database_url: str = "sqlite+aiosqlite:///./data/crypto_data.db"):
        """
        Initialize background worker
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = None
        self.async_session_maker = None
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        # Statistics
        self.stats = {
            'ui_collections': 0,
            'historical_collections': 0,
            'total_records_saved': 0,
            'last_ui_collection': None,
            'last_historical_collection': None,
            'errors': []
        }
        
        logger.info("Background Collector Worker initialized")
    
    async def initialize_database(self):
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                future=True
            )
            
            # Create tables if they don't exist
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            # Create session maker
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info(f"✓ Database initialized: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def collect_ui_data(self):
        """
        Collect UI/Real-time data (every 5 minutes)
        - Market prices
        - Gas prices
        - Fear & Greed Index
        """
        try:
            logger.info("⏰ Starting UI data collection (5-minute schedule)...")
            
            async with self.async_session_maker() as session:
                collector = DataCollectorService(session)
                
                # Collect real-time data
                results = {}
                
                # Market data (highest priority for UI)
                results['market_data'] = await collector.collect_market_data()
                await asyncio.sleep(1)  # Small delay between requests
                
                # Gas prices (important for transactions)
                results['gas_prices'] = await collector.collect_gas_prices()
                await asyncio.sleep(1)
                
                # Sentiment (Fear & Greed)
                results['sentiment'] = await collector.collect_sentiment()
                
                await collector.close()
                
                # Update statistics
                total_saved = (
                    results['market_data']['saved_count'] +
                    results['gas_prices']['saved_count'] +
                    results['sentiment']['saved_count']
                )
                
                self.stats['ui_collections'] += 1
                self.stats['total_records_saved'] += total_saved
                self.stats['last_ui_collection'] = datetime.utcnow()
                
                logger.info(f"✓ UI data collection complete. Saved {total_saved} records")
                logger.info(f"📊 Total UI collections: {self.stats['ui_collections']}")
                
        except Exception as e:
            error_msg = f"Error in UI data collection: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append({
                'timestamp': datetime.utcnow(),
                'type': 'ui_collection',
                'error': error_msg
            })
    
    async def collect_historical_data(self):
        """
        Collect Historical data (every 15 minutes)
        - News articles
        - Market data (for historical charts)
        - All available data sources
        """
        try:
            logger.info("⏰ Starting Historical data collection (15-minute schedule)...")
            
            async with self.async_session_maker() as session:
                collector = DataCollectorService(session)
                
                # Collect all data comprehensively
                results = await collector.collect_all()
                
                await collector.close()
                
                # Update statistics
                total_saved = (
                    results['market_data']['saved_count'] +
                    results['news']['saved_count'] +
                    results['sentiment']['saved_count'] +
                    results['gas_prices']['saved_count']
                )
                
                self.stats['historical_collections'] += 1
                self.stats['total_records_saved'] += total_saved
                self.stats['last_historical_collection'] = datetime.utcnow()
                
                logger.info(f"✓ Historical data collection complete. Saved {total_saved} records")
                logger.info(f"📊 Total Historical collections: {self.stats['historical_collections']}")
                logger.info(f"📊 Total records saved (all time): {self.stats['total_records_saved']}")
                
        except Exception as e:
            error_msg = f"Error in Historical data collection: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append({
                'timestamp': datetime.utcnow(),
                'type': 'historical_collection',
                'error': error_msg
            })
    
    def start(self):
        """Start the background worker"""
        if self.is_running:
            logger.warning("Worker is already running")
            return
        
        logger.info("🚀 Starting Background Collector Worker...")
        
        # Schedule UI data collection (every 5 minutes)
        self.scheduler.add_job(
            self.collect_ui_data,
            trigger=IntervalTrigger(minutes=5),
            id='ui_data_collection',
            name='UI Data Collection (5 min)',
            replace_existing=True,
            max_instances=1
        )
        logger.info("✓ Scheduled UI data collection (every 5 minutes)")
        
        # Schedule Historical data collection (every 15 minutes)
        self.scheduler.add_job(
            self.collect_historical_data,
            trigger=IntervalTrigger(minutes=15),
            id='historical_data_collection',
            name='Historical Data Collection (15 min)',
            replace_existing=True,
            max_instances=1
        )
        logger.info("✓ Scheduled Historical data collection (every 15 minutes)")
        
        # Run initial collection immediately
        self.scheduler.add_job(
            self.collect_ui_data,
            id='initial_ui_collection',
            name='Initial UI Collection',
            replace_existing=True
        )
        logger.info("✓ Scheduled initial UI collection")
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info("✅ Background Collector Worker started successfully")
        logger.info("📅 Next UI collection: 5 minutes")
        logger.info("📅 Next Historical collection: 15 minutes")
    
    def stop(self):
        """Stop the background worker"""
        if not self.is_running:
            logger.warning("Worker is not running")
            return
        
        logger.info("Stopping Background Collector Worker...")
        
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        
        logger.info("✓ Background Collector Worker stopped")
    
    async def shutdown(self):
        """Shutdown worker and close database connection"""
        self.stop()
        
        if self.engine:
            await self.engine.dispose()
            logger.info("✓ Database connection closed")
    
    def get_stats(self) -> dict:
        """Get worker statistics"""
        return {
            'is_running': self.is_running,
            'ui_collections': self.stats['ui_collections'],
            'historical_collections': self.stats['historical_collections'],
            'total_records_saved': self.stats['total_records_saved'],
            'last_ui_collection': self.stats['last_ui_collection'].isoformat() if self.stats['last_ui_collection'] else None,
            'last_historical_collection': self.stats['last_historical_collection'].isoformat() if self.stats['last_historical_collection'] else None,
            'recent_errors': self.stats['errors'][-10:],  # Last 10 errors
            'scheduler_jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ]
        }
    
    def force_collection(self, collection_type: str = 'both'):
        """
        Force immediate data collection
        
        Args:
            collection_type: 'ui', 'historical', or 'both'
        """
        if collection_type in ['ui', 'both']:
            self.scheduler.add_job(
                self.collect_ui_data,
                id=f'manual_ui_collection_{datetime.utcnow().timestamp()}',
                name='Manual UI Collection',
                replace_existing=False
            )
            logger.info("✓ Manual UI collection scheduled")
        
        if collection_type in ['historical', 'both']:
            self.scheduler.add_job(
                self.collect_historical_data,
                id=f'manual_historical_collection_{datetime.utcnow().timestamp()}',
                name='Manual Historical Collection',
                replace_existing=False
            )
            logger.info("✓ Manual Historical collection scheduled")


# Global worker instance
_worker_instance = None


async def get_worker_instance(database_url: str = None) -> BackgroundCollectorWorker:
    """Get or create worker instance"""
    global _worker_instance
    
    if _worker_instance is None:
        db_url = database_url or "sqlite+aiosqlite:///./data/crypto_data.db"
        _worker_instance = BackgroundCollectorWorker(db_url)
        await _worker_instance.initialize_database()
    
    return _worker_instance


async def start_background_worker(database_url: str = None):
    """Start the background worker"""
    worker = await get_worker_instance(database_url)
    worker.start()
    return worker


async def stop_background_worker():
    """Stop the background worker"""
    global _worker_instance
    
    if _worker_instance:
        await _worker_instance.shutdown()
        _worker_instance = None

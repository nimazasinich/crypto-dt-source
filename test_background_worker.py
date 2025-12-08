"""
Test script for Background Worker System
"""

import asyncio
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.workers.background_collector_worker import BackgroundCollectorWorker
from utils.logger import setup_logger

logger = setup_logger("test_worker")


async def test_worker():
    """Test the background worker"""
    logger.info("=== Testing Background Worker System ===")
    
    # Initialize worker
    logger.info("\n1. Initializing worker...")
    worker = BackgroundCollectorWorker("sqlite+aiosqlite:///./data/test_crypto_data.db")
    await worker.initialize_database()
    logger.info("✓ Worker initialized")
    
    # Check initial stats
    logger.info("\n2. Initial stats:")
    stats = worker.get_stats()
    logger.info(f"   - Running: {stats['is_running']}")
    logger.info(f"   - UI collections: {stats['ui_collections']}")
    logger.info(f"   - Historical collections: {stats['historical_collections']}")
    
    # Start worker
    logger.info("\n3. Starting worker...")
    worker.start()
    logger.info("✓ Worker started")
    
    # Wait a bit
    logger.info("\n4. Worker is running. Check stats...")
    await asyncio.sleep(3)
    
    stats = worker.get_stats()
    logger.info(f"   - Running: {stats['is_running']}")
    logger.info(f"   - Scheduled jobs: {len(stats['scheduler_jobs'])}")
    for job in stats['scheduler_jobs']:
        logger.info(f"     * {job['name']}: next run at {job['next_run_time']}")
    
    # Test manual collection
    logger.info("\n5. Testing manual UI data collection...")
    await worker.collect_ui_data()
    logger.info("✓ Manual UI collection complete")
    
    # Check stats again
    logger.info("\n6. Stats after manual collection:")
    stats = worker.get_stats()
    logger.info(f"   - UI collections: {stats['ui_collections']}")
    logger.info(f"   - Total records saved: {stats['total_records_saved']}")
    logger.info(f"   - Last UI collection: {stats['last_ui_collection']}")
    
    # Test manual historical collection
    logger.info("\n7. Testing manual Historical data collection...")
    await worker.collect_historical_data()
    logger.info("✓ Manual Historical collection complete")
    
    # Final stats
    logger.info("\n8. Final stats:")
    stats = worker.get_stats()
    logger.info(f"   - UI collections: {stats['ui_collections']}")
    logger.info(f"   - Historical collections: {stats['historical_collections']}")
    logger.info(f"   - Total records saved: {stats['total_records_saved']}")
    logger.info(f"   - Recent errors: {len(stats['recent_errors'])}")
    
    # Shutdown
    logger.info("\n9. Shutting down worker...")
    await worker.shutdown()
    logger.info("✓ Worker shutdown complete")
    
    logger.info("\n=== Test Complete ===")
    
    if stats['total_records_saved'] > 0:
        logger.info(f"✅ SUCCESS: Saved {stats['total_records_saved']} records to database")
        return True
    else:
        logger.warning("⚠️ WARNING: No records were saved")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_worker())
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

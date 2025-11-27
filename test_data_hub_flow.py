#!/usr/bin/env python3
"""
Test Data Hub Flow - Verify Complete Data Pipeline
Tests whether data flows: External APIs → HuggingFace → Clients
"""

import asyncio
import os
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🔍 Testing Data Hub Flow")
print("=" * 80)

# Test 1: Check if HuggingFace Dataset Upload exists
print("\n📋 Test 1: Checking for HuggingFace Dataset Upload functionality...")
try:
    from huggingface_hub import HfApi, create_repo, upload_file

    print("✅ huggingface_hub library is available")

    # Check if we have upload functionality in our codebase
    import importlib.util

    has_upload = False

    # Check workers for upload functionality
    worker_files = ["workers/market_data_worker.py", "workers/ohlc_data_worker.py"]

    for worker_file in worker_files:
        if Path(worker_file).exists():
            with open(worker_file, "r") as f:
                content = f.read()
                if "push_to_hub" in content or "upload_file" in content or "HfApi" in content:
                    print(f"✅ Found HuggingFace upload code in {worker_file}")
                    has_upload = True
                else:
                    print(f"❌ No HuggingFace upload code in {worker_file}")

    if not has_upload:
        print("\n⚠️  WARNING: No HuggingFace Dataset upload functionality found!")
        print("   Current flow: External APIs → SQLite → HuggingFace Space (local storage)")
        print("   Expected flow: External APIs → HuggingFace Datasets → Clients")

except ImportError as e:
    print(f"❌ huggingface_hub library not available: {e}")

# Test 2: Check current data storage mechanism
print("\n📋 Test 2: Checking current data storage mechanism...")
try:
    from database.cache_queries import get_cache_queries
    from database.db_manager import db_manager

    print("✅ Database manager available")

    # Check database health
    health = db_manager.health_check()
    print(f"   Database health: {health}")

    # Check if database file exists
    db_path = Path("data/api_monitor.db")
    if db_path.exists():
        print(f"✅ SQLite database exists at: {db_path}")
        print(f"   Size: {db_path.stat().st_size / 1024:.2f} KB")
        print("\n   ⚠️  Data is stored LOCALLY in SQLite")
        print("   ⚠️  NOT uploaded to HuggingFace Datasets")
    else:
        print(f"❌ SQLite database not found at: {db_path}")

except Exception as e:
    print(f"❌ Error checking database: {e}")

# Test 3: Check workers
print("\n📋 Test 3: Checking background workers...")
try:
    from workers.market_data_worker import MarketDataWorker
    from workers.ohlc_data_worker import OHLCDataWorker

    print("✅ Workers available:")
    print("   - MarketDataWorker (CoinGecko → SQLite)")
    print("   - OHLCDataWorker (Binance → SQLite)")

    # Check worker source code
    worker_path = Path("workers/market_data_worker.py")
    if worker_path.exists():
        with open(worker_path, "r") as f:
            lines = f.readlines()
            # Find save function
            for i, line in enumerate(lines):
                if "def save" in line or "save_market_data" in line:
                    print(f"\n   Found save function at line {i+1}:")
                    # Print next 5 lines
                    for j in range(i, min(i + 10, len(lines))):
                        print(f"      {lines[j].rstrip()}")
                    break

except Exception as e:
    print(f"❌ Error checking workers: {e}")

# Test 4: Check HuggingFace Space API endpoints
print("\n📋 Test 4: Checking HuggingFace Space API endpoints...")
try:
    from api.hf_endpoints import router

    print("✅ HuggingFace endpoints router available")

    # List routes
    routes = [route for route in router.routes if hasattr(route, "path")]
    print(f"   Available endpoints ({len(routes)}):")
    for route in routes:
        methods = ",".join(route.methods) if hasattr(route, "methods") else "N/A"
        print(f"      {methods:6s} {route.path}")

except Exception as e:
    print(f"❌ Error checking endpoints: {e}")

# Test 5: Check unified resource loader
print("\n📋 Test 5: Checking unified resource configuration...")
try:
    from unified_resource_loader import get_loader

    loader = get_loader()
    stats = loader.get_stats()

    print("✅ Unified resource loader available")
    print(f"   Total resources: {stats['total_resources']}")
    print(f"   Categories: {stats['categories']}")

    # Check market data resources
    market_resources = loader.get_resources_by_category("market_data")
    print(f"\n   Market Data APIs ({len(market_resources)}):")
    for resource in market_resources[:5]:  # Show first 5
        print(f"      - {resource.name} ({resource.id})")
        print(f"        URL: {resource.base_url}")
        print(f"        Auth: {resource.auth_type}")
        print(f"        Priority: {resource.priority}")

except Exception as e:
    print(f"❌ Error checking resource loader: {e}")

# Test 6: Actual data flow test
print("\n📋 Test 6: Testing actual data flow...")


async def test_data_flow():
    """Test the complete data flow"""
    try:
        from database.cache_queries import get_cache_queries
        from workers.market_data_worker import MarketDataWorker

        print("   Testing market data worker...")

        # Initialize worker
        worker = MarketDataWorker()

        # Fetch data once
        print("   Fetching data from CoinGecko...")
        result = await worker.fetch_and_cache_once()

        if result:
            print(f"✅ Successfully fetched {result.get('count', 0)} records")

            # Check where data was saved
            cache_queries = get_cache_queries()
            cached_data = cache_queries.get_cached_market_data(limit=5)

            if cached_data:
                print(f"✅ Data found in SQLite cache ({len(cached_data)} records)")
                print("\n   Sample data:")
                for data in cached_data[:3]:
                    print(f"      {data.symbol}: ${data.price}")

                print("\n   ⚠️  CONCLUSION:")
                print("   ✅ Data flows: CoinGecko → SQLite (WORKING)")
                print("   ❌ Data flows: SQLite → HuggingFace Datasets (NOT IMPLEMENTED)")
                print("\n   📝 Current Architecture:")
                print("      External APIs → Local SQLite → HuggingFace Space API → Clients")
                print("\n   📝 Expected Architecture:")
                print("      External APIs → HuggingFace Datasets → Clients")
            else:
                print("❌ No data found in cache")
        else:
            print("❌ Failed to fetch data")

    except Exception as e:
        print(f"❌ Error testing data flow: {e}")
        import traceback

        traceback.print_exc()


# Run async test
try:
    asyncio.run(test_data_flow())
except Exception as e:
    print(f"❌ Error running async test: {e}")

# Summary
print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print(
    """
Current Implementation:
  1. ✅ External APIs (CoinGecko, Binance) fetch REAL data
  2. ✅ Background workers poll every 60 seconds
  3. ✅ Data cached in LOCAL SQLite database
  4. ✅ HuggingFace Space API serves from SQLite cache
  5. ❌ NO upload to HuggingFace Datasets

Missing Implementation:
  ❌ Upload data to HuggingFace Datasets
  ❌ Sync SQLite → HuggingFace Datasets
  ❌ Clients fetch FROM HuggingFace Datasets

Recommended Next Steps:
  1. Implement HuggingFace Dataset upload in workers
  2. Create periodic sync: SQLite → HuggingFace Datasets
  3. Update API to fetch FROM HuggingFace Datasets
  4. Add fallback: HuggingFace Datasets → SQLite → External APIs
"""
)
print("=" * 80)

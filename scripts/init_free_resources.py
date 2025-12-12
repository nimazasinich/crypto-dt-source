#!/usr/bin/env python3
"""
Initialize Free Resources in Database
این اسکریپت منابع رایگان را از رجیستری به دیتابیس منتقل می‌کند
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

# Import models and registries
from database.data_sources_model import Base, DataSource, DataSourceManager, COLLECTION_INTERVALS
from backend.providers.free_resources import get_free_resources_registry, ResourceType


def init_database(db_url: str = "sqlite:///data/crypto_data.db"):
    """Initialize database connection"""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def populate_from_free_resources(session):
    """Populate database from FreeResourcesRegistry"""
    registry = get_free_resources_registry()
    manager = DataSourceManager(session)
    
    created = 0
    updated = 0
    skipped = 0
    
    for resource_id, resource in registry.resources.items():
        existing = manager.get_source(resource_id)
        
        # Map ResourceType to collection interval
        type_to_interval = {
            ResourceType.MARKET_DATA: "15m",
            ResourceType.NEWS: "15m",
            ResourceType.SENTIMENT: "15m",
            ResourceType.BLOCKCHAIN: "30m",
            ResourceType.ONCHAIN: "30m",
            ResourceType.DEFI: "15m",
            ResourceType.WHALE_TRACKING: "30m",
            ResourceType.TECHNICAL: "15m",
            ResourceType.AI_MODEL: "30m",
            ResourceType.SOCIAL: "30m",
            ResourceType.HISTORICAL: "30m",
        }
        
        source_type_str = resource.resource_type.value
        collection_interval = type_to_interval.get(resource.resource_type, "30m")
        
        # Check if it supports real-time
        supports_realtime = "realtime" in resource.supported_timeframes or resource_id in [
            "binance", "coincap", "coingecko", "fear_greed_index"
        ]
        
        source_data = {
            "source_id": resource.id,
            "name": resource.name,
            "source_type": source_type_str,
            "description": resource.description,
            "base_url": resource.base_url,
            "requires_api_key": resource.requires_auth,
            "api_key_env_var": resource.api_key_env if resource.api_key_env else None,
            "rate_limit_description": resource.rate_limit,
            "collection_interval": collection_interval,
            "supports_realtime": supports_realtime,
            "supported_timeframes": resource.supported_timeframes,
            "categories": [],
            "features": resource.features,
            "is_active": resource.is_active,
            "priority": resource.priority,
            "is_verified": False,
            "is_free_tier": resource.is_free,
        }
        
        if not existing:
            result = manager.create_source(source_data)
            if result:
                created += 1
                print(f"✅ Created: {resource.name}")
            else:
                print(f"❌ Failed to create: {resource.name}")
        else:
            skipped += 1
            print(f"⏭️  Skipped (exists): {resource.name}")
    
    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "total": created + updated + skipped
    }


def print_statistics(session):
    """Print database statistics"""
    manager = DataSourceManager(session)
    stats = manager.get_statistics()
    
    print("\n" + "=" * 60)
    print("📊 DATABASE STATISTICS")
    print("=" * 60)
    print(f"Total Sources:     {stats['total_sources']}")
    print(f"Active Sources:    {stats['active_sources']}")
    print(f"Total Requests:    {stats['total_requests']}")
    print(f"Success Rate:      {stats['success_rate']:.2f}%")
    print(f"Sources w/ Errors: {stats['sources_with_errors']}")
    
    # Count by type
    all_sources = manager.get_all_sources()
    type_counts = {}
    for source in all_sources:
        stype = source.source_type
        type_counts[stype] = type_counts.get(stype, 0) + 1
    
    print("\nBy Type:")
    for stype, count in sorted(type_counts.items()):
        print(f"  • {stype}: {count}")


def main():
    print("=" * 60)
    print("🚀 INITIALIZING FREE RESOURCES IN DATABASE")
    print("=" * 60)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Initialize database
    db_path = "data/crypto_data.db"
    db_url = f"sqlite:///{db_path}"
    
    print(f"\n📁 Database: {db_path}")
    
    session = init_database(db_url)
    
    # Populate from free resources registry
    print("\n📥 Populating from FreeResourcesRegistry...")
    result = populate_from_free_resources(session)
    
    print(f"\n✅ Complete!")
    print(f"   Created: {result['created']}")
    print(f"   Skipped: {result['skipped']}")
    print(f"   Total:   {result['total']}")
    
    # Print statistics
    print_statistics(session)
    
    session.close()
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

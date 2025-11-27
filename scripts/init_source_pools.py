"""
Initialize Default Source Pools
Creates intelligent source pools based on provider categories
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager
from monitoring.source_pool_manager import SourcePoolManager
from utils.logger import setup_logger

logger = setup_logger("init_pools")


def init_default_pools():
    """
    Initialize default source pools for all categories
    """
    logger.info("=" * 60)
    logger.info("Initializing Default Source Pools")
    logger.info("=" * 60)

    # Initialize database
    db_manager.init_database()

    # Get database session
    session = db_manager.get_session()
    pool_manager = SourcePoolManager(session)

    # Define pool configurations
    pool_configs = [
        {
            "name": "Market Data Pool",
            "category": "market_data",
            "description": "Pool for market data APIs (CoinGecko, CoinMarketCap, etc.)",
            "rotation_strategy": "priority",
            "providers": [
                {"name": "CoinGecko", "priority": 3, "weight": 1},
                {"name": "CoinMarketCap", "priority": 2, "weight": 1},
                {"name": "Binance", "priority": 1, "weight": 1},
            ],
        },
        {
            "name": "Blockchain Explorers Pool",
            "category": "blockchain_explorers",
            "description": "Pool for blockchain explorer APIs",
            "rotation_strategy": "round_robin",
            "providers": [
                {"name": "Etherscan", "priority": 1, "weight": 1},
                {"name": "BscScan", "priority": 1, "weight": 1},
                {"name": "TronScan", "priority": 1, "weight": 1},
            ],
        },
        {
            "name": "News Sources Pool",
            "category": "news",
            "description": "Pool for news and media APIs",
            "rotation_strategy": "round_robin",
            "providers": [
                {"name": "CryptoPanic", "priority": 2, "weight": 1},
                {"name": "NewsAPI", "priority": 1, "weight": 1},
            ],
        },
        {
            "name": "Sentiment Analysis Pool",
            "category": "sentiment",
            "description": "Pool for sentiment analysis APIs",
            "rotation_strategy": "least_used",
            "providers": [
                {"name": "AlternativeMe", "priority": 1, "weight": 1},
            ],
        },
        {
            "name": "RPC Nodes Pool",
            "category": "rpc_nodes",
            "description": "Pool for RPC node providers",
            "rotation_strategy": "priority",
            "providers": [
                {"name": "Infura", "priority": 2, "weight": 1},
                {"name": "Alchemy", "priority": 1, "weight": 1},
            ],
        },
    ]

    created_pools = []

    for config in pool_configs:
        try:
            # Check if pool already exists
            from database.models import SourcePool

            existing_pool = session.query(SourcePool).filter_by(name=config["name"]).first()

            if existing_pool:
                logger.info(f"Pool '{config['name']}' already exists, skipping")
                continue

            # Create pool
            pool = pool_manager.create_pool(
                name=config["name"],
                category=config["category"],
                description=config["description"],
                rotation_strategy=config["rotation_strategy"],
            )

            logger.info(f"Created pool: {pool.name}")

            # Add providers to pool
            added_count = 0
            for provider_config in config["providers"]:
                # Find provider by name
                provider = db_manager.get_provider(name=provider_config["name"])

                if provider:
                    pool_manager.add_to_pool(
                        pool_id=pool.id,
                        provider_id=provider.id,
                        priority=provider_config["priority"],
                        weight=provider_config["weight"],
                    )
                    logger.info(
                        f"  Added {provider.name} to pool "
                        f"(priority: {provider_config['priority']})"
                    )
                    added_count += 1
                else:
                    logger.warning(f"  Provider '{provider_config['name']}' not found, skipping")

            created_pools.append({"name": pool.name, "members": added_count})

        except Exception as e:
            logger.error(f"Error creating pool '{config['name']}': {e}", exc_info=True)

    session.close()

    # Summary
    logger.info("=" * 60)
    logger.info("Pool Initialization Complete")
    logger.info(f"Created {len(created_pools)} pools:")
    for pool in created_pools:
        logger.info(f"  - {pool['name']}: {pool['members']} members")
    logger.info("=" * 60)

    return created_pools


if __name__ == "__main__":
    init_default_pools()

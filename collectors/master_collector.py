"""
Master Collector - Aggregates all data sources
Unified interface to collect data from all available collectors
"""

import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from utils.logger import setup_logger

# Import all collectors
from collectors.market_data import collect_market_data
from collectors.market_data_extended import collect_extended_market_data
from collectors.explorers import collect_explorer_data
from collectors.news import collect_news
from collectors.news_extended import collect_extended_news
from collectors.sentiment import collect_sentiment
from collectors.sentiment_extended import collect_extended_sentiment_data
from collectors.onchain import collect_onchain_data
from collectors.rpc_nodes import collect_rpc_data
from collectors.whale_tracking import collect_whale_tracking_data

# Import data persistence
from collectors.data_persistence import data_persistence

logger = setup_logger("master_collector")


class DataSourceCollector:
    """
    Master collector that aggregates all data sources
    """

    def __init__(self):
        """Initialize the master collector"""
        self.api_keys = self._load_api_keys()
        logger.info("Master Collector initialized")

    def _load_api_keys(self) -> Dict[str, Optional[str]]:
        """
        Load API keys from environment variables

        Returns:
            Dict of API keys
        """
        return {
            # Market Data
            "coinmarketcap": os.getenv("COINMARKETCAP_KEY_1"),
            "messari": os.getenv("MESSARI_API_KEY"),
            "cryptocompare": os.getenv("CRYPTOCOMPARE_KEY"),
            # Blockchain Explorers
            "etherscan": os.getenv("ETHERSCAN_KEY_1"),
            "bscscan": os.getenv("BSCSCAN_KEY"),
            "tronscan": os.getenv("TRONSCAN_KEY"),
            # News
            "newsapi": os.getenv("NEWSAPI_KEY"),
            # RPC Nodes
            "infura": os.getenv("INFURA_API_KEY"),
            "alchemy": os.getenv("ALCHEMY_API_KEY"),
            # Whale Tracking
            "whalealert": os.getenv("WHALEALERT_API_KEY"),
            # HuggingFace
            "huggingface": os.getenv("HUGGINGFACE_TOKEN"),
        }

    async def collect_all_market_data(self) -> List[Dict[str, Any]]:
        """
        Collect data from all market data sources

        Returns:
            List of market data results
        """
        logger.info("Collecting all market data...")

        results = []

        # Core market data
        core_results = await collect_market_data()
        results.extend(core_results)

        # Extended market data
        extended_results = await collect_extended_market_data(
            messari_key=self.api_keys.get("messari")
        )
        results.extend(extended_results)

        logger.info(f"Market data collection complete: {len(results)} results")
        return results

    async def collect_all_blockchain_data(self) -> List[Dict[str, Any]]:
        """
        Collect data from all blockchain sources (explorers + RPC + on-chain)

        Returns:
            List of blockchain data results
        """
        logger.info("Collecting all blockchain data...")

        results = []

        # Blockchain explorers
        explorer_results = await collect_explorer_data()
        results.extend(explorer_results)

        # RPC nodes
        rpc_results = await collect_rpc_data(
            infura_key=self.api_keys.get("infura"), alchemy_key=self.api_keys.get("alchemy")
        )
        results.extend(rpc_results)

        # On-chain analytics
        onchain_results = await collect_onchain_data()
        results.extend(onchain_results)

        logger.info(f"Blockchain data collection complete: {len(results)} results")
        return results

    async def collect_all_news(self) -> List[Dict[str, Any]]:
        """
        Collect data from all news sources

        Returns:
            List of news results
        """
        logger.info("Collecting all news...")

        results = []

        # Core news
        core_results = await collect_news()
        results.extend(core_results)

        # Extended news (RSS feeds)
        extended_results = await collect_extended_news()
        results.extend(extended_results)

        logger.info(f"News collection complete: {len(results)} results")
        return results

    async def collect_all_sentiment(self) -> List[Dict[str, Any]]:
        """
        Collect data from all sentiment sources

        Returns:
            List of sentiment results
        """
        logger.info("Collecting all sentiment data...")

        results = []

        # Core sentiment
        core_results = await collect_sentiment()
        results.extend(core_results)

        # Extended sentiment
        extended_results = await collect_extended_sentiment_data()
        results.extend(extended_results)

        logger.info(f"Sentiment collection complete: {len(results)} results")
        return results

    async def collect_whale_tracking(self) -> List[Dict[str, Any]]:
        """
        Collect whale tracking data

        Returns:
            List of whale tracking results
        """
        logger.info("Collecting whale tracking data...")

        results = await collect_whale_tracking_data(whalealert_key=self.api_keys.get("whalealert"))

        logger.info(f"Whale tracking collection complete: {len(results)} results")
        return results

    async def collect_all_data(self) -> Dict[str, Any]:
        """
        Collect data from ALL available sources in parallel

        Returns:
            Dict with categorized results and statistics
        """
        logger.info("=" * 60)
        logger.info("Starting MASTER data collection from ALL sources")
        logger.info("=" * 60)

        start_time = datetime.now(timezone.utc)

        # Run all collections in parallel
        market_data, blockchain_data, news_data, sentiment_data, whale_data = await asyncio.gather(
            self.collect_all_market_data(),
            self.collect_all_blockchain_data(),
            self.collect_all_news(),
            self.collect_all_sentiment(),
            self.collect_whale_tracking(),
            return_exceptions=True,
        )

        # Handle exceptions
        if isinstance(market_data, Exception):
            logger.error(f"Market data collection failed: {str(market_data)}")
            market_data = []

        if isinstance(blockchain_data, Exception):
            logger.error(f"Blockchain data collection failed: {str(blockchain_data)}")
            blockchain_data = []

        if isinstance(news_data, Exception):
            logger.error(f"News collection failed: {str(news_data)}")
            news_data = []

        if isinstance(sentiment_data, Exception):
            logger.error(f"Sentiment collection failed: {str(sentiment_data)}")
            sentiment_data = []

        if isinstance(whale_data, Exception):
            logger.error(f"Whale tracking collection failed: {str(whale_data)}")
            whale_data = []

        # Calculate statistics
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        total_sources = (
            len(market_data)
            + len(blockchain_data)
            + len(news_data)
            + len(sentiment_data)
            + len(whale_data)
        )

        successful_sources = sum(
            [
                sum(1 for r in market_data if r.get("success", False)),
                sum(1 for r in blockchain_data if r.get("success", False)),
                sum(1 for r in news_data if r.get("success", False)),
                sum(1 for r in sentiment_data if r.get("success", False)),
                sum(1 for r in whale_data if r.get("success", False)),
            ]
        )

        placeholder_count = sum(
            [
                sum(1 for r in market_data if r.get("is_placeholder", False)),
                sum(1 for r in blockchain_data if r.get("is_placeholder", False)),
                sum(1 for r in news_data if r.get("is_placeholder", False)),
                sum(1 for r in sentiment_data if r.get("is_placeholder", False)),
                sum(1 for r in whale_data if r.get("is_placeholder", False)),
            ]
        )

        # Aggregate results
        results = {
            "collection_timestamp": start_time.isoformat(),
            "duration_seconds": round(duration, 2),
            "statistics": {
                "total_sources": total_sources,
                "successful_sources": successful_sources,
                "failed_sources": total_sources - successful_sources,
                "placeholder_sources": placeholder_count,
                "success_rate": (
                    round(successful_sources / total_sources * 100, 2) if total_sources > 0 else 0
                ),
                "categories": {
                    "market_data": {
                        "total": len(market_data),
                        "successful": sum(1 for r in market_data if r.get("success", False)),
                    },
                    "blockchain": {
                        "total": len(blockchain_data),
                        "successful": sum(1 for r in blockchain_data if r.get("success", False)),
                    },
                    "news": {
                        "total": len(news_data),
                        "successful": sum(1 for r in news_data if r.get("success", False)),
                    },
                    "sentiment": {
                        "total": len(sentiment_data),
                        "successful": sum(1 for r in sentiment_data if r.get("success", False)),
                    },
                    "whale_tracking": {
                        "total": len(whale_data),
                        "successful": sum(1 for r in whale_data if r.get("success", False)),
                    },
                },
            },
            "data": {
                "market_data": market_data,
                "blockchain": blockchain_data,
                "news": news_data,
                "sentiment": sentiment_data,
                "whale_tracking": whale_data,
            },
        }

        # Log summary
        logger.info("=" * 60)
        logger.info("MASTER COLLECTION COMPLETE")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Total Sources: {total_sources}")
        logger.info(f"Successful: {successful_sources} ({results['statistics']['success_rate']}%)")
        logger.info(f"Failed: {total_sources - successful_sources}")
        logger.info(f"Placeholders: {placeholder_count}")
        logger.info("=" * 60)
        logger.info("Category Breakdown:")
        for category, stats in results["statistics"]["categories"].items():
            logger.info(f"  {category}: {stats['successful']}/{stats['total']}")
        logger.info("=" * 60)

        # Save all collected data to database
        try:
            persistence_stats = data_persistence.save_all_data(results)
            results["persistence_stats"] = persistence_stats
        except Exception as e:
            logger.error(f"Error persisting data to database: {e}", exc_info=True)
            results["persistence_stats"] = {"error": str(e)}

        return results

    async def collect_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Collect data from a specific category

        Args:
            category: Category name (market_data, blockchain, news, sentiment, whale_tracking)

        Returns:
            List of results for the category
        """
        logger.info(f"Collecting data for category: {category}")

        if category == "market_data":
            return await self.collect_all_market_data()
        elif category == "blockchain":
            return await self.collect_all_blockchain_data()
        elif category == "news":
            return await self.collect_all_news()
        elif category == "sentiment":
            return await self.collect_all_sentiment()
        elif category == "whale_tracking":
            return await self.collect_whale_tracking()
        else:
            logger.error(f"Unknown category: {category}")
            return []


# Example usage
if __name__ == "__main__":

    async def main():
        collector = DataSourceCollector()

        print("\n" + "=" * 80)
        print("CRYPTO DATA SOURCE MASTER COLLECTOR")
        print("Collecting data from ALL available sources...")
        print("=" * 80 + "\n")

        # Collect all data
        results = await collector.collect_all_data()

        # Print summary
        print("\n" + "=" * 80)
        print("COLLECTION SUMMARY")
        print("=" * 80)
        print(f"Duration: {results['duration_seconds']} seconds")
        print(f"Total Sources: {results['statistics']['total_sources']}")
        print(
            f"Successful: {results['statistics']['successful_sources']} "
            f"({results['statistics']['success_rate']}%)"
        )
        print(f"Failed: {results['statistics']['failed_sources']}")
        print(f"Placeholders: {results['statistics']['placeholder_sources']}")
        print("\n" + "-" * 80)
        print("CATEGORY BREAKDOWN:")
        print("-" * 80)

        for category, stats in results["statistics"]["categories"].items():
            success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(
                f"{category:20} {stats['successful']:3}/{stats['total']:3} ({success_rate:5.1f}%)"
            )

        print("=" * 80)

        # Print sample data from each category
        print("\n" + "=" * 80)
        print("SAMPLE DATA FROM EACH CATEGORY")
        print("=" * 80)

        for category, data_list in results["data"].items():
            print(f"\n{category.upper()}:")
            successful = [d for d in data_list if d.get("success", False)]
            if successful:
                sample = successful[0]
                print(f"  Provider: {sample.get('provider', 'N/A')}")
                print(f"  Success: {sample.get('success', False)}")
                if sample.get("data"):
                    print(f"  Data keys: {list(sample.get('data', {}).keys())[:5]}")
            else:
                print("  No successful data")

        print("\n" + "=" * 80)

    asyncio.run(main())

"""
Data Persistence Module
Saves collected data from all collectors into the database
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from database.db_manager import db_manager
from utils.logger import setup_logger

logger = setup_logger("data_persistence")


class DataPersistence:
    """
    Handles saving collected data to the database
    """

    def __init__(self):
        """Initialize data persistence"""
        self.stats = {
            'market_prices_saved': 0,
            'news_saved': 0,
            'sentiment_saved': 0,
            'whale_txs_saved': 0,
            'gas_prices_saved': 0,
            'blockchain_stats_saved': 0
        }

    def reset_stats(self):
        """Reset persistence statistics"""
        for key in self.stats:
            self.stats[key] = 0

    def get_stats(self) -> Dict[str, int]:
        """Get persistence statistics"""
        return self.stats.copy()

    def save_market_data(self, results: List[Dict[str, Any]]) -> int:
        """
        Save market data to database

        Args:
            results: List of market data results from collectors

        Returns:
            Number of prices saved
        """
        saved_count = 0

        for result in results:
            if not result.get('success', False):
                continue

            provider = result.get('provider', 'Unknown')
            data = result.get('data')

            if not data:
                continue

            try:
                # CoinGecko format
                if provider == "CoinGecko" and isinstance(data, dict):
                    # Map CoinGecko coin IDs to symbols
                    symbol_map = {
                        'bitcoin': 'BTC',
                        'ethereum': 'ETH',
                        'binancecoin': 'BNB'
                    }

                    for coin_id, coin_data in data.items():
                        if isinstance(coin_data, dict) and 'usd' in coin_data:
                            symbol = symbol_map.get(coin_id, coin_id.upper())

                            db_manager.save_market_price(
                                symbol=symbol,
                                price_usd=coin_data.get('usd', 0),
                                market_cap=coin_data.get('usd_market_cap'),
                                volume_24h=coin_data.get('usd_24h_vol'),
                                price_change_24h=coin_data.get('usd_24h_change'),
                                source=provider
                            )
                            saved_count += 1

                # Binance format
                elif provider == "Binance" and isinstance(data, dict):
                    # Binance returns symbol -> price mapping
                    for symbol, price in data.items():
                        if isinstance(price, (int, float)):
                            # Remove "USDT" suffix if present
                            clean_symbol = symbol.replace('USDT', '')

                            db_manager.save_market_price(
                                symbol=clean_symbol,
                                price_usd=float(price),
                                source=provider
                            )
                            saved_count += 1

                # CoinMarketCap format
                elif provider == "CoinMarketCap" and isinstance(data, dict):
                    if 'data' in data:
                        for coin_id, coin_data in data['data'].items():
                            if isinstance(coin_data, dict):
                                symbol = coin_data.get('symbol', '').upper()
                                quote_usd = coin_data.get('quote', {}).get('USD', {})

                                if symbol and quote_usd:
                                    db_manager.save_market_price(
                                        symbol=symbol,
                                        price_usd=quote_usd.get('price', 0),
                                        market_cap=quote_usd.get('market_cap'),
                                        volume_24h=quote_usd.get('volume_24h'),
                                        price_change_24h=quote_usd.get('percent_change_24h'),
                                        source=provider
                                    )
                                    saved_count += 1

            except Exception as e:
                logger.error(f"Error saving market data from {provider}: {e}", exc_info=True)

        self.stats['market_prices_saved'] += saved_count
        if saved_count > 0:
            logger.info(f"Saved {saved_count} market prices to database")

        return saved_count

    def save_news_data(self, results: List[Dict[str, Any]]) -> int:
        """
        Save news data to database

        Args:
            results: List of news results from collectors

        Returns:
            Number of articles saved
        """
        saved_count = 0

        for result in results:
            if not result.get('success', False):
                continue

            provider = result.get('provider', 'Unknown')
            data = result.get('data')

            if not data:
                continue

            try:
                # CryptoPanic format
                if provider == "CryptoPanic" and isinstance(data, dict):
                    results_list = data.get('results', [])

                    for article in results_list:
                        if not isinstance(article, dict):
                            continue

                        # Parse published_at
                        published_at = None
                        if 'created_at' in article:
                            try:
                                pub_str = article['created_at']
                                if pub_str.endswith('Z'):
                                    pub_str = pub_str.replace('Z', '+00:00')
                                published_at = datetime.fromisoformat(pub_str)
                            except:
                                published_at = datetime.utcnow()

                        if not published_at:
                            published_at = datetime.utcnow()

                        # Extract currencies as tags
                        currencies = article.get('currencies', [])
                        tags = ','.join([c.get('code', '') for c in currencies if isinstance(c, dict)])

                        db_manager.save_news_article(
                            title=article.get('title', ''),
                            content=article.get('body', ''),
                            source=provider,
                            url=article.get('url', ''),
                            published_at=published_at,
                            sentiment=article.get('sentiment'),
                            tags=tags
                        )
                        saved_count += 1

                # NewsAPI format (newsdata.io)
                elif provider == "NewsAPI" and isinstance(data, dict):
                    results_list = data.get('results', [])

                    for article in results_list:
                        if not isinstance(article, dict):
                            continue

                        # Parse published_at
                        published_at = None
                        if 'pubDate' in article:
                            try:
                                pub_str = article['pubDate']
                                if pub_str.endswith('Z'):
                                    pub_str = pub_str.replace('Z', '+00:00')
                                published_at = datetime.fromisoformat(pub_str)
                            except:
                                published_at = datetime.utcnow()

                        if not published_at:
                            published_at = datetime.utcnow()

                        # Extract keywords as tags
                        keywords = article.get('keywords', [])
                        tags = ','.join(keywords) if isinstance(keywords, list) else ''

                        db_manager.save_news_article(
                            title=article.get('title', ''),
                            content=article.get('description', ''),
                            source=provider,
                            url=article.get('link', ''),
                            published_at=published_at,
                            tags=tags
                        )
                        saved_count += 1

            except Exception as e:
                logger.error(f"Error saving news data from {provider}: {e}", exc_info=True)

        self.stats['news_saved'] += saved_count
        if saved_count > 0:
            logger.info(f"Saved {saved_count} news articles to database")

        return saved_count

    def save_sentiment_data(self, results: List[Dict[str, Any]]) -> int:
        """
        Save sentiment data to database

        Args:
            results: List of sentiment results from collectors

        Returns:
            Number of sentiment metrics saved
        """
        saved_count = 0

        for result in results:
            if not result.get('success', False):
                continue

            provider = result.get('provider', 'Unknown')
            data = result.get('data')

            if not data:
                continue

            try:
                # Fear & Greed Index format
                if provider == "AlternativeMe" and isinstance(data, dict):
                    data_list = data.get('data', [])

                    if data_list and isinstance(data_list, list):
                        index_data = data_list[0]

                        if isinstance(index_data, dict):
                            value = float(index_data.get('value', 50))
                            value_classification = index_data.get('value_classification', 'neutral')

                            # Map classification to standard format
                            classification_map = {
                                'Extreme Fear': 'extreme_fear',
                                'Fear': 'fear',
                                'Neutral': 'neutral',
                                'Greed': 'greed',
                                'Extreme Greed': 'extreme_greed'
                            }

                            classification = classification_map.get(
                                value_classification,
                                value_classification.lower().replace(' ', '_')
                            )

                            # Parse timestamp
                            timestamp = None
                            if 'timestamp' in index_data:
                                try:
                                    timestamp = datetime.fromtimestamp(int(index_data['timestamp']))
                                except:
                                    pass

                            db_manager.save_sentiment_metric(
                                metric_name='fear_greed_index',
                                value=value,
                                classification=classification,
                                source=provider,
                                timestamp=timestamp
                            )
                            saved_count += 1

            except Exception as e:
                logger.error(f"Error saving sentiment data from {provider}: {e}", exc_info=True)

        self.stats['sentiment_saved'] += saved_count
        if saved_count > 0:
            logger.info(f"Saved {saved_count} sentiment metrics to database")

        return saved_count

    def save_whale_data(self, results: List[Dict[str, Any]]) -> int:
        """
        Save whale transaction data to database

        Args:
            results: List of whale tracking results from collectors

        Returns:
            Number of whale transactions saved
        """
        saved_count = 0

        for result in results:
            if not result.get('success', False):
                continue

            provider = result.get('provider', 'Unknown')
            data = result.get('data')

            if not data:
                continue

            try:
                # WhaleAlert format
                if provider == "WhaleAlert" and isinstance(data, dict):
                    transactions = data.get('transactions', [])

                    for tx in transactions:
                        if not isinstance(tx, dict):
                            continue

                        # Parse timestamp
                        timestamp = None
                        if 'timestamp' in tx:
                            try:
                                timestamp = datetime.fromtimestamp(tx['timestamp'])
                            except:
                                timestamp = datetime.utcnow()

                        if not timestamp:
                            timestamp = datetime.utcnow()

                        # Extract addresses
                        from_address = tx.get('from', {}).get('address', '') if isinstance(tx.get('from'), dict) else ''
                        to_address = tx.get('to', {}).get('address', '') if isinstance(tx.get('to'), dict) else ''

                        db_manager.save_whale_transaction(
                            blockchain=tx.get('blockchain', 'unknown'),
                            transaction_hash=tx.get('hash', ''),
                            from_address=from_address,
                            to_address=to_address,
                            amount=float(tx.get('amount', 0)),
                            amount_usd=float(tx.get('amount_usd', 0)),
                            source=provider,
                            timestamp=timestamp
                        )
                        saved_count += 1

            except Exception as e:
                logger.error(f"Error saving whale data from {provider}: {e}", exc_info=True)

        self.stats['whale_txs_saved'] += saved_count
        if saved_count > 0:
            logger.info(f"Saved {saved_count} whale transactions to database")

        return saved_count

    def save_blockchain_data(self, results: List[Dict[str, Any]]) -> int:
        """
        Save blockchain data (gas prices, stats) to database

        Args:
            results: List of blockchain results from collectors

        Returns:
            Number of records saved
        """
        saved_count = 0

        for result in results:
            if not result.get('success', False):
                continue

            provider = result.get('provider', 'Unknown')
            data = result.get('data')

            if not data:
                continue

            try:
                # Etherscan gas price format
                if provider == "Etherscan" and isinstance(data, dict):
                    if 'result' in data:
                        gas_data = data['result']

                        if isinstance(gas_data, dict):
                            db_manager.save_gas_price(
                                blockchain='ethereum',
                                gas_price_gwei=float(gas_data.get('ProposeGasPrice', 0)),
                                fast_gas_price=float(gas_data.get('FastGasPrice', 0)),
                                standard_gas_price=float(gas_data.get('ProposeGasPrice', 0)),
                                slow_gas_price=float(gas_data.get('SafeGasPrice', 0)),
                                source=provider
                            )
                            saved_count += 1
                            self.stats['gas_prices_saved'] += 1

                # Other blockchain explorers
                elif provider in ["BSCScan", "PolygonScan"]:
                    blockchain_map = {
                        "BSCScan": "bsc",
                        "PolygonScan": "polygon"
                    }
                    blockchain = blockchain_map.get(provider, provider.lower())

                    if 'result' in data and isinstance(data['result'], dict):
                        gas_data = data['result']

                        db_manager.save_gas_price(
                            blockchain=blockchain,
                            gas_price_gwei=float(gas_data.get('ProposeGasPrice', 0)),
                            fast_gas_price=float(gas_data.get('FastGasPrice', 0)),
                            standard_gas_price=float(gas_data.get('ProposeGasPrice', 0)),
                            slow_gas_price=float(gas_data.get('SafeGasPrice', 0)),
                            source=provider
                        )
                        saved_count += 1
                        self.stats['gas_prices_saved'] += 1

            except Exception as e:
                logger.error(f"Error saving blockchain data from {provider}: {e}", exc_info=True)

        if saved_count > 0:
            logger.info(f"Saved {saved_count} blockchain records to database")

        return saved_count

    def save_all_data(self, results: Dict[str, Any]) -> Dict[str, int]:
        """
        Save all collected data to database

        Args:
            results: Results dictionary from master collector

        Returns:
            Dictionary with save statistics
        """
        logger.info("=" * 60)
        logger.info("Saving collected data to database...")
        logger.info("=" * 60)

        self.reset_stats()

        data = results.get('data', {})

        # Save market data
        if 'market_data' in data:
            self.save_market_data(data['market_data'])

        # Save news data
        if 'news' in data:
            self.save_news_data(data['news'])

        # Save sentiment data
        if 'sentiment' in data:
            self.save_sentiment_data(data['sentiment'])

        # Save whale tracking data
        if 'whale_tracking' in data:
            self.save_whale_data(data['whale_tracking'])

        # Save blockchain data
        if 'blockchain' in data:
            self.save_blockchain_data(data['blockchain'])

        stats = self.get_stats()
        total_saved = sum(stats.values())

        logger.info("=" * 60)
        logger.info("Data Persistence Complete")
        logger.info(f"Total records saved: {total_saved}")
        logger.info(f"  Market prices: {stats['market_prices_saved']}")
        logger.info(f"  News articles: {stats['news_saved']}")
        logger.info(f"  Sentiment metrics: {stats['sentiment_saved']}")
        logger.info(f"  Whale transactions: {stats['whale_txs_saved']}")
        logger.info(f"  Gas prices: {stats['gas_prices_saved']}")
        logger.info(f"  Blockchain stats: {stats['blockchain_stats_saved']}")
        logger.info("=" * 60)

        return stats


# Global instance
data_persistence = DataPersistence()

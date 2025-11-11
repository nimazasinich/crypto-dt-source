"""
Data Access Layer for Crypto Data
Extends DatabaseManager with methods to access collected cryptocurrency data
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import desc, func, and_
from sqlalchemy.orm import Session

from database.models import (
    MarketPrice,
    NewsArticle,
    WhaleTransaction,
    SentimentMetric,
    GasPrice,
    BlockchainStat
)
from utils.logger import setup_logger

logger = setup_logger("data_access")


class DataAccessMixin:
    """
    Mixin class to add data access methods to DatabaseManager
    Provides methods to query collected cryptocurrency data
    """

    # ============================================================================
    # Market Price Methods
    # ============================================================================

    def save_market_price(
        self,
        symbol: str,
        price_usd: float,
        market_cap: Optional[float] = None,
        volume_24h: Optional[float] = None,
        price_change_24h: Optional[float] = None,
        source: str = "unknown",
        timestamp: Optional[datetime] = None
    ) -> Optional[MarketPrice]:
        """
        Save market price data
        
        Args:
            symbol: Cryptocurrency symbol (e.g., BTC, ETH)
            price_usd: Price in USD
            market_cap: Market capitalization
            volume_24h: 24-hour trading volume
            price_change_24h: 24-hour price change percentage
            source: Data source name
            timestamp: Data timestamp (defaults to now)
        
        Returns:
            MarketPrice object if successful, None otherwise
        """
        try:
            with self.get_session() as session:
                price = MarketPrice(
                    symbol=symbol.upper(),
                    price_usd=price_usd,
                    market_cap=market_cap,
                    volume_24h=volume_24h,
                    price_change_24h=price_change_24h,
                    source=source,
                    timestamp=timestamp or datetime.utcnow()
                )
                session.add(price)
                session.flush()
                logger.debug(f"Saved price for {symbol}: ${price_usd}")
                return price
        
        except Exception as e:
            logger.error(f"Error saving market price for {symbol}: {e}", exc_info=True)
            return None

    def get_latest_prices(self, limit: int = 100) -> List[MarketPrice]:
        """Get latest prices for all cryptocurrencies"""
        try:
            with self.get_session() as session:
                # Get latest price for each symbol
                subquery = (
                    session.query(
                        MarketPrice.symbol,
                        func.max(MarketPrice.timestamp).label('max_timestamp')
                    )
                    .group_by(MarketPrice.symbol)
                    .subquery()
                )
                
                prices = (
                    session.query(MarketPrice)
                    .join(
                        subquery,
                        and_(
                            MarketPrice.symbol == subquery.c.symbol,
                            MarketPrice.timestamp == subquery.c.max_timestamp
                        )
                    )
                    .order_by(desc(MarketPrice.market_cap))
                    .limit(limit)
                    .all()
                )
                
                return prices
        
        except Exception as e:
            logger.error(f"Error getting latest prices: {e}", exc_info=True)
            return []

    def get_latest_price_by_symbol(self, symbol: str) -> Optional[MarketPrice]:
        """Get latest price for a specific cryptocurrency"""
        try:
            with self.get_session() as session:
                price = (
                    session.query(MarketPrice)
                    .filter(MarketPrice.symbol == symbol.upper())
                    .order_by(desc(MarketPrice.timestamp))
                    .first()
                )
                return price
        
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}", exc_info=True)
            return None

    def get_price_history(self, symbol: str, hours: int = 24) -> List[MarketPrice]:
        """Get price history for a cryptocurrency"""
        try:
            with self.get_session() as session:
                cutoff = datetime.utcnow() - timedelta(hours=hours)
                
                history = (
                    session.query(MarketPrice)
                    .filter(
                        MarketPrice.symbol == symbol.upper(),
                        MarketPrice.timestamp >= cutoff
                    )
                    .order_by(MarketPrice.timestamp)
                    .all()
                )
                
                return history
        
        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}", exc_info=True)
            return []

    # ============================================================================
    # News Methods
    # ============================================================================

    def save_news_article(
        self,
        title: str,
        source: str,
        published_at: datetime,
        content: Optional[str] = None,
        url: Optional[str] = None,
        sentiment: Optional[str] = None,
        tags: Optional[str] = None
    ) -> Optional[NewsArticle]:
        """Save news article"""
        try:
            with self.get_session() as session:
                article = NewsArticle(
                    title=title,
                    content=content,
                    source=source,
                    url=url,
                    published_at=published_at,
                    sentiment=sentiment,
                    tags=tags
                )
                session.add(article)
                session.flush()
                logger.debug(f"Saved news article: {title[:50]}...")
                return article
        
        except Exception as e:
            logger.error(f"Error saving news article: {e}", exc_info=True)
            return None

    def get_latest_news(
        self,
        limit: int = 50,
        source: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> List[NewsArticle]:
        """Get latest news articles"""
        try:
            with self.get_session() as session:
                query = session.query(NewsArticle)
                
                if source:
                    query = query.filter(NewsArticle.source == source)
                
                if sentiment:
                    query = query.filter(NewsArticle.sentiment == sentiment)
                
                articles = (
                    query
                    .order_by(desc(NewsArticle.published_at))
                    .limit(limit)
                    .all()
                )
                
                return articles
        
        except Exception as e:
            logger.error(f"Error getting latest news: {e}", exc_info=True)
            return []

    def get_news_by_id(self, news_id: int) -> Optional[NewsArticle]:
        """Get a specific news article by ID"""
        try:
            with self.get_session() as session:
                article = session.query(NewsArticle).filter(NewsArticle.id == news_id).first()
                return article
        
        except Exception as e:
            logger.error(f"Error getting news {news_id}: {e}", exc_info=True)
            return None

    def search_news(self, query: str, limit: int = 50) -> List[NewsArticle]:
        """Search news articles by keyword"""
        try:
            with self.get_session() as session:
                articles = (
                    session.query(NewsArticle)
                    .filter(
                        NewsArticle.title.contains(query) | 
                        NewsArticle.content.contains(query)
                    )
                    .order_by(desc(NewsArticle.published_at))
                    .limit(limit)
                    .all()
                )
                
                return articles
        
        except Exception as e:
            logger.error(f"Error searching news: {e}", exc_info=True)
            return []

    # ============================================================================
    # Sentiment Methods
    # ============================================================================

    def save_sentiment_metric(
        self,
        metric_name: str,
        value: float,
        classification: str,
        source: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[SentimentMetric]:
        """Save sentiment metric"""
        try:
            with self.get_session() as session:
                metric = SentimentMetric(
                    metric_name=metric_name,
                    value=value,
                    classification=classification,
                    source=source,
                    timestamp=timestamp or datetime.utcnow()
                )
                session.add(metric)
                session.flush()
                logger.debug(f"Saved sentiment: {metric_name} = {value} ({classification})")
                return metric
        
        except Exception as e:
            logger.error(f"Error saving sentiment metric: {e}", exc_info=True)
            return None

    def get_latest_sentiment(self) -> Optional[SentimentMetric]:
        """Get latest sentiment metric"""
        try:
            with self.get_session() as session:
                metric = (
                    session.query(SentimentMetric)
                    .order_by(desc(SentimentMetric.timestamp))
                    .first()
                )
                return metric
        
        except Exception as e:
            logger.error(f"Error getting latest sentiment: {e}", exc_info=True)
            return None

    def get_sentiment_history(self, hours: int = 168) -> List[SentimentMetric]:
        """Get sentiment history"""
        try:
            with self.get_session() as session:
                cutoff = datetime.utcnow() - timedelta(hours=hours)
                
                history = (
                    session.query(SentimentMetric)
                    .filter(SentimentMetric.timestamp >= cutoff)
                    .order_by(SentimentMetric.timestamp)
                    .all()
                )
                
                return history
        
        except Exception as e:
            logger.error(f"Error getting sentiment history: {e}", exc_info=True)
            return []

    # ============================================================================
    # Whale Transaction Methods
    # ============================================================================

    def save_whale_transaction(
        self,
        blockchain: str,
        transaction_hash: str,
        from_address: str,
        to_address: str,
        amount: float,
        amount_usd: float,
        source: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[WhaleTransaction]:
        """Save whale transaction"""
        try:
            with self.get_session() as session:
                # Check if transaction already exists
                existing = (
                    session.query(WhaleTransaction)
                    .filter(WhaleTransaction.transaction_hash == transaction_hash)
                    .first()
                )
                
                if existing:
                    logger.debug(f"Transaction {transaction_hash} already exists")
                    return existing
                
                transaction = WhaleTransaction(
                    blockchain=blockchain,
                    transaction_hash=transaction_hash,
                    from_address=from_address,
                    to_address=to_address,
                    amount=amount,
                    amount_usd=amount_usd,
                    source=source,
                    timestamp=timestamp or datetime.utcnow()
                )
                session.add(transaction)
                session.flush()
                logger.debug(f"Saved whale transaction: {amount_usd} USD on {blockchain}")
                return transaction
        
        except Exception as e:
            logger.error(f"Error saving whale transaction: {e}", exc_info=True)
            return None

    def get_whale_transactions(
        self,
        limit: int = 50,
        blockchain: Optional[str] = None,
        min_amount_usd: Optional[float] = None
    ) -> List[WhaleTransaction]:
        """Get recent whale transactions"""
        try:
            with self.get_session() as session:
                query = session.query(WhaleTransaction)
                
                if blockchain:
                    query = query.filter(WhaleTransaction.blockchain == blockchain)
                
                if min_amount_usd:
                    query = query.filter(WhaleTransaction.amount_usd >= min_amount_usd)
                
                transactions = (
                    query
                    .order_by(desc(WhaleTransaction.timestamp))
                    .limit(limit)
                    .all()
                )
                
                return transactions
        
        except Exception as e:
            logger.error(f"Error getting whale transactions: {e}", exc_info=True)
            return []

    def get_whale_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get whale activity statistics"""
        try:
            with self.get_session() as session:
                cutoff = datetime.utcnow() - timedelta(hours=hours)
                
                transactions = (
                    session.query(WhaleTransaction)
                    .filter(WhaleTransaction.timestamp >= cutoff)
                    .all()
                )
                
                if not transactions:
                    return {
                        'total_transactions': 0,
                        'total_volume_usd': 0,
                        'avg_transaction_usd': 0,
                        'largest_transaction_usd': 0,
                        'by_blockchain': {}
                    }
                
                total_volume = sum(tx.amount_usd for tx in transactions)
                avg_transaction = total_volume / len(transactions)
                largest = max(tx.amount_usd for tx in transactions)
                
                # Group by blockchain
                by_blockchain = {}
                for tx in transactions:
                    if tx.blockchain not in by_blockchain:
                        by_blockchain[tx.blockchain] = {
                            'count': 0,
                            'volume_usd': 0
                        }
                    by_blockchain[tx.blockchain]['count'] += 1
                    by_blockchain[tx.blockchain]['volume_usd'] += tx.amount_usd
                
                return {
                    'total_transactions': len(transactions),
                    'total_volume_usd': total_volume,
                    'avg_transaction_usd': avg_transaction,
                    'largest_transaction_usd': largest,
                    'by_blockchain': by_blockchain
                }
        
        except Exception as e:
            logger.error(f"Error getting whale stats: {e}", exc_info=True)
            return {}

    # ============================================================================
    # Gas Price Methods
    # ============================================================================

    def save_gas_price(
        self,
        blockchain: str,
        gas_price_gwei: float,
        source: str,
        fast_gas_price: Optional[float] = None,
        standard_gas_price: Optional[float] = None,
        slow_gas_price: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> Optional[GasPrice]:
        """Save gas price data"""
        try:
            with self.get_session() as session:
                gas_price = GasPrice(
                    blockchain=blockchain,
                    gas_price_gwei=gas_price_gwei,
                    fast_gas_price=fast_gas_price,
                    standard_gas_price=standard_gas_price,
                    slow_gas_price=slow_gas_price,
                    source=source,
                    timestamp=timestamp or datetime.utcnow()
                )
                session.add(gas_price)
                session.flush()
                logger.debug(f"Saved gas price for {blockchain}: {gas_price_gwei} Gwei")
                return gas_price
        
        except Exception as e:
            logger.error(f"Error saving gas price: {e}", exc_info=True)
            return None

    def get_latest_gas_prices(self) -> Dict[str, Any]:
        """Get latest gas prices for all blockchains"""
        try:
            with self.get_session() as session:
                # Get latest gas price for each blockchain
                subquery = (
                    session.query(
                        GasPrice.blockchain,
                        func.max(GasPrice.timestamp).label('max_timestamp')
                    )
                    .group_by(GasPrice.blockchain)
                    .subquery()
                )
                
                gas_prices = (
                    session.query(GasPrice)
                    .join(
                        subquery,
                        and_(
                            GasPrice.blockchain == subquery.c.blockchain,
                            GasPrice.timestamp == subquery.c.max_timestamp
                        )
                    )
                    .all()
                )
                
                result = {}
                for gp in gas_prices:
                    result[gp.blockchain] = {
                        'gas_price_gwei': gp.gas_price_gwei,
                        'fast': gp.fast_gas_price,
                        'standard': gp.standard_gas_price,
                        'slow': gp.slow_gas_price,
                        'timestamp': gp.timestamp.isoformat()
                    }
                
                return result
        
        except Exception as e:
            logger.error(f"Error getting gas prices: {e}", exc_info=True)
            return {}

    # ============================================================================
    # Blockchain Stats Methods
    # ============================================================================

    def save_blockchain_stat(
        self,
        blockchain: str,
        source: str,
        latest_block: Optional[int] = None,
        total_transactions: Optional[int] = None,
        network_hashrate: Optional[float] = None,
        difficulty: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> Optional[BlockchainStat]:
        """Save blockchain statistics"""
        try:
            with self.get_session() as session:
                stat = BlockchainStat(
                    blockchain=blockchain,
                    latest_block=latest_block,
                    total_transactions=total_transactions,
                    network_hashrate=network_hashrate,
                    difficulty=difficulty,
                    source=source,
                    timestamp=timestamp or datetime.utcnow()
                )
                session.add(stat)
                session.flush()
                logger.debug(f"Saved blockchain stat for {blockchain}")
                return stat
        
        except Exception as e:
            logger.error(f"Error saving blockchain stat: {e}", exc_info=True)
            return None

    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get latest blockchain statistics"""
        try:
            with self.get_session() as session:
                # Get latest stat for each blockchain
                subquery = (
                    session.query(
                        BlockchainStat.blockchain,
                        func.max(BlockchainStat.timestamp).label('max_timestamp')
                    )
                    .group_by(BlockchainStat.blockchain)
                    .subquery()
                )
                
                stats = (
                    session.query(BlockchainStat)
                    .join(
                        subquery,
                        and_(
                            BlockchainStat.blockchain == subquery.c.blockchain,
                            BlockchainStat.timestamp == subquery.c.max_timestamp
                        )
                    )
                    .all()
                )
                
                result = {}
                for stat in stats:
                    result[stat.blockchain] = {
                        'latest_block': stat.latest_block,
                        'total_transactions': stat.total_transactions,
                        'network_hashrate': stat.network_hashrate,
                        'difficulty': stat.difficulty,
                        'timestamp': stat.timestamp.isoformat()
                    }
                
                return result
        
        except Exception as e:
            logger.error(f"Error getting blockchain stats: {e}", exc_info=True)
            return {}


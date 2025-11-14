#!/usr/bin/env python3
"""
Database module for Crypto Data Aggregator
Complete CRUD operations with the exact schema specified
"""

import sqlite3
import threading
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from contextlib import contextmanager
import logging

import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CryptoDatabase:
    """
    Database manager for cryptocurrency data with full CRUD operations
    Thread-safe implementation using context managers
    """

    def __init__(self, db_path: str = None):
        """Initialize database with connection pooling"""
        self.db_path = str(db_path or config.DATABASE_PATH)
        self._local = threading.local()
        self._init_database()
        logger.info(f"Database initialized at {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Get thread-safe database connection"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.conn.row_factory = sqlite3.Row

        try:
            yield self._local.conn
        except Exception as e:
            self._local.conn.rollback()
            logger.error(f"Database error: {e}")
            raise

    def _init_database(self):
        """Initialize all database tables with exact schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # ==================== PRICES TABLE ====================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    name TEXT,
                    price_usd REAL NOT NULL,
                    volume_24h REAL,
                    market_cap REAL,
                    percent_change_1h REAL,
                    percent_change_24h REAL,
                    percent_change_7d REAL,
                    rank INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ==================== NEWS TABLE ====================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    summary TEXT,
                    url TEXT UNIQUE,
                    source TEXT,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    related_coins TEXT,
                    published_date DATETIME,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ==================== MARKET ANALYSIS TABLE ====================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT,
                    trend TEXT,
                    support_level REAL,
                    resistance_level REAL,
                    prediction TEXT,
                    confidence REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ==================== USER QUERIES TABLE ====================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    result_count INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ==================== CREATE INDEXES ====================
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_symbol ON prices(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_rank ON prices(rank)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_url ON news(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_sentiment ON news(sentiment_label)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_symbol ON market_analysis(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_timestamp ON market_analysis(timestamp)")

            conn.commit()
            logger.info("Database tables and indexes created successfully")

    # ==================== PRICES CRUD OPERATIONS ====================

    def save_price(self, price_data: Dict[str, Any]) -> bool:
        """
        Save a single price record

        Args:
            price_data: Dictionary containing price information

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO prices
                    (symbol, name, price_usd, volume_24h, market_cap,
                     percent_change_1h, percent_change_24h, percent_change_7d, rank)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    price_data.get('symbol'),
                    price_data.get('name'),
                    price_data.get('price_usd', 0.0),
                    price_data.get('volume_24h'),
                    price_data.get('market_cap'),
                    price_data.get('percent_change_1h'),
                    price_data.get('percent_change_24h'),
                    price_data.get('percent_change_7d'),
                    price_data.get('rank')
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving price: {e}")
            return False

    def save_prices_batch(self, prices: List[Dict[str, Any]]) -> int:
        """
        Save multiple price records in batch (minimum 100 records for efficiency)

        Args:
            prices: List of price dictionaries

        Returns:
            int: Number of records saved
        """
        saved_count = 0
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for price_data in prices:
                    try:
                        cursor.execute("""
                            INSERT INTO prices
                            (symbol, name, price_usd, volume_24h, market_cap,
                             percent_change_1h, percent_change_24h, percent_change_7d, rank)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            price_data.get('symbol'),
                            price_data.get('name'),
                            price_data.get('price_usd', 0.0),
                            price_data.get('volume_24h'),
                            price_data.get('market_cap'),
                            price_data.get('percent_change_1h'),
                            price_data.get('percent_change_24h'),
                            price_data.get('percent_change_7d'),
                            price_data.get('rank')
                        ))
                        saved_count += 1
                    except Exception as e:
                        logger.warning(f"Error saving individual price: {e}")
                        continue
                conn.commit()
                logger.info(f"Batch saved {saved_count} price records")
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
        return saved_count

    def get_latest_prices(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get latest prices for top cryptocurrencies

        Args:
            limit: Maximum number of records to return

        Returns:
            List of price dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT ON (symbol) *
                    FROM prices
                    WHERE timestamp >= datetime('now', '-1 hour')
                    ORDER BY symbol, timestamp DESC, rank ASC
                    LIMIT ?
                """, (limit,))

                # SQLite doesn't support DISTINCT ON, use subquery instead
                cursor.execute("""
                    SELECT p1.*
                    FROM prices p1
                    INNER JOIN (
                        SELECT symbol, MAX(timestamp) as max_ts
                        FROM prices
                        WHERE timestamp >= datetime('now', '-1 hour')
                        GROUP BY symbol
                    ) p2 ON p1.symbol = p2.symbol AND p1.timestamp = p2.max_ts
                    ORDER BY p1.rank ASC, p1.market_cap DESC
                    LIMIT ?
                """, (limit,))

                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting latest prices: {e}")
            return []

    def get_price_history(self, symbol: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get price history for a specific symbol

        Args:
            symbol: Cryptocurrency symbol
            hours: Number of hours to look back

        Returns:
            List of price dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM prices
                    WHERE symbol = ?
                    AND timestamp >= datetime('now', '-' || ? || ' hours')
                    ORDER BY timestamp ASC
                """, (symbol, hours))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []

    def get_top_gainers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top gaining cryptocurrencies in last 24h"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p1.*
                    FROM prices p1
                    INNER JOIN (
                        SELECT symbol, MAX(timestamp) as max_ts
                        FROM prices
                        WHERE timestamp >= datetime('now', '-1 hour')
                        GROUP BY symbol
                    ) p2 ON p1.symbol = p2.symbol AND p1.timestamp = p2.max_ts
                    WHERE p1.percent_change_24h IS NOT NULL
                    ORDER BY p1.percent_change_24h DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting top gainers: {e}")
            return []

    def delete_old_prices(self, days: int = 30) -> int:
        """
        Delete price records older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted records
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM prices
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                """, (days,))
                conn.commit()
                deleted = cursor.rowcount
                logger.info(f"Deleted {deleted} old price records")
                return deleted
        except Exception as e:
            logger.error(f"Error deleting old prices: {e}")
            return 0

    # ==================== NEWS CRUD OPERATIONS ====================

    def save_news(self, news_data: Dict[str, Any]) -> bool:
        """
        Save a single news record

        Args:
            news_data: Dictionary containing news information

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO news
                    (title, summary, url, source, sentiment_score,
                     sentiment_label, related_coins, published_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    news_data.get('title'),
                    news_data.get('summary'),
                    news_data.get('url'),
                    news_data.get('source'),
                    news_data.get('sentiment_score'),
                    news_data.get('sentiment_label'),
                    json.dumps(news_data.get('related_coins', [])),
                    news_data.get('published_date')
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving news: {e}")
            return False

    def get_latest_news(self, limit: int = 50, sentiment: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get latest news articles

        Args:
            limit: Maximum number of articles
            sentiment: Filter by sentiment label (optional)

        Returns:
            List of news dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if sentiment:
                    cursor.execute("""
                        SELECT * FROM news
                        WHERE sentiment_label = ?
                        ORDER BY published_date DESC, timestamp DESC
                        LIMIT ?
                    """, (sentiment, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM news
                        ORDER BY published_date DESC, timestamp DESC
                        LIMIT ?
                    """, (limit,))

                results = []
                for row in cursor.fetchall():
                    news_dict = dict(row)
                    if news_dict.get('related_coins'):
                        try:
                            news_dict['related_coins'] = json.loads(news_dict['related_coins'])
                        except:
                            news_dict['related_coins'] = []
                    results.append(news_dict)

                return results
        except Exception as e:
            logger.error(f"Error getting latest news: {e}")
            return []

    def get_news_by_coin(self, coin: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get news related to a specific coin"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM news
                    WHERE related_coins LIKE ?
                    ORDER BY published_date DESC
                    LIMIT ?
                """, (f'%{coin}%', limit))

                results = []
                for row in cursor.fetchall():
                    news_dict = dict(row)
                    if news_dict.get('related_coins'):
                        try:
                            news_dict['related_coins'] = json.loads(news_dict['related_coins'])
                        except:
                            news_dict['related_coins'] = []
                    results.append(news_dict)

                return results
        except Exception as e:
            logger.error(f"Error getting news by coin: {e}")
            return []

    def update_news_sentiment(self, news_id: int, sentiment_score: float, sentiment_label: str) -> bool:
        """Update sentiment for a news article"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE news
                    SET sentiment_score = ?, sentiment_label = ?
                    WHERE id = ?
                """, (sentiment_score, sentiment_label, news_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating news sentiment: {e}")
            return False

    def delete_old_news(self, days: int = 30) -> int:
        """Delete news older than specified days"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM news
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                """, (days,))
                conn.commit()
                deleted = cursor.rowcount
                logger.info(f"Deleted {deleted} old news records")
                return deleted
        except Exception as e:
            logger.error(f"Error deleting old news: {e}")
            return 0

    # ==================== MARKET ANALYSIS CRUD OPERATIONS ====================

    def save_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """Save market analysis"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO market_analysis
                    (symbol, timeframe, trend, support_level, resistance_level,
                     prediction, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_data.get('symbol'),
                    analysis_data.get('timeframe'),
                    analysis_data.get('trend'),
                    analysis_data.get('support_level'),
                    analysis_data.get('resistance_level'),
                    analysis_data.get('prediction'),
                    analysis_data.get('confidence')
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return False

    def get_latest_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest analysis for a symbol"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM market_analysis
                    WHERE symbol = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (symbol,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting latest analysis: {e}")
            return None

    def get_all_analyses(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all market analyses"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM market_analysis
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all analyses: {e}")
            return []

    # ==================== USER QUERIES CRUD OPERATIONS ====================

    def log_user_query(self, query: str, result_count: int) -> bool:
        """Log a user query"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_queries (query, result_count)
                    VALUES (?, ?)
                """, (query, result_count))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging user query: {e}")
            return False

    def get_recent_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent user queries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM user_queries
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting recent queries: {e}")
            return []

    # ==================== UTILITY OPERATIONS ====================

    def execute_safe_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a safe read-only query

        Args:
            query: SQL query (must start with SELECT)
            params: Query parameters

        Returns:
            List of result dictionaries
        """
        try:
            # Security: Only allow SELECT queries
            if not query.strip().upper().startswith('SELECT'):
                logger.warning(f"Attempted non-SELECT query: {query}")
                return []

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error executing safe query: {e}")
            return []

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                stats = {}

                # Count records in each table
                for table in ['prices', 'news', 'market_analysis', 'user_queries']:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    stats[f'{table}_count'] = cursor.fetchone()['count']

                # Get unique symbols
                cursor.execute("SELECT COUNT(DISTINCT symbol) as count FROM prices")
                stats['unique_symbols'] = cursor.fetchone()['count']

                # Get latest price update
                cursor.execute("SELECT MAX(timestamp) as latest FROM prices")
                stats['latest_price_update'] = cursor.fetchone()['latest']

                # Get latest news update
                cursor.execute("SELECT MAX(timestamp) as latest FROM news")
                stats['latest_news_update'] = cursor.fetchone()['latest']

                # Database file size
                import os
                if os.path.exists(self.db_path):
                    stats['database_size_bytes'] = os.path.getsize(self.db_path)
                    stats['database_size_mb'] = stats['database_size_bytes'] / (1024 * 1024)

                return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    def vacuum_database(self) -> bool:
        """Vacuum database to reclaim space"""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuumed successfully")
                return True
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}")
            return False

    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """Create database backup"""
        try:
            import shutil
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = config.DATABASE_BACKUP_DIR / f"backup_{timestamp}.db"

            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False

    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            delattr(self._local, 'conn')
            logger.info("Database connection closed")


# Singleton instance
_db_instance = None


def get_database() -> CryptoDatabase:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = CryptoDatabase()
    return _db_instance

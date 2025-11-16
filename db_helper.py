#!/usr/bin/env python3
"""
Simple Database Helper - SQLite only, no SQLAlchemy required
For HuggingFace deployment
"""

import sqlite3
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import logging
import os
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

# Database configuration
# Use /app/data in Docker, or current directory in development
if os.path.exists("/app"):
    DB_DIR = Path("/app/data/database")
else:
    DB_DIR = Path(__file__).parent / "data" / "database"

DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "crypto_aggregator.db"


class CryptoDatabase:
    """Simple SQLite database for cryptocurrency data"""
    
    def __init__(self, db_path: str = None):
        """Initialize database"""
        self.db_path = str(db_path or DB_PATH)
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
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Prices table
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
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_symbol ON prices(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp)")
            
            conn.commit()
            logger.info("Database tables created successfully")
    
    def save_price(self, price_data: Dict[str, Any]) -> bool:
        """Save a single price record"""
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
    
    def get_price_history(self, symbol: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get price history for a specific symbol"""
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
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) as count FROM prices")
                prices_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(DISTINCT symbol) as count FROM prices")
                unique_symbols = cursor.fetchone()['count']
                
                cursor.execute("SELECT MAX(timestamp) as latest FROM prices")
                latest_update = cursor.fetchone()['latest']
                
                # Database file size
                db_size_bytes = 0
                if os.path.exists(self.db_path):
                    db_size_bytes = os.path.getsize(self.db_path)
                
                return {
                    'prices_count': prices_count,
                    'unique_symbols': unique_symbols,
                    'latest_price_update': latest_update,
                    'database_size_bytes': db_size_bytes,
                    'database_size_mb': db_size_bytes / (1024 * 1024)
                }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            delattr(self._local, 'conn')


# Singleton instance
_db_instance = None


def get_database() -> CryptoDatabase:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = CryptoDatabase()
    return _db_instance

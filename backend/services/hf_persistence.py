"""
HF Space Persistence Layer
SQLite-based storage for signals, whale transactions, and cache
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class HFPersistence:
    """Persistence layer for HF Space API"""

    def __init__(self, db_path: str = "data/hf_space.db"):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Signals table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS signals (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    type TEXT NOT NULL,
                    score REAL NOT NULL,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0,
                    acknowledged_at TEXT,
                    metadata TEXT
                )
            """
            )

            # Whale transactions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS whale_transactions (
                    id TEXT PRIMARY KEY,
                    tx_hash TEXT NOT NULL,
                    chain TEXT NOT NULL,
                    from_address TEXT NOT NULL,
                    to_address TEXT NOT NULL,
                    amount_usd REAL NOT NULL,
                    token TEXT NOT NULL,
                    block INTEGER NOT NULL,
                    tx_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """
            )

            # Cache table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """
            )

            # Provider health log
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS provider_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time_ms INTEGER,
                    error_message TEXT,
                    timestamp TEXT NOT NULL
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_whale_chain ON whale_transactions(chain)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_whale_tx_at ON whale_transactions(tx_at)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_timestamp ON provider_health(timestamp)"
            )

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    # ========================================================================
    # Signals Operations
    # ========================================================================

    def save_signal(self, signal: Dict[str, Any]) -> bool:
        """Save a trading signal"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO signals 
                    (id, symbol, type, score, model, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        signal["id"],
                        signal["symbol"],
                        signal["type"],
                        signal["score"],
                        signal["model"],
                        signal["created_at"],
                        json.dumps(signal.get("metadata", {})),
                    ),
                )
                return True
        except Exception as e:
            logger.error(f"Error saving signal: {e}")
            return False

    def get_signals(self, limit: int = 50, symbol: Optional[str] = None) -> List[Dict]:
        """Get recent signals"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if symbol:
                    cursor.execute(
                        """
                        SELECT * FROM signals 
                        WHERE symbol = ? 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    """,
                        (symbol, limit),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT * FROM signals 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    """,
                        (limit,),
                    )

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return []

    def acknowledge_signal(self, signal_id: str) -> bool:
        """Acknowledge a signal"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE signals 
                    SET acknowledged = 1, acknowledged_at = ? 
                    WHERE id = ?
                """,
                    (datetime.now().isoformat(), signal_id),
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error acknowledging signal: {e}")
            return False

    # ========================================================================
    # Whale Transactions Operations
    # ========================================================================

    def save_whale_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Save a whale transaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO whale_transactions 
                    (id, tx_hash, chain, from_address, to_address, amount_usd, token, block, tx_at, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        transaction["id"],
                        transaction["tx_hash"],
                        transaction["chain"],
                        transaction["from_address"],
                        transaction["to_address"],
                        transaction["amount_usd"],
                        transaction["token"],
                        transaction["block"],
                        transaction["tx_at"],
                        datetime.now().isoformat(),
                        json.dumps(transaction.get("metadata", {})),
                    ),
                )
                return True
        except Exception as e:
            logger.error(f"Error saving whale transaction: {e}")
            return False

    def get_whale_transactions(
        self, limit: int = 50, chain: Optional[str] = None, min_amount_usd: Optional[float] = None
    ) -> List[Dict]:
        """Get recent whale transactions"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM whale_transactions WHERE 1=1"
                params = []

                if chain:
                    query += " AND chain = ?"
                    params.append(chain)

                if min_amount_usd:
                    query += " AND amount_usd >= ?"
                    params.append(min_amount_usd)

                query += " ORDER BY tx_at DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting whale transactions: {e}")
            return []

    def get_whale_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get whale activity statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                since = (datetime.now() - timedelta(hours=hours)).isoformat()

                # Total stats
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_transactions,
                        SUM(amount_usd) as total_volume_usd,
                        AVG(amount_usd) as avg_transaction_usd
                    FROM whale_transactions
                    WHERE tx_at >= ?
                """,
                    (since,),
                )

                stats = dict(cursor.fetchone())

                # Top chains
                cursor.execute(
                    """
                    SELECT 
                        chain,
                        COUNT(*) as count,
                        SUM(amount_usd) as volume
                    FROM whale_transactions
                    WHERE tx_at >= ?
                    GROUP BY chain
                    ORDER BY volume DESC
                    LIMIT 5
                """,
                    (since,),
                )

                stats["top_chains"] = [dict(row) for row in cursor.fetchall()]

                return stats
        except Exception as e:
            logger.error(f"Error getting whale stats: {e}")
            return {
                "total_transactions": 0,
                "total_volume_usd": 0,
                "avg_transaction_usd": 0,
                "top_chains": [],
            }

    # ========================================================================
    # Cache Operations
    # ========================================================================

    def set_cache(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Set cache value with TTL"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
                value_json = json.dumps(value)

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO cache (key, value, expires_at, created_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (key, value_json, expires_at, datetime.now().isoformat()),
                )

                return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT value FROM cache 
                    WHERE key = ? AND expires_at > ?
                """,
                    (key, datetime.now().isoformat()),
                )

                row = cursor.fetchone()
                if row:
                    return json.loads(row["value"])
                return None
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None

    def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    DELETE FROM cache WHERE expires_at <= ?
                """,
                    (datetime.now().isoformat(),),
                )
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0

    # ========================================================================
    # Provider Health Logging
    # ========================================================================

    def log_provider_health(
        self,
        provider: str,
        category: str,
        status: str,
        response_time_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Log provider health status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO provider_health 
                    (provider, category, status, response_time_ms, error_message, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        provider,
                        category,
                        status,
                        response_time_ms,
                        error_message,
                        datetime.now().isoformat(),
                    ),
                )
                return True
        except Exception as e:
            logger.error(f"Error logging provider health: {e}")
            return False

    def get_provider_health_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get provider health statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                since = (datetime.now() - timedelta(hours=hours)).isoformat()

                cursor.execute(
                    """
                    SELECT 
                        provider,
                        category,
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                        AVG(response_time_ms) as avg_response_time
                    FROM provider_health
                    WHERE timestamp >= ?
                    GROUP BY provider, category
                """,
                    (since,),
                )

                stats = [dict(row) for row in cursor.fetchall()]

                return {"period_hours": hours, "providers": stats}
        except Exception as e:
            logger.error(f"Error getting provider health stats: {e}")
            return {"period_hours": hours, "providers": []}

    # ========================================================================
    # Cleanup Operations
    # ========================================================================

    def cleanup_old_data(self, days: int = 7) -> Dict[str, int]:
        """Remove data older than specified days"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cutoff = (datetime.now() - timedelta(days=days)).isoformat()

                # Clean signals
                cursor.execute("DELETE FROM signals WHERE created_at < ?", (cutoff,))
                signals_deleted = cursor.rowcount

                # Clean whale transactions
                cursor.execute("DELETE FROM whale_transactions WHERE created_at < ?", (cutoff,))
                whales_deleted = cursor.rowcount

                # Clean expired cache
                cursor.execute(
                    "DELETE FROM cache WHERE expires_at < ?", (datetime.now().isoformat(),)
                )
                cache_deleted = cursor.rowcount

                # Clean old health logs
                cursor.execute("DELETE FROM provider_health WHERE timestamp < ?", (cutoff,))
                health_deleted = cursor.rowcount

                conn.commit()

                return {
                    "signals_deleted": signals_deleted,
                    "whales_deleted": whales_deleted,
                    "cache_deleted": cache_deleted,
                    "health_logs_deleted": health_deleted,
                    "total_deleted": signals_deleted
                    + whales_deleted
                    + cache_deleted
                    + health_deleted,
                }
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return {
                "signals_deleted": 0,
                "whales_deleted": 0,
                "cache_deleted": 0,
                "health_logs_deleted": 0,
                "total_deleted": 0,
            }

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                stats = {}

                # Count signals
                cursor.execute("SELECT COUNT(*) as count FROM signals")
                stats["signals_count"] = cursor.fetchone()["count"]

                # Count whale transactions
                cursor.execute("SELECT COUNT(*) as count FROM whale_transactions")
                stats["whale_transactions_count"] = cursor.fetchone()["count"]

                # Count cache entries
                cursor.execute(
                    "SELECT COUNT(*) as count FROM cache WHERE expires_at > ?",
                    (datetime.now().isoformat(),),
                )
                stats["cache_entries"] = cursor.fetchone()["count"]

                # Count health logs
                cursor.execute("SELECT COUNT(*) as count FROM provider_health")
                stats["health_logs_count"] = cursor.fetchone()["count"]

                # Database file size
                stats["database_size_bytes"] = Path(self.db_path).stat().st_size
                stats["database_size_mb"] = round(stats["database_size_bytes"] / (1024 * 1024), 2)

                return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


# Global persistence instance
_persistence_instance = None


def get_persistence() -> HFPersistence:
    """Get global persistence instance"""
    global _persistence_instance
    if _persistence_instance is None:
        _persistence_instance = HFPersistence()
    return _persistence_instance

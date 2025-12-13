"""
Database Migration System
Handles schema versioning and migrations for SQLite database
"""

import sqlite3
import logging
from typing import List, Callable, Tuple
from datetime import datetime
from pathlib import Path
import traceback

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration"""

    def __init__(
        self,
        version: int,
        description: str,
        up_sql: str,
        down_sql: str = ""
    ):
        """
        Initialize migration

        Args:
            version: Migration version number (sequential)
            description: Human-readable description
            up_sql: SQL to apply migration
            down_sql: SQL to rollback migration
        """
        self.version = version
        self.description = description
        self.up_sql = up_sql
        self.down_sql = down_sql


class MigrationManager:
    """
    Manages database schema migrations
    Tracks applied migrations and handles upgrades/downgrades
    """

    def __init__(self, db_path: str):
        """
        Initialize migration manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.migrations: List[Migration] = []
        self._init_migrations_table()
        self._register_migrations()

    def _init_migrations_table(self):
        """Create migrations tracking table if not exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    description TEXT NOT NULL,
                    applied_at TIMESTAMP NOT NULL,
                    execution_time_ms INTEGER
                )
            """)

            conn.commit()
            conn.close()

            logger.info("Migrations table initialized")

        except Exception as e:
            logger.error(f"Failed to initialize migrations table: {e}")
            raise

    def _register_migrations(self):
        """Register all migrations in order"""

        # Migration 1: Add whale tracking table
        self.migrations.append(Migration(
            version=1,
            description="Add whale tracking table",
            up_sql="""
                CREATE TABLE IF NOT EXISTS whale_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_hash TEXT UNIQUE NOT NULL,
                    blockchain TEXT NOT NULL,
                    from_address TEXT NOT NULL,
                    to_address TEXT NOT NULL,
                    amount REAL NOT NULL,
                    token_symbol TEXT,
                    usd_value REAL,
                    timestamp TIMESTAMP NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_whale_timestamp
                ON whale_transactions(timestamp);

                CREATE INDEX IF NOT EXISTS idx_whale_blockchain
                ON whale_transactions(blockchain);
            """,
            down_sql="DROP TABLE IF EXISTS whale_transactions;"
        ))

        # Migration 2: Add indices for performance
        self.migrations.append(Migration(
            version=2,
            description="Add performance indices",
            up_sql="""
                CREATE INDEX IF NOT EXISTS idx_prices_symbol_timestamp
                ON prices(symbol, timestamp);

                CREATE INDEX IF NOT EXISTS idx_news_published_date
                ON news(published_date DESC);

                CREATE INDEX IF NOT EXISTS idx_analysis_symbol_timestamp
                ON market_analysis(symbol, timestamp DESC);
            """,
            down_sql="""
                DROP INDEX IF EXISTS idx_prices_symbol_timestamp;
                DROP INDEX IF EXISTS idx_news_published_date;
                DROP INDEX IF EXISTS idx_analysis_symbol_timestamp;
            """
        ))

        # Migration 3: Add API key tracking
        self.migrations.append(Migration(
            version=3,
            description="Add API key tracking table",
            up_sql="""
                CREATE TABLE IF NOT EXISTS api_key_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key_hash TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time_ms INTEGER,
                    status_code INTEGER,
                    ip_address TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp
                ON api_key_usage(timestamp);

                CREATE INDEX IF NOT EXISTS idx_api_usage_key
                ON api_key_usage(api_key_hash);
            """,
            down_sql="DROP TABLE IF EXISTS api_key_usage;"
        ))

        # Migration 4: Add user queries metadata
        self.migrations.append(Migration(
            version=4,
            description="Enhance user queries table with metadata",
            up_sql="""
                CREATE TABLE IF NOT EXISTS user_queries_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    query_type TEXT,
                    result_count INTEGER,
                    execution_time_ms INTEGER,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Migrate old data if exists
                INSERT INTO user_queries_v2 (query, result_count, timestamp)
                SELECT query, result_count, timestamp
                FROM user_queries
                WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='user_queries');

                DROP TABLE IF EXISTS user_queries;

                ALTER TABLE user_queries_v2 RENAME TO user_queries;

                CREATE INDEX IF NOT EXISTS idx_user_queries_timestamp
                ON user_queries(timestamp);
            """,
            down_sql="-- Cannot rollback data migration"
        ))

        # Migration 5: Add caching metadata table
        self.migrations.append(Migration(
            version=5,
            description="Add cache metadata table",
            up_sql="""
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    cache_key TEXT PRIMARY KEY,
                    data_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    size_bytes INTEGER
                );

                CREATE INDEX IF NOT EXISTS idx_cache_expires
                ON cache_metadata(expires_at);
            """,
            down_sql="DROP TABLE IF EXISTS cache_metadata;"
        ))

        logger.info(f"Registered {len(self.migrations)} migrations")

    def get_current_version(self) -> int:
        """
        Get current database schema version

        Returns:
            Current version number (0 if no migrations applied)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT MAX(version) FROM schema_migrations"
            )
            result = cursor.fetchone()

            conn.close()

            return result[0] if result[0] is not None else 0

        except Exception as e:
            logger.error(f"Failed to get current version: {e}")
            return 0

    def get_pending_migrations(self) -> List[Migration]:
        """
        Get list of pending migrations

        Returns:
            List of migrations not yet applied
        """
        current_version = self.get_current_version()

        return [
            migration for migration in self.migrations
            if migration.version > current_version
        ]

    def apply_migration(self, migration: Migration) -> bool:
        """
        Apply a single migration

        Args:
            migration: Migration to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            start_time = datetime.now()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Execute migration SQL
            cursor.executescript(migration.up_sql)

            # Record migration
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            cursor.execute(
                """
                INSERT INTO schema_migrations
                (version, description, applied_at, execution_time_ms)
                VALUES (?, ?, ?, ?)
                """,
                (
                    migration.version,
                    migration.description,
                    datetime.now(),
                    execution_time
                )
            )

            conn.commit()
            conn.close()

            logger.info(
                f"Applied migration {migration.version}: {migration.description} "
                f"({execution_time}ms)"
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to apply migration {migration.version}: {e}\n"
                f"{traceback.format_exc()}"
            )
            return False

    def migrate_to_latest(self) -> Tuple[bool, List[int]]:
        """
        Apply all pending migrations

        Returns:
            Tuple of (success: bool, applied_versions: List[int])
        """
        pending = self.get_pending_migrations()

        if not pending:
            logger.info("No pending migrations")
            return True, []

        logger.info(f"Applying {len(pending)} pending migrations...")

        applied = []
        for migration in pending:
            if self.apply_migration(migration):
                applied.append(migration.version)
            else:
                logger.error(f"Migration failed at version {migration.version}")
                return False, applied

        logger.info(f"Successfully applied {len(applied)} migrations")
        return True, applied

    def rollback_migration(self, version: int) -> bool:
        """
        Rollback a specific migration

        Args:
            version: Migration version to rollback

        Returns:
            True if successful, False otherwise
        """
        migration = next(
            (m for m in self.migrations if m.version == version),
            None
        )

        if not migration:
            logger.error(f"Migration {version} not found")
            return False

        if not migration.down_sql:
            logger.error(f"Migration {version} has no rollback SQL")
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Execute rollback SQL
            cursor.executescript(migration.down_sql)

            # Remove migration record
            cursor.execute(
                "DELETE FROM schema_migrations WHERE version = ?",
                (version,)
            )

            conn.commit()
            conn.close()

            logger.info(f"Rolled back migration {version}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False

    def get_migration_history(self) -> List[Tuple[int, str, str]]:
        """
        Get migration history

        Returns:
            List of (version, description, applied_at) tuples
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT version, description, applied_at
                FROM schema_migrations
                ORDER BY version
            """)

            history = cursor.fetchall()
            conn.close()

            return history

        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []


# ==================== CONVENIENCE FUNCTIONS ====================


def auto_migrate(db_path: str) -> bool:
    """
    Automatically apply all pending migrations on startup

    Args:
        db_path: Path to database file

    Returns:
        True if all migrations applied successfully
    """
    try:
        manager = MigrationManager(db_path)
        current = manager.get_current_version()
        logger.info(f"Current schema version: {current}")

        success, applied = manager.migrate_to_latest()

        if success and applied:
            logger.info(f"Database migrated to version {max(applied)}")
        elif success:
            logger.info("Database already at latest version")
        else:
            logger.error("Migration failed")

        return success

    except Exception as e:
        logger.error(f"Auto-migration failed: {e}")
        return False

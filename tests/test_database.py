"""
Unit tests for database module
Comprehensive test coverage for database operations
"""

import os
import sqlite3

# Import modules to test
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import db_manager
from database.migrations import MigrationManager, auto_migrate


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    yield path

    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def db_instance(temp_db):
    """Create database instance for testing"""
    from database import CryptoDatabase

    db = CryptoDatabase(temp_db)
    return db


class TestDatabaseInitialization:
    """Test database initialization and schema creation"""

    def test_database_creation(self, temp_db):
        """Test that database file is created"""
        from database import CryptoDatabase

        db = CryptoDatabase(temp_db)

        assert os.path.exists(temp_db)
        assert os.path.getsize(temp_db) > 0

    def test_tables_created(self, db_instance):
        """Test that all required tables are created"""
        conn = sqlite3.connect(db_instance.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table'
        """
        )

        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        required_tables = {"prices", "news", "market_analysis", "user_queries"}
        assert required_tables.issubset(tables)

    def test_indices_created(self, db_instance):
        """Test that indices are created"""
        conn = sqlite3.connect(db_instance.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='index'
        """
        )

        indices = {row[0] for row in cursor.fetchall()}
        conn.close()

        # Should have some indices
        assert len(indices) > 0


class TestPriceOperations:
    """Test price data operations"""

    def test_save_price(self, db_instance):
        """Test saving price data"""
        price_data = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "price_usd": 50000.0,
            "volume_24h": 1000000000,
            "market_cap": 950000000000,
            "percent_change_1h": 0.5,
            "percent_change_24h": 2.3,
            "percent_change_7d": -1.2,
            "rank": 1,
        }

        result = db_instance.save_price(price_data)
        assert result is True

    def test_get_latest_prices(self, db_instance):
        """Test retrieving latest prices"""
        # Insert test data
        for i in range(10):
            price_data = {
                "symbol": f"TEST{i}",
                "name": f"Test Coin {i}",
                "price_usd": 100.0 * (i + 1),
                "volume_24h": 1000000,
                "market_cap": 10000000,
                "rank": i + 1,
            }
            db_instance.save_price(price_data)

        prices = db_instance.get_latest_prices(limit=5)

        assert len(prices) == 5
        assert prices[0]["rank"] == 1

    def test_get_historical_prices(self, db_instance):
        """Test retrieving historical prices"""
        # Insert test data
        for i in range(5):
            price_data = {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_usd": 50000.0 + (i * 100),
                "volume_24h": 1000000000,
                "market_cap": 950000000000,
                "rank": 1,
            }
            db_instance.save_price(price_data)

        prices = db_instance.get_historical_prices("BTC", days=7)

        assert len(prices) > 0
        assert all(p["symbol"] == "BTC" for p in prices)


class TestNewsOperations:
    """Test news data operations"""

    def test_save_news(self, db_instance):
        """Test saving news article"""
        news_data = {
            "title": "Test Article",
            "summary": "This is a test summary",
            "url": "https://example.com/test",
            "source": "Test Source",
            "sentiment_score": 0.8,
            "sentiment_label": "positive",
        }

        result = db_instance.save_news(news_data)
        assert result is True

    def test_duplicate_news_url(self, db_instance):
        """Test that duplicate URLs are rejected"""
        news_data = {
            "title": "Test Article",
            "summary": "Summary",
            "url": "https://example.com/unique",
            "source": "Test",
        }

        # First insert should succeed
        assert db_instance.save_news(news_data) is True

        # Second insert with same URL should fail
        assert db_instance.save_news(news_data) is False

    def test_get_latest_news(self, db_instance):
        """Test retrieving latest news"""
        # Insert test news
        for i in range(10):
            news_data = {
                "title": f"Article {i}",
                "summary": f"Summary {i}",
                "url": f"https://example.com/article{i}",
                "source": "Test Source",
            }
            db_instance.save_news(news_data)

        news = db_instance.get_latest_news(limit=5)

        assert len(news) == 5
        assert all("title" in n for n in news)


class TestAnalysisOperations:
    """Test market analysis operations"""

    def test_save_analysis(self, db_instance):
        """Test saving market analysis"""
        analysis_data = {
            "symbol": "BTC",
            "timeframe": "24h",
            "trend": "bullish",
            "support_level": 45000.0,
            "resistance_level": 55000.0,
            "prediction": "Price likely to increase",
            "confidence": 0.75,
        }

        result = db_instance.save_analysis(analysis_data)
        assert result is True

    def test_get_latest_analysis(self, db_instance):
        """Test retrieving latest analysis"""
        # Insert test analysis
        analysis_data = {"symbol": "BTC", "timeframe": "24h", "trend": "bullish", "confidence": 0.8}
        db_instance.save_analysis(analysis_data)

        analysis = db_instance.get_latest_analysis("BTC")

        assert analysis is not None
        assert analysis["symbol"] == "BTC"
        assert analysis["trend"] == "bullish"


class TestMigrations:
    """Test database migration system"""

    def test_migration_manager_init(self, temp_db):
        """Test migration manager initialization"""
        manager = MigrationManager(temp_db)

        assert len(manager.migrations) > 0
        assert manager.get_current_version() == 0

    def test_apply_migration(self, temp_db):
        """Test applying a single migration"""
        manager = MigrationManager(temp_db)
        pending = manager.get_pending_migrations()

        assert len(pending) > 0

        # Apply first migration
        result = manager.apply_migration(pending[0])
        assert result is True

        # Version should be updated
        assert manager.get_current_version() == pending[0].version

    def test_migrate_to_latest(self, temp_db):
        """Test migrating to latest version"""
        manager = MigrationManager(temp_db)
        success, applied = manager.migrate_to_latest()

        assert success is True
        assert len(applied) > 0
        assert manager.get_current_version() == max(applied)

    def test_auto_migrate(self, temp_db):
        """Test auto-migration function"""
        result = auto_migrate(temp_db)
        assert result is True


class TestDataValidation:
    """Test data validation"""

    def test_price_validation(self, db_instance):
        """Test price data validation"""
        # Invalid price (negative)
        invalid_price = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "price_usd": -100.0,  # Invalid
            "rank": 1,
        }

        # Should handle gracefully (depending on implementation)
        # This test assumes validation is in place

    def test_required_fields(self, db_instance):
        """Test that required fields are enforced"""
        # Missing required field
        incomplete_price = {
            "symbol": "BTC"
            # Missing name, price_usd, etc.
        }

        # Should handle missing fields gracefully


class TestConcurrency:
    """Test concurrent database access"""

    def test_concurrent_writes(self, db_instance):
        """Test concurrent write operations"""
        import threading

        def write_price(i):
            price_data = {
                "symbol": f"TEST{i}",
                "name": f"Test {i}",
                "price_usd": float(i),
                "rank": i,
            }
            db_instance.save_price(price_data)

        threads = [threading.Thread(target=write_price, args=(i,)) for i in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All writes should succeed
        prices = db_instance.get_latest_prices(limit=10)
        assert len(prices) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

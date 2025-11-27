#!/usr/bin/env python3
"""
بانک اطلاعاتی قدرتمند رمزارز
Powerful Crypto Data Bank - Database Layer
"""

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class CryptoDataBank:
    """بانک اطلاعاتی قدرتمند برای ذخیره و مدیریت داده‌های رمزارز"""

    def __init__(self, db_path: str = "data/crypto_bank.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Get thread-safe database connection"""
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row

        try:
            yield self._local.conn
        except Exception as e:
            self._local.conn.rollback()
            raise e

    def _init_database(self):
        """Initialize all database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # جدول قیمت‌های لحظه‌ای
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    price_usd REAL NOT NULL,
                    change_1h REAL,
                    change_24h REAL,
                    change_7d REAL,
                    volume_24h REAL,
                    market_cap REAL,
                    rank INTEGER,
                    source TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            """
            )

            # جدول OHLCV (کندل‌ها)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ohlcv (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    timestamp BIGINT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    source TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, interval, timestamp)
                )
            """
            )

            # جدول اخبار
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    published_at DATETIME,
                    sentiment REAL,
                    coins TEXT,
                    category TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # جدول احساسات بازار
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS market_sentiment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fear_greed_value INTEGER,
                    fear_greed_classification TEXT,
                    overall_sentiment TEXT,
                    sentiment_score REAL,
                    confidence REAL,
                    source TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # جدول داده‌های on-chain
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS onchain_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chain TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    unit TEXT,
                    source TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(chain, metric_name, timestamp)
                )
            """
            )

            # جدول social media metrics
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS social_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    followers INTEGER,
                    posts_24h INTEGER,
                    engagement_rate REAL,
                    sentiment_score REAL,
                    trending_rank INTEGER,
                    source TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # جدول DeFi metrics
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS defi_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol TEXT NOT NULL,
                    chain TEXT NOT NULL,
                    tvl REAL,
                    volume_24h REAL,
                    fees_24h REAL,
                    users_24h INTEGER,
                    source TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # جدول پیش‌بینی‌ها (از مدل‌های ML)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    predicted_value REAL NOT NULL,
                    confidence REAL,
                    horizon TEXT,
                    features TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # جدول تحلیل‌های هوش مصنوعی
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    analysis_type TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT NOT NULL,
                    confidence REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # جدول کش API
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS api_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    params TEXT,
                    response TEXT NOT NULL,
                    ttl INTEGER DEFAULT 300,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    UNIQUE(endpoint, params)
                )
            """
            )

            # Indexes برای بهبود کارایی
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_symbol ON prices(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_interval ON ohlcv(symbol, interval)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_sentiment_timestamp ON market_sentiment(timestamp)"
            )

            conn.commit()

    # === PRICE OPERATIONS ===

    def save_price(self, symbol: str, price_data: Dict[str, Any], source: str = "auto"):
        """ذخیره قیمت"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO prices
                (symbol, price, price_usd, change_1h, change_24h, change_7d,
                 volume_24h, market_cap, rank, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    symbol,
                    price_data.get("price", 0),
                    price_data.get("priceUsd", price_data.get("price", 0)),
                    price_data.get("change1h"),
                    price_data.get("change24h"),
                    price_data.get("change7d"),
                    price_data.get("volume24h"),
                    price_data.get("marketCap"),
                    price_data.get("rank"),
                    source,
                    datetime.now(),
                ),
            )
            conn.commit()

    def get_latest_prices(
        self, symbols: Optional[List[str]] = None, limit: int = 100
    ) -> List[Dict]:
        """دریافت آخرین قیمت‌ها"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if symbols:
                placeholders = ",".join("?" * len(symbols))
                query = f"""
                    SELECT * FROM prices
                    WHERE symbol IN ({placeholders})
                    AND timestamp = (
                        SELECT MAX(timestamp) FROM prices p2
                        WHERE p2.symbol = prices.symbol
                    )
                    ORDER BY market_cap DESC
                    LIMIT ?
                """
                cursor.execute(query, (*symbols, limit))
            else:
                cursor.execute(
                    """
                    SELECT * FROM prices
                    WHERE timestamp = (
                        SELECT MAX(timestamp) FROM prices p2
                        WHERE p2.symbol = prices.symbol
                    )
                    ORDER BY market_cap DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            return [dict(row) for row in cursor.fetchall()]

    def get_price_history(self, symbol: str, hours: int = 24) -> List[Dict]:
        """تاریخچه قیمت"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            since = datetime.now() - timedelta(hours=hours)

            cursor.execute(
                """
                SELECT * FROM prices
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """,
                (symbol, since),
            )

            return [dict(row) for row in cursor.fetchall()]

    # === OHLCV OPERATIONS ===

    def save_ohlcv_batch(
        self, symbol: str, interval: str, candles: List[Dict], source: str = "auto"
    ):
        """ذخیره دسته‌ای کندل‌ها"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for candle in candles:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO ohlcv
                    (symbol, interval, timestamp, open, high, low, close, volume, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        symbol,
                        interval,
                        candle["timestamp"],
                        candle["open"],
                        candle["high"],
                        candle["low"],
                        candle["close"],
                        candle["volume"],
                        source,
                    ),
                )

            conn.commit()

    def get_ohlcv(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """دریافت کندل‌ها"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM ohlcv
                WHERE symbol = ? AND interval = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (symbol, interval, limit),
            )

            results = [dict(row) for row in cursor.fetchall()]
            results.reverse()  # برگشت به ترتیب صعودی
            return results

    # === NEWS OPERATIONS ===

    def save_news(self, news_data: Dict[str, Any]):
        """ذخیره خبر"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO news
                (title, description, url, source, published_at, sentiment, coins, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    news_data.get("title"),
                    news_data.get("description"),
                    news_data["url"],
                    news_data.get("source", "unknown"),
                    news_data.get("published_at"),
                    news_data.get("sentiment"),
                    json.dumps(news_data.get("coins", [])),
                    news_data.get("category"),
                ),
            )
            conn.commit()

    def get_latest_news(self, limit: int = 50, category: Optional[str] = None) -> List[Dict]:
        """دریافت آخرین اخبار"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if category:
                cursor.execute(
                    """
                    SELECT * FROM news
                    WHERE category = ?
                    ORDER BY published_at DESC
                    LIMIT ?
                """,
                    (category, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM news
                    ORDER BY published_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get("coins"):
                    result["coins"] = json.loads(result["coins"])
                results.append(result)

            return results

    # === SENTIMENT OPERATIONS ===

    def save_sentiment(self, sentiment_data: Dict[str, Any], source: str = "auto"):
        """ذخیره احساسات بازار"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO market_sentiment
                (fear_greed_value, fear_greed_classification, overall_sentiment,
                 sentiment_score, confidence, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    sentiment_data.get("fear_greed_value"),
                    sentiment_data.get("fear_greed_classification"),
                    sentiment_data.get("overall_sentiment"),
                    sentiment_data.get("sentiment_score"),
                    sentiment_data.get("confidence"),
                    source,
                ),
            )
            conn.commit()

    def get_latest_sentiment(self) -> Optional[Dict]:
        """دریافت آخرین احساسات"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM market_sentiment
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            return dict(row) if row else None

    # === AI ANALYSIS OPERATIONS ===

    def save_ai_analysis(self, analysis_data: Dict[str, Any]):
        """ذخیره تحلیل هوش مصنوعی"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO ai_analysis
                (symbol, analysis_type, model_used, input_data, output_data, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    analysis_data.get("symbol"),
                    analysis_data["analysis_type"],
                    analysis_data["model_used"],
                    json.dumps(analysis_data["input_data"]),
                    json.dumps(analysis_data["output_data"]),
                    analysis_data.get("confidence"),
                ),
            )
            conn.commit()

    def get_ai_analyses(self, symbol: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """دریافت تحلیل‌های AI"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if symbol:
                cursor.execute(
                    """
                    SELECT * FROM ai_analysis
                    WHERE symbol = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (symbol, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM ai_analysis
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result["input_data"] = json.loads(result["input_data"])
                result["output_data"] = json.loads(result["output_data"])
                results.append(result)

            return results

    # === CACHE OPERATIONS ===

    def cache_set(self, endpoint: str, params: str, response: Any, ttl: int = 300):
        """ذخیره در کش"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            expires_at = datetime.now() + timedelta(seconds=ttl)

            cursor.execute(
                """
                INSERT OR REPLACE INTO api_cache
                (endpoint, params, response, ttl, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (endpoint, params, json.dumps(response), ttl, expires_at),
            )

            conn.commit()

    def cache_get(self, endpoint: str, params: str = "") -> Optional[Any]:
        """دریافت از کش"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT response FROM api_cache
                WHERE endpoint = ? AND params = ? AND expires_at > ?
            """,
                (endpoint, params, datetime.now()),
            )

            row = cursor.fetchone()
            if row:
                return json.loads(row["response"])
            return None

    def cache_clear_expired(self):
        """پاک کردن کش‌های منقضی شده"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_cache WHERE expires_at <= ?", (datetime.now(),))
            conn.commit()

    # === STATISTICS ===

    def get_statistics(self) -> Dict[str, Any]:
        """آمار کلی دیتابیس"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # تعداد رکوردها
            tables = ["prices", "ohlcv", "news", "market_sentiment", "ai_analysis", "predictions"]

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()["count"]

            # تعداد سمبل‌های یونیک
            cursor.execute("SELECT COUNT(DISTINCT symbol) as count FROM prices")
            stats["unique_symbols"] = cursor.fetchone()["count"]

            # آخرین به‌روزرسانی
            cursor.execute("SELECT MAX(timestamp) as last_update FROM prices")
            stats["last_price_update"] = cursor.fetchone()["last_update"]

            # حجم دیتابیس
            stats["database_size"] = Path(self.db_path).stat().st_size

            return stats


# سینگلتون برای استفاده در کل برنامه
_db_instance = None


def get_db() -> CryptoDataBank:
    """دریافت instance دیتابیس"""
    global _db_instance
    if _db_instance is None:
        _db_instance = CryptoDataBank()
    return _db_instance

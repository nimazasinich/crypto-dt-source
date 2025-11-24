"""
SQLAlchemy Database Models
Defines all database tables for the crypto API monitoring system
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class ProviderCategory(enum.Enum):
    """Provider category enumeration"""
    MARKET_DATA = "market_data"
    BLOCKCHAIN_EXPLORERS = "blockchain_explorers"
    NEWS = "news"
    SENTIMENT = "sentiment"
    ONCHAIN_ANALYTICS = "onchain_analytics"
    RPC_NODES = "rpc_nodes"
    CORS_PROXIES = "cors_proxies"


class RateLimitType(enum.Enum):
    """Rate limit period type"""
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"


class ConnectionStatus(enum.Enum):
    """Connection attempt status"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


class Provider(Base):
    """API Provider configuration table"""
    __tablename__ = 'providers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=False)
    endpoint_url = Column(String(500), nullable=False)
    requires_key = Column(Boolean, default=False)
    api_key_masked = Column(String(100), nullable=True)
    rate_limit_type = Column(String(50), nullable=True)
    rate_limit_value = Column(Integer, nullable=True)
    timeout_ms = Column(Integer, default=10000)
    priority_tier = Column(Integer, default=3)  # 1-4, 1 is highest priority
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connection_attempts = relationship("ConnectionAttempt", back_populates="provider", cascade="all, delete-orphan")
    data_collections = relationship("DataCollection", back_populates="provider", cascade="all, delete-orphan")
    rate_limit_usage = relationship("RateLimitUsage", back_populates="provider", cascade="all, delete-orphan")
    schedule_config = relationship("ScheduleConfig", back_populates="provider", uselist=False, cascade="all, delete-orphan")


class ConnectionAttempt(Base):
    """Connection attempts log table"""
    __tablename__ = 'connection_attempts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False, index=True)
    endpoint = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    http_status_code = Column(Integer, nullable=True)
    error_type = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    retry_result = Column(String(100), nullable=True)

    # Relationships
    provider = relationship("Provider", back_populates="connection_attempts")


class DataCollection(Base):
    """Data collections table"""
    __tablename__ = 'data_collections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    actual_fetch_time = Column(DateTime, nullable=False)
    data_timestamp = Column(DateTime, nullable=True)  # Timestamp from API response
    staleness_minutes = Column(Float, nullable=True)
    record_count = Column(Integer, default=0)
    payload_size_bytes = Column(Integer, default=0)
    data_quality_score = Column(Float, default=1.0)
    on_schedule = Column(Boolean, default=True)
    skip_reason = Column(String(255), nullable=True)

    # Relationships
    provider = relationship("Provider", back_populates="data_collections")


class RateLimitUsage(Base):
    """Rate limit usage tracking table"""
    __tablename__ = 'rate_limit_usage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False, index=True)
    limit_type = Column(String(50), nullable=False)
    limit_value = Column(Integer, nullable=False)
    current_usage = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    reset_time = Column(DateTime, nullable=False)

    # Relationships
    provider = relationship("Provider", back_populates="rate_limit_usage")


class ScheduleConfig(Base):
    """Schedule configuration table"""
    __tablename__ = 'schedule_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False, unique=True)
    schedule_interval = Column(String(50), nullable=False)  # e.g., "every_1_min", "every_5_min"
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    on_time_count = Column(Integer, default=0)
    late_count = Column(Integer, default=0)
    skip_count = Column(Integer, default=0)

    # Relationships
    provider = relationship("Provider", back_populates="schedule_config")


class ScheduleCompliance(Base):
    """Schedule compliance tracking table"""
    __tablename__ = 'schedule_compliance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False, index=True)
    expected_time = Column(DateTime, nullable=False)
    actual_time = Column(DateTime, nullable=True)
    delay_seconds = Column(Integer, nullable=True)
    on_time = Column(Boolean, default=True)
    skip_reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class FailureLog(Base):
    """Detailed failure tracking table"""
    __tablename__ = 'failure_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False, index=True)
    endpoint = Column(String(500), nullable=False)
    error_type = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    http_status = Column(Integer, nullable=True)
    retry_attempted = Column(Boolean, default=False)
    retry_result = Column(String(100), nullable=True)
    remediation_applied = Column(String(255), nullable=True)


class Alert(Base):
    """Alerts table"""
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="medium")
    message = Column(Text, nullable=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)


class SystemMetrics(Base):
    """System-wide metrics table"""
    __tablename__ = 'system_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    total_providers = Column(Integer, default=0)
    online_count = Column(Integer, default=0)
    degraded_count = Column(Integer, default=0)
    offline_count = Column(Integer, default=0)
    avg_response_time_ms = Column(Float, default=0)
    total_requests_hour = Column(Integer, default=0)
    total_failures_hour = Column(Integer, default=0)
    system_health = Column(String(50), default="healthy")


class SourcePool(Base):
    """Source pools for intelligent rotation"""
    __tablename__ = 'source_pools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    rotation_strategy = Column(String(50), default="round_robin")  # round_robin, least_used, priority
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pool_members = relationship("PoolMember", back_populates="pool", cascade="all, delete-orphan")
    rotation_history = relationship("RotationHistory", back_populates="pool", cascade="all, delete-orphan")


class PoolMember(Base):
    """Members of source pools"""
    __tablename__ = 'pool_members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, ForeignKey('source_pools.id'), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False, index=True)
    priority = Column(Integer, default=1)  # Higher number = higher priority
    weight = Column(Integer, default=1)  # For weighted rotation
    enabled = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    use_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pool = relationship("SourcePool", back_populates="pool_members")
    provider = relationship("Provider")


class RotationHistory(Base):
    """History of source rotations"""
    __tablename__ = 'rotation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, ForeignKey('source_pools.id'), nullable=False, index=True)
    from_provider_id = Column(Integer, ForeignKey('providers.id'), nullable=True, index=True)
    to_provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False, index=True)
    rotation_reason = Column(String(100), nullable=False)  # rate_limit, failure, manual, scheduled
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    success = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    # Relationships
    pool = relationship("SourcePool", back_populates="rotation_history")
    from_provider = relationship("Provider", foreign_keys=[from_provider_id])
    to_provider = relationship("Provider", foreign_keys=[to_provider_id])


class RotationState(Base):
    """Current rotation state for each pool"""
    __tablename__ = 'rotation_state'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, ForeignKey('source_pools.id'), nullable=False, unique=True, index=True)
    current_provider_id = Column(Integer, ForeignKey('providers.id'), nullable=True)
    last_rotation = Column(DateTime, nullable=True)
    next_rotation = Column(DateTime, nullable=True)
    rotation_count = Column(Integer, default=0)
    state_data = Column(Text, nullable=True)  # JSON field for additional state
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pool = relationship("SourcePool")
    current_provider = relationship("Provider")


# ============================================================================
# Data Storage Tables (Actual Crypto Data)
# ============================================================================

class MarketPrice(Base):
    """Market price data table"""
    __tablename__ = 'market_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    price_usd = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(100), nullable=False)


class NewsArticle(Base):
    """News articles table"""
    __tablename__ = 'news_articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    source = Column(String(100), nullable=False, index=True)
    url = Column(String(1000), nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)
    sentiment = Column(String(50), nullable=True)  # positive, negative, neutral
    tags = Column(String(500), nullable=True)  # comma-separated tags
    created_at = Column(DateTime, default=datetime.utcnow)


class WhaleTransaction(Base):
    """Whale transactions table"""
    __tablename__ = 'whale_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain = Column(String(50), nullable=False, index=True)
    transaction_hash = Column(String(200), nullable=False, unique=True)
    from_address = Column(String(200), nullable=False)
    to_address = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    amount_usd = Column(Float, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SentimentMetric(Base):
    """Sentiment metrics table"""
    __tablename__ = 'sentiment_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    classification = Column(String(50), nullable=False)  # fear, greed, neutral, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(100), nullable=False)


class GasPrice(Base):
    """Gas prices table"""
    __tablename__ = 'gas_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain = Column(String(50), nullable=False, index=True)
    gas_price_gwei = Column(Float, nullable=False)
    fast_gas_price = Column(Float, nullable=True)
    standard_gas_price = Column(Float, nullable=True)
    slow_gas_price = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(100), nullable=False)


class BlockchainStat(Base):
    """Blockchain statistics table"""
    __tablename__ = 'blockchain_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain = Column(String(50), nullable=False, index=True)
    latest_block = Column(Integer, nullable=True)
    total_transactions = Column(Integer, nullable=True)
    network_hashrate = Column(Float, nullable=True)
    difficulty = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(100), nullable=False)


# ============================================================================
# HuggingFace Space API Cache Tables (REAL DATA ONLY)
# ============================================================================

class CachedMarketData(Base):
    """
    Cached market data from FREE APIs (CoinGecko, Binance, etc.)
    
    CRITICAL RULES:
    - ONLY real data from external APIs
    - NEVER fake/mock/generated data
    - Updated by background workers
    """
    __tablename__ = 'cached_market_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)  # BTC, ETH, etc.
    price = Column(Float, nullable=False)  # Current price in USD
    market_cap = Column(Float, nullable=True)  # Market cap in USD
    volume_24h = Column(Float, nullable=True)  # 24h volume in USD
    change_24h = Column(Float, nullable=True)  # 24h price change percentage
    high_24h = Column(Float, nullable=True)  # 24h high price
    low_24h = Column(Float, nullable=True)  # 24h low price
    provider = Column(String(50), nullable=False)  # coingecko, binance, etc.
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)  # When fetched
    
    # Index for fast queries
    __table_args__ = (
        # Unique constraint to prevent duplicates
        # Allow multiple entries per symbol for historical tracking
    )


class CachedOHLC(Base):
    """
    Cached OHLC (candlestick) data from FREE APIs (Binance, CryptoCompare, etc.)
    
    CRITICAL RULES:
    - ONLY real candlestick data from exchanges
    - NEVER generated/interpolated candles
    - Updated by background workers
    """
    __tablename__ = 'cached_ohlc'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)  # BTCUSDT, ETHUSDT, etc.
    interval = Column(String(10), nullable=False, index=True)  # 1m, 5m, 15m, 1h, 4h, 1d
    timestamp = Column(DateTime, nullable=False, index=True)  # Candle open time
    open = Column(Float, nullable=False)  # Open price
    high = Column(Float, nullable=False)  # High price
    low = Column(Float, nullable=False)  # Low price
    close = Column(Float, nullable=False)  # Close price
    volume = Column(Float, nullable=False)  # Volume
    provider = Column(String(50), nullable=False)  # binance, cryptocompare, etc.
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # When fetched
    
    # Composite index for fast queries
    __table_args__ = (
        # Unique constraint to prevent duplicate candles
        # (symbol, interval, timestamp) should be unique
    )

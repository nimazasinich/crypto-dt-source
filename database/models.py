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

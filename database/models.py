"""
SQLAlchemy Database Models for Crypto API Monitor
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class StatusEnum(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    AUTHENTICATION_ERROR = "authentication_error"


class ProviderStatusEnum(enum.Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    endpoint_url = Column(String, nullable=False)
    requires_key = Column(Boolean, default=False)
    api_key_masked = Column(String, nullable=True)
    rate_limit_type = Column(String, default="per_minute")
    rate_limit_value = Column(Integer, default=60)
    timeout_ms = Column(Integer, default=10000)
    priority_tier = Column(Integer, default=2)
    status = Column(Enum(ProviderStatusEnum), default=ProviderStatusEnum.UNKNOWN)
    last_response_time_ms = Column(Integer, nullable=True)
    last_check_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connection_attempts = relationship("ConnectionAttempt", back_populates="provider")
    data_collections = relationship("DataCollection", back_populates="provider")
    rate_limit_usages = relationship("RateLimitUsage", back_populates="provider")
    schedule_config = relationship("ScheduleConfig", back_populates="provider", uselist=False)


class ConnectionAttempt(Base):
    __tablename__ = "connection_attempts"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    endpoint = Column(String, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, index=True)
    response_time_ms = Column(Integer, nullable=True)
    http_status_code = Column(Integer, nullable=True)
    error_type = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    retry_result = Column(String, nullable=True)

    # Relationship
    provider = relationship("Provider", back_populates="connection_attempts")


class DataCollection(Base):
    __tablename__ = "data_collections"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    category = Column(String, index=True, nullable=False)
    scheduled_time = Column(DateTime, nullable=True)
    actual_fetch_time = Column(DateTime, default=datetime.utcnow, index=True)
    data_timestamp = Column(DateTime, nullable=True)
    staleness_minutes = Column(Float, nullable=True)
    record_count = Column(Integer, default=0)
    payload_size_bytes = Column(Integer, default=0)
    data_quality_score = Column(Float, default=1.0)
    on_schedule = Column(Boolean, default=True)
    skip_reason = Column(String, nullable=True)

    # Relationship
    provider = relationship("Provider", back_populates="data_collections")


class RateLimitUsage(Base):
    __tablename__ = "rate_limit_usage"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    limit_type = Column(String, nullable=False)
    limit_value = Column(Integer, nullable=False)
    current_usage = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    reset_time = Column(DateTime, nullable=True)

    # Relationship
    provider = relationship("Provider", back_populates="rate_limit_usages")


class ScheduleConfig(Base):
    __tablename__ = "schedule_config"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, unique=True)
    schedule_interval = Column(String, nullable=False)  # every_1_min, every_5_min, etc.
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)

    # Relationship
    provider = relationship("Provider", back_populates="schedule_config")

"""
Database Manager Module
Provides comprehensive database operations for the crypto API monitoring system
"""

import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

from sqlalchemy import create_engine, func, and_, or_, desc, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from database.models import (
    Base,
    Provider,
    ConnectionAttempt,
    DataCollection,
    RateLimitUsage,
    ScheduleConfig,
    ScheduleCompliance,
    FailureLog,
    Alert,
    SystemMetrics,
    ConnectionStatus,
    ProviderCategory,
    # Crypto data models
    MarketPrice,
    NewsArticle,
    WhaleTransaction,
    SentimentMetric,
    GasPrice,
    BlockchainStat
)
from database.data_access import DataAccessMixin
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger("db_manager", level="INFO")


class DatabaseManager(DataAccessMixin):
    """
    Comprehensive database manager for API monitoring system
    Handles all database operations with proper error handling and logging
    """

    def __init__(self, db_path: str = "data/api_monitor.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_directory()

        # Create SQLAlchemy engine
        db_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(
            db_url,
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False}  # SQLite specific
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False  # Allow access to attributes after commit
        )

        logger.info(f"Database manager initialized with database: {self.db_path}")

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions
        Automatically handles commit/rollback and cleanup

        Yields:
            SQLAlchemy session

        Example:
            with db_manager.get_session() as session:
                provider = session.query(Provider).first()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {str(e)}", exc_info=True)
            raise
        finally:
            session.close()

    def init_database(self) -> bool:
        """
        Initialize database by creating all tables

        Returns:
            True if successful, False otherwise
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
            return False

    def drop_all_tables(self) -> bool:
        """
        Drop all tables (use with caution!)

        Returns:
            True if successful, False otherwise
        """
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop tables: {str(e)}", exc_info=True)
            return False

    # ============================================================================
    # Provider CRUD Operations
    # ============================================================================

    def create_provider(
        self,
        name: str,
        category: str,
        endpoint_url: str,
        requires_key: bool = False,
        api_key_masked: Optional[str] = None,
        rate_limit_type: Optional[str] = None,
        rate_limit_value: Optional[int] = None,
        timeout_ms: int = 10000,
        priority_tier: int = 3
    ) -> Optional[Provider]:
        """
        Create a new provider

        Args:
            name: Provider name
            category: Provider category
            endpoint_url: API endpoint URL
            requires_key: Whether API key is required
            api_key_masked: Masked API key for display
            rate_limit_type: Rate limit type (per_minute, per_hour, per_day)
            rate_limit_value: Rate limit value
            timeout_ms: Timeout in milliseconds
            priority_tier: Priority tier (1-4, 1 is highest)

        Returns:
            Created Provider object or None if failed
        """
        try:
            with self.get_session() as session:
                provider = Provider(
                    name=name,
                    category=category,
                    endpoint_url=endpoint_url,
                    requires_key=requires_key,
                    api_key_masked=api_key_masked,
                    rate_limit_type=rate_limit_type,
                    rate_limit_value=rate_limit_value,
                    timeout_ms=timeout_ms,
                    priority_tier=priority_tier
                )
                session.add(provider)
                session.commit()
                session.refresh(provider)
                logger.info(f"Created provider: {name}")
                return provider
        except IntegrityError:
            logger.error(f"Provider already exists: {name}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Failed to create provider {name}: {str(e)}", exc_info=True)
            return None

    def get_provider(self, provider_id: Optional[int] = None, name: Optional[str] = None) -> Optional[Provider]:
        """
        Get a provider by ID or name

        Args:
            provider_id: Provider ID
            name: Provider name

        Returns:
            Provider object or None if not found
        """
        try:
            with self.get_session() as session:
                if provider_id:
                    provider = session.query(Provider).filter(Provider.id == provider_id).first()
                elif name:
                    provider = session.query(Provider).filter(Provider.name == name).first()
                else:
                    logger.warning("Either provider_id or name must be provided")
                    return None

                if provider:
                    session.refresh(provider)
                return provider
        except SQLAlchemyError as e:
            logger.error(f"Failed to get provider: {str(e)}", exc_info=True)
            return None

    def get_all_providers(self, category: Optional[str] = None, enabled_only: bool = False) -> List[Provider]:
        """
        Get all providers with optional filtering

        Args:
            category: Filter by category
            enabled_only: Only return enabled providers (based on schedule_config)

        Returns:
            List of Provider objects
        """
        try:
            with self.get_session() as session:
                query = session.query(Provider)

                if category:
                    query = query.filter(Provider.category == category)

                if enabled_only:
                    query = query.join(ScheduleConfig).filter(ScheduleConfig.enabled == True)

                providers = query.order_by(Provider.priority_tier, Provider.name).all()

                # Refresh all providers to ensure data is loaded
                for provider in providers:
                    session.refresh(provider)

                return providers
        except SQLAlchemyError as e:
            logger.error(f"Failed to get providers: {str(e)}", exc_info=True)
            return []

    def update_provider(self, provider_id: int, **kwargs) -> bool:
        """
        Update a provider's attributes

        Args:
            provider_id: Provider ID
            **kwargs: Attributes to update

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                provider = session.query(Provider).filter(Provider.id == provider_id).first()
                if not provider:
                    logger.warning(f"Provider not found: {provider_id}")
                    return False

                for key, value in kwargs.items():
                    if hasattr(provider, key):
                        setattr(provider, key, value)

                provider.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated provider: {provider.name}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to update provider {provider_id}: {str(e)}", exc_info=True)
            return False

    def delete_provider(self, provider_id: int) -> bool:
        """
        Delete a provider and all related records

        Args:
            provider_id: Provider ID

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                provider = session.query(Provider).filter(Provider.id == provider_id).first()
                if not provider:
                    logger.warning(f"Provider not found: {provider_id}")
                    return False

                provider_name = provider.name
                session.delete(provider)
                session.commit()
                logger.info(f"Deleted provider: {provider_name}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete provider {provider_id}: {str(e)}", exc_info=True)
            return False

    # ============================================================================
    # Connection Attempt Operations
    # ============================================================================

    def save_connection_attempt(
        self,
        provider_id: int,
        endpoint: str,
        status: str,
        response_time_ms: Optional[int] = None,
        http_status_code: Optional[int] = None,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        retry_result: Optional[str] = None
    ) -> Optional[ConnectionAttempt]:
        """
        Save a connection attempt log

        Args:
            provider_id: Provider ID
            endpoint: API endpoint
            status: Connection status
            response_time_ms: Response time in milliseconds
            http_status_code: HTTP status code
            error_type: Error type if failed
            error_message: Error message if failed
            retry_count: Number of retries
            retry_result: Result of retry attempt

        Returns:
            Created ConnectionAttempt object or None if failed
        """
        try:
            with self.get_session() as session:
                attempt = ConnectionAttempt(
                    provider_id=provider_id,
                    endpoint=endpoint,
                    status=status,
                    response_time_ms=response_time_ms,
                    http_status_code=http_status_code,
                    error_type=error_type,
                    error_message=error_message,
                    retry_count=retry_count,
                    retry_result=retry_result
                )
                session.add(attempt)
                session.commit()
                session.refresh(attempt)
                return attempt
        except SQLAlchemyError as e:
            logger.error(f"Failed to save connection attempt: {str(e)}", exc_info=True)
            return None

    def get_connection_attempts(
        self,
        provider_id: Optional[int] = None,
        status: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[ConnectionAttempt]:
        """
        Get connection attempts with filtering

        Args:
            provider_id: Filter by provider ID
            status: Filter by status
            hours: Get attempts from last N hours
            limit: Maximum number of records to return

        Returns:
            List of ConnectionAttempt objects
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                query = session.query(ConnectionAttempt).filter(
                    ConnectionAttempt.timestamp >= cutoff_time
                )

                if provider_id:
                    query = query.filter(ConnectionAttempt.provider_id == provider_id)

                if status:
                    query = query.filter(ConnectionAttempt.status == status)

                attempts = query.order_by(desc(ConnectionAttempt.timestamp)).limit(limit).all()

                for attempt in attempts:
                    session.refresh(attempt)

                return attempts
        except SQLAlchemyError as e:
            logger.error(f"Failed to get connection attempts: {str(e)}", exc_info=True)
            return []

    # ============================================================================
    # Data Collection Operations
    # ============================================================================

    def save_data_collection(
        self,
        provider_id: int,
        category: str,
        scheduled_time: datetime,
        actual_fetch_time: datetime,
        data_timestamp: Optional[datetime] = None,
        staleness_minutes: Optional[float] = None,
        record_count: int = 0,
        payload_size_bytes: int = 0,
        data_quality_score: float = 1.0,
        on_schedule: bool = True,
        skip_reason: Optional[str] = None
    ) -> Optional[DataCollection]:
        """
        Save a data collection record

        Args:
            provider_id: Provider ID
            category: Data category
            scheduled_time: Scheduled collection time
            actual_fetch_time: Actual fetch time
            data_timestamp: Timestamp from API response
            staleness_minutes: Data staleness in minutes
            record_count: Number of records collected
            payload_size_bytes: Payload size in bytes
            data_quality_score: Data quality score (0-1)
            on_schedule: Whether collection was on schedule
            skip_reason: Reason if skipped

        Returns:
            Created DataCollection object or None if failed
        """
        try:
            with self.get_session() as session:
                collection = DataCollection(
                    provider_id=provider_id,
                    category=category,
                    scheduled_time=scheduled_time,
                    actual_fetch_time=actual_fetch_time,
                    data_timestamp=data_timestamp,
                    staleness_minutes=staleness_minutes,
                    record_count=record_count,
                    payload_size_bytes=payload_size_bytes,
                    data_quality_score=data_quality_score,
                    on_schedule=on_schedule,
                    skip_reason=skip_reason
                )
                session.add(collection)
                session.commit()
                session.refresh(collection)
                return collection
        except SQLAlchemyError as e:
            logger.error(f"Failed to save data collection: {str(e)}", exc_info=True)
            return None

    def get_data_collections(
        self,
        provider_id: Optional[int] = None,
        category: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[DataCollection]:
        """
        Get data collections with filtering

        Args:
            provider_id: Filter by provider ID
            category: Filter by category
            hours: Get collections from last N hours
            limit: Maximum number of records to return

        Returns:
            List of DataCollection objects
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                query = session.query(DataCollection).filter(
                    DataCollection.actual_fetch_time >= cutoff_time
                )

                if provider_id:
                    query = query.filter(DataCollection.provider_id == provider_id)

                if category:
                    query = query.filter(DataCollection.category == category)

                collections = query.order_by(desc(DataCollection.actual_fetch_time)).limit(limit).all()

                for collection in collections:
                    session.refresh(collection)

                return collections
        except SQLAlchemyError as e:
            logger.error(f"Failed to get data collections: {str(e)}", exc_info=True)
            return []

    # ============================================================================
    # Rate Limit Usage Operations
    # ============================================================================

    def save_rate_limit_usage(
        self,
        provider_id: int,
        limit_type: str,
        limit_value: int,
        current_usage: int,
        reset_time: datetime
    ) -> Optional[RateLimitUsage]:
        """
        Save rate limit usage record

        Args:
            provider_id: Provider ID
            limit_type: Limit type (per_minute, per_hour, per_day)
            limit_value: Rate limit value
            current_usage: Current usage count
            reset_time: When the limit resets

        Returns:
            Created RateLimitUsage object or None if failed
        """
        try:
            with self.get_session() as session:
                percentage = (current_usage / limit_value * 100) if limit_value > 0 else 0

                usage = RateLimitUsage(
                    provider_id=provider_id,
                    limit_type=limit_type,
                    limit_value=limit_value,
                    current_usage=current_usage,
                    percentage=percentage,
                    reset_time=reset_time
                )
                session.add(usage)
                session.commit()
                session.refresh(usage)
                return usage
        except SQLAlchemyError as e:
            logger.error(f"Failed to save rate limit usage: {str(e)}", exc_info=True)
            return None

    def get_rate_limit_usage(
        self,
        provider_id: Optional[int] = None,
        hours: int = 24,
        high_usage_only: bool = False,
        threshold: float = 80.0
    ) -> List[RateLimitUsage]:
        """
        Get rate limit usage records

        Args:
            provider_id: Filter by provider ID
            hours: Get usage from last N hours
            high_usage_only: Only return high usage records
            threshold: Percentage threshold for high usage

        Returns:
            List of RateLimitUsage objects
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                query = session.query(RateLimitUsage).filter(
                    RateLimitUsage.timestamp >= cutoff_time
                )

                if provider_id:
                    query = query.filter(RateLimitUsage.provider_id == provider_id)

                if high_usage_only:
                    query = query.filter(RateLimitUsage.percentage >= threshold)

                usage_records = query.order_by(desc(RateLimitUsage.timestamp)).all()

                for record in usage_records:
                    session.refresh(record)

                return usage_records
        except SQLAlchemyError as e:
            logger.error(f"Failed to get rate limit usage: {str(e)}", exc_info=True)
            return []

    # ============================================================================
    # Schedule Configuration Operations
    # ============================================================================

    def create_schedule_config(
        self,
        provider_id: int,
        schedule_interval: str,
        enabled: bool = True,
        next_run: Optional[datetime] = None
    ) -> Optional[ScheduleConfig]:
        """
        Create schedule configuration for a provider

        Args:
            provider_id: Provider ID
            schedule_interval: Schedule interval (e.g., "every_1_min")
            enabled: Whether schedule is enabled
            next_run: Next scheduled run time

        Returns:
            Created ScheduleConfig object or None if failed
        """
        try:
            with self.get_session() as session:
                config = ScheduleConfig(
                    provider_id=provider_id,
                    schedule_interval=schedule_interval,
                    enabled=enabled,
                    next_run=next_run
                )
                session.add(config)
                session.commit()
                session.refresh(config)
                logger.info(f"Created schedule config for provider {provider_id}")
                return config
        except IntegrityError:
            logger.error(f"Schedule config already exists for provider {provider_id}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Failed to create schedule config: {str(e)}", exc_info=True)
            return None

    def get_schedule_config(self, provider_id: int) -> Optional[ScheduleConfig]:
        """
        Get schedule configuration for a provider

        Args:
            provider_id: Provider ID

        Returns:
            ScheduleConfig object or None if not found
        """
        try:
            with self.get_session() as session:
                config = session.query(ScheduleConfig).filter(
                    ScheduleConfig.provider_id == provider_id
                ).first()

                if config:
                    session.refresh(config)
                return config
        except SQLAlchemyError as e:
            logger.error(f"Failed to get schedule config: {str(e)}", exc_info=True)
            return None

    def update_schedule_config(self, provider_id: int, **kwargs) -> bool:
        """
        Update schedule configuration

        Args:
            provider_id: Provider ID
            **kwargs: Attributes to update

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                config = session.query(ScheduleConfig).filter(
                    ScheduleConfig.provider_id == provider_id
                ).first()

                if not config:
                    logger.warning(f"Schedule config not found for provider {provider_id}")
                    return False

                for key, value in kwargs.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

                session.commit()
                logger.info(f"Updated schedule config for provider {provider_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to update schedule config: {str(e)}", exc_info=True)
            return False

    def get_all_schedule_configs(self, enabled_only: bool = True) -> List[ScheduleConfig]:
        """
        Get all schedule configurations

        Args:
            enabled_only: Only return enabled schedules

        Returns:
            List of ScheduleConfig objects
        """
        try:
            with self.get_session() as session:
                query = session.query(ScheduleConfig)

                if enabled_only:
                    query = query.filter(ScheduleConfig.enabled == True)

                configs = query.all()

                for config in configs:
                    session.refresh(config)

                return configs
        except SQLAlchemyError as e:
            logger.error(f"Failed to get schedule configs: {str(e)}", exc_info=True)
            return []

    # ============================================================================
    # Schedule Compliance Operations
    # ============================================================================

    def save_schedule_compliance(
        self,
        provider_id: int,
        expected_time: datetime,
        actual_time: Optional[datetime] = None,
        delay_seconds: Optional[int] = None,
        on_time: bool = True,
        skip_reason: Optional[str] = None
    ) -> Optional[ScheduleCompliance]:
        """
        Save schedule compliance record

        Args:
            provider_id: Provider ID
            expected_time: Expected execution time
            actual_time: Actual execution time
            delay_seconds: Delay in seconds
            on_time: Whether execution was on time
            skip_reason: Reason if skipped

        Returns:
            Created ScheduleCompliance object or None if failed
        """
        try:
            with self.get_session() as session:
                compliance = ScheduleCompliance(
                    provider_id=provider_id,
                    expected_time=expected_time,
                    actual_time=actual_time,
                    delay_seconds=delay_seconds,
                    on_time=on_time,
                    skip_reason=skip_reason
                )
                session.add(compliance)
                session.commit()
                session.refresh(compliance)
                return compliance
        except SQLAlchemyError as e:
            logger.error(f"Failed to save schedule compliance: {str(e)}", exc_info=True)
            return None

    def get_schedule_compliance(
        self,
        provider_id: Optional[int] = None,
        hours: int = 24,
        late_only: bool = False
    ) -> List[ScheduleCompliance]:
        """
        Get schedule compliance records

        Args:
            provider_id: Filter by provider ID
            hours: Get records from last N hours
            late_only: Only return late executions

        Returns:
            List of ScheduleCompliance objects
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                query = session.query(ScheduleCompliance).filter(
                    ScheduleCompliance.timestamp >= cutoff_time
                )

                if provider_id:
                    query = query.filter(ScheduleCompliance.provider_id == provider_id)

                if late_only:
                    query = query.filter(ScheduleCompliance.on_time == False)

                compliance_records = query.order_by(desc(ScheduleCompliance.timestamp)).all()

                for record in compliance_records:
                    session.refresh(record)

                return compliance_records
        except SQLAlchemyError as e:
            logger.error(f"Failed to get schedule compliance: {str(e)}", exc_info=True)
            return []

    # ============================================================================
    # Failure Log Operations
    # ============================================================================

    def save_failure_log(
        self,
        provider_id: int,
        endpoint: str,
        error_type: str,
        error_message: Optional[str] = None,
        http_status: Optional[int] = None,
        retry_attempted: bool = False,
        retry_result: Optional[str] = None,
        remediation_applied: Optional[str] = None
    ) -> Optional[FailureLog]:
        """
        Save failure log record

        Args:
            provider_id: Provider ID
            endpoint: API endpoint
            error_type: Type of error
            error_message: Error message
            http_status: HTTP status code
            retry_attempted: Whether retry was attempted
            retry_result: Result of retry
            remediation_applied: Remediation action taken

        Returns:
            Created FailureLog object or None if failed
        """
        try:
            with self.get_session() as session:
                failure = FailureLog(
                    provider_id=provider_id,
                    endpoint=endpoint,
                    error_type=error_type,
                    error_message=error_message,
                    http_status=http_status,
                    retry_attempted=retry_attempted,
                    retry_result=retry_result,
                    remediation_applied=remediation_applied
                )
                session.add(failure)
                session.commit()
                session.refresh(failure)
                return failure
        except SQLAlchemyError as e:
            logger.error(f"Failed to save failure log: {str(e)}", exc_info=True)
            return None

    def get_failure_logs(
        self,
        provider_id: Optional[int] = None,
        error_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[FailureLog]:
        """
        Get failure logs with filtering

        Args:
            provider_id: Filter by provider ID
            error_type: Filter by error type
            hours: Get logs from last N hours
            limit: Maximum number of records to return

        Returns:
            List of FailureLog objects
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                query = session.query(FailureLog).filter(
                    FailureLog.timestamp >= cutoff_time
                )

                if provider_id:
                    query = query.filter(FailureLog.provider_id == provider_id)

                if error_type:
                    query = query.filter(FailureLog.error_type == error_type)

                failures = query.order_by(desc(FailureLog.timestamp)).limit(limit).all()

                for failure in failures:
                    session.refresh(failure)

                return failures
        except SQLAlchemyError as e:
            logger.error(f"Failed to get failure logs: {str(e)}", exc_info=True)
            return []

    # ============================================================================
    # Alert Operations
    # ============================================================================

    def create_alert(
        self,
        provider_id: int,
        alert_type: str,
        message: str,
        severity: str = "medium"
    ) -> Optional[Alert]:
        """
        Create an alert

        Args:
            provider_id: Provider ID
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity (low, medium, high, critical)

        Returns:
            Created Alert object or None if failed
        """
        try:
            with self.get_session() as session:
                alert = Alert(
                    provider_id=provider_id,
                    alert_type=alert_type,
                    message=message,
                    severity=severity
                )
                session.add(alert)
                session.commit()
                session.refresh(alert)
                logger.warning(f"Alert created: {alert_type} - {message}")
                return alert
        except SQLAlchemyError as e:
            logger.error(f"Failed to create alert: {str(e)}", exc_info=True)
            return None

    def get_alerts(
        self,
        provider_id: Optional[int] = None,
        alert_type: Optional[str] = None,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        hours: int = 24
    ) -> List[Alert]:
        """
        Get alerts with filtering

        Args:
            provider_id: Filter by provider ID
            alert_type: Filter by alert type
            severity: Filter by severity
            acknowledged: Filter by acknowledgment status
            hours: Get alerts from last N hours

        Returns:
            List of Alert objects
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                query = session.query(Alert).filter(
                    Alert.timestamp >= cutoff_time
                )

                if provider_id:
                    query = query.filter(Alert.provider_id == provider_id)

                if alert_type:
                    query = query.filter(Alert.alert_type == alert_type)

                if severity:
                    query = query.filter(Alert.severity == severity)

                if acknowledged is not None:
                    query = query.filter(Alert.acknowledged == acknowledged)

                alerts = query.order_by(desc(Alert.timestamp)).all()

                for alert in alerts:
                    session.refresh(alert)

                return alerts
        except SQLAlchemyError as e:
            logger.error(f"Failed to get alerts: {str(e)}", exc_info=True)
            return []

    def acknowledge_alert(self, alert_id: int) -> bool:
        """
        Acknowledge an alert

        Args:
            alert_id: Alert ID

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                alert = session.query(Alert).filter(Alert.id == alert_id).first()
                if not alert:
                    logger.warning(f"Alert not found: {alert_id}")
                    return False

                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                session.commit()
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to acknowledge alert: {str(e)}", exc_info=True)
            return False

    # ============================================================================
    # System Metrics Operations
    # ============================================================================

    def save_system_metrics(
        self,
        total_providers: int,
        online_count: int,
        degraded_count: int,
        offline_count: int,
        avg_response_time_ms: float,
        total_requests_hour: int,
        total_failures_hour: int,
        system_health: str = "healthy"
    ) -> Optional[SystemMetrics]:
        """
        Save system metrics snapshot

        Args:
            total_providers: Total number of providers
            online_count: Number of online providers
            degraded_count: Number of degraded providers
            offline_count: Number of offline providers
            avg_response_time_ms: Average response time
            total_requests_hour: Total requests in last hour
            total_failures_hour: Total failures in last hour
            system_health: Overall system health

        Returns:
            Created SystemMetrics object or None if failed
        """
        try:
            with self.get_session() as session:
                metrics = SystemMetrics(
                    total_providers=total_providers,
                    online_count=online_count,
                    degraded_count=degraded_count,
                    offline_count=offline_count,
                    avg_response_time_ms=avg_response_time_ms,
                    total_requests_hour=total_requests_hour,
                    total_failures_hour=total_failures_hour,
                    system_health=system_health
                )
                session.add(metrics)
                session.commit()
                session.refresh(metrics)
                return metrics
        except SQLAlchemyError as e:
            logger.error(f"Failed to save system metrics: {str(e)}", exc_info=True)
            return None

    def get_system_metrics(self, hours: int = 24, limit: int = 1000) -> List[SystemMetrics]:
        """
        Get system metrics history

        Args:
            hours: Get metrics from last N hours
            limit: Maximum number of records to return

        Returns:
            List of SystemMetrics objects
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                metrics = session.query(SystemMetrics).filter(
                    SystemMetrics.timestamp >= cutoff_time
                ).order_by(desc(SystemMetrics.timestamp)).limit(limit).all()

                for metric in metrics:
                    session.refresh(metric)

                return metrics
        except SQLAlchemyError as e:
            logger.error(f"Failed to get system metrics: {str(e)}", exc_info=True)
            return []

    def get_latest_system_metrics(self) -> Optional[SystemMetrics]:
        """
        Get the most recent system metrics

        Returns:
            Latest SystemMetrics object or None
        """
        try:
            with self.get_session() as session:
                metrics = session.query(SystemMetrics).order_by(
                    desc(SystemMetrics.timestamp)
                ).first()

                if metrics:
                    session.refresh(metrics)
                return metrics
        except SQLAlchemyError as e:
            logger.error(f"Failed to get latest system metrics: {str(e)}", exc_info=True)
            return None

    # ============================================================================
    # Advanced Analytics Methods
    # ============================================================================

    def get_provider_stats(self, provider_id: int, hours: int = 24) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a provider

        Args:
            provider_id: Provider ID
            hours: Time window in hours

        Returns:
            Dictionary with provider statistics
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)

                # Get provider info
                provider = session.query(Provider).filter(Provider.id == provider_id).first()
                if not provider:
                    return {}

                # Connection attempt stats
                connection_stats = session.query(
                    func.count(ConnectionAttempt.id).label('total_attempts'),
                    func.sum(func.case((ConnectionAttempt.status == 'success', 1), else_=0)).label('successful'),
                    func.sum(func.case((ConnectionAttempt.status == 'failed', 1), else_=0)).label('failed'),
                    func.sum(func.case((ConnectionAttempt.status == 'timeout', 1), else_=0)).label('timeout'),
                    func.sum(func.case((ConnectionAttempt.status == 'rate_limited', 1), else_=0)).label('rate_limited'),
                    func.avg(ConnectionAttempt.response_time_ms).label('avg_response_time')
                ).filter(
                    ConnectionAttempt.provider_id == provider_id,
                    ConnectionAttempt.timestamp >= cutoff_time
                ).first()

                # Data collection stats
                collection_stats = session.query(
                    func.count(DataCollection.id).label('total_collections'),
                    func.sum(DataCollection.record_count).label('total_records'),
                    func.sum(DataCollection.payload_size_bytes).label('total_bytes'),
                    func.avg(DataCollection.data_quality_score).label('avg_quality'),
                    func.avg(DataCollection.staleness_minutes).label('avg_staleness')
                ).filter(
                    DataCollection.provider_id == provider_id,
                    DataCollection.actual_fetch_time >= cutoff_time
                ).first()

                # Failure stats
                failure_count = session.query(func.count(FailureLog.id)).filter(
                    FailureLog.provider_id == provider_id,
                    FailureLog.timestamp >= cutoff_time
                ).scalar()

                # Calculate success rate
                total_attempts = connection_stats.total_attempts or 0
                successful = connection_stats.successful or 0
                success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0

                return {
                    'provider_name': provider.name,
                    'provider_id': provider_id,
                    'time_window_hours': hours,
                    'connection_stats': {
                        'total_attempts': total_attempts,
                        'successful': successful,
                        'failed': connection_stats.failed or 0,
                        'timeout': connection_stats.timeout or 0,
                        'rate_limited': connection_stats.rate_limited or 0,
                        'success_rate': round(success_rate, 2),
                        'avg_response_time_ms': round(connection_stats.avg_response_time or 0, 2)
                    },
                    'data_collection_stats': {
                        'total_collections': collection_stats.total_collections or 0,
                        'total_records': collection_stats.total_records or 0,
                        'total_bytes': collection_stats.total_bytes or 0,
                        'avg_quality_score': round(collection_stats.avg_quality or 0, 2),
                        'avg_staleness_minutes': round(collection_stats.avg_staleness or 0, 2)
                    },
                    'failure_count': failure_count or 0
                }
        except SQLAlchemyError as e:
            logger.error(f"Failed to get provider stats: {str(e)}", exc_info=True)
            return {}

    def get_failure_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get comprehensive failure analysis across all providers

        Args:
            hours: Time window in hours

        Returns:
            Dictionary with failure analysis
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)

                # Failures by error type
                error_type_stats = session.query(
                    FailureLog.error_type,
                    func.count(FailureLog.id).label('count')
                ).filter(
                    FailureLog.timestamp >= cutoff_time
                ).group_by(FailureLog.error_type).all()

                # Failures by provider
                provider_stats = session.query(
                    Provider.name,
                    func.count(FailureLog.id).label('count')
                ).join(
                    FailureLog, Provider.id == FailureLog.provider_id
                ).filter(
                    FailureLog.timestamp >= cutoff_time
                ).group_by(Provider.name).order_by(desc('count')).limit(10).all()

                # Retry statistics
                retry_stats = session.query(
                    func.sum(func.case((FailureLog.retry_attempted == True, 1), else_=0)).label('total_retries'),
                    func.sum(func.case((FailureLog.retry_result == 'success', 1), else_=0)).label('successful_retries')
                ).filter(
                    FailureLog.timestamp >= cutoff_time
                ).first()

                total_retries = retry_stats.total_retries or 0
                successful_retries = retry_stats.successful_retries or 0
                retry_success_rate = (successful_retries / total_retries * 100) if total_retries > 0 else 0

                return {
                    'time_window_hours': hours,
                    'failures_by_error_type': [
                        {'error_type': stat.error_type, 'count': stat.count}
                        for stat in error_type_stats
                    ],
                    'top_failing_providers': [
                        {'provider': stat.name, 'failure_count': stat.count}
                        for stat in provider_stats
                    ],
                    'retry_statistics': {
                        'total_retries': total_retries,
                        'successful_retries': successful_retries,
                        'retry_success_rate': round(retry_success_rate, 2)
                    }
                }
        except SQLAlchemyError as e:
            logger.error(f"Failed to get failure analysis: {str(e)}", exc_info=True)
            return {}

    def get_recent_logs(
        self,
        log_type: str,
        provider_id: Optional[int] = None,
        hours: int = 1,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent logs of specified type with filtering

        Args:
            log_type: Type of logs (connection, failure, collection, rate_limit)
            provider_id: Filter by provider ID
            hours: Get logs from last N hours
            limit: Maximum number of records

        Returns:
            List of log dictionaries
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            if log_type == 'connection':
                attempts = self.get_connection_attempts(provider_id=provider_id, hours=hours, limit=limit)
                return [
                    {
                        'id': a.id,
                        'timestamp': a.timestamp.isoformat(),
                        'provider_id': a.provider_id,
                        'endpoint': a.endpoint,
                        'status': a.status,
                        'response_time_ms': a.response_time_ms,
                        'http_status_code': a.http_status_code,
                        'error_type': a.error_type,
                        'error_message': a.error_message
                    }
                    for a in attempts
                ]

            elif log_type == 'failure':
                failures = self.get_failure_logs(provider_id=provider_id, hours=hours, limit=limit)
                return [
                    {
                        'id': f.id,
                        'timestamp': f.timestamp.isoformat(),
                        'provider_id': f.provider_id,
                        'endpoint': f.endpoint,
                        'error_type': f.error_type,
                        'error_message': f.error_message,
                        'http_status': f.http_status,
                        'retry_attempted': f.retry_attempted,
                        'retry_result': f.retry_result
                    }
                    for f in failures
                ]

            elif log_type == 'collection':
                collections = self.get_data_collections(provider_id=provider_id, hours=hours, limit=limit)
                return [
                    {
                        'id': c.id,
                        'provider_id': c.provider_id,
                        'category': c.category,
                        'scheduled_time': c.scheduled_time.isoformat(),
                        'actual_fetch_time': c.actual_fetch_time.isoformat(),
                        'record_count': c.record_count,
                        'payload_size_bytes': c.payload_size_bytes,
                        'data_quality_score': c.data_quality_score,
                        'on_schedule': c.on_schedule
                    }
                    for c in collections
                ]

            elif log_type == 'rate_limit':
                usage = self.get_rate_limit_usage(provider_id=provider_id, hours=hours)
                return [
                    {
                        'id': u.id,
                        'timestamp': u.timestamp.isoformat(),
                        'provider_id': u.provider_id,
                        'limit_type': u.limit_type,
                        'limit_value': u.limit_value,
                        'current_usage': u.current_usage,
                        'percentage': u.percentage,
                        'reset_time': u.reset_time.isoformat()
                    }
                    for u in usage[:limit]
                ]

            else:
                logger.warning(f"Unknown log type: {log_type}")
                return []

        except Exception as e:
            logger.error(f"Failed to get recent logs: {str(e)}", exc_info=True)
            return []

    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """
        Remove old records from the database to manage storage

        Args:
            days: Remove records older than N days

        Returns:
            Dictionary with count of deleted records per table
        """
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(days=days)
                deleted_counts = {}

                # Clean connection attempts
                deleted = session.query(ConnectionAttempt).filter(
                    ConnectionAttempt.timestamp < cutoff_time
                ).delete()
                deleted_counts['connection_attempts'] = deleted

                # Clean data collections
                deleted = session.query(DataCollection).filter(
                    DataCollection.actual_fetch_time < cutoff_time
                ).delete()
                deleted_counts['data_collections'] = deleted

                # Clean rate limit usage
                deleted = session.query(RateLimitUsage).filter(
                    RateLimitUsage.timestamp < cutoff_time
                ).delete()
                deleted_counts['rate_limit_usage'] = deleted

                # Clean schedule compliance
                deleted = session.query(ScheduleCompliance).filter(
                    ScheduleCompliance.timestamp < cutoff_time
                ).delete()
                deleted_counts['schedule_compliance'] = deleted

                # Clean failure logs
                deleted = session.query(FailureLog).filter(
                    FailureLog.timestamp < cutoff_time
                ).delete()
                deleted_counts['failure_logs'] = deleted

                # Clean acknowledged alerts
                deleted = session.query(Alert).filter(
                    and_(
                        Alert.timestamp < cutoff_time,
                        Alert.acknowledged == True
                    )
                ).delete()
                deleted_counts['alerts'] = deleted

                # Clean system metrics
                deleted = session.query(SystemMetrics).filter(
                    SystemMetrics.timestamp < cutoff_time
                ).delete()
                deleted_counts['system_metrics'] = deleted

                session.commit()

                total_deleted = sum(deleted_counts.values())
                logger.info(f"Cleaned up {total_deleted} old records (older than {days} days)")

                return deleted_counts
        except SQLAlchemyError as e:
            logger.error(f"Failed to cleanup old data: {str(e)}", exc_info=True)
            return {}

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary with database statistics
        """
        try:
            with self.get_session() as session:
                stats = {
                    'providers': session.query(func.count(Provider.id)).scalar(),
                    'connection_attempts': session.query(func.count(ConnectionAttempt.id)).scalar(),
                    'data_collections': session.query(func.count(DataCollection.id)).scalar(),
                    'rate_limit_usage': session.query(func.count(RateLimitUsage.id)).scalar(),
                    'schedule_configs': session.query(func.count(ScheduleConfig.id)).scalar(),
                    'schedule_compliance': session.query(func.count(ScheduleCompliance.id)).scalar(),
                    'failure_logs': session.query(func.count(FailureLog.id)).scalar(),
                    'alerts': session.query(func.count(Alert.id)).scalar(),
                    'system_metrics': session.query(func.count(SystemMetrics.id)).scalar(),
                }

                # Get database file size if it exists
                if os.path.exists(self.db_path):
                    stats['database_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
                else:
                    stats['database_size_mb'] = 0

                return stats
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database stats: {str(e)}", exc_info=True)
            return {}

    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check

        Returns:
            Dictionary with health check results
        """
        try:
            with self.get_session() as session:
                # Test connection with a simple query
                result = session.execute(text("SELECT 1")).scalar()

                # Get stats
                stats = self.get_database_stats()

                return {
                    'status': 'healthy' if result == 1 else 'unhealthy',
                    'database_path': self.db_path,
                    'database_exists': os.path.exists(self.db_path),
                    'stats': stats,
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}", exc_info=True)
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# ============================================================================
# Global Database Manager Instance
# ============================================================================

# Create a global instance (can be reconfigured as needed)
db_manager = DatabaseManager()


# ============================================================================
# Convenience Functions
# ============================================================================

def init_db(db_path: str = "data/api_monitor.db") -> DatabaseManager:
    """
    Initialize database and return manager instance

    Args:
        db_path: Path to database file

    Returns:
        DatabaseManager instance
    """
    manager = DatabaseManager(db_path=db_path)
    manager.init_database()
    logger.info("Database initialized successfully")
    return manager


if __name__ == "__main__":
    # Example usage and testing
    print("Database Manager Module")
    print("=" * 80)

    # Initialize database
    manager = init_db()

    # Run health check
    health = manager.health_check()
    print(f"\nHealth Check: {health['status']}")
    print(f"Database Stats: {health.get('stats', {})}")

    # Get database statistics
    stats = manager.get_database_stats()
    print(f"\nDatabase Statistics:")
    for table, count in stats.items():
        if table != 'database_size_mb':
            print(f"  {table}: {count}")
    print(f"  Database Size: {stats.get('database_size_mb', 0)} MB")

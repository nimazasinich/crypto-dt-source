"""
Database Initialization and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config import config
from database.models import Base, Provider, ProviderStatusEnum
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database and populate providers"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Populate providers from config
        db = SessionLocal()
        try:
            for provider_config in config.PROVIDERS:
                existing = db.query(Provider).filter(Provider.name == provider_config.name).first()
                if not existing:
                    provider = Provider(
                        name=provider_config.name,
                        category=provider_config.category,
                        endpoint_url=provider_config.endpoint_url,
                        requires_key=provider_config.requires_key,
                        api_key_masked=mask_api_key(provider_config.api_key) if provider_config.api_key else None,
                        rate_limit_type=provider_config.rate_limit_type,
                        rate_limit_value=provider_config.rate_limit_value,
                        timeout_ms=provider_config.timeout_ms,
                        priority_tier=provider_config.priority_tier,
                        status=ProviderStatusEnum.UNKNOWN
                    )
                    db.add(provider)

            db.commit()
            logger.info(f"Initialized {len(config.PROVIDERS)} providers")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


@contextmanager
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def mask_api_key(key: str) -> str:
    """Mask API key showing only first 4 and last 4 characters"""
    if not key or len(key) < 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"

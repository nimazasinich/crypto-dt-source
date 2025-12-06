"""Configuration management for HuggingFace Crypto Data Engine"""
from __future__ import annotations
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "production"
    VERSION: str = "1.0.0"

    # Cache
    CACHE_TYPE: str = "memory"  # or 'redis'
    CACHE_TTL_PRICES: int = 30  # seconds
    CACHE_TTL_OHLCV: int = 300  # seconds (5 minutes)
    CACHE_TTL_SENTIMENT: int = 600  # seconds (10 minutes)
    CACHE_TTL_MARKET: int = 300  # seconds (5 minutes)
    REDIS_URL: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PRICES: int = 120  # requests per minute
    RATE_LIMIT_OHLCV: int = 60  # requests per minute
    RATE_LIMIT_SENTIMENT: int = 30  # requests per minute
    RATE_LIMIT_HEALTH: int = 0  # unlimited

    # Data Providers (Optional API Keys)
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    COINGECKO_API_KEY: Optional[str] = None
    CRYPTOCOMPARE_API_KEY: Optional[str] = None
    CRYPTOPANIC_API_KEY: Optional[str] = None
    NEWSAPI_KEY: Optional[str] = None

    # Features
    ENABLE_SENTIMENT: bool = True
    ENABLE_NEWS: bool = False

    # Circuit Breaker
    CIRCUIT_BREAKER_THRESHOLD: int = 5  # consecutive failures
    CIRCUIT_BREAKER_TIMEOUT: int = 60  # seconds

    # Request Timeouts
    REQUEST_TIMEOUT: int = 10  # seconds

    # Supported Symbols
    SUPPORTED_SYMBOLS: str = "BTC,ETH,SOL,XRP,BNB,ADA,DOT,LINK,LTC,BCH,MATIC,AVAX,XLM,TRX"

    # Supported Intervals
    SUPPORTED_INTERVALS: str = "1m,5m,15m,1h,4h,1d,1w"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_supported_symbols() -> list[str]:
    """Get list of supported symbols"""
    return [s.strip() for s in settings.SUPPORTED_SYMBOLS.split(",")]


def get_supported_intervals() -> list[str]:
    """Get list of supported intervals"""
    return [i.strip() for i in settings.SUPPORTED_INTERVALS.split(",")]

#!/usr/bin/env python3
"""
Configuration constants for Crypto Data Aggregator
All configuration in one place - no hardcoded values
"""

import os
from pathlib import Path

# ==================== DIRECTORIES ====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
DB_DIR = DATA_DIR / "database"

# Create directories if they don't exist
for directory in [DATA_DIR, LOG_DIR, DB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==================== DATABASE ====================
DATABASE_PATH = DB_DIR / "crypto_aggregator.db"
DATABASE_BACKUP_DIR = DATA_DIR / "backups"
DATABASE_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# ==================== API ENDPOINTS (NO KEYS REQUIRED) ====================

# CoinGecko API (Free, no key)
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_ENDPOINTS = {
    "ping": "/ping",
    "price": "/simple/price",
    "coins_list": "/coins/list",
    "coins_markets": "/coins/markets",
    "coin_data": "/coins/{id}",
    "trending": "/search/trending",
    "global": "/global",
}

# CoinCap API (Free, no key)
COINCAP_BASE_URL = "https://api.coincap.io/v2"
COINCAP_ENDPOINTS = {
    "assets": "/assets",
    "asset_detail": "/assets/{id}",
    "asset_history": "/assets/{id}/history",
    "markets": "/markets",
    "rates": "/rates",
}

# Binance Public API (Free, no key)
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
BINANCE_ENDPOINTS = {
    "ping": "/ping",
    "ticker_24h": "/ticker/24hr",
    "ticker_price": "/ticker/price",
    "klines": "/klines",
    "trades": "/trades",
}

# Alternative.me Fear & Greed Index (Free, no key)
ALTERNATIVE_ME_URL = "https://api.alternative.me/fng/"

# ==================== RSS FEEDS ====================
RSS_FEEDS = {
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "cointelegraph": "https://cointelegraph.com/rss",
    "bitcoin_magazine": "https://bitcoinmagazine.com/.rss/full/",
    "decrypt": "https://decrypt.co/feed",
    "bitcoinist": "https://bitcoinist.com/feed/",
}

# ==================== REDDIT ENDPOINTS (NO AUTH) ====================
REDDIT_ENDPOINTS = {
    "cryptocurrency": "https://www.reddit.com/r/cryptocurrency/.json",
    "bitcoin": "https://www.reddit.com/r/bitcoin/.json",
    "ethtrader": "https://www.reddit.com/r/ethtrader/.json",
    "cryptomarkets": "https://www.reddit.com/r/CryptoMarkets/.json",
}

# ==================== HUGGING FACE MODELS ====================
HUGGINGFACE_MODELS = {
    "sentiment_twitter": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "sentiment_financial": "ProsusAI/finbert",
    "summarization": "facebook/bart-large-cnn",
}

# ==================== DATA COLLECTION SETTINGS ====================
COLLECTION_INTERVALS = {
    "price_data": 300,  # 5 minutes in seconds
    "news_data": 1800,  # 30 minutes in seconds
    "sentiment_data": 1800,  # 30 minutes in seconds
}

# Number of top cryptocurrencies to track
TOP_COINS_LIMIT = 100

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Max retries for failed requests
MAX_RETRIES = 3

# ==================== CACHE SETTINGS ====================
CACHE_TTL = 300  # 5 minutes in seconds
CACHE_MAX_SIZE = 1000  # Maximum number of cached items

# ==================== LOGGING SETTINGS ====================
LOG_FILE = LOG_DIR / "crypto_aggregator.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ==================== GRADIO SETTINGS ====================
GRADIO_SHARE = False
GRADIO_SERVER_NAME = "0.0.0.0"
GRADIO_SERVER_PORT = 7860
GRADIO_THEME = "default"
AUTO_REFRESH_INTERVAL = 30  # seconds

# ==================== DATA VALIDATION ====================
MIN_PRICE = 0.0
MAX_PRICE = 1000000000.0  # 1 billion
MIN_VOLUME = 0.0
MIN_MARKET_CAP = 0.0

# ==================== CHART SETTINGS ====================
CHART_TIMEFRAMES = {
    "1d": {"days": 1, "interval": "1h"},
    "7d": {"days": 7, "interval": "4h"},
    "30d": {"days": 30, "interval": "1d"},
    "90d": {"days": 90, "interval": "1d"},
    "1y": {"days": 365, "interval": "1w"},
}

# Technical indicators
MA_PERIODS = [7, 30]  # Moving Average periods
RSI_PERIOD = 14  # RSI period

# ==================== SENTIMENT THRESHOLDS ====================
SENTIMENT_LABELS = {
    "very_negative": (-1.0, -0.6),
    "negative": (-0.6, -0.2),
    "neutral": (-0.2, 0.2),
    "positive": (0.2, 0.6),
    "very_positive": (0.6, 1.0),
}

# ==================== AI ANALYSIS SETTINGS ====================
AI_CONFIDENCE_THRESHOLD = 0.6
PREDICTION_HORIZON_HOURS = 72

# ==================== USER AGENT ====================
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ==================== RATE LIMITING ====================
RATE_LIMIT_CALLS = 50
RATE_LIMIT_PERIOD = 60  # seconds

# ==================== COIN SYMBOLS ====================
# Top cryptocurrencies to focus on
FOCUS_COINS = [
    "bitcoin", "ethereum", "binancecoin", "ripple", "cardano",
    "solana", "polkadot", "dogecoin", "avalanche-2", "polygon",
    "chainlink", "uniswap", "litecoin", "cosmos", "algorand"
]

COIN_SYMBOL_MAPPING = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "binancecoin": "BNB",
    "ripple": "XRP",
    "cardano": "ADA",
    "solana": "SOL",
    "polkadot": "DOT",
    "dogecoin": "DOGE",
    "avalanche-2": "AVAX",
    "polygon": "MATIC",
}

# ==================== ERROR MESSAGES ====================
ERROR_MESSAGES = {
    "api_unavailable": "API service is currently unavailable. Using cached data.",
    "no_data": "No data available at the moment.",
    "database_error": "Database operation failed.",
    "network_error": "Network connection error.",
    "invalid_input": "Invalid input provided.",
}

# ==================== SUCCESS MESSAGES ====================
SUCCESS_MESSAGES = {
    "data_collected": "Data successfully collected and saved.",
    "cache_cleared": "Cache cleared successfully.",
    "database_initialized": "Database initialized successfully.",
}

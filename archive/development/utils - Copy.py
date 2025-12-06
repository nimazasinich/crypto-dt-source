#!/usr/bin/env python3
"""
Utility functions for Crypto Data Aggregator
Complete collection of helper functions for caching, validation, formatting, and analysis
"""

import time
import functools
import logging
import datetime
import json
import csv
from typing import Dict, List, Optional, Any, Callable
from logging.handlers import RotatingFileHandler

import config


def setup_logging() -> logging.Logger:
    """
    Configure logging with rotating file handler and console output.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('crypto_aggregator')
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))

    # Prevent duplicate handlers if function is called multiple times
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)

    try:
        # Setup RotatingFileHandler for file output
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")

    # Add StreamHandler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logging system initialized successfully")
    return logger


def cache_with_ttl(ttl_seconds: int = 300) -> Callable:
    """
    Decorator for caching function results with time-to-live (TTL).

    Args:
        ttl_seconds: Cache expiration time in seconds (default: 300)

    Returns:
        Callable: Decorated function with caching

    Example:
        @cache_with_ttl(ttl_seconds=600)
        def expensive_function(arg1, arg2):
            return result
    """
    def decorator(func: Callable) -> Callable:
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function arguments
            cache_key = str(args) + str(sorted(kwargs.items()))

            # Check if cached value exists and is not expired
            if cache_key in cache:
                cached_value, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    logger = logging.getLogger('crypto_aggregator')
                    logger.debug(f"Cache hit for {func.__name__} (TTL: {ttl_seconds}s)")
                    return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())

            # Limit cache size to prevent memory issues
            if len(cache) > config.CACHE_MAX_SIZE:
                # Remove oldest entry
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]

            return result

        # Add cache clearing method
        wrapper.clear_cache = lambda: cache.clear()
        return wrapper

    return decorator


def validate_price_data(price_data: Dict) -> bool:
    """
    Validate cryptocurrency price data against configuration thresholds.

    Args:
        price_data: Dictionary containing price information

    Returns:
        bool: True if data is valid, False otherwise
    """
    logger = logging.getLogger('crypto_aggregator')

    try:
        # Check if all required fields exist
        required_fields = ['price_usd', 'volume_24h', 'market_cap']
        for field in required_fields:
            if field not in price_data:
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate price_usd
        price_usd = float(price_data['price_usd'])
        if not (config.MIN_PRICE <= price_usd <= config.MAX_PRICE):
            logger.warning(
                f"Price ${price_usd} outside valid range "
                f"[${config.MIN_PRICE}, ${config.MAX_PRICE}]"
            )
            return False

        # Validate volume_24h
        volume_24h = float(price_data['volume_24h'])
        if volume_24h < config.MIN_VOLUME:
            logger.warning(
                f"Volume ${volume_24h} below minimum ${config.MIN_VOLUME}"
            )
            return False

        # Validate market_cap
        market_cap = float(price_data['market_cap'])
        if market_cap < config.MIN_MARKET_CAP:
            logger.warning(
                f"Market cap ${market_cap} below minimum ${config.MIN_MARKET_CAP}"
            )
            return False

        return True

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating price data: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in validate_price_data: {e}")
        return False


def format_number(num: float, decimals: int = 2) -> str:
    """
    Format large numbers with K, M, B suffixes for readability.

    Args:
        num: Number to format
        decimals: Number of decimal places (default: 2)

    Returns:
        str: Formatted number string

    Examples:
        format_number(1234) -> "1.23K"
        format_number(1234567) -> "1.23M"
        format_number(1234567890) -> "1.23B"
    """
    if num is None:
        return "N/A"

    try:
        num = float(num)

        if num < 0:
            sign = "-"
            num = abs(num)
        else:
            sign = ""

        if num >= 1_000_000_000:
            formatted = f"{sign}{num / 1_000_000_000:.{decimals}f}B"
        elif num >= 1_000_000:
            formatted = f"{sign}{num / 1_000_000:.{decimals}f}M"
        elif num >= 1_000:
            formatted = f"{sign}{num / 1_000:.{decimals}f}K"
        else:
            formatted = f"{sign}{num:.{decimals}f}"

        return formatted

    except (ValueError, TypeError):
        return "N/A"


def calculate_moving_average(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate simple moving average (SMA) for a list of prices.

    Args:
        prices: List of price values
        period: Number of periods for moving average

    Returns:
        float: Moving average value, or None if calculation not possible
    """
    logger = logging.getLogger('crypto_aggregator')

    try:
        # Handle edge cases
        if not prices:
            logger.warning("Empty price list provided to calculate_moving_average")
            return None

        if period <= 0:
            logger.warning(f"Invalid period {period} for moving average")
            return None

        if len(prices) < period:
            logger.warning(
                f"Not enough data points ({len(prices)}) for period {period}"
            )
            return None

        # Calculate moving average from the last 'period' prices
        recent_prices = prices[-period:]
        average = sum(recent_prices) / period

        return round(average, 8)  # Round to 8 decimal places for precision

    except (TypeError, ValueError) as e:
        logger.error(f"Error calculating moving average: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in calculate_moving_average: {e}")
        return None


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate Relative Strength Index (RSI) technical indicator.

    Args:
        prices: List of price values
        period: RSI period (default: 14)

    Returns:
        float: RSI value between 0-100, or None if calculation not possible
    """
    logger = logging.getLogger('crypto_aggregator')

    try:
        # Handle edge cases
        if not prices or len(prices) < period + 1:
            logger.warning(
                f"Not enough data points ({len(prices)}) for RSI calculation (need {period + 1})"
            )
            return None

        if period <= 0:
            logger.warning(f"Invalid period {period} for RSI")
            return None

        # Calculate price changes
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

        # Separate gains and losses
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]

        # Calculate average gains and losses for the period
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        # Handle case where avg_loss is zero
        if avg_loss == 0:
            if avg_gain == 0:
                return 50.0  # No movement
            return 100.0  # All gains, no losses

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    except (TypeError, ValueError, ZeroDivisionError) as e:
        logger.error(f"Error calculating RSI: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in calculate_rsi: {e}")
        return None


def extract_coins_from_text(text: str) -> List[str]:
    """
    Extract cryptocurrency symbols from text using case-insensitive matching.

    Args:
        text: Text to search for coin symbols

    Returns:
        List[str]: List of found coin symbols (e.g., ['BTC', 'ETH'])
    """
    if not text:
        return []

    found_coins = []
    text_upper = text.upper()

    try:
        # Search for coin symbols from mapping
        for coin_id, symbol in config.COIN_SYMBOL_MAPPING.items():
            # Check for symbol (e.g., "BTC")
            if symbol.upper() in text_upper:
                if symbol not in found_coins:
                    found_coins.append(symbol)
            # Check for full name (e.g., "bitcoin")
            elif coin_id.upper() in text_upper:
                if symbol not in found_coins:
                    found_coins.append(symbol)

        # Also check for common patterns like $BTC or #BTC
        import re
        pattern = r'[$#]?([A-Z]{2,10})\b'
        matches = re.findall(pattern, text_upper)

        for match in matches:
            # Check if it's a known symbol
            for coin_id, symbol in config.COIN_SYMBOL_MAPPING.items():
                if match == symbol.upper():
                    if symbol not in found_coins:
                        found_coins.append(symbol)

        return sorted(list(set(found_coins)))  # Remove duplicates and sort

    except Exception as e:
        logger = logging.getLogger('crypto_aggregator')
        logger.error(f"Error extracting coins from text: {e}")
        return []


def export_to_csv(data: List[Dict], filename: str) -> bool:
    """
    Export list of dictionaries to CSV file.

    Args:
        data: List of dictionaries to export
        filename: Output CSV filename (can be relative or absolute path)

    Returns:
        bool: True if export successful, False otherwise
    """
    logger = logging.getLogger('crypto_aggregator')

    if not data:
        logger.warning("No data to export to CSV")
        return False

    try:
        # Ensure filename ends with .csv
        if not filename.endswith('.csv'):
            filename += '.csv'

        # Get all unique keys from all dictionaries
        fieldnames = set()
        for row in data:
            fieldnames.update(row.keys())
        fieldnames = sorted(list(fieldnames))

        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"Successfully exported {len(data)} rows to {filename}")
        return True

    except IOError as e:
        logger.error(f"IO error exporting to CSV {filename}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error exporting to CSV {filename}: {e}")
        return False


def is_data_stale(timestamp_str: str, max_age_minutes: int = 30) -> bool:
    """
    Check if data is stale based on timestamp and maximum age.

    Args:
        timestamp_str: Timestamp string in ISO format or Unix timestamp
        max_age_minutes: Maximum age in minutes before data is considered stale

    Returns:
        bool: True if data is stale (older than max_age_minutes), False otherwise
    """
    logger = logging.getLogger('crypto_aggregator')

    try:
        # Try to parse as Unix timestamp (float/int)
        try:
            timestamp = float(timestamp_str)
            data_time = datetime.datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            # Try to parse as ISO format string
            # Support multiple datetime formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
            ]:
                try:
                    data_time = datetime.datetime.strptime(timestamp_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                # If no format matched, try fromisoformat
                data_time = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

        # Calculate age
        current_time = datetime.datetime.now()
        age = current_time - data_time
        age_minutes = age.total_seconds() / 60

        is_stale = age_minutes > max_age_minutes

        if is_stale:
            logger.debug(
                f"Data is stale: {age_minutes:.1f} minutes old "
                f"(threshold: {max_age_minutes} minutes)"
            )

        return is_stale

    except Exception as e:
        logger.error(f"Error checking data staleness for timestamp '{timestamp_str}': {e}")
        # If we can't parse the timestamp, consider it stale
        return True


# Utility function to get logger easily
def get_logger(name: str = 'crypto_aggregator') -> logging.Logger:
    """
    Get or create logger instance.

    Args:
        name: Logger name

    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logging()
    return logger


# Additional helper functions for common operations
def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with default fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        float: Converted value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer with default fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        int: Converted value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        str: Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def percentage_change(old_value: float, new_value: float) -> Optional[float]:
    """
    Calculate percentage change between two values.

    Args:
        old_value: Original value
        new_value: New value

    Returns:
        float: Percentage change, or None if calculation not possible
    """
    try:
        if old_value == 0:
            return None
        return ((new_value - old_value) / old_value) * 100
    except (TypeError, ValueError, ZeroDivisionError):
        return None


if __name__ == "__main__":
    # Test utilities
    print("Testing Crypto Data Aggregator Utilities")
    print("=" * 50)

    # Test logging
    logger = setup_logging()
    logger.info("Logger test successful")

    # Test number formatting
    print(f"\nNumber Formatting:")
    print(f"  1234 -> {format_number(1234)}")
    print(f"  1234567 -> {format_number(1234567)}")
    print(f"  1234567890 -> {format_number(1234567890)}")

    # Test moving average
    prices = [100, 102, 104, 103, 105, 107, 106]
    ma = calculate_moving_average(prices, 5)
    print(f"\nMoving Average (5-period): {ma}")

    # Test RSI
    rsi_prices = [44, 44.5, 45, 45.5, 45, 44.5, 44, 43.5, 43, 43.5, 44, 44.5, 45, 45.5, 46]
    rsi = calculate_rsi(rsi_prices, 14)
    print(f"RSI (14-period): {rsi}")

    # Test coin extraction
    text = "Bitcoin (BTC) and Ethereum (ETH) are leading cryptocurrencies"
    coins = extract_coins_from_text(text)
    print(f"\nExtracted coins from text: {coins}")

    # Test data validation
    valid_data = {
        'price_usd': 45000.0,
        'volume_24h': 1000000.0,
        'market_cap': 800000000.0
    }
    is_valid = validate_price_data(valid_data)
    print(f"\nPrice data validation: {is_valid}")

    print("\n" + "=" * 50)
    print("All tests completed!")

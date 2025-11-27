"""
Utils package - Consolidated utility functions
Provides logging setup and other utility functions for the application
"""

# Import logger functions first (most critical)
try:
    from .logger import setup_logger
except ImportError as e:
    print(f"ERROR: Failed to import setup_logger from .logger: {e}")
    import logging

    def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
        """Fallback setup_logger if import fails"""
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, level.upper()))
        return logger


# Create setup_logging as an alias for setup_logger for backward compatibility
# This MUST be defined before any other imports that might use it
def setup_logging():
    """
    Setup logging for the application
    This is a compatibility wrapper around setup_logger

    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger("crypto_aggregator", level="INFO")


# Import utility functions from the standalone utils.py module
# We need to access it via a different path since we're inside the utils package
import sys
import os

# Add parent directory to path to import standalone utils module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from standalone utils.py with a different name to avoid circular imports
try:
    # Try importing specific functions from the standalone utils file
    import importlib.util

    utils_path = os.path.join(parent_dir, "utils.py")
    spec = importlib.util.spec_from_file_location("utils_standalone", utils_path)
    if spec and spec.loader:
        utils_standalone = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(utils_standalone)

        # Expose the functions
        format_number = utils_standalone.format_number
        calculate_moving_average = utils_standalone.calculate_moving_average
        calculate_rsi = utils_standalone.calculate_rsi
        extract_coins_from_text = utils_standalone.extract_coins_from_text
        export_to_csv = utils_standalone.export_to_csv
        validate_price_data = utils_standalone.validate_price_data
        is_data_stale = utils_standalone.is_data_stale
        cache_with_ttl = utils_standalone.cache_with_ttl
        safe_float = utils_standalone.safe_float
        safe_int = utils_standalone.safe_int
        truncate_string = utils_standalone.truncate_string
        percentage_change = utils_standalone.percentage_change
except Exception as e:
    print(f"Warning: Could not import from standalone utils.py: {e}")

    # Provide dummy implementations to prevent errors
    def format_number(num, decimals=2):
        return str(num)

    def calculate_moving_average(prices, period):
        return None

    def calculate_rsi(prices, period=14):
        return None

    def extract_coins_from_text(text):
        return []

    def export_to_csv(data, filename):
        return False

    def validate_price_data(price_data):
        return True

    def is_data_stale(timestamp_str, max_age_minutes=30):
        return False

    def cache_with_ttl(ttl_seconds=300):
        def decorator(func):
            return func

        return decorator

    def safe_float(value, default=0.0):
        return default

    def safe_int(value, default=0):
        return default

    def truncate_string(text, max_length=100, suffix="..."):
        return text

    def percentage_change(old_value, new_value):
        return None


__all__ = [
    "setup_logging",
    "setup_logger",
    "format_number",
    "calculate_moving_average",
    "calculate_rsi",
    "extract_coins_from_text",
    "export_to_csv",
    "validate_price_data",
    "is_data_stale",
    "cache_with_ttl",
    "safe_float",
    "safe_int",
    "truncate_string",
    "percentage_change",
]

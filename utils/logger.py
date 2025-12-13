"""
Structured JSON Logging Configuration
Provides consistent logging across the application
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, 'provider'):
            log_data['provider'] = record.provider
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        if hasattr(record, 'status'):
            log_data['status'] = record.status
        if hasattr(record, 'http_code'):
            log_data['http_code'] = record.http_code

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add stack trace if present
        if record.stack_info:
            log_data['stack_trace'] = self.formatStack(record.stack_info)

        return json.dumps(log_data)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup a logger with JSON formatting

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Clear any existing handlers
    logger.handlers = []

    # Set level
    logger.setLevel(getattr(logging, level.upper()))

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # Set JSON formatter
    json_formatter = JSONFormatter()
    console_handler.setFormatter(json_formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def log_api_request(
    logger: logging.Logger,
    provider: str,
    endpoint: str,
    duration_ms: float,
    status: str,
    http_code: Optional[int] = None,
    level: str = "INFO"
):
    """
    Log an API request with structured data

    Args:
        logger: Logger instance
        provider: Provider name
        endpoint: API endpoint
        duration_ms: Request duration in milliseconds
        status: Request status (success/error)
        http_code: HTTP status code
        level: Log level
    """
    log_level = getattr(logging, level.upper())

    extra = {
        'provider': provider,
        'endpoint': endpoint,
        'duration': duration_ms,
        'status': status,
    }

    if http_code:
        extra['http_code'] = http_code

    message = f"{provider} - {endpoint} - {status} - {duration_ms}ms"

    logger.log(log_level, message, extra=extra)


def log_error(
    logger: logging.Logger,
    provider: str,
    error_type: str,
    error_message: str,
    endpoint: Optional[str] = None,
    exc_info: bool = False
):
    """
    Log an error with structured data

    Args:
        logger: Logger instance
        provider: Provider name
        error_type: Type of error
        error_message: Error message
        endpoint: API endpoint (optional)
        exc_info: Include exception info
    """
    extra = {
        'provider': provider,
        'error_type': error_type,
    }

    if endpoint:
        extra['endpoint'] = endpoint

    message = f"{provider} - {error_type}: {error_message}"

    logger.error(message, extra=extra, exc_info=exc_info)


# Global application logger
app_logger = setup_logger("crypto_monitor", level="INFO")

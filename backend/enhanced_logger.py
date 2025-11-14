"""
Enhanced Logging System
Provides structured logging with provider health tracking and error classification
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import json


class ProviderHealthLogger:
    """Enhanced logger with provider health tracking"""

    def __init__(self, name: str = "crypto_monitor"):
        self.logger = logging.getLogger(name)
        self.health_log_path = Path("data/logs/provider_health.jsonl")
        self.error_log_path = Path("data/logs/errors.jsonl")

        # Create log directories
        self.health_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Set up handlers if not already configured
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Set up logging handlers"""
        self.logger.setLevel(logging.DEBUG)

        # Console handler with color
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Custom formatter with colors (if terminal supports it)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

        # File handler for all logs
        file_handler = logging.FileHandler('data/logs/app.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # Error file handler
        error_handler = logging.FileHandler('data/logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)

        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)

    def log_provider_request(
        self,
        provider_name: str,
        endpoint: str,
        status: str,
        response_time_ms: Optional[float] = None,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        used_proxy: bool = False
    ):
        """Log a provider API request with full context"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider_name,
            "endpoint": endpoint,
            "status": status,
            "response_time_ms": response_time_ms,
            "status_code": status_code,
            "error_message": error_message,
            "used_proxy": used_proxy
        }

        # Log to console
        if status == "success":
            self.logger.info(
                f"✓ {provider_name} | {endpoint} | {response_time_ms:.0f}ms | HTTP {status_code}"
            )
        elif status == "error":
            self.logger.error(
                f"✗ {provider_name} | {endpoint} | {error_message}"
            )
        elif status == "timeout":
            self.logger.warning(
                f"⏱ {provider_name} | {endpoint} | Timeout"
            )
        elif status == "proxy_fallback":
            self.logger.info(
                f"🌐 {provider_name} | {endpoint} | Switched to proxy"
            )

        # Append to JSONL health log
        try:
            with open(self.health_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write health log: {e}")

    def log_error(
        self,
        error_type: str,
        message: str,
        provider: Optional[str] = None,
        endpoint: Optional[str] = None,
        traceback: Optional[str] = None,
        **extra
    ):
        """Log an error with classification"""

        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "message": message,
            "provider": provider,
            "endpoint": endpoint,
            "traceback": traceback,
            **extra
        }

        # Log to console
        self.logger.error(f"[{error_type}] {message}")

        if traceback:
            self.logger.debug(f"Traceback: {traceback}")

        # Append to JSONL error log
        try:
            with open(self.error_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write error log: {e}")

    def log_proxy_switch(self, provider: str, reason: str):
        """Log when a provider switches to proxy mode"""
        self.logger.info(f"🌐 Proxy activated for {provider}: {reason}")

    def log_feature_flag_change(self, flag_name: str, old_value: bool, new_value: bool):
        """Log feature flag changes"""
        self.logger.info(f"⚙️ Feature flag '{flag_name}' changed: {old_value} → {new_value}")

    def log_health_check(self, provider: str, status: str, details: Optional[Dict] = None):
        """Log provider health check results"""
        if status == "online":
            self.logger.info(f"✓ Health check passed: {provider}")
        elif status == "degraded":
            self.logger.warning(f"⚠ Health check degraded: {provider}")
        else:
            self.logger.error(f"✗ Health check failed: {provider}")

        if details:
            self.logger.debug(f"Health details for {provider}: {details}")

    def get_recent_errors(self, limit: int = 100) -> list:
        """Read recent errors from log file"""
        errors = []
        try:
            if self.error_log_path.exists():
                with open(self.error_log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-limit:]:
                        try:
                            errors.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"Failed to read error log: {e}")

        return errors

    def get_provider_stats(self, provider: str, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a specific provider from logs"""
        from datetime import timedelta

        stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "proxy_requests": 0,
            "errors": []
        }

        try:
            if self.health_log_path.exists():
                cutoff_time = datetime.now() - timedelta(hours=hours)
                response_times = []

                with open(self.health_log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            entry_time = datetime.fromisoformat(entry["timestamp"])

                            if entry_time < cutoff_time:
                                continue

                            if entry.get("provider") != provider:
                                continue

                            stats["total_requests"] += 1

                            if entry.get("status") == "success":
                                stats["successful_requests"] += 1
                                if entry.get("response_time_ms"):
                                    response_times.append(entry["response_time_ms"])
                            else:
                                stats["failed_requests"] += 1
                                if entry.get("error_message"):
                                    stats["errors"].append({
                                        "timestamp": entry["timestamp"],
                                        "message": entry["error_message"]
                                    })

                            if entry.get("used_proxy"):
                                stats["proxy_requests"] += 1

                        except (json.JSONDecodeError, KeyError):
                            continue

                if response_times:
                    stats["avg_response_time"] = sum(response_times) / len(response_times)

        except Exception as e:
            self.logger.error(f"Failed to get provider stats: {e}")

        return stats


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )

        return super().format(record)


# Global instance
provider_health_logger = ProviderHealthLogger()


# Convenience functions
def log_request(provider: str, endpoint: str, **kwargs):
    """Log a provider request"""
    provider_health_logger.log_provider_request(provider, endpoint, **kwargs)


def log_error(error_type: str, message: str, **kwargs):
    """Log an error"""
    provider_health_logger.log_error(error_type, message, **kwargs)


def log_proxy_switch(provider: str, reason: str):
    """Log proxy switch"""
    provider_health_logger.log_proxy_switch(provider, reason)


def get_provider_stats(provider: str, hours: int = 24):
    """Get provider statistics"""
    return provider_health_logger.get_provider_stats(provider, hours)

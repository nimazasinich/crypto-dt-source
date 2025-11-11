"""
Input Validation Helpers
"""

from typing import Optional
from datetime import datetime
import re


def validate_date(date_str: str) -> Optional[datetime]:
    """Validate and parse date string"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None


def validate_provider_name(name: str) -> bool:
    """Validate provider name"""
    if not name or not isinstance(name, str):
        return False
    return len(name) >= 2 and len(name) <= 50


def validate_category(category: str) -> bool:
    """Validate category name"""
    valid_categories = [
        "market_data",
        "blockchain_explorers",
        "news",
        "sentiment",
        "onchain_analytics"
    ]
    return category in valid_categories


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

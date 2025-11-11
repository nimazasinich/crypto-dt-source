"""
Database module for Crypto API Monitor
"""

from database.db_manager import DatabaseManager, db_manager

# Create alias for backward compatibility
Database = DatabaseManager

__all__ = ['DatabaseManager', 'Database', 'db_manager']

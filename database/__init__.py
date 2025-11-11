"""Database module for crypto API monitoring"""

from database.db_manager import DatabaseManager

# For backward compatibility
Database = DatabaseManager

__all__ = ['DatabaseManager', 'Database']

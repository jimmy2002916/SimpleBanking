"""
Database module for the Simple Banking System.

This module provides database-related functionality.
"""

# Import main classes for easier access
from .sqlite_storage import SQLiteStorage
from .database_manager import DatabaseManager

# Public API
__all__ = ['SQLiteStorage', 'DatabaseManager']

"""
Transaction Management for the Simple Banking System.

Handles atomicity and concurrency for financial operations.
"""

# Export the main class
from .transaction_manager import TransactionManager

# Public API
__all__ = ['TransactionManager']

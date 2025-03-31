"""
Facade module for the Simple Banking System.

Provides a simplified interface to the banking system components.
"""

# Import core components from banking.py
from .banking import (
    BankAccount, 
    BankingSystem, 
    TransactionLogger, 
    TransactionManager
)

# Public API
__all__ = [
    'BankAccount', 
    'BankingSystem', 
    'TransactionLogger', 
    'TransactionManager'
]

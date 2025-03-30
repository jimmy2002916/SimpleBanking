"""
Main banking module for the Simple Banking System.

This module imports and exposes the classes from the basic_required_features module
and advanced_features modules.
"""

# Import the classes directly - using absolute imports for better compatibility
from basic_required_features.account import BankAccount
from basic_required_features.banking_system import BankingSystem

# Import advanced features
from advanced_features.logging import TransactionLogger

# This file serves as a facade for the banking system components
# It allows the tests to import BankAccount, BankingSystem, and advanced features
# directly from 'banking'

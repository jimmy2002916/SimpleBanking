"""
Main banking module for the Simple Banking System.

This module imports and exposes the classes from the basic_required_features module.
"""

from basic_required_features.account import BankAccount
from basic_required_features.banking_system import BankingSystem

# This file serves as a facade for the banking system components
# It allows the tests to import BankAccount and BankingSystem directly from 'banking'

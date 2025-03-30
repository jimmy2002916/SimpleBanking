"""
Logging package for the Simple Banking System.

This package provides logging functionality for banking operations,
with a scalable architecture that can grow from a simple file-based
implementation to an enterprise-level solution.
"""

# Import main classes for easier access
from .transaction_logger import TransactionLogger
from .architecture.facade import LoggingFacade

# This allows imports like:
# from advanced_features.logging import TransactionLogger

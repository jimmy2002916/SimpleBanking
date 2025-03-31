# Core banking classes
from basic_required_features.account import BankAccount
from basic_required_features.banking_system import BankingSystem

# Advanced features
from advanced_features.logging.transaction_logger import TransactionLogger
from advanced_features.transaction_management import TransactionManager

# Note: This facade pattern makes imports cleaner in client code
# and provides a stable API even if the underlying implementation changes

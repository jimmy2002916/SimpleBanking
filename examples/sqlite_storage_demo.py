"""
Demo script for using SQLite storage with the Banking System.

This script demonstrates how to use SQLite storage for account data
while keeping the transaction logging system unchanged.
"""
from decimal import Decimal
import os

from basic_required_features.banking_system import BankingSystem
from advanced_features.storage.storage_factory import StorageFactory
from advanced_features.logging.transaction_logger import TransactionLogger


def main():
    """Run the SQLite storage demo."""
    print("Simple Banking System - SQLite Storage Demo")
    print("===========================================")
    
    # Create SQLite storage
    print("\nInitializing SQLite storage...")
    sqlite_storage = StorageFactory.create_storage("sqlite", db_path="banking.db")
    
    # Create banking system with SQLite storage
    print("Creating banking system with SQLite storage...")
    banking_system = BankingSystem(sqlite_storage)
    
    # Attach transaction logger (still using file-based logging)
    print("Attaching transaction logger...")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    logger = TransactionLogger(f"{log_dir}/transactions.log")
    banking_system.attach_logger(logger)
    
    # Create some accounts
    print("\nCreating accounts...")
    acc1 = banking_system.create_account("Alice", Decimal("1000.00"))
    print(f"Created account for Alice: {acc1}")
    
    acc2 = banking_system.create_account("Bob", Decimal("500.00"))
    print(f"Created account for Bob: {acc2}")
    
    # Perform some transactions
    print("\nPerforming transactions...")
    banking_system.deposit(acc1, Decimal("200.00"))
    print(f"Deposited $200.00 to Alice's account")
    
    banking_system.withdraw(acc2, Decimal("100.00"))
    print(f"Withdrew $100.00 from Bob's account")
    
    banking_system.transfer(acc1, acc2, Decimal("300.00"))
    print(f"Transferred $300.00 from Alice's account to Bob's account")
    
    # Display account balances
    print("\nCurrent account balances:")
    alice_account = banking_system.get_account(acc1)
    bob_account = banking_system.get_account(acc2)
    
    print(f"Alice's balance: ${alice_account.balance}")
    print(f"Bob's balance: ${bob_account.balance}")
    
    # Save accounts to SQLite
    print("\nSaving accounts to SQLite database...")
    banking_system.save_to_storage()
    
    print("\nDemo completed. Account data is stored in 'banking.db'")
    print("Transaction logs are stored in 'logs/transactions.log'")


if __name__ == "__main__":
    main()

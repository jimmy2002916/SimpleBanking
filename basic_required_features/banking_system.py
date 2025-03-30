"""
Banking System module for the Simple Banking System.

This module defines the BankingSystem class which manages bank accounts
and provides operations like creating accounts, deposits, withdrawals, and transfers.
"""
from decimal import Decimal
import csv
import os
from typing import Optional, Dict, Any, Union

from .account import BankAccount
from .storage_interface import IStorage
from .csv_storage import CSVStorage

class BankingSystem:
    """
    Manages bank accounts and provides system-wide operations.
    """
    def __init__(self, storage: Optional[IStorage] = None):
        """
        Initialize a new banking system with an empty accounts dictionary.
        
        Args:
            storage (Optional[IStorage]): Storage implementation to use
                                         (defaults to CSV storage if None)
        """
        self.accounts = {}
        self.next_account_id = 1
        self.logger = None
        
        # Set up storage
        self.storage = storage if storage is not None else CSVStorage()
        
        # Try to load existing accounts
        self._load_from_storage()
    
    def attach_logger(self, logger):
        """
        Attach a transaction logger to the banking system.
        
        Args:
            logger: A transaction logger object
        """
        self.logger = logger
    
    def create_account(self, name, initial_balance=Decimal("0.00")):
        """
        Create a new bank account.
        
        Args:
            name (str): Name of the account holder
            initial_balance (Decimal): Initial balance for the account
            
        Returns:
            str: The account ID of the newly created account
            
        Raises:
            ValueError: If initial_balance is negative
        """
        # Validate initial balance
        if initial_balance < Decimal("0.00"):
            raise ValueError("Initial balance cannot be negative")
        
        # Generate a unique account ID
        account_id = f"ACC{self.next_account_id:04d}"
        self.next_account_id += 1
        
        # Create and store the account
        self.accounts[account_id] = BankAccount(account_id, name, initial_balance)
        
        # Log the account creation if logger is attached
        if self.logger:
            self.logger.log_transaction({
                "action": "create_account",
                "account_id": account_id,
                "name": name,
                "initial_balance": initial_balance,
                "status": "success"
            })
        
        return account_id
    
    def get_account(self, account_id):
        """
        Get an account by its ID.
        
        Args:
            account_id (str): The ID of the account to retrieve
            
        Returns:
            BankAccount: The account if found, None otherwise
        """
        return self.accounts.get(account_id)
    
    def deposit(self, account_id, amount):
        """
        Deposit money into an account.
        
        Args:
            account_id (str): ID of the account
            amount (Decimal): Amount to deposit
            
        Returns:
            bool: True if deposit was successful, False otherwise
        """
        account = self.get_account(account_id)
        if not account:
            # Log failed deposit if logger is attached
            if self.logger:
                self.logger.log_deposit(account_id, amount, "failed", "Account not found")
            return False
        
        result = account.deposit(amount)
        
        # Log the deposit if logger is attached
        if self.logger:
            if result:
                self.logger.log_deposit(account_id, amount, "success")
            else:
                self.logger.log_deposit(account_id, amount, "failed", "Invalid amount")
        
        return result
    
    def withdraw(self, account_id, amount):
        """
        Withdraw money from an account.
        
        Args:
            account_id (str): ID of the account
            amount (Decimal): Amount to withdraw
            
        Returns:
            bool: True if withdrawal was successful, False otherwise
        """
        account = self.get_account(account_id)
        if not account:
            # Log failed withdrawal if logger is attached
            if self.logger:
                self.logger.log_withdraw(account_id, amount, "failed", "Account not found")
            return False
        
        # Check if amount is positive
        if amount <= Decimal("0.00"):
            if self.logger:
                self.logger.log_withdraw(account_id, amount, "failed", "Invalid amount")
            return False
        
        # Check if there's enough balance
        if amount > account.balance:
            if self.logger:
                self.logger.log_withdraw(account_id, amount, "failed", "Insufficient funds")
            return False
        
        result = account.withdraw(amount)
        
        # Log the withdrawal if logger is attached
        if self.logger and result:
            self.logger.log_withdraw(account_id, amount, "success")
        
        return result
    
    def transfer(self, from_account_id, to_account_id, amount):
        """
        Transfer money between accounts.
        
        Args:
            from_account_id (str): ID of the source account
            to_account_id (str): ID of the destination account
            amount (Decimal): Amount to transfer
            
        Returns:
            bool: True if transfer was successful, False otherwise
        """
        # Check if amount is positive
        if amount <= Decimal("0.00"):
            if self.logger:
                self.logger.log_transfer(from_account_id, to_account_id, amount, "failed", "Invalid amount")
            return False
        
        # Get the accounts
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        
        # Check if both accounts exist
        if not from_account or not to_account:
            if self.logger:
                self.logger.log_transfer(from_account_id, to_account_id, amount, "failed", "Account not found")
            return False
        
        # Check if the source account has enough balance
        if from_account.balance < amount:
            if self.logger:
                self.logger.log_transfer(from_account_id, to_account_id, amount, "failed", "Insufficient funds")
            return False
        
        # Perform the transfer
        from_account.balance -= amount
        to_account.balance += amount
        
        # Log the transfer if logger is attached
        if self.logger:
            self.logger.log_transfer(from_account_id, to_account_id, amount, "success")
        
        return True
    
    def save_to_storage(self) -> bool:
        """
        Save the banking system state to the configured storage.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            result = self.storage.save_accounts(self.accounts, self.next_account_id)
            
            # Log the save operation if logger is attached
            if self.logger:
                self.logger.log_transaction({
                    "action": "save_to_storage",
                    "status": "success" if result else "failed"
                })
            
            return result
        except Exception as e:
            # Log the failed save operation if logger is attached
            if self.logger:
                self.logger.log_transaction({
                    "action": "save_to_storage",
                    "status": "failed",
                    "reason": str(e)
                })
            print(f"Error saving to storage: {e}")
            return False
    
    def _load_from_storage(self) -> bool:
        """
        Load the banking system state from the configured storage.
        
        Returns:
            bool: True if load was successful, False otherwise
        """
        try:
            # Load accounts from storage
            self.accounts = self.storage.load_accounts()
            
            # If using CSV storage, get the next_account_id
            if hasattr(self.storage, 'get_next_account_id'):
                self.next_account_id = self.storage.get_next_account_id()
            else:
                # For other storage types, determine next_account_id from accounts
                self._determine_next_account_id()
            
            # Log the load operation if logger is attached
            if self.logger:
                self.logger.log_transaction({
                    "action": "load_from_storage",
                    "status": "success"
                })
            
            return True
        except Exception as e:
            # Log the failed load operation if logger is attached
            if self.logger:
                self.logger.log_transaction({
                    "action": "load_from_storage",
                    "status": "failed",
                    "reason": str(e)
                })
            print(f"Error loading from storage: {e}")
            return False
    
    def _determine_next_account_id(self) -> None:
        """
        Determine the next account ID based on existing accounts.
        """
        max_id = 0
        for account_id in self.accounts.keys():
            if account_id.startswith("ACC"):
                try:
                    id_num = int(account_id[3:])
                    max_id = max(max_id, id_num)
                except ValueError:
                    pass
        
        self.next_account_id = max_id + 1
    
    # Legacy methods below can be removed as they're now handled by the storage interface
    # and StorageFactory. Keeping them would create duplicate code paths.
    def save_to_csv(self, filepath):
        """
        Save the banking system state to a CSV file.
        
        Args:
            filepath (str): Path to the CSV file
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        csv_storage = CSVStorage(filepath)
        result = csv_storage.save_accounts(self.accounts, self.next_account_id)
        
        # Log the save operation if logger is attached
        if self.logger:
            self.logger.log_transaction({
                "action": "save_to_csv",
                "filepath": filepath,
                "status": "success" if result else "failed"
            })
        
        return result
    
    # For backward compatibility
    def load_from_csv(self, filepath):
        """
        Load the banking system state from a CSV file.
        
        Args:
            filepath (str): Path to the CSV file
            
        Returns:
            bool: True if load was successful, False otherwise
        """
        try:
            csv_storage = CSVStorage(filepath)
            self.accounts = csv_storage.load_accounts()
            self.next_account_id = csv_storage.get_next_account_id()
            
            # Log the load operation if logger is attached
            if self.logger:
                self.logger.log_transaction({
                    "action": "load_from_csv",
                    "filepath": filepath,
                    "status": "success"
                })
            
            return True
        except Exception as e:
            # Log the failed load operation if logger is attached
            if self.logger:
                self.logger.log_transaction({
                    "action": "load_from_csv",
                    "filepath": filepath,
                    "status": "failed",
                    "reason": str(e)
                })
            print(f"Error loading from CSV: {e}")
            return False

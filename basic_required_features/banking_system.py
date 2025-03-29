"""
Banking System module for the Simple Banking System.

This module defines the BankingSystem class which manages bank accounts
and provides operations like creating accounts, deposits, withdrawals, and transfers.
"""
from decimal import Decimal
from .account import BankAccount

class BankingSystem:
    """
    Manages bank accounts and provides system-wide operations.
    """
    def __init__(self):
        """
        Initialize a new banking system with an empty accounts dictionary.
        """
        self.accounts = {}
        self.next_account_id = 1
    
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
            return False
        
        return account.deposit(amount)
    
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
            return False
        
        return account.withdraw(amount)

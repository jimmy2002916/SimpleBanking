"""
Account module for the Simple Banking System.

This module defines the BankAccount class which represents a single bank account
in our system.
"""
from decimal import Decimal

class BankAccount:
    """
    Represents a bank account with basic functionality.
    """
    def __init__(self, account_id, name, balance=Decimal("0.00")):
        """
        Initialize a new bank account.
        
        Args:
            account_id (str): Unique identifier for the account
            name (str): Name of the account holder
            balance (Decimal): Initial balance, defaults to 0.00
        """
        self.account_id = account_id
        self.name = name
        self.balance = balance
        
    def deposit(self, amount):
        """
        Deposit money into the account.
        
        Args:
            amount (Decimal): Amount to deposit
            
        Returns:
            bool: True if deposit was successful, False otherwise
        """
        # Check if amount is positive
        if amount <= Decimal("0.00"):
            return False
        
        # Add amount to balance
        self.balance += amount
        return True
    
    def withdraw(self, amount):
        """
        Withdraw money from the account.
        
        Args:
            amount (Decimal): Amount to withdraw
            
        Returns:
            bool: True if withdrawal was successful, False otherwise
        """
        # Check if amount is positive
        if amount <= Decimal("0.00"):
            return False
        
        # Check if there's enough balance (overdraft protection)
        if amount > self.balance:
            return False
        
        # Subtract amount from balance
        self.balance -= amount
        return True

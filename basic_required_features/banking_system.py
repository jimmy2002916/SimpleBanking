"""
Banking System module for the Simple Banking System.

This module defines the BankingSystem class which manages bank accounts
and provides operations like creating accounts, deposits, withdrawals, and transfers.
"""
from decimal import Decimal
import csv
import os
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
            return False
        
        # Get the accounts
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        
        # Check if both accounts exist
        if not from_account or not to_account:
            return False
        
        # Check if the source account has enough balance
        if from_account.balance < amount:
            return False
        
        # Perform the transfer
        from_account.balance -= amount
        to_account.balance += amount
        
        return True
    
    def save_to_csv(self, filepath):
        """
        Save the banking system state to a CSV file.
        
        Args:
            filepath (str): Path to the CSV file
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(filepath, 'w', newline='') as csvfile:
                # Create CSV writer
                writer = csv.writer(csvfile)
                
                # Write header row
                writer.writerow(['account_id', 'name', 'balance', 'next_account_id'])
                
                # Write system state (next_account_id)
                writer.writerow(['SYSTEM', '', '', self.next_account_id])
                
                # Write account data
                for account_id, account in self.accounts.items():
                    writer.writerow([
                        account.account_id,
                        account.name,
                        str(account.balance)
                    ])
            
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    
    def load_from_csv(self, filepath):
        """
        Load the banking system state from a CSV file.
        
        Args:
            filepath (str): Path to the CSV file
            
        Returns:
            bool: True if load was successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                return False
            
            # Clear current state
            self.accounts = {}
            
            with open(filepath, 'r', newline='') as csvfile:
                # Create CSV reader
                reader = csv.reader(csvfile)
                
                # Skip header row
                next(reader)
                
                # Process rows
                for row in reader:
                    if row[0] == 'SYSTEM':
                        # System state row
                        self.next_account_id = int(row[3])
                    else:
                        # Account row
                        account_id = row[0]
                        name = row[1]
                        balance = Decimal(row[2])
                        
                        # Create account object directly (bypass create_account to preserve IDs)
                        self.accounts[account_id] = BankAccount(account_id, name, balance)
            
            return True
        except Exception as e:
            print(f"Error loading from CSV: {e}")
            return False

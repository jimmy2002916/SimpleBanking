"""
CSV Storage for the Simple Banking System.

This module provides CSV-based persistence for bank accounts.
"""
import os
import csv
from decimal import Decimal
from typing import Dict, Optional

from .storage_interface import IStorage
from .account import BankAccount


class CSVStorage(IStorage):
    """
    Provides CSV-based persistence for bank accounts.
    """
    
    def __init__(self, filepath: str = "accounts.csv"):
        """
        Initialize the CSV storage.
        
        Args:
            filepath (str): Path to the CSV file
        """
        self.filepath = filepath
        self.next_account_id = 1
    
    def save_accounts(self, accounts: Dict[str, BankAccount], next_account_id: int = None) -> bool:
        """
        Save accounts to a CSV file.
        
        Args:
            accounts (Dict[str, BankAccount]): Dictionary of account_id -> BankAccount
            next_account_id (int, optional): Next account ID for the system
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(self.filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(self.filepath, 'w', newline='') as csvfile:
                # Create CSV writer
                writer = csv.writer(csvfile)
                
                # Write header row
                writer.writerow(['account_id', 'name', 'balance', 'next_account_id'])
                
                # Write system state (next_account_id)
                writer.writerow(['SYSTEM', '', '', next_account_id or self.next_account_id])
                
                # Write account data
                for account_id, account in accounts.items():
                    writer.writerow([
                        account.account_id,
                        account.name,
                        str(account.balance)
                    ])
            
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    
    def load_accounts(self) -> Dict[str, BankAccount]:
        """
        Load accounts from a CSV file.
        
        Returns:
            Dict[str, BankAccount]: Dictionary of account_id -> BankAccount
            
        Note:
            Also updates self.next_account_id based on the file content
        """
        accounts = {}
        
        try:
            # Check if file exists
            if not os.path.exists(self.filepath):
                return accounts
            
            with open(self.filepath, 'r', newline='') as csvfile:
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
                        
                        # Create account object
                        accounts[account_id] = BankAccount(account_id, name, balance)
            
        except Exception as e:
            print(f"Error loading from CSV: {e}")
        
        return accounts
    
    def get_account(self, account_id: str) -> Optional[BankAccount]:
        """
        Get a specific account from the CSV file.
        
        Args:
            account_id (str): ID of the account to retrieve
            
        Returns:
            Optional[BankAccount]: The account if found, None otherwise
        """
        # For CSV, we need to load all accounts and find the one we want
        accounts = self.load_accounts()
        return accounts.get(account_id)
    
    def get_next_account_id(self) -> int:
        """
        Get the next account ID from the CSV file.
        
        Returns:
            int: Next account ID
        """
        # Load accounts to update next_account_id
        self.load_accounts()
        return self.next_account_id
    
    def close(self) -> None:
        """
        Close the storage connection.
        
        Note:
            No-op for CSV storage as there's no persistent connection.
        """
        pass

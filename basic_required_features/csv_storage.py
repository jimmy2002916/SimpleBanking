import csv
import os
from decimal import Decimal
from typing import Dict, Optional

from .i_storage import IStorage
from .account import BankAccount


class CSVStorage(IStorage):
    
    def __init__(self, filepath: str = "data/accounts.csv"):
        self.filepath = filepath
        self.next_account_id = 1
    
    def save_accounts(self, accounts: Dict[str, BankAccount], next_account_id: int = None) -> bool:
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
        # For CSV, we need to load all accounts and find the one we want
        accounts = self.load_accounts()
        return accounts.get(account_id)
    
    def get_next_account_id(self) -> int:
        # Load accounts to update next_account_id
        self.load_accounts()
        return self.next_account_id
    
    def close(self) -> None:
        pass

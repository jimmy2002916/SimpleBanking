from decimal import Decimal
import csv
import os
from typing import Optional, Dict, Any, Union

from .account import BankAccount
from .i_storage import IStorage
from .csv_storage import CSVStorage
from advanced_features.transaction_management import TransactionManager

class BankingSystem:

    def __init__(self, storage: Optional[IStorage] = None):
        self.accounts = {}
        self.next_account_id = 1
        self.logger = None
        
        self.storage = storage if storage is not None else CSVStorage()
        
        self.transaction_manager = TransactionManager()
        
        self._load_from_storage()
    
    def attach_logger(self, logger):
        self.logger = logger
    
    def create_account(self, name, initial_balance=Decimal("0.00"), validate_only=False):
        if not name or name.strip() == "":
            if validate_only:
                raise ValueError("Account holder name cannot be empty")
            return None
            
        if initial_balance < Decimal("0.00"):
            if validate_only:
                raise ValueError("Initial balance cannot be negative")
            return None
        
        account_id = f"ACC{self.next_account_id:04d}"
        self.next_account_id += 1
        
        self.accounts[account_id] = BankAccount(account_id, name, initial_balance)
        
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
        return self.accounts.get(account_id)
    
    def deposit(self, account_id, amount, validate_only=False):
        # Validate amount before acquiring any locks
        if amount < Decimal("0.00"):
            if self.logger:
                self.logger.log_deposit(account_id, amount, "failed", reason="Negative amount")
            if validate_only:
                raise ValueError("Deposit amount cannot be negative")
            return False
            
        if amount == Decimal("0.00"):
            if self.logger:
                self.logger.log_deposit(account_id, amount, "failed", reason="Zero amount")
            if validate_only:
                raise ValueError("Deposit amount cannot be zero")
            return False
            
        # Check if account exists before attempting transaction
        if account_id not in self.accounts:
            if self.logger:
                self.logger.log_deposit(account_id, amount, "failed", reason="Account not found")
            if validate_only:
                raise ValueError(f"Account {account_id} not found")
            return False
            
        def deposit_operation(transaction_accounts):
            account = transaction_accounts[account_id]
            result = account.deposit(amount)
            return result
            
        try:
            result = self.transaction_manager.execute_atomic(
                [account_id], 
                self.accounts,
                deposit_operation
            )
            
            if self.logger:
                if result:
                    # Get the updated balance
                    current_balance = self.accounts[account_id].balance
                    self.logger.log_deposit(account_id, amount, "success", balance=current_balance)
                else:
                    self.logger.log_deposit(account_id, amount, "failed", reason="Operation failed")
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.log_deposit(account_id, amount, "failed", reason=str(e))
            return False
    
    def withdraw(self, account_id, amount, validate_only=False):
        if amount < Decimal("0.00"):
            if self.logger:
                self.logger.log_withdraw(account_id, amount, "failed", reason="Negative amount")
            if validate_only:
                raise ValueError("Withdrawal amount cannot be negative")
            return False
            
        if amount == Decimal("0.00"):
            if self.logger:
                self.logger.log_withdraw(account_id, amount, "failed", reason="Zero amount")
            if validate_only:
                raise ValueError("Withdrawal amount cannot be zero")
            return False
            
        if account_id not in self.accounts:
            if self.logger:
                self.logger.log_withdraw(account_id, amount, "failed", reason="Account not found")
            if validate_only:
                raise ValueError(f"Account {account_id} not found")
            return False
            
        account = self.get_account(account_id)
        if account and amount > account.balance:
            if self.logger:
                self.logger.log_withdraw(account_id, amount, "failed", reason="Insufficient funds")
            if validate_only:
                raise ValueError("Insufficient funds for withdrawal")
            return False
        
        def withdraw_operation(transaction_accounts):
            account = transaction_accounts[account_id]
            # Double-check balance after acquiring lock
            if amount > account.balance:
                return False
            result = account.withdraw(amount)
            return result
            
        try:
            result = self.transaction_manager.execute_atomic(
                [account_id], 
                self.accounts,
                withdraw_operation
            )
            
            if self.logger:
                if result:
                    # Get the updated balance
                    current_balance = self.accounts[account_id].balance
                    self.logger.log_withdraw(account_id, amount, "success", balance=current_balance)
                else:
                    self.logger.log_withdraw(account_id, amount, "failed", reason="Operation failed")
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.log_withdraw(account_id, amount, "failed", reason=str(e))
            return False
    
    def transfer(self, from_account_id, to_account_id, amount):
        if amount <= Decimal("0.00"):
            if self.logger:
                self.logger.log_transfer(from_account_id, to_account_id, amount, "failed", reason="Invalid amount")
            return False
        
        if from_account_id not in self.accounts or to_account_id not in self.accounts:
            if self.logger:
                self.logger.log_transfer(from_account_id, to_account_id, amount, "failed", reason="Account not found")
            return False
            
        from_account = self.get_account(from_account_id)
        if from_account and from_account.balance < amount:
            if self.logger:
                self.logger.log_transfer(from_account_id, to_account_id, amount, "failed", reason="Insufficient funds")
            return False
            
        def transfer_operation(transaction_accounts):
            from_account = transaction_accounts[from_account_id]
            to_account = transaction_accounts[to_account_id]
            
            if from_account.balance < amount:
                return False
                
            from_account.balance -= amount
            to_account.balance += amount
            return True
            
        try:
            result = self.transaction_manager.execute_atomic(
                [from_account_id, to_account_id], 
                self.accounts,
                transfer_operation
            )
            
            if self.logger:
                if result:
                    # Get the updated balances
                    from_balance = self.accounts[from_account_id].balance
                    to_balance = self.accounts[to_account_id].balance
                    self.logger.log_transfer(
                        from_account_id, 
                        to_account_id, 
                        amount, 
                        "success",
                        from_balance=from_balance,
                        to_balance=to_balance
                    )
                else:
                    self.logger.log_transfer(from_account_id, to_account_id, amount, "failed", reason="Operation failed")
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.log_transfer(from_account_id, to_account_id, amount, "failed", reason=str(e))
            return False
    
    def save_to_storage(self) -> bool:
        try:
            result = self.storage.save_accounts(self.accounts, self.next_account_id)
            
            if self.logger:
                self.logger.log_transaction({
                    "action": "save_to_storage",
                    "status": "success" if result else "failed"
                })
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.log_transaction({
                    "action": "save_to_storage",
                    "status": "failed",
                    "reason": str(e)
                })
            print(f"Error saving to storage: {e}")
            return False
    
    def load_from_storage(self) -> bool:
        return self._load_from_storage()
    
    def _load_from_storage(self) -> bool:
        try:
            # Load accounts from storage
            self.accounts = self.storage.load_accounts()
            
            # If using CSV storage, get the next_account_id
            if hasattr(self.storage, 'get_next_account_id'):
                self.next_account_id = self.storage.get_next_account_id()
            else:
                self._determine_next_account_id()
            
            if self.logger:
                self.logger.log_transaction({
                    "action": "load_from_storage",
                    "status": "success"
                })
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.log_transaction({
                    "action": "load_from_storage",
                    "status": "failed",
                    "reason": str(e)
                })
            print(f"Error loading from storage: {e}")
            return False
    
    def _determine_next_account_id(self) -> None:
        max_id = 0
        for account_id in self.accounts.keys():
            if account_id.startswith("ACC"):
                try:
                    id_num = int(account_id[3:])
                    max_id = max(max_id, id_num)
                except ValueError:
                    pass
        
        self.next_account_id = max_id + 1

    def save_to_csv(self, filepath):
        csv_storage = CSVStorage(filepath)
        result = csv_storage.save_accounts(self.accounts, self.next_account_id)
        
        if self.logger:
            self.logger.log_transaction({
                "action": "save_to_csv",
                "filepath": filepath,
                "status": "success" if result else "failed"
            })
        
        return result
    
    def load_from_csv(self, filepath):
        try:
            csv_storage = CSVStorage(filepath)
            self.accounts = csv_storage.load_accounts()
            self.next_account_id = csv_storage.get_next_account_id()
            
            if self.logger:
                self.logger.log_transaction({
                    "action": "load_from_csv",
                    "filepath": filepath,
                    "status": "success"
                })
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.log_transaction({
                    "action": "load_from_csv",
                    "filepath": filepath,
                    "status": "failed",
                    "reason": str(e)
                })
            print(f"Error loading from CSV: {e}")
            return False

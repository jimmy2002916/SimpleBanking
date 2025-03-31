import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional

# Import the new logging architecture
from .architecture.facade import LoggingFacade


class TransactionLogger:
    
    def __init__(self, log_file="transactions.log"):

        self.log_file = log_file
        
        # Create the logging facade
        self.logging_facade = LoggingFacade(log_file)
    
    def log_transaction(self, transaction_data):
        # Add timestamp to transaction data if not present
        if "timestamp" not in transaction_data:
            transaction_data["timestamp"] = datetime.now().isoformat()
        
        # Use the logging facade to log the transaction
        self.logging_facade.log_transaction(transaction_data)
    
    def log_deposit(self, account_id, amount, status, balance=None, reason=None):
        transaction_data = {
            "action": "deposit",
            "account_id": account_id,
            "amount": amount,
            "status": status
        }
        
        # Include the new balance if provided
        if balance is not None and status == "success":
            transaction_data["new_balance"] = balance
            
        if reason:
            transaction_data["reason"] = reason
            
        self.log_transaction(transaction_data)
    
    def log_withdraw(self, account_id, amount, status, balance=None, reason=None):
        transaction_data = {
            "action": "withdraw",
            "account_id": account_id,
            "amount": amount,
            "status": status
        }
        
        # Include the new balance if provided
        if balance is not None and status == "success":
            transaction_data["new_balance"] = balance
            
        if reason:
            transaction_data["reason"] = reason
            
        self.log_transaction(transaction_data)
    
    def log_transfer(self, from_account_id, to_account_id, amount, status, from_balance=None, to_balance=None, reason=None):
        transaction_data = {
            "action": "transfer",
            "from_account_id": from_account_id,
            "to_account_id": to_account_id,
            "amount": amount,
            "status": status
        }
        
        # Include the new balances if provided
        if status == "success":
            if from_balance is not None:
                transaction_data["from_account_balance"] = from_balance
            if to_balance is not None:
                transaction_data["to_account_balance"] = to_balance
            
        if reason:
            transaction_data["reason"] = reason
            
        self.log_transaction(transaction_data)
    
    def get_all_logs(self):
        return self.logging_facade.get_all_logs()
    
    def get_logs_by_account(self, account_id):
        return self.logging_facade.get_logs_by_account(account_id)
    
    def get_logs_by_action(self, action):
        return self.logging_facade.get_logs_by_action(action)

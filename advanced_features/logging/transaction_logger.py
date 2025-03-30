"""
Transaction Logging module for the Simple Banking System.

This module provides logging functionality for transactions in the banking system,
which is useful for audit purposes and can serve as a foundation for analytics.
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional

# Import the new logging architecture
from .architecture.facade import LoggingFacade


class TransactionLogger:
    """
    Logs banking transactions for audit and analytics purposes.
    
    This class now uses the scalable logging architecture internally
    while maintaining the same interface for backward compatibility.
    """
    
    def __init__(self, log_file="transactions.log"):
        """
        Initialize a new transaction logger.
        
        Args:
            log_file (str): Path to the log file
        """
        self.log_file = log_file
        
        # Create the logging facade
        self.logging_facade = LoggingFacade(log_file)
    
    def log_transaction(self, transaction_data):
        """
        Log a transaction to the log file.
        
        Args:
            transaction_data (dict): Data about the transaction
        """
        # Add timestamp to transaction data if not present
        if "timestamp" not in transaction_data:
            transaction_data["timestamp"] = datetime.now().isoformat()
        
        # Use the logging facade to log the transaction
        self.logging_facade.log_transaction(transaction_data)
    
    def log_deposit(self, account_id, amount, status, reason=None):
        """
        Log a deposit transaction.
        
        Args:
            account_id (str): ID of the account
            amount (Decimal): Amount deposited
            status (str): Status of the transaction (success or failed)
            reason (str, optional): Reason for failure if status is failed
        """
        transaction_data = {
            "action": "deposit",
            "account_id": account_id,
            "amount": amount,
            "status": status
        }
        
        if reason:
            transaction_data["reason"] = reason
            
        self.log_transaction(transaction_data)
    
    def log_withdraw(self, account_id, amount, status, reason=None):
        """
        Log a withdrawal transaction.
        
        Args:
            account_id (str): ID of the account
            amount (Decimal): Amount withdrawn
            status (str): Status of the transaction (success or failed)
            reason (str, optional): Reason for failure if status is failed
        """
        transaction_data = {
            "action": "withdraw",
            "account_id": account_id,
            "amount": amount,
            "status": status
        }
        
        if reason:
            transaction_data["reason"] = reason
            
        self.log_transaction(transaction_data)
    
    def log_transfer(self, from_account_id, to_account_id, amount, status, reason=None):
        """
        Log a transfer transaction.
        
        Args:
            from_account_id (str): ID of the source account
            to_account_id (str): ID of the destination account
            amount (Decimal): Amount transferred
            status (str): Status of the transaction (success or failed)
            reason (str, optional): Reason for failure if status is failed
        """
        transaction_data = {
            "action": "transfer",
            "from_account_id": from_account_id,
            "to_account_id": to_account_id,
            "amount": amount,
            "status": status
        }
        
        if reason:
            transaction_data["reason"] = reason
            
        self.log_transaction(transaction_data)
    
    def get_all_logs(self):
        """
        Get all transaction logs.
        
        Returns:
            list: List of transaction logs
        """
        return self.logging_facade.get_all_logs()
    
    def get_logs_by_account(self, account_id):
        """
        Get all transaction logs for a specific account.
        
        Args:
            account_id (str): ID of the account
            
        Returns:
            list: List of transaction logs for the account
        """
        return self.logging_facade.get_logs_by_account(account_id)
    
    def get_logs_by_action(self, action):
        """
        Get all transaction logs for a specific action type.
        
        Args:
            action (str): Type of action (deposit, withdraw, transfer)
            
        Returns:
            list: List of transaction logs for the action
        """
        return self.logging_facade.get_logs_by_action(action)

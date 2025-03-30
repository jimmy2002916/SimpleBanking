"""
Storage Interface for the Simple Banking System.

This module defines the interface for storage implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from .account import BankAccount


class IStorage(ABC):
    """
    Interface for storage implementations.
    """
    
    @abstractmethod
    def save_accounts(self, accounts: Dict[str, BankAccount]) -> bool:
        """
        Save accounts to storage.
        
        Args:
            accounts (Dict[str, BankAccount]): Dictionary of account_id -> BankAccount
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load_accounts(self) -> Dict[str, BankAccount]:
        """
        Load accounts from storage.
        
        Returns:
            Dict[str, BankAccount]: Dictionary of account_id -> BankAccount
        """
        pass
    
    @abstractmethod
    def get_account(self, account_id: str) -> Optional[BankAccount]:
        """
        Get a specific account from storage.
        
        Args:
            account_id (str): ID of the account to retrieve
            
        Returns:
            Optional[BankAccount]: The account if found, None otherwise
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        Close the storage connection if applicable.
        """
        pass

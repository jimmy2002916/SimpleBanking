"""
Storage Factory for the Simple Banking System.

This module provides a factory for creating storage implementations.
"""
from typing import Optional
from basic_required_features.storage_interface import IStorage
from basic_required_features.csv_storage import CSVStorage
from .database.sqlite_storage import SQLiteStorage


class StorageFactory:
    """
    Factory for creating storage implementations.
    """
    
    @staticmethod
    def create_storage(storage_type: str, **kwargs) -> IStorage:
        """
        Create a storage implementation.
        
        Args:
            storage_type (str): Type of storage to create ('csv', 'sqlite')
            **kwargs: Additional arguments for the storage implementation
            
        Returns:
            IStorage: Storage implementation
            
        Raises:
            ValueError: If storage_type is not supported
        """
        if storage_type.lower() == 'csv':
            filepath = kwargs.get('filepath', 'accounts.csv')
            return CSVStorage(filepath)
        elif storage_type.lower() == 'sqlite':
            db_path = kwargs.get('db_path', 'banking.db')
            return SQLiteStorage(db_path)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

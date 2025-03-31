from typing import Optional
from basic_required_features.i_storage import IStorage
from basic_required_features.csv_storage import CSVStorage
from .database.sqlite_storage import SQLiteStorage


class StorageFactory:
    
    @staticmethod
    def create_storage(storage_type: str, **kwargs) -> IStorage:
        if storage_type == "csv":
            filepath = kwargs.get("filepath", "banking_data.csv")
            return CSVStorage(filepath)
        elif storage_type == "sqlite":
            db_path = kwargs.get("db_path", "banking.db")
            return SQLiteStorage(db_path)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")

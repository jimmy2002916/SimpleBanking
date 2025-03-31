# Database Storage

## Overview
The SimpleBanking system supports multiple storage backends, with CSV as the default and SQLite as an optional enterprise-ready alternative.

## Storage Options

### CSV Storage (Default)
CSV storage provides a simple, file-based storage solution that is easy to understand and inspect. Data is stored in `banking_data.csv` by default, or in a custom location if specified:

### SQLite Storage
SQLite storage provides better data integrity, concurrency support, and query capabilities. Data is stored in `banking.db` by default, or in a custom location if specified:

## Implementation Details

The storage system is implemented through a clean abstraction layer:

### Storage Interface
The `IStorage` interface is defined in `basic_required_features/storage_interface.py` and provides the contract that all storage implementations must follow:

```python
from abc import ABC, abstractmethod
from typing import Dict
from .account import BankAccount

class IStorage(ABC):
    """Interface for storage implementations."""
    
    @abstractmethod
    def save_accounts(self, accounts: Dict[str, BankAccount]) -> bool:
        """Save accounts to storage."""
        pass
    
    @abstractmethod
    def load_accounts(self) -> Dict[str, BankAccount]:
        """Load accounts from storage."""
        pass
```

This interface ensures that all storage implementations provide consistent save and load functionality, allowing the banking system to work with any storage backend without changing its code.

### Storage Factory
The `StorageFactory` class is defined in `advanced_features/storage/storage_factory.py` and provides a factory method for creating storage implementations:

```python
from basic_required_features.storage_interface import IStorage
from basic_required_features.csv_storage import CSVStorage
from .database.sqlite_storage import SQLiteStorage

class StorageFactory:
    """Factory for creating storage implementations."""
    
    @staticmethod
    def create_storage(storage_type: str, **kwargs) -> IStorage:
        """Create a storage implementation."""
        if storage_type == "csv":
            filepath = kwargs.get("filepath", "banking_data.csv")
            return CSVStorage(filepath)
        elif storage_type == "sqlite":
            db_path = kwargs.get("db_path", "banking.db")
            return SQLiteStorage(db_path)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")
```

This factory pattern makes it easy to create different storage implementations based on configuration, allowing the system to switch between storage backends at runtime.

### Storage Implementations

1. **CSVStorage** (`basic_required_features/csv_storage.py`):
   - Simple file-based storage using CSV format
   - Stores account data in a human-readable format
   - Suitable for small-scale deployments and development

2. **SQLiteStorage** (`advanced_features/storage/database/sqlite_storage.py`):
   - Database storage using SQLite
   - Provides better data integrity and query capabilities
   - Suitable for production deployments and larger datasets

## Automatic Saving
The system automatically saves the state before exiting, ensuring that no data is lost. You can also manually save at any time using option 6 from the main menu.
## Accessing the SQLite Database

To run SQL queries on the SQLite database:
1. Use the SQLite command-line tool to access the database:
   ```
   # Install SQLite if not already installed
   # macOS: brew install sqlite
   # Ubuntu: sudo apt install sqlite3
   
   # Open the database
   sqlite3 data/banking.db
   ```

2. Inside the SQLite shell, you can run queries:
   ```sql
   -- Show tables in the database
   .tables
   
   -- Show schema for accounts table
   .schema accounts
   
   -- Run queries on the data
   SELECT * FROM accounts;
   ```

3. Useful SQLite shell commands:
   ```
   .help     - Show help
   .tables   - List tables
   .schema   - Show schema
   .mode column  - Format output as columns
   .headers on   - Show column headers
   .quit     - Exit SQLite shell
   ```
## Example SQLite Queries
For advanced users who want to query the SQLite database directly:

```sql
-- List all accounts
SELECT * FROM accounts;

-- Get total balance across all accounts
SELECT SUM(balance) FROM accounts;

-- Find accounts with balance over 1000
SELECT * FROM accounts WHERE balance > 1000;
```

## Troubleshooting

If you encounter issues with database storage:
1. Verify the database file exists and is not corrupted
2. Check file permissions
3. Ensure SQLite is properly installed if using SQLite storage

"""
Tests for the SQLite storage implementation.
"""
import os
import unittest
from decimal import Decimal
import tempfile

from basic_required_features.account import BankAccount
from basic_required_features.banking_system import BankingSystem
from advanced_features.storage.database.sqlite_storage import SQLiteStorage
from advanced_features.storage.storage_factory import StorageFactory


class TestSQLiteStorage(unittest.TestCase):
    """Test cases for the SQLite storage implementation."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        # Create a SQLite storage instance
        self.storage = SQLiteStorage(self.temp_db.name)
        
        # Create some test accounts
        self.accounts = {
            "ACC1": BankAccount("ACC1", "Alice", Decimal("100.00")),
            "ACC2": BankAccount("ACC2", "Bob", Decimal("200.00")),
            "ACC3": BankAccount("ACC3", "Charlie", Decimal("300.00"))
        }
    
    def tearDown(self):
        """Clean up after tests."""
        # Close the storage connection
        self.storage.close()
        
        # Remove the temporary database file
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_save_and_load_accounts(self):
        """Test saving and loading accounts."""
        # Save accounts
        result = self.storage.save_accounts(self.accounts)
        self.assertTrue(result, "Failed to save accounts")
        
        # Load accounts
        loaded_accounts = self.storage.load_accounts()
        
        # Check if all accounts were loaded
        self.assertEqual(len(loaded_accounts), len(self.accounts), 
                         "Number of loaded accounts doesn't match")
        
        # Check if account data is correct
        for account_id, account in self.accounts.items():
            self.assertIn(account_id, loaded_accounts, 
                          f"Account {account_id} not found in loaded accounts")
            loaded_account = loaded_accounts[account_id]
            self.assertEqual(loaded_account.name, account.name, 
                             f"Name mismatch for account {account_id}")
            self.assertEqual(loaded_account.balance, account.balance, 
                             f"Balance mismatch for account {account_id}")
    
    def test_get_account(self):
        """Test getting a specific account."""
        # Save accounts
        self.storage.save_accounts(self.accounts)
        
        # Get a specific account
        account = self.storage.get_account("ACC2")
        
        # Check if account data is correct
        self.assertIsNotNone(account, "Account not found")
        self.assertEqual(account.account_id, "ACC2", "Account ID mismatch")
        self.assertEqual(account.name, "Bob", "Account name mismatch")
        self.assertEqual(account.balance, Decimal("200.00"), "Account balance mismatch")
        
        # Try to get a non-existent account
        account = self.storage.get_account("ACC999")
        self.assertIsNone(account, "Non-existent account should return None")
    
    def test_update_account(self):
        """Test updating an existing account."""
        # Save accounts
        self.storage.save_accounts(self.accounts)
        
        # Modify an account
        self.accounts["ACC2"].balance = Decimal("250.00")
        
        # Save again
        self.storage.save_accounts(self.accounts)
        
        # Get the updated account
        account = self.storage.get_account("ACC2")
        
        # Check if account data was updated
        self.assertEqual(account.balance, Decimal("250.00"), 
                         "Account balance was not updated")
    
    def test_delete_account(self):
        """Test deleting an account."""
        # Save accounts
        self.storage.save_accounts(self.accounts)
        
        # Delete an account
        result = self.storage.delete_account("ACC3")
        self.assertTrue(result, "Failed to delete account")
        
        # Try to get the deleted account
        account = self.storage.get_account("ACC3")
        self.assertIsNone(account, "Deleted account should not be found")
        
        # Load all accounts and check if the deleted account is gone
        loaded_accounts = self.storage.load_accounts()
        self.assertNotIn("ACC3", loaded_accounts, 
                         "Deleted account should not be in loaded accounts")
    
    def test_banking_system_with_sqlite(self):
        """Test using SQLite storage with the BankingSystem."""
        # Create a banking system with SQLite storage
        banking_system = BankingSystem(self.storage)
        
        # Create some accounts
        acc1 = banking_system.create_account("Dave", Decimal("150.00"))
        acc2 = banking_system.create_account("Eve", Decimal("250.00"))
        
        # Make some transactions
        banking_system.deposit(acc1, Decimal("50.00"))
        banking_system.withdraw(acc2, Decimal("30.00"))
        banking_system.transfer(acc1, acc2, Decimal("20.00"))
        
        # Save to storage
        banking_system.save_to_storage()
        
        # Create a new banking system with the same storage
        new_banking_system = BankingSystem(self.storage)
        
        # Check if accounts were loaded correctly
        self.assertEqual(len(new_banking_system.accounts), 2, 
                         "Number of loaded accounts doesn't match")
        
        # Check account balances
        self.assertEqual(new_banking_system.get_account(acc1).balance, 
                         Decimal("180.00"), "Account 1 balance mismatch")
        self.assertEqual(new_banking_system.get_account(acc2).balance, 
                         Decimal("240.00"), "Account 2 balance mismatch")
    
    def test_storage_factory(self):
        """Test creating storage using the StorageFactory."""
        # Create SQLite storage
        sqlite_storage = StorageFactory.create_storage("sqlite", db_path=self.temp_db.name)
        self.assertIsInstance(sqlite_storage, SQLiteStorage, 
                              "Factory should create SQLiteStorage instance")
        
        # Create CSV storage
        csv_storage = StorageFactory.create_storage("csv", filepath="test_accounts.csv")
        self.assertIsInstance(csv_storage, type(BankingSystem().storage), 
                              "Factory should create CSVStorage instance")
        
        # Clean up CSV file if created
        if os.path.exists("test_accounts.csv"):
            os.remove("test_accounts.csv")
        
        # Test invalid storage type
        with self.assertRaises(ValueError):
            StorageFactory.create_storage("invalid_type")


if __name__ == "__main__":
    unittest.main()

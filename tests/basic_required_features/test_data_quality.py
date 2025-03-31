import unittest
import os
import tempfile
import sqlite3
from decimal import Decimal

from facade import BankingSystem
from advanced_features.storage.storage_factory import StorageFactory


class TestDataQuality(unittest.TestCase):

    def setUp(self):
        self.csv_fd, self.csv_path = tempfile.mkstemp(suffix='.csv')
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        os.close(self.csv_fd)
        os.close(self.db_fd)
        
        self.csv_storage = StorageFactory.create_storage("csv", filepath=self.csv_path)
        self.sqlite_storage = StorageFactory.create_storage("sqlite", db_path=self.db_path)
        
        self.csv_banking = BankingSystem(self.csv_storage)
        self.sqlite_banking = BankingSystem(self.sqlite_storage)
    
    def tearDown(self):
        os.unlink(self.csv_path)
        os.unlink(self.db_path)
    
    def test_account_data_integrity(self):
        account1_id = self.csv_banking.create_account("Test User 1", Decimal("1000.00"))
        account2_id = self.csv_banking.create_account("Test User 2", Decimal("500.00"))
        
        self.csv_banking.deposit(account1_id, Decimal("200.00"))
        self.csv_banking.withdraw(account2_id, Decimal("100.00"))
        self.csv_banking.transfer(account1_id, account2_id, Decimal("300.00"))
        
        account1 = self.csv_banking.get_account(account1_id)
        account2 = self.csv_banking.get_account(account2_id)
        
        self.assertEqual(account1.balance, Decimal("900.00"))  # 1000 + 200 - 300
        self.assertEqual(account2.balance, Decimal("700.00"))  # 500 - 100 + 300
    
    def test_data_consistency_after_save_load(self):
        account1_id = self.csv_banking.create_account("Save Load User", Decimal("1500.00"))
        self.csv_banking.deposit(account1_id, Decimal("250.00"))
        
        self.csv_banking.save_to_storage()
        
        new_csv_storage = StorageFactory.create_storage("csv", filepath=self.csv_path)
        new_banking = BankingSystem(new_csv_storage)
        new_banking.load_from_storage()
        
        loaded_account = new_banking.get_account(account1_id)
        self.assertEqual(loaded_account.name, "Save Load User")
        self.assertEqual(loaded_account.balance, Decimal("1750.00"))
    
    def test_cross_storage_data_consistency(self):
        account1_id = self.csv_banking.create_account("Migration User", Decimal("2000.00"))
        self.csv_banking.deposit(account1_id, Decimal("500.00"))
        
        self.csv_banking.save_to_storage()
        
        accounts_data = self.csv_storage.load_accounts()
        
        self.sqlite_storage.save_accounts(accounts_data)
        
        sqlite_banking = BankingSystem(self.sqlite_storage)
        sqlite_banking.load_from_storage()
        
        sqlite_account = sqlite_banking.get_account(account1_id)
        self.assertEqual(sqlite_account.name, "Migration User")
        self.assertEqual(sqlite_account.balance, Decimal("2500.00"))
    
    def test_decimal_precision(self):
        account_id = self.csv_banking.create_account("Precision Test", Decimal("1000.50"))
        
        self.csv_banking.deposit(account_id, Decimal("99.95"))
        self.csv_banking.withdraw(account_id, Decimal("33.33"))
        
        account = self.csv_banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("1067.12"))
        
        self.csv_banking.deposit(account_id, Decimal("0.005"))
        account = self.csv_banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("1067.125"))
    
    def test_data_validation(self):
        with self.assertRaises(ValueError):
            self.csv_banking.create_account("", Decimal("100.00"), validate_only=True)  # Empty name

        with self.assertRaises(ValueError):
            self.csv_banking.create_account("Invalid Balance", Decimal("-50.00"), validate_only=True)  # Negative balance
        
        account_id = self.csv_banking.create_account("Validation Test", Decimal("100.00"))
        
        with self.assertRaises(ValueError):
            self.csv_banking.deposit(account_id, Decimal("-10.00"), validate_only=True)  # Negative deposit
        
        with self.assertRaises(ValueError):
            self.csv_banking.deposit(account_id, Decimal("0.00"), validate_only=True)  # Zero deposit
        
        with self.assertRaises(ValueError):
            self.csv_banking.withdraw(account_id, Decimal("-10.00"), validate_only=True)  # Negative withdrawal
        
        with self.assertRaises(ValueError):
            self.csv_banking.withdraw(account_id, Decimal("0.00"), validate_only=True)  # Zero withdrawal
        
        with self.assertRaises(ValueError):
            self.csv_banking.withdraw(account_id, Decimal("200.00"), validate_only=True)  # Exceeds balance
    
    def test_account_id_uniqueness(self):
        account_ids = set()
        for i in range(10):
            account_id = self.csv_banking.create_account(f"User {i}", Decimal("100.00"))
            # Verify this ID hasn't been seen before
            self.assertNotIn(account_id, account_ids)
            account_ids.add(account_id)
    
    def test_account_id_format(self):
        # Test that account IDs follow the correct format (ACC0001)
        account_id = self.csv_banking.create_account("Format Test", Decimal("100.00"))
        
        # Verify the format is correct (ACC followed by 4 digits)
        self.assertTrue(account_id.startswith("ACC"), f"Account ID {account_id} should start with 'ACC'")
        self.assertEqual(len(account_id), 7, f"Account ID {account_id} should be 7 characters long (ACC + 4 digits)")
        
        # Verify the numeric part is properly formatted with leading zeros
        numeric_part = account_id[3:]
        self.assertTrue(numeric_part.isdigit(), f"The part after 'ACC' should be numeric, got {numeric_part}")
        self.assertEqual(len(numeric_part), 4, f"The numeric part should be 4 digits, got {numeric_part}")
        
        # Create multiple accounts and verify they all follow the format
        for i in range(5):
            account_id = self.csv_banking.create_account(f"Format User {i}", Decimal("200.00"))
            self.assertTrue(account_id.startswith("ACC"), f"Account ID {account_id} should start with 'ACC'")
            self.assertEqual(len(account_id), 7, f"Account ID {account_id} should be 7 characters long")
            numeric_part = account_id[3:]
            self.assertTrue(numeric_part.isdigit(), f"The part after 'ACC' should be numeric, got {numeric_part}")
            self.assertEqual(len(numeric_part), 4, f"The numeric part should be 4 digits, got {numeric_part}")
    
    def test_sqlite_schema_integrity(self):
        self.sqlite_banking.create_account("Schema Test", Decimal("100.00"))
        self.sqlite_banking.save_to_storage()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(accounts)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        self.assertIn("account_id", columns)
        self.assertIn("name", columns)
        self.assertIn("balance", columns)
        
        cursor.execute("PRAGMA table_info(metadata)")
        metadata_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        self.assertIn("key", metadata_columns)
        self.assertIn("value", metadata_columns)
        
        conn.close()


if __name__ == "__main__":
    unittest.main()

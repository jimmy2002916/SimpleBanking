import os
import unittest
from decimal import Decimal
import tempfile

from basic_required_features.account import BankAccount
from basic_required_features.banking_system import BankingSystem
from advanced_features.storage.database.sqlite_storage import SQLiteStorage
from advanced_features.storage.storage_factory import StorageFactory


class TestSQLiteStorage(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        self.storage = SQLiteStorage(self.temp_db.name)
        
        self.accounts = {
            "ACC1": BankAccount("ACC1", "Alice", Decimal("100.00")),
            "ACC2": BankAccount("ACC2", "Bob", Decimal("200.00")),
            "ACC3": BankAccount("ACC3", "Charlie", Decimal("300.00"))
        }
    
    def tearDown(self):
        self.storage.close()
        
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_save_and_load_accounts(self):
        result = self.storage.save_accounts(self.accounts)
        self.assertTrue(result, "Failed to save accounts")
        
        loaded_accounts = self.storage.load_accounts()
        
        self.assertEqual(len(loaded_accounts), len(self.accounts),
                         "Number of loaded accounts doesn't match")
        
        for account_id, account in self.accounts.items():
            self.assertIn(account_id, loaded_accounts, 
                          f"Account {account_id} not found in loaded accounts")
            loaded_account = loaded_accounts[account_id]
            self.assertEqual(loaded_account.name, account.name, 
                             f"Name mismatch for account {account_id}")
            self.assertEqual(loaded_account.balance, account.balance, 
                             f"Balance mismatch for account {account_id}")
    
    def test_get_account(self):
        self.storage.save_accounts(self.accounts)
        
        account = self.storage.get_account("ACC2")
        
        self.assertIsNotNone(account, "Account not found")
        self.assertEqual(account.account_id, "ACC2", "Account ID mismatch")
        self.assertEqual(account.name, "Bob", "Account name mismatch")
        self.assertEqual(account.balance, Decimal("200.00"), "Account balance mismatch")
        
        account = self.storage.get_account("ACC999")
        self.assertIsNone(account, "Non-existent account should return None")
    
    def test_update_account(self):
        self.storage.save_accounts(self.accounts)

        self.accounts["ACC2"].balance = Decimal("250.00")
        
        self.storage.save_accounts(self.accounts)
        
        account = self.storage.get_account("ACC2")
        
        self.assertEqual(account.balance, Decimal("250.00"),
                         "Account balance was not updated")
    
    def test_delete_account(self):
        self.storage.save_accounts(self.accounts)
        
        result = self.storage.delete_account("ACC3")
        self.assertTrue(result, "Failed to delete account")
        
        account = self.storage.get_account("ACC3")
        self.assertIsNone(account, "Deleted account should not be found")
        
        loaded_accounts = self.storage.load_accounts()
        self.assertNotIn("ACC3", loaded_accounts, 
                         "Deleted account should not be in loaded accounts")
    
    def test_banking_system_with_sqlite(self):
        banking_system = BankingSystem(self.storage)
        
        acc1 = banking_system.create_account("Dave", Decimal("150.00"))
        acc2 = banking_system.create_account("Eve", Decimal("250.00"))
        
        banking_system.deposit(acc1, Decimal("50.00"))
        banking_system.withdraw(acc2, Decimal("30.00"))
        banking_system.transfer(acc1, acc2, Decimal("20.00"))
        
        banking_system.save_to_storage()
        
        new_banking_system = BankingSystem(self.storage)
        
        self.assertEqual(len(new_banking_system.accounts), 2,
                         "Number of loaded accounts doesn't match")
        
        self.assertEqual(new_banking_system.get_account(acc1).balance,
                         Decimal("180.00"), "Account 1 balance mismatch")
        self.assertEqual(new_banking_system.get_account(acc2).balance, 
                         Decimal("240.00"), "Account 2 balance mismatch")
    
    def test_storage_factory(self):
        sqlite_storage = StorageFactory.create_storage("sqlite", db_path=self.temp_db.name)
        self.assertIsInstance(sqlite_storage, SQLiteStorage, 
                              "Factory should create SQLiteStorage instance")
        
        csv_storage = StorageFactory.create_storage("csv", filepath="test_accounts.csv")
        self.assertIsInstance(csv_storage, type(BankingSystem().storage), 
                              "Factory should create CSVStorage instance")
        
        if os.path.exists("test_accounts.csv"):
            os.remove("test_accounts.csv")
        
        with self.assertRaises(ValueError):
            StorageFactory.create_storage("invalid_type")


if __name__ == "__main__":
    unittest.main()

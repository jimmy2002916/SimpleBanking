import unittest
import os
import tempfile
from decimal import Decimal

# Following TDD approach - write tests first, then implement
# We'll define what we expect from our banking system

class TestBankingSystem(unittest.TestCase):

    # Feature 1: Users can create a new bank account with a name and starting balance
    def test_create_account(self):
        from facade import BankAccount, BankingSystem
        
        banking = BankingSystem()
        
        account_id = banking.create_account("John Doe", Decimal("1000.00"))
        
        account = banking.get_account(account_id)
        self.assertEqual(account.name, "John Doe")
        self.assertEqual(account.balance, Decimal("1000.00"))
        
        with self.assertRaises(ValueError):
            banking.create_account("Invalid User", Decimal("-100.00"), validate_only=True)
    
    # Feature 2: Users can deposit money to their accounts
    def test_deposit(self):
        from facade import BankAccount, BankingSystem
        
        banking = BankingSystem()
        account_id = banking.create_account("John Doe", Decimal("1000.00"))
        
        self.assertTrue(banking.deposit(account_id, Decimal("500.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("1500.00"))
        
        self.assertFalse(banking.deposit(account_id, Decimal("-100.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("1500.00"))  # Balance should remain unchanged
        
        self.assertFalse(banking.deposit(account_id, Decimal("0.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("1500.00"))  # Balance should remain unchanged
        
        self.assertFalse(banking.deposit("INVALID_ID", Decimal("500.00")))
    
    # Feature 3: Users can withdraw money from their accounts
    def test_withdraw(self):
        from facade import BankAccount, BankingSystem
        
        banking = BankingSystem()
        account_id = banking.create_account("John Doe", Decimal("1000.00"))
        
        self.assertTrue(banking.withdraw(account_id, Decimal("300.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("700.00"))
        
        self.assertFalse(banking.withdraw(account_id, Decimal("-100.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("700.00"))  # Balance should remain unchanged
        
        self.assertFalse(banking.withdraw(account_id, Decimal("0.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("700.00"))  # Balance should remain unchanged
        
        self.assertFalse(banking.withdraw("INVALID_ID", Decimal("100.00")))
    
    # Feature 4: Users are not allowed to overdraft their accounts
    def test_overdraft_protection(self):
        from facade import BankAccount, BankingSystem
        banking = BankingSystem()
        account_id = banking.create_account("John Doe", Decimal("500.00"))
        
        self.assertFalse(banking.withdraw(account_id, Decimal("600.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("500.00"))  # Balance should remain unchanged
        
        self.assertTrue(banking.withdraw(account_id, Decimal("500.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("0.00"))
        
        self.assertFalse(banking.withdraw(account_id, Decimal("0.01")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("0.00"))  # Balance should remain unchanged
    
    # Feature 5: Users can transfer money to other accounts in the same banking system
    def test_transfer(self):
        from facade import BankAccount, BankingSystem
        
        banking = BankingSystem()
        account1_id = banking.create_account("John Doe", Decimal("1000.00"))
        account2_id = banking.create_account("Jane Smith", Decimal("500.00"))
        
        self.assertTrue(banking.transfer(account1_id, account2_id, Decimal("300.00")))
        
        account1 = banking.get_account(account1_id)
        account2 = banking.get_account(account2_id)
        self.assertEqual(account1.balance, Decimal("700.00"))
        self.assertEqual(account2.balance, Decimal("800.00"))
        
        self.assertFalse(banking.transfer(account1_id, account2_id, Decimal("800.00")))
    
    # Feature 6: Save and load system state to CSV
    def test_save_load_csv(self):
        from facade import BankAccount, BankingSystem
        
        banking = BankingSystem()
        account1_id = banking.create_account("John Doe", Decimal("1000.00"))
        account2_id = banking.create_account("Jane Smith", Decimal("500.00"))
        
        banking.deposit(account1_id, Decimal("200.00"))
        banking.withdraw(account2_id, Decimal("100.00"))
        banking.transfer(account1_id, account2_id, Decimal("300.00"))
        
        test_file = "test_banking_data.csv"
        self.assertTrue(banking.save_to_csv(test_file))
        
        new_banking = BankingSystem()
        self.assertTrue(new_banking.load_from_csv(test_file))
        
        loaded_account1 = new_banking.get_account(account1_id)
        loaded_account2 = new_banking.get_account(account2_id)
        
        self.assertEqual(loaded_account1.name, "John Doe")
        self.assertEqual(loaded_account1.balance, Decimal("900.00"))  # 1000 + 200 - 300
        self.assertEqual(loaded_account2.name, "Jane Smith")
        self.assertEqual(loaded_account2.balance, Decimal("700.00"))  # 500 - 100 + 300
        
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    unittest.main()

import unittest
import os
from decimal import Decimal

# Following TDD approach - write tests first, then implement
# We'll define what we expect from our banking system

class TestBankingSystem(unittest.TestCase):
    """Test cases for the Simple Banking System."""
    
    # Feature: Users can create a new bank account with a name and starting balance
    def test_create_account(self):
        """Test creating a new bank account."""
        from banking import BankAccount, BankingSystem
        
        # Create a banking system
        banking = BankingSystem()
        
        # Create a new account
        account_id = banking.create_account("John Doe", Decimal("1000.00"))
        
        # Verify the account was created with correct values
        account = banking.get_account(account_id)
        self.assertEqual(account.name, "John Doe")
        self.assertEqual(account.balance, Decimal("1000.00"))
        
        # Test creating an account with negative balance (should raise ValueError)
        with self.assertRaises(ValueError):
            banking.create_account("Invalid User", Decimal("-100.00"))
    
    # Features: 
    # - Users can deposit money to their accounts
    # - Users can withdraw money from their accounts
    # - Users are not allowed to overdraft their accounts
    def test_deposit_withdraw(self):
        """Test depositing and withdrawing money."""
        from banking import BankAccount, BankingSystem
        
        # Create a banking system with an account
        banking = BankingSystem()
        account_id = banking.create_account("John Doe", Decimal("1000.00"))
        
        # Test valid deposit
        self.assertTrue(banking.deposit(account_id, Decimal("500.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("1500.00"))
        
        # Test invalid deposit (negative amount)
        self.assertFalse(banking.deposit(account_id, Decimal("-100.00")))
        
        # Test valid withdrawal
        self.assertTrue(banking.withdraw(account_id, Decimal("300.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("1200.00"))
        
        # Test overdraft protection (withdrawal amount > balance)
        self.assertFalse(banking.withdraw(account_id, Decimal("2000.00")))
        account = banking.get_account(account_id)
        self.assertEqual(account.balance, Decimal("1200.00"))
    
    # Feature: Users can transfer money to other accounts in the same banking system
    def test_transfer(self):
        """Test transferring money between accounts."""
        from banking import BankAccount, BankingSystem
        
        # Create a banking system with two accounts
        banking = BankingSystem()
        account1_id = banking.create_account("John Doe", Decimal("1000.00"))
        account2_id = banking.create_account("Jane Smith", Decimal("500.00"))
        
        # Test valid transfer
        self.assertTrue(banking.transfer(account1_id, account2_id, Decimal("300.00")))
        
        # Verify both balances were updated correctly
        account1 = banking.get_account(account1_id)
        account2 = banking.get_account(account2_id)
        self.assertEqual(account1.balance, Decimal("700.00"))
        self.assertEqual(account2.balance, Decimal("800.00"))
        
        # Test transfer with insufficient funds (overdraft protection)
        self.assertFalse(banking.transfer(account1_id, account2_id, Decimal("800.00")))
    
    # Feature: Save and load system state to CSV
    def test_save_load_csv(self):
        """Test saving and loading the system state to/from CSV."""
        from banking import BankAccount, BankingSystem
        
        # Create a banking system with accounts and transactions
        banking = BankingSystem()
        account1_id = banking.create_account("John Doe", Decimal("1000.00"))
        account2_id = banking.create_account("Jane Smith", Decimal("500.00"))
        
        # Perform some transactions
        banking.deposit(account1_id, Decimal("200.00"))
        banking.withdraw(account2_id, Decimal("100.00"))
        banking.transfer(account1_id, account2_id, Decimal("300.00"))
        
        # Save the state to a test CSV file
        test_file = "test_banking_data.csv"
        self.assertTrue(banking.save_to_csv(test_file))
        
        # Create a new banking system and load the state
        new_banking = BankingSystem()
        self.assertTrue(new_banking.load_from_csv(test_file))
        
        # Verify the accounts were loaded correctly
        loaded_account1 = new_banking.get_account(account1_id)
        loaded_account2 = new_banking.get_account(account2_id)
        
        self.assertEqual(loaded_account1.name, "John Doe")
        self.assertEqual(loaded_account1.balance, Decimal("900.00"))  # 1000 + 200 - 300
        self.assertEqual(loaded_account2.name, "Jane Smith")
        self.assertEqual(loaded_account2.balance, Decimal("700.00"))  # 500 - 100 + 300
        
        # Clean up the test file
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    unittest.main()

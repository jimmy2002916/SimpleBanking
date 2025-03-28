import unittest
from decimal import Decimal

# Implement the TDD approach - write tests first, then implement the code to make them pass
# We haven't created the BankAccount class yet, but we'll define what we expect from it

class TestBankAccount(unittest.TestCase):

    def test_account_creation(self):
        """Test that we can create an account with the correct initial values."""
        # This will fail until we implement the BankAccount class
        from bank_account import BankAccount
        
        # Create a test account
        account = BankAccount("12345", "John Doe", Decimal("100.00"))
        
        # Check that the properties are set correctly
        self.assertEqual(account.account_id, "12345")
        self.assertEqual(account.name, "John Doe")
        self.assertEqual(account.balance, Decimal("100.00"))
    
    def test_deposit(self):
        """Test that we can deposit money into an account."""
        from bank_account import BankAccount
        
        # Create a test account
        account = BankAccount("12345", "John Doe", Decimal("100.00"))
        
        # Test a valid deposit
        result = account.deposit(Decimal("50.00"))
        self.assertTrue(result)
        self.assertEqual(account.balance, Decimal("150.00"))
        
        # Test an invalid deposit (negative amount)
        result = account.deposit(Decimal("-20.00"))
        self.assertFalse(result)
        self.assertEqual(account.balance, Decimal("150.00"))  # Balance should not change
        
        # Test a zero deposit
        result = account.deposit(Decimal("0.00"))
        self.assertFalse(result)
        self.assertEqual(account.balance, Decimal("150.00"))  # Balance should not change
    
    def test_withdraw(self):
        """Test that we can withdraw money from an account."""
        from bank_account import BankAccount
        
        # Create a test account
        account = BankAccount("12345", "John Doe", Decimal("100.00"))
        
        # Test a valid withdrawal
        result = account.withdraw(Decimal("50.00"))
        self.assertTrue(result)
        self.assertEqual(account.balance, Decimal("50.00"))
        
        # Test an invalid withdrawal (negative amount)
        result = account.withdraw(Decimal("-20.00"))
        self.assertFalse(result)
        self.assertEqual(account.balance, Decimal("50.00"))  # Balance should not change
        
        # Test a zero withdrawal
        result = account.withdraw(Decimal("0.00"))
        self.assertFalse(result)
        self.assertEqual(account.balance, Decimal("50.00"))  # Balance should not change
        
        # Test overdraft protection
        result = account.withdraw(Decimal("100.00"))
        self.assertFalse(result)
        self.assertEqual(account.balance, Decimal("50.00"))  # Balance should not change


if __name__ == "__main__":
    unittest.main()

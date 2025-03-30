import unittest
import os
from decimal import Decimal
import json
from datetime import datetime

class TestTransactionLogging(unittest.TestCase):
    """Test cases for the transaction logging feature."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Import here to avoid circular imports
        from banking import BankingSystem
        from advanced_features.logging import TransactionLogger
        
        # Create a banking system
        self.banking = BankingSystem()
        
        # Create test accounts
        self.account1_id = self.banking.create_account("John Doe", Decimal("1000.00"))
        self.account2_id = self.banking.create_account("Jane Smith", Decimal("500.00"))
        
        # Create a transaction logger and attach AFTER creating accounts
        # to avoid logging account creation
        self.log_file = "test_transactions.log"
        self.logger = TransactionLogger(self.log_file)
        self.banking.attach_logger(self.logger)
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove test log file if it exists
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def test_deposit_logging(self):
        """Test that deposits are properly logged."""
        # Perform a deposit
        amount = Decimal("200.00")
        self.banking.deposit(self.account1_id, amount)
        
        # Check log file
        with open(self.log_file, 'r') as f:
            logs = f.readlines()
            
        # Verify log entry
        latest_log = json.loads(logs[-1])
        self.assertEqual(latest_log["action"], "deposit")
        self.assertEqual(latest_log["account_id"], self.account1_id)
        self.assertEqual(Decimal(latest_log["amount"]), amount)
        self.assertEqual(latest_log["status"], "success")
        self.assertTrue("timestamp" in latest_log)
    
    def test_withdraw_logging(self):
        """Test that withdrawals are properly logged."""
        # Perform a withdrawal
        amount = Decimal("200.00")
        self.banking.withdraw(self.account1_id, amount)
        
        # Check log file
        with open(self.log_file, 'r') as f:
            logs = f.readlines()
            
        # Verify log entry
        latest_log = json.loads(logs[-1])
        self.assertEqual(latest_log["action"], "withdraw")
        self.assertEqual(latest_log["account_id"], self.account1_id)
        self.assertEqual(Decimal(latest_log["amount"]), amount)
        self.assertEqual(latest_log["status"], "success")
        self.assertTrue("timestamp" in latest_log)
    
    def test_transfer_logging(self):
        """Test that transfers are properly logged."""
        # Perform a transfer
        amount = Decimal("200.00")
        self.banking.transfer(self.account1_id, self.account2_id, amount)
        
        # Check log file
        with open(self.log_file, 'r') as f:
            logs = f.readlines()
            
        # Verify log entry
        latest_log = json.loads(logs[-1])
        self.assertEqual(latest_log["action"], "transfer")
        self.assertEqual(latest_log["from_account_id"], self.account1_id)
        self.assertEqual(latest_log["to_account_id"], self.account2_id)
        self.assertEqual(Decimal(latest_log["amount"]), amount)
        self.assertEqual(latest_log["status"], "success")
        self.assertTrue("timestamp" in latest_log)
    
    def test_failed_operation_logging(self):
        """Test that failed operations are properly logged."""
        # Attempt a withdrawal that will fail (overdraft)
        amount = Decimal("2000.00")
        self.banking.withdraw(self.account1_id, amount)
        
        # Check log file
        with open(self.log_file, 'r') as f:
            logs = f.readlines()
            
        # Verify log entry
        latest_log = json.loads(logs[-1])
        self.assertEqual(latest_log["action"], "withdraw")
        self.assertEqual(latest_log["account_id"], self.account1_id)
        self.assertEqual(Decimal(latest_log["amount"]), amount)
        self.assertEqual(latest_log["status"], "failed")
        self.assertTrue("timestamp" in latest_log)
        self.assertTrue("reason" in latest_log)
    
    def test_query_logs(self):
        """Test querying transaction logs."""
        # Perform various operations
        self.banking.deposit(self.account1_id, Decimal("100.00"))
        self.banking.withdraw(self.account1_id, Decimal("50.00"))
        self.banking.transfer(self.account1_id, self.account2_id, Decimal("25.00"))
        
        # Query logs for account1
        account1_logs = self.logger.get_logs_by_account(self.account1_id)
        
        # Verify we got 3 logs for account1
        self.assertEqual(len(account1_logs), 3)
        
        # Query logs by action type
        deposit_logs = self.logger.get_logs_by_action("deposit")
        
        # Verify we got 1 deposit log
        self.assertEqual(len(deposit_logs), 1)
        self.assertEqual(deposit_logs[0]["action"], "deposit")


if __name__ == "__main__":
    unittest.main()

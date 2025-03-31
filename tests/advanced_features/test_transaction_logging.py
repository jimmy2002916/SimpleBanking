import unittest
import os
import tempfile
import json
from decimal import Decimal
from datetime import datetime

class TestTransactionLogging(unittest.TestCase):

    def setUp(self):
        from facade import BankingSystem
        from advanced_features.logging import TransactionLogger
        
        self.banking = BankingSystem()
        
        self.account1_id = self.banking.create_account("John Doe", Decimal("1000.00"))
        self.account2_id = self.banking.create_account("Jane Smith", Decimal("500.00"))
        
        self.log_file = "test_transactions.log"
        self.logger = TransactionLogger(self.log_file)
        self.banking.attach_logger(self.logger)
    
    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def test_deposit_logging(self):
        amount = Decimal("200.00")
        self.banking.deposit(self.account1_id, amount)
        
        with open(self.log_file, 'r') as f:
            logs = f.readlines()
            
        latest_log = json.loads(logs[-1])
        self.assertEqual(latest_log["action"], "deposit")
        self.assertEqual(latest_log["account_id"], self.account1_id)
        self.assertEqual(Decimal(latest_log["amount"]), amount)
        self.assertEqual(latest_log["status"], "success")
        self.assertTrue("timestamp" in latest_log)
    
    def test_withdraw_logging(self):
        amount = Decimal("200.00")
        self.banking.withdraw(self.account1_id, amount)
        
        with open(self.log_file, 'r') as f:
            logs = f.readlines()
            
        latest_log = json.loads(logs[-1])
        self.assertEqual(latest_log["action"], "withdraw")
        self.assertEqual(latest_log["account_id"], self.account1_id)
        self.assertEqual(Decimal(latest_log["amount"]), amount)
        self.assertEqual(latest_log["status"], "success")
        self.assertTrue("timestamp" in latest_log)
    
    def test_transfer_logging(self):
        amount = Decimal("200.00")
        self.banking.transfer(self.account1_id, self.account2_id, amount)
        
        with open(self.log_file, 'r') as f:
            logs = f.readlines()
            
        latest_log = json.loads(logs[-1])
        self.assertEqual(latest_log["action"], "transfer")
        self.assertEqual(latest_log["from_account_id"], self.account1_id)
        self.assertEqual(latest_log["to_account_id"], self.account2_id)
        self.assertEqual(Decimal(latest_log["amount"]), amount)
        self.assertEqual(latest_log["status"], "success")
        self.assertTrue("timestamp" in latest_log)
    
    def test_failed_operation_logging(self):
        amount = Decimal("2000.00")
        self.banking.withdraw(self.account1_id, amount)
        
        with open(self.log_file, 'r') as f:
            logs = f.readlines()
            
        latest_log = json.loads(logs[-1])
        self.assertEqual(latest_log["action"], "withdraw")
        self.assertEqual(latest_log["account_id"], self.account1_id)
        self.assertEqual(Decimal(latest_log["amount"]), amount)
        self.assertEqual(latest_log["status"], "failed")
        self.assertTrue("timestamp" in latest_log)
        self.assertTrue("reason" in latest_log)
    
    def test_query_logs(self):
        self.banking.deposit(self.account1_id, Decimal("100.00"))
        self.banking.withdraw(self.account1_id, Decimal("50.00"))
        self.banking.transfer(self.account1_id, self.account2_id, Decimal("25.00"))
        
        account1_logs = self.logger.get_logs_by_account(self.account1_id)
        
        self.assertEqual(len(account1_logs), 3)
        
        deposit_logs = self.logger.get_logs_by_action("deposit")
        
        self.assertEqual(len(deposit_logs), 1)
        self.assertEqual(deposit_logs[0]["action"], "deposit")


if __name__ == "__main__":
    unittest.main()

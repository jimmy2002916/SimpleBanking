import unittest
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from decimal import Decimal
from unittest.mock import MagicMock, patch
import os
import logging
import tempfile
from datetime import datetime

from basic_required_features.account import BankAccount
from basic_required_features.banking_system import BankingSystem
from advanced_features.transaction_management import TransactionManager


class TestTransactionAtomicity(unittest.TestCase):

    def setUp(self):
        self.banking = BankingSystem()
        self.acc1 = self.banking.create_account("Alice", Decimal("1000.00"))
        self.acc2 = self.banking.create_account("Bob", Decimal("500.00"))
    
    def test_successful_transfer(self):
        result = self.banking.transfer(self.acc1, self.acc2, Decimal("200.00"))
        
        self.assertTrue(result)
        
        self.assertEqual(self.banking.get_account(self.acc1).balance, Decimal("800.00"))
        self.assertEqual(self.banking.get_account(self.acc2).balance, Decimal("700.00"))
    
    def test_failed_transfer_no_partial_updates(self):
        result = self.banking.transfer(self.acc1, self.acc2, Decimal("1500.00"))
        
        self.assertFalse(result)
        
        self.assertEqual(self.banking.get_account(self.acc1).balance, Decimal("1000.00"))
        self.assertEqual(self.banking.get_account(self.acc2).balance, Decimal("500.00"))
    
    def test_exception_during_transfer(self):
        banking = BankingSystem()
        acc1 = banking.create_account("Alice", Decimal("1000.00"))
        acc2 = banking.create_account("Bob", Decimal("500.00"))
        
        def failing_operation(accounts):
            accounts[acc1].balance -= Decimal("200.00")
            accounts[acc2].balance += Decimal("200.00")
            raise ValueError("Simulated error during transfer")
        
        try:
            with self.assertRaises(ValueError):
                banking.transaction_manager.execute_atomic(
                    [acc1, acc2],
                    banking.accounts,
                    failing_operation
                )
            
            self.assertEqual(banking.get_account(acc1).balance, Decimal("1000.00"))
            self.assertEqual(banking.get_account(acc2).balance, Decimal("500.00"))
        except AssertionError:
            self.fail("Exception was not raised or caught properly")
    
    def test_withdraw_exact_balance(self):
        acc = self.banking.create_account("ExactBalance", Decimal("300.00"))
        account = self.banking.get_account(acc)
        
        result = self.banking.withdraw(acc, Decimal("300.00"))
        
        self.assertTrue(result)
        
        self.assertEqual(account.balance, Decimal("0.00"))


class TestEdgeCases(unittest.TestCase):

    def setUp(self):
        self.banking = BankingSystem()
    
    def test_create_account_negative_balance(self):
        with self.assertRaises(ValueError):
            self.banking.create_account("NegativeBalance", Decimal("-100.00"), validate_only=True)
    
    def test_deposit_negative_amount(self):
        acc = self.banking.create_account("TestUser", Decimal("500.00"))
        
        result = self.banking.deposit(acc, Decimal("-50.00"))
        
        self.assertFalse(result)
        
        self.assertEqual(self.banking.get_account(acc).balance, Decimal("500.00"))
    
    def test_withdraw_negative_amount(self):
        acc = self.banking.create_account("TestUser", Decimal("500.00"))

        result = self.banking.withdraw(acc, Decimal("-50.00"))

        self.assertFalse(result)

        self.assertEqual(self.banking.get_account(acc).balance, Decimal("500.00"))
    
    def test_transfer_negative_amount(self):
        acc1 = self.banking.create_account("Alice", Decimal("1000.00"))
        acc2 = self.banking.create_account("Bob", Decimal("500.00"))
        
        result = self.banking.transfer(acc1, acc2, Decimal("-50.00"))
        
        self.assertFalse(result)
        
        self.assertEqual(self.banking.get_account(acc1).balance, Decimal("1000.00"))
        self.assertEqual(self.banking.get_account(acc2).balance, Decimal("500.00"))
    
    def test_transfer_to_nonexistent_account(self):
        acc1 = self.banking.create_account("Alice", Decimal("1000.00"))
        
        result = self.banking.transfer(acc1, "NONEXISTENT", Decimal("50.00"))
        
        self.assertFalse(result)
        
        self.assertEqual(self.banking.get_account(acc1).balance, Decimal("1000.00"))
    
    def test_transfer_from_nonexistent_account(self):
        acc2 = self.banking.create_account("Bob", Decimal("500.00"))
        
        result = self.banking.transfer("NONEXISTENT", acc2, Decimal("50.00"))
        
        self.assertFalse(result)
        
        self.assertEqual(self.banking.get_account(acc2).balance, Decimal("500.00"))


class TestConcurrencySupport(unittest.TestCase):
    def setUp(self):
        self.banking = BankingSystem()
        self.acc1 = self.banking.create_account("Alice", Decimal("1000.00"))
        self.acc2 = self.banking.create_account("Bob", Decimal("1000.00"))
    
    def test_concurrent_deposits(self):
        num_deposits = 100
        deposit_amount = Decimal("10.00")
        expected_balance = Decimal("1000.00") + (num_deposits * deposit_amount)
        
        def perform_deposit():
            self.banking.deposit(self.acc1, deposit_amount)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_deposit) for _ in range(num_deposits)]
            for future in futures:
                future.result()
        
        self.assertEqual(self.banking.get_account(self.acc1).balance, expected_balance)
    
    def test_concurrent_withdrawals(self):
        num_withdrawals = 50
        withdrawal_amount = Decimal("10.00")
        initial_balance = Decimal("1000.00")
        expected_balance = initial_balance - (num_withdrawals * withdrawal_amount)
        
        def perform_withdrawal():
            self.banking.withdraw(self.acc1, withdrawal_amount)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_withdrawal) for _ in range(num_withdrawals)]
            for future in futures:
                future.result()
        
        self.assertEqual(self.banking.get_account(self.acc1).balance, expected_balance)
    
    def test_concurrent_transfers(self):
        num_transfers = 50
        transfer_amount = Decimal("10.00")
        
        def transfer_1_to_2():
            self.banking.transfer(self.acc1, self.acc2, transfer_amount)
        
        def transfer_2_to_1():
            self.banking.transfer(self.acc2, self.acc1, transfer_amount)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures1 = [executor.submit(transfer_1_to_2) for _ in range(num_transfers)]
            futures2 = [executor.submit(transfer_2_to_1) for _ in range(num_transfers)]
            for future in futures1 + futures2:
                future.result()

        self.assertEqual(self.banking.get_account(self.acc1).balance, Decimal("1000.00"))
        self.assertEqual(self.banking.get_account(self.acc2).balance, Decimal("1000.00"))
    
    def test_deadlock_prevention(self):
        acc3 = self.banking.create_account("Charlie", Decimal("1000.00"))
        acc4 = self.banking.create_account("Dave", Decimal("1000.00"))
        
        deadlock_detected = threading.Event()
        
        def perform_transfer_with_timeout(from_acc, to_acc, amount, timeout=2):
            start_time = time.time()
            result = self.banking.transfer(from_acc, to_acc, amount)
            elapsed_time = time.time() - start_time
            
            if elapsed_time > timeout:
                deadlock_detected.set()
            
            return result
        
        thread1 = threading.Thread(
            target=perform_transfer_with_timeout,
            args=(self.acc1, self.acc2, Decimal("100.00"))
        )
        thread2 = threading.Thread(
            target=perform_transfer_with_timeout,
            args=(self.acc2, self.acc1, Decimal("50.00"))
        )
        thread3 = threading.Thread(
            target=perform_transfer_with_timeout,
            args=(acc3, acc4, Decimal("75.00"))
        )
        thread4 = threading.Thread(
            target=perform_transfer_with_timeout,
            args=(acc4, acc3, Decimal("25.00"))
        )
        
        # Start all threads
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        
        # Wait for all threads to complete
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        
        self.assertFalse(deadlock_detected.is_set(), "Potential deadlock detected")
        
        # Check that all transfers were completed
        # The net change should be:
        # acc1: -100 + 50 = -50
        # acc2: +100 - 50 = +50
        # acc3: -75 + 25 = -50
        # acc4: +75 - 25 = +50
        self.assertEqual(self.banking.get_account(self.acc1).balance, Decimal("950.00"))
        self.assertEqual(self.banking.get_account(self.acc2).balance, Decimal("1050.00"))
        self.assertEqual(self.banking.get_account(acc3).balance, Decimal("950.00"))
        self.assertEqual(self.banking.get_account(acc4).balance, Decimal("1050.00"))
    
    def test_concurrent_mixed_operations(self):
        acc3 = self.banking.create_account("Charlie", Decimal("1000.00"))
        
        successful_ops = {"deposits": 0, "withdrawals": 0, "transfers": 0}
        ops_lock = threading.Lock()
        
        deposit_amount = Decimal("20.00")
        withdrawal_amount = Decimal("15.00")
        transfer_amount = Decimal("25.00")
        
        def perform_deposit():
            result = self.banking.deposit(self.acc1, deposit_amount)
            if result:
                with ops_lock:
                    successful_ops["deposits"] += 1
        
        def perform_withdrawal():
            result = self.banking.withdraw(self.acc2, withdrawal_amount)
            if result:
                with ops_lock:
                    successful_ops["withdrawals"] += 1
        
        def perform_transfer():
            result = self.banking.transfer(self.acc1, acc3, transfer_amount)
            if result:
                with ops_lock:
                    successful_ops["transfers"] += 1
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            deposit_futures = [executor.submit(perform_deposit) for _ in range(30)]
            withdrawal_futures = [executor.submit(perform_withdrawal) for _ in range(20)]
            transfer_futures = [executor.submit(perform_transfer) for _ in range(10)]
            
            for future in deposit_futures + withdrawal_futures + transfer_futures:
                future.result()
        
        acc1_expected = Decimal("1000.00") + \
                        (successful_ops["deposits"] * deposit_amount) - \
                        (successful_ops["transfers"] * transfer_amount)
        acc2_expected = Decimal("1000.00") - \
                        (successful_ops["withdrawals"] * withdrawal_amount)
        acc3_expected = Decimal("1000.00") + \
                        (successful_ops["transfers"] * transfer_amount)
        
        self.assertEqual(self.banking.get_account(self.acc1).balance, acc1_expected)
        self.assertEqual(self.banking.get_account(self.acc2).balance, acc2_expected)
        self.assertEqual(self.banking.get_account(acc3).balance, acc3_expected)


class TestAuditLogging(unittest.TestCase):

    def setUp(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_result_dir = os.path.join(
            os.path.dirname(__file__),
            "test_result", timestamp
        )
        os.makedirs(self.test_result_dir, exist_ok=True)
        
        self.audit_log_file = os.path.join(self.test_result_dir, "audit.log")
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        self.file_handler = logging.FileHandler(self.audit_log_file)
        self.file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        
        root_logger.addHandler(self.file_handler)
        
        self.banking = BankingSystem()
        
        logging.info(f"Setting up test in {self.__class__.__name__}")
    
    def test_transaction_logging(self):
        acc1 = self.banking.create_account("Alice", Decimal("1000.00"))
        acc2 = self.banking.create_account("Bob", Decimal("500.00"))
        
        logging.info(f"Created account {acc1} with balance 1000.00")
        logging.info(f"Created account {acc2} with balance 500.00")
        
        self.banking.deposit(acc1, Decimal("200.00"))
        logging.info(f"Deposited 200.00 to account {acc1}")
        
        self.banking.withdraw(acc2, Decimal("100.00"))
        logging.info(f"Withdrew 100.00 from account {acc2}")
        
        self.banking.transfer(acc1, acc2, Decimal("300.00"))
        logging.info(f"Transferred 300.00 from account {acc1} to account {acc2}")
        
        self.file_handler.flush()
        
        self.assertTrue(os.path.exists(self.audit_log_file), "Audit log file was not created")
        
        log_size = os.path.getsize(self.audit_log_file)
        self.assertGreater(log_size, 0, "Audit log file is empty")
        
        with open(self.audit_log_file, 'r') as log_file:
            log_content = log_file.read()
        
        self.assertIn("Created account", log_content)
        self.assertIn("Deposited", log_content)
        self.assertIn("Withdrew", log_content)
        self.assertIn("Transferred", log_content)
    
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'file_handler'):
            self.file_handler.flush()
            self.file_handler.close()
        
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)
                handler.close()
        
        logging.info(f"Tearing down test in {self.__class__.__name__}")


if __name__ == "__main__":
    unittest.main()

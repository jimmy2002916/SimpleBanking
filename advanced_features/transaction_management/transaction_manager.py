import threading
from decimal import Decimal
from typing import List, Dict, Any, Callable, TypeVar, Optional
from contextlib import contextmanager

from basic_required_features.account import BankAccount

T = TypeVar('T')

class TransactionManager:

    def __init__(self):
        # Dictionary to store locks for each account
        self._account_locks = {}
        # Master lock to protect the account_locks dictionary itself
        self._master_lock = threading.RLock()
    
    def get_account_lock(self, account_id: str) -> threading.RLock:
        with self._master_lock:
            if account_id not in self._account_locks:
                self._account_locks[account_id] = threading.RLock()
            return self._account_locks[account_id]
    
    @contextmanager
    def atomic_transaction(self, account_ids: List[str], accounts: Dict[str, BankAccount]):
        sorted_account_ids = sorted(account_ids)
        locks = []
        backup_balances = {}
        transaction_accounts = {}
        
        try:
            for account_id in sorted_account_ids:
                if account_id in accounts:
                    lock = self.get_account_lock(account_id)
                    lock.acquire()
                    locks.append((account_id, lock))
                    
                    transaction_accounts[account_id] = accounts[account_id]
                    
                    backup_balances[account_id] = accounts[account_id].balance
            
            yield transaction_accounts
            
        except Exception as e:
            for account_id, balance in backup_balances.items():
                accounts[account_id].balance = balance
            raise e
            
        finally:
            for account_id, lock in reversed(locks):
                lock.release()
    
    def execute_atomic(self, account_ids: List[str], accounts: Dict[str, BankAccount], 
                      operation: Callable[[Dict[str, BankAccount]], T]) -> T:
        with self.atomic_transaction(account_ids, accounts) as transaction_accounts:
            return operation(transaction_accounts)

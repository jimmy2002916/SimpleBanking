import os
import sqlite3
from decimal import Decimal
from typing import Dict, Any, List, Optional

from basic_required_features.i_storage import IStorage
from basic_required_features.account import BankAccount
from .database_manager import DatabaseManager, DecimalEncoder


class SQLiteStorage(IStorage):
    
    def __init__(self, db_path: str = "data/banking.db"):
        self.db_manager = DatabaseManager(db_path)
        self.next_account_id = 1
    
    def save_accounts(self, accounts: Dict[str, BankAccount], next_account_id: int = None) -> bool:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Store next_account_id if provided
            if next_account_id is not None:
                self.next_account_id = next_account_id
            
            # First, get all existing account IDs
            existing_accounts = self.db_manager.execute_query("SELECT account_id FROM accounts")
            existing_ids = {account['account_id'] for account in existing_accounts}
            
            # Process each account
            for account_id, account in accounts.items():
                # Encode balance as string
                balance_str = DecimalEncoder.encode(account.balance)
                
                if account_id in existing_ids:
                    # Update existing account
                    cursor.execute(
                        "UPDATE accounts SET name = ?, balance = ? WHERE account_id = ?",
                        (account.name, balance_str, account_id)
                    )
                else:
                    # Insert new account
                    cursor.execute(
                        "INSERT INTO accounts (account_id, name, balance) VALUES (?, ?, ?)",
                        (account_id, account.name, balance_str)
                    )
            
            # Store system metadata in a separate table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            ''')
            
            # Store next_account_id
            cursor.execute(
                "INSERT OR REPLACE INTO system_metadata (key, value) VALUES (?, ?)",
                ("next_account_id", str(self.next_account_id))
            )
            
            # Commit the changes
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving accounts to SQLite: {e}")
            return False
    
    def load_accounts(self) -> Dict[str, BankAccount]:
        accounts = {}
        
        try:
            # Query all accounts
            rows = self.db_manager.execute_query("SELECT * FROM accounts")
            
            # Create BankAccount objects
            for row in rows:
                account_id = row['account_id']
                name = row['name']
                balance = DecimalEncoder.decode(row['balance'])
                
                accounts[account_id] = BankAccount(account_id, name, balance)
            
            # Load system metadata if available
            try:
                metadata_rows = self.db_manager.execute_query(
                    "SELECT * FROM system_metadata WHERE key = ?", 
                    ("next_account_id",)
                )
                if metadata_rows:
                    self.next_account_id = int(metadata_rows[0]['value'])
            except:
                # Table might not exist yet, which is fine
                pass
            
        except Exception as e:
            print(f"Error loading accounts from SQLite: {e}")
        
        return accounts
    
    def get_account(self, account_id: str) -> Optional[BankAccount]:
        try:
            rows = self.db_manager.execute_query(
                "SELECT * FROM accounts WHERE account_id = ?", 
                (account_id,)
            )
            
            if rows:
                row = rows[0]
                name = row['name']
                balance = DecimalEncoder.decode(row['balance'])
                return BankAccount(account_id, name, balance)
            
        except Exception as e:
            print(f"Error getting account from SQLite: {e}")
        
        return None
    
    def get_next_account_id(self) -> int:
        return self.next_account_id
    
    def delete_account(self, account_id: str) -> bool:
        try:
            self.db_manager.execute_query(
                "DELETE FROM accounts WHERE account_id = ?", 
                (account_id,)
            )
            return True
            
        except Exception as e:
            print(f"Error deleting account from SQLite: {e}")
            return False
    
    def query_accounts(self, query_params=None):
        try:
            base_query = "SELECT * FROM accounts"
            params = []
            
            # Build WHERE clause if query_params provided
            if query_params:
                where_clauses = []
                
                if 'account_id' in query_params:
                    where_clauses.append("account_id = ?")
                    params.append(query_params['account_id'])
                
                if 'name' in query_params:
                    where_clauses.append("name LIKE ?")
                    params.append(f"%{query_params['name']}%")
                
                if 'balance_min' in query_params:
                    where_clauses.append("CAST(balance AS REAL) >= ?")
                    params.append(float(query_params['balance_min']))
                
                if 'balance_max' in query_params:
                    where_clauses.append("CAST(balance AS REAL) <= ?")
                    params.append(float(query_params['balance_max']))
                
                if where_clauses:
                    base_query += " WHERE " + " AND ".join(where_clauses)
            
            # Execute the query
            results = self.db_manager.execute_query(base_query, tuple(params))
            
            # Convert balance strings to Decimal
            for result in results:
                if 'balance' in result:
                    result['balance'] = DecimalEncoder.decode(result['balance'])
            
            return results
            
        except Exception as e:
            print(f"Error querying accounts from SQLite: {e}")
            return []
    
    def execute_raw_query(self, query, params=()):
        try:
            return self.db_manager.execute_query(query, params)
        except Exception as e:
            print(f"Error executing raw query: {e}")
            return []
    
    def close(self) -> None:
        self.db_manager.close_connection()

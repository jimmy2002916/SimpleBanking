import sqlite3
import os
from decimal import Decimal
from typing import Dict, Any, List, Optional


class DatabaseManager:

    
    def __init__(self, db_path: str = "data/banking.db"):
        self.db_path = db_path
        self.connection = None
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        self.create_tables()
    
    def get_connection(self) -> sqlite3.Connection:
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Configure SQLite to return rows as dictionaries
            self.connection.row_factory = sqlite3.Row
        
        return self.connection
    
    def close_connection(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
    
    def create_tables(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create accounts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            balance TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create metadata table for system information
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        
        conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        
        # If this is a SELECT query, return the results
        if query.strip().upper().startswith("SELECT"):
            results = [dict(row) for row in cursor.fetchall()]
            return results
        
        # For other queries, commit the changes and return empty list
        conn.commit()
        return []


class DecimalEncoder:
    
    @staticmethod
    def encode(value: Decimal) -> str:
        return str(value)
    
    @staticmethod
    def decode(value: str) -> Decimal:
        return Decimal(value)

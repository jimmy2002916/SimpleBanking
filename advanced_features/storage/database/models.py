"""
Database models for the Simple Banking System.

This module defines the database models for storing bank accounts and related data.
"""
import sqlite3
from decimal import Decimal
from typing import Dict, Any, List, Optional


class DatabaseManager:
    """
    Manages the SQLite database connection and schema.
    """
    
    def __init__(self, db_path: str = "banking.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.create_tables()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the SQLite database.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Configure SQLite to return rows as dictionaries
            self.connection.row_factory = sqlite3.Row
        
        return self.connection
    
    def close_connection(self) -> None:
        """
        Close the database connection if open.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None
    
    def create_tables(self) -> None:
        """
        Create the necessary tables if they don't exist.
        """
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
        
        conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return the results.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Parameters for the query
            
        Returns:
            List[Dict[str, Any]]: Query results as a list of dictionaries
        """
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
    """
    Utility class for encoding/decoding Decimal values for SQLite storage.
    """
    
    @staticmethod
    def encode(value: Decimal) -> str:
        """
        Encode a Decimal value as a string for storage.
        
        Args:
            value (Decimal): Decimal value to encode
            
        Returns:
            str: String representation of the Decimal value
        """
        return str(value)
    
    @staticmethod
    def decode(value: str) -> Decimal:
        """
        Decode a string value to a Decimal.
        
        Args:
            value (str): String representation of a Decimal value
            
        Returns:
            Decimal: Decoded Decimal value
        """
        return Decimal(value)

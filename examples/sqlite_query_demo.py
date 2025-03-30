"""
Demo script for querying data from SQLite storage.

This script demonstrates how to query account data from the SQLite database
using both the query_accounts method and raw SQL queries.
"""
from decimal import Decimal

from advanced_features.storage.storage_factory import StorageFactory


def main():
    """Run the SQLite query demo."""
    print("Simple Banking System - SQLite Query Demo")
    print("=========================================")
    
    # Create SQLite storage
    print("\nConnecting to SQLite database...")
    sqlite_storage = StorageFactory.create_storage("sqlite", db_path="banking.db")
    
    # Query all accounts
    print("\n1. Query all accounts:")
    accounts = sqlite_storage.query_accounts()
    display_accounts(accounts)
    
    # Query accounts by name
    print("\n2. Query accounts with 'Alice' in the name:")
    accounts = sqlite_storage.query_accounts({'name': 'Alice'})
    display_accounts(accounts)
    
    # Query accounts by minimum balance
    print("\n3. Query accounts with balance >= 500:")
    accounts = sqlite_storage.query_accounts({'balance_min': 500})
    display_accounts(accounts)
    
    # Query accounts with multiple filters
    print("\n4. Query accounts with 'Bob' in name and balance <= 800:")
    accounts = sqlite_storage.query_accounts({
        'name': 'Bob',
        'balance_max': 800
    })
    display_accounts(accounts)
    
    # Execute a raw SQL query
    print("\n5. Execute a raw SQL query (accounts ordered by balance):")
    accounts = sqlite_storage.execute_raw_query(
        "SELECT * FROM accounts ORDER BY CAST(balance AS REAL) DESC"
    )
    display_accounts(accounts)
    
    # Query system metadata
    print("\n6. Query system metadata:")
    metadata = sqlite_storage.execute_raw_query("SELECT * FROM system_metadata")
    if metadata:
        print("System Metadata:")
        for item in metadata:
            print(f"  {item['key']}: {item['value']}")
    else:
        print("No system metadata found.")
    
    # Close the database connection
    sqlite_storage.close()
    print("\nDemo completed.")


def display_accounts(accounts):
    """Display account information in a formatted way."""
    if not accounts:
        print("  No accounts found.")
        return
    
    print(f"  Found {len(accounts)} account(s):")
    for account in accounts:
        print(f"  - ID: {account['account_id']}, Name: {account['name']}, Balance: ${account['balance']}")


if __name__ == "__main__":
    main()

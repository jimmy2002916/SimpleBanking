from decimal import Decimal

from advanced_features.storage.storage_factory import StorageFactory


def main():
    print("Simple Banking System - SQLite Query Demo")
    print("=========================================")
    
    print("\nConnecting to SQLite database...")
    sqlite_storage = StorageFactory.create_storage("sqlite", db_path="banking.db")
    
    print("\n1. Query all accounts:")
    accounts = sqlite_storage.query_accounts()
    display_accounts(accounts)
    
    print("\n2. Query accounts with 'Alice' in the name:")
    accounts = sqlite_storage.query_accounts({'name': 'Alice'})
    display_accounts(accounts)
    
    print("\n3. Query accounts with balance >= 500:")
    accounts = sqlite_storage.query_accounts({'balance_min': 500})
    display_accounts(accounts)
    
    print("\n4. Query accounts with 'Bob' in name and balance <= 800:")
    accounts = sqlite_storage.query_accounts({
        'name': 'Bob',
        'balance_max': 800
    })
    display_accounts(accounts)
    
    print("\n5. Execute a raw SQL query (accounts ordered by balance):")
    accounts = sqlite_storage.execute_raw_query(
        "SELECT * FROM accounts ORDER BY CAST(balance AS REAL) DESC"
    )
    display_accounts(accounts)
    
    print("\n6. Query system metadata:")
    metadata = sqlite_storage.execute_raw_query("SELECT * FROM system_metadata")
    if metadata:
        print("System Metadata:")
        for item in metadata:
            print(f"  {item['key']}: {item['value']}")
    else:
        print("No system metadata found.")
    
    sqlite_storage.close()
    print("\nDemo completed.")


def display_accounts(accounts):
    if not accounts:
        print("  No accounts found.")
        return
    
    print(f"  Found {len(accounts)} account(s):")
    for account in accounts:
        print(f"  - ID: {account['account_id']}, Name: {account['name']}, Balance: ${account['balance']}")


if __name__ == "__main__":
    main()

# Database Storage for Simple Banking System

This document provides a comprehensive guide to using SQLite database storage with the Simple Banking System, including step-by-step instructions with examples.

## Overview

The Simple Banking System now supports SQLite database storage for account information, providing better data integrity, query capabilities, and scalability compared to the traditional file-based approach. The system uses CSV storage by default, but you can easily switch to SQLite storage as described below.

### Storage Locations

- **CSV Storage (Default)**: Data is stored in `banking_data.csv` in the current directory by default
- **SQLite Storage**: Data is stored in `banking.db` in the current directory by default

Both storage locations can be customized using the `-DStoragePath` parameter.

### Data Loading at Startup

When the banking system starts:

1. It automatically attempts to load existing account data from the storage file (`banking_data.csv` for CSV storage or `banking.db` for SQLite storage)
2. If the file exists and contains valid data, all accounts will be loaded into the system
3. If the file doesn't exist or is empty, the system starts with no accounts
4. You don't need to explicitly load the data - this happens automatically during initialization

### Automatic Saving on Exit

The system now automatically saves the state before exiting:

1. When you select option `9` (Exit) from the main menu, the system will automatically save all account data
2. The data will be saved to the appropriate storage format based on your startup configuration:
   - CSV storage: Saves to `banking_data.csv` (or your custom path)
   - SQLite storage: Saves to `banking.db` (or your custom path)
3. You'll see a confirmation message that the system state was saved before the program exits

You can still manually save the system state at any time using option `6` from the main menu.

## Step-by-Step Guide with Examples

### 1. Starting the Banking System with SQLite Storage

By default, the system uses CSV storage. To use SQLite storage instead, start the banking system with the appropriate command-line arguments:

```bash
python main.py -DStorage sqlite -DStoragePath banking.db
```

Example output:
```
Using SQLITE storage at: banking.db
Transaction logging enabled. Logs will be saved to: logs/transactions.log

===== Simple Banking System =====
1. Create a new account
2. Deposit money
3. Withdraw money
4. Transfer money
5. View account details
6. Save system state
7. Load system state
8. View transaction logs
9. Exit
================================
Enter your choice (1-9):
```

### 2. Creating a User Account

To create a new account:

1. Select option `1` from the main menu
2. Enter the account holder's name
3. Enter the initial balance

Example:
```
Enter your choice (1-9): 1
Enter account holder name: Alice
Enter initial balance: 1000
Account created successfully! Account ID: ACC0001

Press Enter to continue...
```

### 3. Performing Transactions

You can perform various transactions:

#### Deposit Money
```
Enter your choice (1-9): 2
Enter account ID: ACC0001
Enter amount to deposit: 500
Deposit successful!
New balance: 1500.00
```

#### Withdraw Money
```
Enter your choice (1-9): 3
Enter account ID: ACC0001
Enter amount to withdraw: 200
Withdrawal successful!
New balance: 1300.00
```

#### Transfer Money
```
Enter your choice (1-9): 4
Enter source account ID: ACC0001
Enter destination account ID: ACC0002
Enter amount to transfer: 300
Transfer successful!
Source account balance: 1000.00
Destination account balance: 800.00
```

### 4. CRITICAL: Saving Data to SQLite

**This step is essential!** You must explicitly save the system state before exiting:

1. Select option `6` from the main menu
2. Wait for confirmation that the state was saved

Example:
```
Enter your choice (1-9): 6
Saving system state...
System state saved successfully

Press Enter to continue...
```

If you don't perform this step, your changes will NOT be saved to the database!

### 5. Querying the SQLite Database

After saving your data, you can query the SQLite database directly:

#### Opening the SQLite Shell
```bash
sqlite3 banking.db
```

Output:
```
SQLite version 3.36.0 2021-06-18 18:36:39
Enter ".help" for usage hints.
sqlite>
```

#### Viewing All Tables
```sql
.tables
```

Output:
```
accounts         system_metadata
```

#### Viewing All Accounts
```sql
SELECT * FROM accounts;
```

Example output:
```
ACC0001|Alice|1000.00|2025-03-30 09:30:21
ACC0002|Bob|800.00|2025-03-30 09:31:15
```

#### Viewing Account Details
```sql
SELECT * FROM accounts WHERE account_id = 'ACC0001';
```

Example output:
```
ACC0001|Alice|1000.00|2025-03-30 09:30:21
```

#### Filtering Accounts by Balance
```sql
SELECT * FROM accounts WHERE CAST(balance AS REAL) > 500;
```

Example output:
```
ACC0001|Alice|1000.00|2025-03-30 09:30:21
ACC0002|Bob|800.00|2025-03-30 09:31:15
```

#### Viewing System Metadata
```sql
SELECT * FROM system_metadata;
```

Example output:
```
next_account_id|3
```

#### Exiting the SQLite Shell
```
.exit
```

## Troubleshooting

### No Data in Database After Creating Accounts

If you don't see your accounts in the database:

1. **Did you save the system state?** Always select option `6` before exiting.
2. **Check the database path** - Make sure you're querying the correct database file.
3. **Verify SQLite storage was selected** - Confirm you started with `-DStorage sqlite`.

### Example Debugging Session

```bash
# Check if the database file exists
ls -la banking.db

# Check the number of accounts in the database
sqlite3 banking.db "SELECT COUNT(*) FROM accounts;"

# If count is 0, you likely didn't save the system state
```

## Implementation Details

### Storage Architecture

The storage system uses the following components:

1. **IStorage Interface**: Defines the contract for all storage implementations
2. **CSVStorage**: Implements file-based storage using CSV format
3. **SQLiteStorage**: Implements database storage using SQLite
4. **StorageFactory**: Creates appropriate storage instances based on configuration
5. **DatabaseManager**: Handles SQLite database connections and operations

### Database Schema

The SQLite database includes the following tables:

1. **accounts**: Stores account information
   - account_id (TEXT): Primary key
   - name (TEXT): Account holder's name
   - balance (TEXT): Account balance stored as string
   - created_at (TIMESTAMP): Account creation timestamp

2. **system_metadata**: Stores system-level information
   - key (TEXT): Metadata key (e.g., "next_account_id")
   - value (TEXT): Metadata value

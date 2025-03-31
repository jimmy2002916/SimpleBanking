#!/usr/bin/env python3
import sys
import os
import argparse
from decimal import Decimal

from basic_required_features.banking_system import BankingSystem
from advanced_features.logging.transaction_logger import TransactionLogger
from advanced_features.storage.storage_factory import StorageFactory


def print_menu():
    print("\n===== Simple Banking System =====")
    print("1. Create a new account")
    print("2. Deposit money")
    print("3. Withdraw money")
    print("4. Transfer money")
    print("5. View account details")
    print("6. Save system state")
    print("7. Load system state")
    print("8. View transaction logs")
    print("9. Exit")
    print("================================")


def get_decimal_input(prompt):
    while True:
        try:
            return Decimal(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def get_account_id_input(prompt, banking=None):
    example_text = ""
    if banking and banking.accounts:
        # Get up to 2 account IDs as examples
        example_ids = list(banking.accounts.keys())[:2]
        if example_ids:
            example_text = f" (e.g., {', '.join(example_ids)})"
    
    return input(f"{prompt}{example_text}: ")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Simple Banking System")
    
    parser.add_argument("-DStorage",
                        choices=["csv", "sqlite"], 
                        default="csv",
                        help="Storage mechanism to use (csv or sqlite)")
    
    parser.add_argument("-DStoragePath",
                        help="Path for the storage file/database")
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    storage_type = args.DStorage
    storage_path = args.DStoragePath
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    if not storage_path:
        if storage_type == "csv":
            storage_path = os.path.join(data_dir, "banking_data.csv")
        else:  # sqlite
            storage_path = os.path.join(data_dir, "banking.db")
    
    print(f"Using {storage_type.upper()} storage at: {storage_path}")
    
    storage_kwargs = {}
    if storage_type == "csv":
        storage_kwargs["filepath"] = storage_path
    else:  # sqlite
        storage_kwargs["db_path"] = storage_path
    
    storage = StorageFactory.create_storage(storage_type, **storage_kwargs)
    
    banking = BankingSystem(storage)
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "transactions.log")
    logger = TransactionLogger(log_file)
    banking.attach_logger(logger)
    
    print(f"Transaction logging enabled. Logs will be saved to: {log_file}")
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-9): ")
        
        if choice == '1':
            # Create a new account
            name = input("Enter account holder name: ")
            initial_balance = get_decimal_input("Enter initial balance: ")
            
            try:
                account_id = banking.create_account(name, initial_balance)
                print(f"Account created successfully! Account ID: {account_id}")
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == '2':
            # Deposit money
            account_id = get_account_id_input("Enter account ID", banking)
            amount = get_decimal_input("Enter amount to deposit: ")
            
            if banking.deposit(account_id, amount):
                print("Deposit successful!")
                account = banking.get_account(account_id)
                print(f"New balance: {account.balance}")
            else:
                print("Deposit failed. Please check account ID and amount.")
                
        elif choice == '3':
            # Withdraw money
            account_id = get_account_id_input("Enter account ID", banking)
            amount = get_decimal_input("Enter amount to withdraw: ")
            
            if banking.withdraw(account_id, amount):
                print("Withdrawal successful!")
                account = banking.get_account(account_id)
                print(f"New balance: {account.balance}")
            else:
                print("Withdrawal failed. Please check account ID, amount, and balance.")
                
        elif choice == '4':
            # Transfer money
            from_account_id = get_account_id_input("Enter source account ID", banking)
            to_account_id = get_account_id_input("Enter destination account ID", banking)
            amount = get_decimal_input("Enter amount to transfer: ")
            
            if banking.transfer(from_account_id, to_account_id, amount):
                print("Transfer successful!")
                from_account = banking.get_account(from_account_id)
                to_account = banking.get_account(to_account_id)
                print(f"New balance for {from_account_id}: {from_account.balance}")
                print(f"New balance for {to_account_id}: {to_account.balance}")
            else:
                print("Transfer failed. Please check account IDs, amount, and balance.")
                
        elif choice == '5':
            # View account details
            account_id = get_account_id_input("Enter account ID", banking)
            account = banking.get_account(account_id)
            
            if account:
                print(f"\nAccount ID: {account_id}")
                print(f"Account Holder: {account.name}")
                print(f"Balance: {account.balance}")
            else:
                print(f"Account {account_id} not found.")
                
        elif choice == '6':
            # Save system state
            banking.save_to_storage()
            print("System state saved successfully.")
            
        elif choice == '7':
            # Load system state
            banking.load_from_storage()
            print("System state loaded successfully.")
            
        elif choice == '8':
            # View transaction logs
            print("\n===== Transaction Logs =====")
            account_filter = input("Filter by account ID (leave empty for all): ")
            
            if account_filter:
                logs = logger.get_logs_by_account(account_filter)
            else:
                logs = logger.get_all_logs()
            
            if logs:
                for log in logs:
                    print(log)
            else:
                print("No transaction logs found.")
                
        elif choice == '9':
            # Save before exiting
            banking.save_to_storage()
            print("System state saved. Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

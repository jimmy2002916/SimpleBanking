#!/usr/bin/env python3
"""
Main entry point for the Simple Banking System.

This script provides a simple command-line interface to interact with the banking system.
"""

import sys
import os
from decimal import Decimal
from banking import BankingSystem, TransactionLogger


def print_menu():
    """Print the main menu options."""
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
    """Get a decimal input from the user."""
    while True:
        try:
            return Decimal(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def main():
    """Main function to run the banking system."""
    # Initialize the banking system
    banking = BankingSystem()
    
    # Set up transaction logging
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
            account_id = input("Enter account ID: ")
            amount = get_decimal_input("Enter amount to deposit: ")
            
            if banking.deposit(account_id, amount):
                print("Deposit successful!")
                account = banking.get_account(account_id)
                print(f"New balance: {account.balance}")
            else:
                print("Deposit failed. Please check account ID and amount.")
                
        elif choice == '3':
            # Withdraw money
            account_id = input("Enter account ID: ")
            amount = get_decimal_input("Enter amount to withdraw: ")
            
            if banking.withdraw(account_id, amount):
                print("Withdrawal successful!")
                account = banking.get_account(account_id)
                print(f"New balance: {account.balance}")
            else:
                print("Withdrawal failed. Please check account ID, amount, and balance.")
                
        elif choice == '4':
            # Transfer money
            from_account_id = input("Enter source account ID: ")
            to_account_id = input("Enter destination account ID: ")
            amount = get_decimal_input("Enter amount to transfer: ")
            
            if banking.transfer(from_account_id, to_account_id, amount):
                print("Transfer successful!")
                from_account = banking.get_account(from_account_id)
                to_account = banking.get_account(to_account_id)
                print(f"Source account balance: {from_account.balance}")
                print(f"Destination account balance: {to_account.balance}")
            else:
                print("Transfer failed. Please check account IDs, amount, and balance.")
                
        elif choice == '5':
            # View account details
            account_id = input("Enter account ID: ")
            account = banking.get_account(account_id)
            
            if account:
                print(f"\nAccount ID: {account.account_id}")
                print(f"Name: {account.name}")
                print(f"Balance: {account.balance}")
            else:
                print("Account not found.")
                
        elif choice == '6':
            # Save system state
            filepath = input("Enter filepath to save (e.g., banking_data.csv): ")
            
            if banking.save_to_csv(filepath):
                print(f"System state saved to {filepath}")
            else:
                print("Failed to save system state.")
                
        elif choice == '7':
            # Load system state
            filepath = input("Enter filepath to load from: ")
            
            if banking.load_from_csv(filepath):
                print(f"System state loaded from {filepath}")
            else:
                print("Failed to load system state.")
                
        elif choice == '8':
            # View transaction logs
            print("\n===== Transaction Logs =====")
            print("1. View all logs")
            print("2. View logs for a specific account")
            print("3. View logs by action type")
            print("4. Back to main menu")
            
            log_choice = input("Enter your choice (1-4): ")
            
            if log_choice == '1':
                # View all logs
                logs = logger.get_all_logs()
                if logs:
                    print("\nAll Transaction Logs:")
                    for i, log in enumerate(logs, 1):
                        print(f"\nLog #{i}:")
                        for key, value in log.items():
                            print(f"  {key}: {value}")
                else:
                    print("No transaction logs found.")
                    
            elif log_choice == '2':
                # View logs for a specific account
                account_id = input("Enter account ID: ")
                logs = logger.get_logs_by_account(account_id)
                
                if logs:
                    print(f"\nTransaction Logs for Account {account_id}:")
                    for i, log in enumerate(logs, 1):
                        print(f"\nLog #{i}:")
                        for key, value in log.items():
                            print(f"  {key}: {value}")
                else:
                    print(f"No transaction logs found for account {account_id}.")
                    
            elif log_choice == '3':
                # View logs by action type
                print("\nAction Types:")
                print("1. deposit")
                print("2. withdraw")
                print("3. transfer")
                print("4. create_account")
                print("5. save_to_csv")
                print("6. load_from_csv")
                
                action_choice = input("Enter action type (1-6): ")
                action_types = ["deposit", "withdraw", "transfer", "create_account", "save_to_csv", "load_from_csv"]
                
                if action_choice.isdigit() and 1 <= int(action_choice) <= 6:
                    action = action_types[int(action_choice) - 1]
                    logs = logger.get_logs_by_action(action)
                    
                    if logs:
                        print(f"\nTransaction Logs for Action '{action}':")
                        for i, log in enumerate(logs, 1):
                            print(f"\nLog #{i}:")
                            for key, value in log.items():
                                print(f"  {key}: {value}")
                    else:
                        print(f"No transaction logs found for action '{action}'.")
                else:
                    print("Invalid action type.")
                    
            elif log_choice == '4':
                # Back to main menu
                continue
                
            else:
                print("Invalid choice.")
                
        elif choice == '9':
            # Exit
            print("Thank you for using Simple Banking System. Goodbye!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please try again.")
            
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

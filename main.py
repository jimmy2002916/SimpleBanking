#!/usr/bin/env python3
"""
Main entry point for the Simple Banking System.

This script provides a simple command-line interface to interact with the banking system.
"""

import sys
from decimal import Decimal
from basic_required_features.banking_system import BankingSystem


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
    print("8. Exit")
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
    banking = BankingSystem()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-8): ")
        
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
            # Exit
            print("Thank you for using Simple Banking System. Goodbye!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please try again.")
            
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

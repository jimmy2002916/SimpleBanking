from decimal import Decimal

class BankAccount:

    def __init__(self, account_id, name, balance=Decimal("0.00")):
        self.account_id = account_id
        self.name = name
        self.balance = balance
        
    def deposit(self, amount):
        if amount <= Decimal("0.00"):
            return False
        
        self.balance += amount
        return True
    
    def withdraw(self, amount):
        if amount <= Decimal("0.00"):
            return False
        
        if amount > self.balance:
            return False
        
        self.balance -= amount
        return True

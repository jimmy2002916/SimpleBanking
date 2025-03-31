from abc import ABC, abstractmethod
from typing import Dict, Optional
from .account import BankAccount


class IStorage(ABC):
    
    @abstractmethod
    def save_accounts(self, accounts: Dict[str, BankAccount]) -> bool:
        pass
    
    @abstractmethod
    def load_accounts(self) -> Dict[str, BankAccount]:
        pass
    
    @abstractmethod
    def get_account(self, account_id: str) -> Optional[BankAccount]:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass

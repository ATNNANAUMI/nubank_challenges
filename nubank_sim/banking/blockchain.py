from banking_system import BankingSystem
from enum import Enum

class Account():

    def __init__(self) -> None:
        self.balance = 0
        self.status = Status.ACTIVE
        self.history = []

    #def update(self, )

class Status(Enum):
    PENDING = 1
    CANCELLED = 2
    SUCCEEDED = 3
    ACTIVE = 4
    INACTIVE = 5

class Payment():

    def __init__(self, value: int, status = Status) -> None:
        self.value = value
        self.status = status

    def set_status(self, status) -> bool:
        if (isinstance(status, Status)):
            self.status = status
            return True
        return False
    
    


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        pass

    def create_account(self, timestamp: int, account_id: str) -> bool:
        return False
        pass

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        pass

    def pay(self, timestamp: int, account_id: str, amount: int) -> int | None:
        pass

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        return []
        pass
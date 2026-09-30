"""
PIX Authorizer -- Live Case 2.

Implement the methods below following README.md.
Keep the class name and the method signatures: the tests call them directly.

All amounts are integers in cents. Timestamps look like "2026-10-05T21:30:00".
"""

from __future__ import annotations

from typing import Optional

class Account:
    def __init__(self, timestamp: str, balance: int) -> None:
        self.balance = balance
        self.timestamp = {timestamp: ["account created"]}
        self.keys = {}
        
class PixAuthorizer:
    def __init__(self) -> None:
        self.accounts = {}
        self.schedule = {}
        self.keys = {}

    # ------------------------------------------------------------ Part 1

    def create_account(self, timestamp: str, account_id: str, balance: int) -> dict:
        """Returns {"status": "approved" | "rejected", "violations": [...]}."""
        if account_id in self.accounts:
            return {"status": "rejected",
                    "violations": ["account-already-exists"]}
        if balance < 0:
            return {"status": "rejected",
                    "violations": ["invalid-amount"]}
        acc = Account(timestamp, balance)

        self.accounts[account_id] = acc
        return {"status": "approved",
                    "violations": []}

    def check_key(self, key) -> str:
        type = "invalid"
        if not key:
            return type
        elif key[0] == '+' and \
            len(key) == 14: # +55 12 34567 8901 == 13 digits and + 
            if key[1] != 5 or key[2] != 5:
                return type
            type = "phone number"
        elif key.count('@') == 1:
            split = key.split('@')
            if split[0] == [] or split[1] == []:
                return type
            if '.' not in split[1] or split[1][0] == '.':
                return type
            type = "e-mail"
        elif len(key) == 36:
            split = key.split('-')
            if len(split) != 5:
                return type
            sizes = [8,4,4,4,12]
            hex = "0123456789abcdef"
            for i in range(5):
                if len(split[i]) != sizes[i]:
                    return type
                for j in range(sizes[i]):
                    if split[i][j] not in hex:
                        return type
            type = "Random Key"
        else:
            "".join(c for c in key if c not in ".-")
            if len(key) != 11:
                return type
            type = "cpf"
        return type


    def register_key(self, timestamp: str, account_id: str, key: str) -> dict:
        """Returns {"status": "approved" | "rejected", "violations": [...]}."""
        acc = self.accounts.get(account_id, None)
        if acc == None:
            return {"status": "rejected",
                "violations": ["account-not-found"]}
        if key in self.keys:
            return {"status": "rejected",
                "violations": ["key-already-registered"]}
        if len(acc.keys) == 5:
            return {"status": "rejected",
                    "violations": ["key-limit-reached"]}
        key_type = self.check_key(key)
        print(key_type)
        if key_type == "invalid":
            return {"status": "rejected",
                    "violations": ["invalid-key"]}
        acc.timestamp[timestamp] = ["registered key", key, key_type]
        acc.keys[key] = key_type
        self.keys[key] = key_type
        return {"status": "approved",
                "violations": []}



    def get_balance(self, timestamp: str, account_id: str) -> Optional[int]:
        """Returns the balance in cents, or None if the account doesn't exist."""
        raise NotImplementedError

    def transfer(
        self, timestamp: str, transfer_id: str, from_account: str, to_key: str, amount: int
    ) -> dict:
        """Returns {"status": "approved" | "rejected", "violations": [...]}."""
        raise NotImplementedError

    # ------------------------------------------------------------ Part 5

    def schedule_transfer(
        self,
        timestamp: str,
        transfer_id: str,
        from_account: str,
        to_key: str,
        amount: int,
        execute_at: str,
    ) -> dict:
        """Returns {"status": "scheduled" | "rejected", "violations": [...]}."""
        raise NotImplementedError

    def cancel_scheduled(self, timestamp: str, transfer_id: str) -> dict:
        """Returns {"status": "approved" | "rejected", "violations": [...]}."""
        raise NotImplementedError

    def get_transfer_status(self, timestamp: str, transfer_id: str) -> Optional[dict]:
        """Returns {"status": ..., "violations": [...]}, or None for an unknown id."""
        raise NotImplementedError

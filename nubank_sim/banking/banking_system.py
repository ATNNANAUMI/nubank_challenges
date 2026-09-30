from abc import ABC, abstractmethod

class BankingSystem(ABC):
    """
    `BankingSystem` interface.

    All amounts are non-negative integers. All account balances start at 0.
    `timestamp` is a strictly increasing integer (milliseconds); every call
    receives a `timestamp` greater than any previous call.
    """

    # -------------------- Level 1 --------------------
    @abstractmethod
    def create_account(self, timestamp: int, account_id: str) -> bool:
        """
        Create a new account with the given identifier and balance 0.
        Return True if the account was created, or False if an account
        with `account_id` already exists.
        """
        return False

    @abstractmethod
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        """
        Deposit `amount` into `account_id` and return the new balance.
        If the account does not exist, return None.
        """
        return None

    @abstractmethod
    def pay(self, timestamp: int, account_id: str, amount: int) -> int | None:
        """
        Withdraw `amount` from `account_id` (a payment) and return the new
        balance. If the account does not exist or has insufficient funds,
        return None (and the balance is left unchanged).
        """
        return None

    # -------------------- Level 2 --------------------
    @abstractmethod
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        """
        Return the identifiers of the top `n` accounts with the highest total
        amount of money spent (via `pay` and via outgoing `transfer`), sorted
        in descending order of amount spent. Ties are broken alphabetically by
        account_id in ascending order.

        Each entry is formatted as `"<account_id>(<total_spent>)"`.
        If there are fewer than `n` accounts, return all of them.
        """
        return []

    # -------------------- Level 3 --------------------
    @abstractmethod
    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None:
        """
        Transfer `amount` from `source_id` to `target_id` and return the
        source balance after the transfer.
        Return None if: either account does not exist, `source_id == target_id`,
        or the source has insufficient funds. Outgoing transfers count toward
        the source's total spent (for `top_spenders`).
        """
        return None

    @abstractmethod
    def schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str | None:
        """
        Schedule a payment of `amount` to be withdrawn from `account_id` at
        time `timestamp + delay`. Return a unique payment id of the form
        `"payment<N>"` (N starts at 1 and increases across ALL scheduled
        payments), or None if the account does not exist.

        Scheduled payments due at or before the current timestamp are processed
        (in order of scheduled time, then creation order) at the START of every
        subsequent call. A due payment executes only if the account has enough
        funds; otherwise it is discarded without changing the balance. Executed
        scheduled payments count toward the account's total spent.
        """
        return None

    @abstractmethod
    def cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool:
        """
        Cancel the scheduled payment `payment_id` belonging to `account_id`
        if it is still pending. Return True on success, or False if the payment
        does not exist, does not belong to the account, or was already executed
        or cancelled.
        """
        return False

    # -------------------- Level 4 --------------------
    @abstractmethod
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        """
        Merge `account_id_2` into `account_id_1`. The balance and total-spent of
        account 2 are added to account 1, account 2's pending scheduled payments
        are reassigned to account 1, and account 2 is removed.
        Return True on success, or False if either account does not exist or
        `account_id_1 == account_id_2`.
        """
        return False

    @abstractmethod
    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        """
        Return the balance of `account_id` as it was at time `time_at`
        (considering every operation with timestamp <= time_at).
        Return None if the account did not exist at `time_at`.
        If the account was merged into another, its balance remains queryable
        for any `time_at` strictly before the merge.
        """
        return None

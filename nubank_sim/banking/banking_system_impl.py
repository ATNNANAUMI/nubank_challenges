from banking_system import BankingSystem

class BankingSystemImpl(BankingSystem):

    def __init__(self):
        self.accounts = {}
        self.scheduled = []
        self.schedule_id = 0

    def check_transfer(self, source_id, target_id, amount) -> bool:
        if (source_id not in self.accounts or 
            target_id not in self.accounts or 
            target_id == source_id or 
            self.accounts[source_id]["status"] == "inactive" or
            self.accounts[target_id]["status"] == "inactive"):
            return False
        elif self.accounts[source_id]["balance"] < amount:
            return False
        return True

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self.check_schedule(timestamp)
        """
        Create a new account with the given identifier and balance 0.
        Return True if the account was created, or False if an account
        with `account_id` already exists.
        """
        if account_id in self.accounts:
            return False
        account = {"balance": 0, 
                   "total_spent": 0,
                   "history": [],
                   "status": "active"}
        self.accounts[account_id] = account
        self.accounts[account_id]["history"].append({"timestamp": timestamp,
                                                    "operation": "create",
                                                    "amount": 0})
        return True
    
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self.check_schedule(timestamp)
        """
        Deposit `amount` into `account_id` and return the new balance.
        If the account does not exist, return None.
        """
        if (account_id not in self.accounts or 
            self.accounts[account_id]["status"] == "inactive"):
            return None
        self.accounts[account_id]["balance"] += amount
        self.accounts[account_id]["history"].append({"timestamp": timestamp,
                                                     "operation": "deposit",
                                                     "amount": amount})
        return self.accounts[account_id]["balance"]

    def pay(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self.check_schedule(timestamp)
        """
        Withdraw `amount` from `account_id` (a payment) and return the new
        balance. If the account does not exist or has insufficient funds,
        return None (and the balance is left unchanged).
        """
        if (account_id not in self.accounts or 
            self.accounts[account_id]["status"] == "inactive"):
            return None
        elif self.accounts[account_id]["balance"] >= amount:
            self.accounts[account_id]["balance"] -= amount
            self.accounts[account_id]["total_spent"] += amount
            self.accounts[account_id]["history"].append({"timestamp": timestamp,
                                                                 "operation": "pay",
                                                                 "amount": amount})
            return self.accounts[account_id]["balance"]
        return None

    # -------------------- Level 2 --------------------
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        self.check_schedule(timestamp)
        """
        Return the identifiers of the top `n` accounts with the highest total
        amount of money spent (via `pay` and via outgoing `transfer`), sorted
        in descending order of amount spent. Ties are broken alphabetically by
        account_id in ascending order.

        Each entry is formatted as `"<account_id>(<total_spent>)"`.
        If there are fewer than `n` accounts, return all of them.
        """
        spenders = []
        self.accounts = dict(sorted(self.accounts.items(), key= lambda item: (-item[1]["total_spent"], item[0])))
        accounts = iter(self.accounts)
        if n > len(self.accounts):
            n = len(self.accounts)
        for i in range(n):
            key = next(accounts)
            account = self.accounts[key]
            amount = account["total_spent"]
            if account["status"] == "inactive":
                continue
            spenders.append(f"{key}({amount})")
        
        return spenders 

    # -------------------- Level 3 --------------------
    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None:
        self.check_schedule(timestamp)
        """
        Transfer `amount` from `source_id` to `target_id` and return the
        source balance after the transfer.
        Return None if: either account does not exist, `source_id == target_id`,
        or the source has insufficient funds. Outgoing transfers count toward
        the source's total spent (for `top_spenders`).
        """
        if self.check_transfer(source_id, target_id, amount):
            self.pay(timestamp, source_id, amount)
            self.deposit(timestamp, target_id, amount)
            print("tranfer")
            return self.accounts[source_id]["balance"]

        return None

    def schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str | None:
        self.check_schedule(timestamp)
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
        self.schedule_id += 1
        if (account_id not in self.accounts or 
            self.accounts[account_id]["status"] == "inactive"):
            return None
        payment = {"account_id": account_id,
                   "amount": amount,
                   "time": timestamp+delay,
                   "payment_id": f"payment{self.schedule_id}"}
        self.scheduled.append(payment)
        return (f"payment{self.schedule_id}")

    def check_schedule(self, timestamp) -> None:
        counter = 0
        while True:
            if not self.scheduled or counter >= len(self.scheduled):
                return None
            payment = self.scheduled[counter]
            counter += 1
            account_id = payment["account_id"]
            amount = payment["amount"]

            if payment["time"] <= timestamp:
                self.scheduled.remove(payment)
                counter -= 1
                if self.accounts[account_id]["balance"] < amount:

                    return None
                self.accounts[account_id]["balance"] -= amount
                self.accounts[account_id]["total_spent"] += amount
                self.accounts[account_id]["history"].append({"timestamp": payment["time"],
                                                            "operation": "pay",
                                                            "amount": amount})
        
        
    def cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool:
        self.check_schedule(timestamp)
        """
        Cancel the scheduled payment `payment_id` belonging to `account_id`
        if it is still pending. Return True on success, or False if the payment
        does not exist, does not belong to the account, or was already executed
        or cancelled.
        """
        for payment in self.scheduled:
            if (payment["account_id"] == account_id and
                payment["payment_id"] == payment_id):
                self.scheduled.remove(payment)
                return True
        return False

    # -------------------- Level 4 --------------------
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        self.check_schedule(timestamp)
        """
        Merge `account_id_2` into `account_id_1`. The balance and total-spent of
        account 2 are added to account 1, account 2's pending scheduled payments
        are reassigned to account 1, and account 2 is removed.
        Return True on success, or False if either account does not exist or
        `account_id_1 == account_id_2`.
        """
        if self.check_transfer(account_id_1, account_id_2, 0):
            self.accounts[account_id_1]["balance"] += self.accounts[account_id_2]["balance"]
            self.accounts[account_id_1]["total_spent"] += self.accounts[account_id_2]["total_spent"]

            self.accounts[account_id_1]["history"].append({"timestamp": timestamp,
                                                            "operation": "deposit",
                                                            "amount": self.accounts[account_id_2]["balance"]})
            self.accounts[account_id_2]["history"].append({"timestamp": timestamp,
                                                            "operation": "inactivation",
                                                            "amount": 0})
            for payment in self.scheduled:
                if (payment["account_id"] == account_id_2):
                    payment["account_id"] = account_id_1
            self.accounts[account_id_2]["status"] = "inactive"
            return True
        return False

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        self.check_schedule(timestamp)
        """
        Return the balance of `account_id` as it was at time `time_at`
        (considering every operation with timestamp <= time_at).
        Return None if the account did not exist at `time_at`.
        If the account was merged into another, its balance remains queryable
        for any `time_at` strictly before the merge.
        """
        if (account_id not in self.accounts or
            self.accounts[account_id]["history"][0]["timestamp"] > time_at):
            return None
        print(self.accounts[account_id]["history"])
        balance = 0
        #print(time_at)
        for transaction in self.accounts[account_id]["history"]:
            #print(transaction)
            if  transaction["timestamp"] > time_at:
                break

            operation = transaction["operation"]
            amount = transaction["amount"]
            if(operation == "deposit"):
                balance += amount
            elif(operation == "pay"):
                balance -= amount
            elif(operation == "inactivation"):
                return None
        return balance

    # TODO: implement interface methods here
    # Level 1: create_account, deposit, pay
    # Level 2: top_spenders
    # Level 3: transfer, schedule_payment, cancel_payment
    # Level 4: merge_accounts, get_balance

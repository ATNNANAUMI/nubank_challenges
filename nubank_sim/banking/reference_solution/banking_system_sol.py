from banking.banking_system import BankingSystem


class _Account:
    def __init__(self, timestamp: int):
        self.balance = 0
        self.spent = 0
        self.created = timestamp
        self.history = [(timestamp, 0)]  # (time, balance), chronological

    def checkpoint(self, time: int):
        self.history.append((time, self.balance))

    def balance_at(self, time_at: int) -> int | None:
        if time_at < self.created:
            return None
        val = None
        for t, b in self.history:
            if t <= time_at:
                val = b
            else:
                break
        return val


class _Payment:
    def __init__(self, pid: str, account_id: str, amount: int, due: int, order: int):
        self.pid = pid
        self.account_id = account_id
        self.amount = amount
        self.due = due
        self.order = order
        self.status = "pending"  # pending | executed | cancelled


class BankingSystemImpl(BankingSystem):
    def __init__(self):
        self.accounts: dict[str, _Account] = {}
        self.merged: dict[str, tuple[_Account, int]] = {}  # id -> (account, merged_at)
        self.payments: dict[str, _Payment] = {}
        self._pcount = 0

    # ---------- internal ----------
    def _process_due(self, timestamp: int):
        due = [p for p in self.payments.values()
               if p.status == "pending" and p.due <= timestamp]
        due.sort(key=lambda p: (p.due, p.order))
        for p in due:
            acc = self.accounts.get(p.account_id)
            if acc is None:
                p.status = "cancelled"
                continue
            if acc.balance >= p.amount:
                acc.balance -= p.amount
                acc.spent += p.amount
                acc.checkpoint(p.due)
            p.status = "executed"

    # ---------- Level 1 ----------
    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._process_due(timestamp)
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = _Account(timestamp)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process_due(timestamp)
        acc = self.accounts.get(account_id)
        if acc is None:
            return None
        acc.balance += amount
        acc.checkpoint(timestamp)
        return acc.balance

    def pay(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process_due(timestamp)
        acc = self.accounts.get(account_id)
        if acc is None or acc.balance < amount:
            return None
        acc.balance -= amount
        acc.spent += amount
        acc.checkpoint(timestamp)
        return acc.balance

    # ---------- Level 2 ----------
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        self._process_due(timestamp)
        ranked = sorted(self.accounts.items(), key=lambda kv: (-kv[1].spent, kv[0]))
        return [f"{aid}({acc.spent})" for aid, acc in ranked[:n]]

    # ---------- Level 3 ----------
    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> int | None:
        self._process_due(timestamp)
        if source_id == target_id:
            return None
        src = self.accounts.get(source_id)
        tgt = self.accounts.get(target_id)
        if src is None or tgt is None or src.balance < amount:
            return None
        src.balance -= amount
        src.spent += amount
        tgt.balance += amount
        src.checkpoint(timestamp)
        tgt.checkpoint(timestamp)
        return src.balance

    def schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str | None:
        self._process_due(timestamp)
        if account_id not in self.accounts:
            return None
        self._pcount += 1
        pid = f"payment{self._pcount}"
        self.payments[pid] = _Payment(pid, account_id, amount, timestamp + delay, self._pcount)
        return pid

    def cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool:
        self._process_due(timestamp)
        p = self.payments.get(payment_id)
        if p is None or p.account_id != account_id or p.status != "pending":
            return False
        p.status = "cancelled"
        return True

    # ---------- Level 4 ----------
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        self._process_due(timestamp)
        if account_id_1 == account_id_2:
            return False
        a1 = self.accounts.get(account_id_1)
        a2 = self.accounts.get(account_id_2)
        if a1 is None or a2 is None:
            return False
        a1.balance += a2.balance
        a1.spent += a2.spent
        a1.checkpoint(timestamp)
        for p in self.payments.values():
            if p.status == "pending" and p.account_id == account_id_2:
                p.account_id = account_id_1
        a2.checkpoint(timestamp)
        self.merged[account_id_2] = (a2, timestamp)
        del self.accounts[account_id_2]
        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        self._process_due(timestamp)
        acc = self.accounts.get(account_id)
        if acc is not None:
            return acc.balance_at(time_at)
        if account_id in self.merged:
            a2, merged_at = self.merged[account_id]
            if time_at < merged_at:
                return a2.balance_at(time_at)
        return None

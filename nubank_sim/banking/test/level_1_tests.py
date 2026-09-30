import inspect, os, sys
frame = inspect.currentframe()
if frame is None:
    exit()
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(frame)))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from timeout_decorator import timeout
import unittest
from banking.banking_system_impl import BankingSystemImpl


class Level1Tests(unittest.TestCase):
    """10 tests for Level 1. All have the same score. Do not modify this file."""

    failureException = Exception

    def setUp(self): # type: ignore
        self.bank = BankingSystemImpl()

    @timeout(0.4)
    def test_level_1_case_01_create_account(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertTrue(self.bank.create_account(2, "acc2"))

    @timeout(0.4)
    def test_level_1_case_02_create_duplicate_account(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertFalse(self.bank.create_account(2, "acc1"))
    
    @timeout(0.4)
    def test_level_1_case_03_deposit_returns_balance(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 2000), 2000)
        self.assertEqual(self.bank.deposit(3, "acc1", 3000), 5000)

    @timeout(0.4)
    def test_level_1_case_04_deposit_missing_account(self):
        self.assertIsNone(self.bank.deposit(1, "acc1", 2000))
        self.assertTrue(self.bank.create_account(2, "acc1"))
        self.assertEqual(self.bank.deposit(3, "acc1", 2000), 2000)

    @timeout(0.4)
    def test_level_1_case_05_pay_returns_balance(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 2000), 2000)
        self.assertEqual(self.bank.pay(3, "acc1", 500), 1500)
        self.assertEqual(self.bank.pay(4, "acc1", 1500), 0)

    @timeout(0.4)
    def test_level_1_case_06_pay_insufficient_funds(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 1000), 1000)
        self.assertIsNone(self.bank.pay(3, "acc1", 1001))
        self.assertEqual(self.bank.deposit(4, "acc1", 0), 1000)

    @timeout(0.4)
    def test_level_1_case_07_pay_missing_account(self):
        self.assertIsNone(self.bank.pay(1, "acc1", 100))

    @timeout(0.4)
    def test_level_1_case_08_pay_exact_balance_then_fail(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 100), 100)
        self.assertEqual(self.bank.pay(3, "acc1", 100), 0)
        self.assertIsNone(self.bank.pay(4, "acc1", 1))

    @timeout(0.4)
    def test_level_1_case_09_multiple_accounts_independent(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertTrue(self.bank.create_account(2, "acc2"))
        self.assertEqual(self.bank.deposit(3, "acc1", 1000), 1000)
        self.assertEqual(self.bank.deposit(4, "acc2", 2000), 2000)
        self.assertEqual(self.bank.pay(5, "acc1", 300), 700)
        self.assertEqual(self.bank.deposit(6, "acc2", 0), 2000)

    @timeout(0.4)
    def test_level_1_case_10_mixed_operations(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertFalse(self.bank.create_account(2, "a"))
        self.assertIsNone(self.bank.pay(3, "a", 10))
        self.assertEqual(self.bank.deposit(4, "a", 50), 50)
        self.assertEqual(self.bank.pay(5, "a", 20), 30)
        self.assertIsNone(self.bank.pay(6, "a", 31))
        self.assertEqual(self.bank.pay(7, "a", 30), 0)
        self.assertIsNone(self.bank.deposit(8, "b", 10))


if __name__ == "__main__":
    unittest.main()

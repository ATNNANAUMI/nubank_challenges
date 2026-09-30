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


class Level4Tests(unittest.TestCase):
    """10 tests for Level 4. All have the same score. Do not modify this file."""

    failureException = Exception

    def setUp(self):
        self.bank = BankingSystemImpl()

    @timeout(0.4)
    def test_level_4_case_01_merge_sums_balances(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "a", 1000), 1000)
        self.assertEqual(self.bank.deposit(4, "b", 500), 500)
        self.assertTrue(self.bank.merge_accounts(5, "a", "b"))
        self.assertEqual(self.bank.deposit(6, "a", 0), 1500)
        self.assertIsNone(self.bank.deposit(7, "b", 0))

    @timeout(0.4)
    def test_level_4_case_02_merge_sums_spend(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "a", 1000), 1000)
        self.assertEqual(self.bank.deposit(4, "b", 1000), 1000)
        self.assertEqual(self.bank.pay(5, "a", 200), 800)
        self.assertEqual(self.bank.pay(6, "b", 300), 700)
        self.assertTrue(self.bank.merge_accounts(7, "a", "b"))
        self.assertEqual(self.bank.top_spenders(8, 5), ["a(500)"])
        self.assertEqual(self.bank.deposit(9, "a", 0), 1500)

    @timeout(0.4)
    def test_level_4_case_03_merge_corner_cases(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertFalse(self.bank.merge_accounts(2, "a", "a"))       # same account
        self.assertFalse(self.bank.merge_accounts(3, "a", "x"))       # missing target
        self.assertFalse(self.bank.merge_accounts(4, "x", "a"))       # missing source
        self.assertFalse(self.bank.merge_accounts(5, "x", "y"))       # both missing

    @timeout(0.4)
    def test_level_4_case_04_merge_reassigns_scheduled_payment(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "b", 1000), 1000)
        self.assertEqual(self.bank.schedule_payment(4, "b", 200, 10), "payment1")
        self.assertTrue(self.bank.merge_accounts(5, "a", "b"))
        self.assertEqual(self.bank.deposit(20, "a", 0), 800)         # payment paid from a
        self.assertEqual(self.bank.top_spenders(21, 1), ["a(200)"])
        self.assertFalse(self.bank.cancel_payment(22, "a", "payment1"))

    @timeout(0.4)
    def test_level_4_case_05_get_balance_history(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertEqual(self.bank.deposit(5, "a", 1000), 1000)
        self.assertEqual(self.bank.pay(10, "a", 200), 800)
        self.assertEqual(self.bank.get_balance(11, "a", 1), 0)
        self.assertEqual(self.bank.get_balance(12, "a", 5), 1000)
        self.assertEqual(self.bank.get_balance(13, "a", 7), 1000)
        self.assertEqual(self.bank.get_balance(14, "a", 10), 800)
        self.assertEqual(self.bank.get_balance(15, "a", 100), 800)

    @timeout(0.4)
    def test_level_4_case_06_get_balance_before_creation_or_missing(self):
        self.assertTrue(self.bank.create_account(5, "a"))
        self.assertIsNone(self.bank.get_balance(6, "a", 4))          # before creation
        self.assertEqual(self.bank.get_balance(7, "a", 5), 0)
        self.assertIsNone(self.bank.get_balance(8, "missing", 5))    # never existed

    @timeout(0.4)
    def test_level_4_case_07_get_balance_with_scheduled_payment(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertEqual(self.bank.deposit(2, "a", 1000), 1000)
        self.assertEqual(self.bank.schedule_payment(3, "a", 200, 10), "payment1")  # due 13
        self.assertEqual(self.bank.get_balance(20, "a", 12), 1000)  # not yet due at t=12
        self.assertEqual(self.bank.get_balance(21, "a", 13), 800)   # due at t=13
        self.assertEqual(self.bank.get_balance(22, "a", 100), 800)

    @timeout(0.4)
    def test_level_4_case_08_get_balance_of_merged_account(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "b", 500), 500)
        self.assertEqual(self.bank.deposit(4, "b", 200), 700)
        self.assertTrue(self.bank.merge_accounts(10, "a", "b"))
        self.assertEqual(self.bank.get_balance(11, "b", 3), 500)    # before merge
        self.assertEqual(self.bank.get_balance(12, "b", 5), 700)    # before merge
        self.assertIsNone(self.bank.get_balance(13, "b", 10))       # at/after merge
        self.assertIsNone(self.bank.get_balance(14, "b", 20))       # after merge
        self.assertIsNone(self.bank.get_balance(15, "b", 1))        # before b existed

    @timeout(0.4)
    def test_level_4_case_09_get_balance_after_merge_target(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "b", 700), 700)
        self.assertTrue(self.bank.merge_accounts(10, "a", "b"))
        self.assertEqual(self.bank.get_balance(11, "a", 5), 0)      # a still empty at t=5
        self.assertEqual(self.bank.get_balance(12, "a", 10), 700)   # inherits at merge
        self.assertEqual(self.bank.get_balance(13, "a", 100), 700)

    @timeout(0.4)
    def test_level_4_case_10_full_scenario(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "a", 2000), 2000)
        self.assertEqual(self.bank.deposit(4, "b", 2000), 2000)
        self.assertEqual(self.bank.transfer(5, "a", "b", 500), 1500)
        self.assertEqual(self.bank.pay(6, "b", 300), 2200)
        self.assertEqual(self.bank.schedule_payment(7, "a", 1000, 10), "payment1")  # due 17
        self.assertTrue(self.bank.merge_accounts(8, "b", "a"))       # a -> b
        self.assertEqual(self.bank.deposit(20, "b", 0), 2700)        # 2200 + 1500 - 1000
        self.assertEqual(self.bank.top_spenders(21, 1), ["b(1800)"]) # 500 + 300 + 1000
        self.assertEqual(self.bank.get_balance(22, "a", 6), 1500)    # a before merge
        self.assertIsNone(self.bank.get_balance(23, "a", 8))         # a gone at merge


if __name__ == "__main__":
    unittest.main()

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


class Level3Tests(unittest.TestCase):
    """10 tests for Level 3. All have the same score. Do not modify this file."""

    failureException = Exception

    def setUp(self):
        self.bank = BankingSystemImpl()

    @timeout(0.4)
    def test_level_3_case_01_transfer_basic(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "a", 1000), 1000)
        self.assertEqual(self.bank.transfer(4, "a", "b", 300), 700)
        self.assertEqual(self.bank.deposit(5, "b", 0), 300)

    @timeout(0.4)
    def test_level_3_case_02_transfer_corner_cases(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "a", 100), 100)
        self.assertIsNone(self.bank.transfer(4, "a", "a", 10))       # self transfer
        self.assertIsNone(self.bank.transfer(5, "a", "c", 10))       # missing target
        self.assertIsNone(self.bank.transfer(6, "c", "a", 10))       # missing source
        self.assertIsNone(self.bank.transfer(7, "a", "b", 101))      # insufficient
        self.assertEqual(self.bank.deposit(8, "a", 0), 100)          # unchanged

    @timeout(0.4)
    def test_level_3_case_03_transfer_counts_as_spend(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "a", 1000), 1000)
        self.assertEqual(self.bank.transfer(4, "a", "b", 300), 700)
        self.assertEqual(self.bank.pay(5, "a", 100), 600)
        self.assertEqual(self.bank.top_spenders(6, 2), ["a(400)", "b(0)"])

    @timeout(0.4)
    def test_level_3_case_04_schedule_returns_id(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertEqual(self.bank.deposit(2, "a", 1000), 1000)
        self.assertEqual(self.bank.schedule_payment(3, "a", 200, 10), "payment1")
        self.assertEqual(self.bank.schedule_payment(4, "a", 100, 20), "payment2")

    @timeout(0.4)
    def test_level_3_case_05_schedule_missing_account(self):
        self.assertIsNone(self.bank.schedule_payment(1, "a", 200, 10))

    @timeout(0.4)
    def test_level_3_case_06_scheduled_executes_when_due(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertEqual(self.bank.deposit(2, "a", 1000), 1000)
        self.assertEqual(self.bank.schedule_payment(3, "a", 200, 10), "payment1")
        self.assertEqual(self.bank.deposit(4, "a", 0), 1000)    # not due (4 < 13)
        self.assertEqual(self.bank.deposit(14, "a", 0), 800)    # due (13 <= 14)
        self.assertEqual(self.bank.deposit(20, "a", 0), 800)    # not executed twice
        self.assertEqual(self.bank.top_spenders(21, 1), ["a(200)"])

    @timeout(0.4)
    def test_level_3_case_07_scheduled_insufficient_is_discarded(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertEqual(self.bank.deposit(2, "a", 100), 100)
        self.assertEqual(self.bank.schedule_payment(3, "a", 500, 10), "payment1")
        self.assertEqual(self.bank.deposit(14, "a", 0), 100)    # discarded, balance kept
        self.assertEqual(self.bank.top_spenders(15, 1), ["a(0)"])

    @timeout(0.4)
    def test_level_3_case_08_cancel_before_due(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertEqual(self.bank.deposit(2, "a", 1000), 1000)
        self.assertEqual(self.bank.schedule_payment(3, "a", 200, 10), "payment1")
        self.assertTrue(self.bank.cancel_payment(4, "a", "payment1"))
        self.assertEqual(self.bank.deposit(14, "a", 0), 1000)   # never executed
        self.assertFalse(self.bank.cancel_payment(15, "a", "payment1"))  # already cancelled

    @timeout(0.4)
    def test_level_3_case_09_cancel_corner_cases(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertTrue(self.bank.create_account(2, "b"))
        self.assertEqual(self.bank.deposit(3, "a", 1000), 1000)
        self.assertEqual(self.bank.schedule_payment(4, "a", 200, 10), "payment1")
        self.assertFalse(self.bank.cancel_payment(5, "a", "payment2"))   # nonexistent
        self.assertFalse(self.bank.cancel_payment(6, "b", "payment1"))   # wrong owner
        self.assertEqual(self.bank.deposit(15, "a", 0), 800)             # still executed
        self.assertFalse(self.bank.cancel_payment(16, "a", "payment1"))  # already executed

    @timeout(0.4)
    def test_level_3_case_10_multiple_scheduled_ordering(self):
        self.assertTrue(self.bank.create_account(1, "a"))
        self.assertEqual(self.bank.deposit(2, "a", 1000), 1000)
        self.assertEqual(self.bank.schedule_payment(5, "a", 400, 25), "payment1")   # due 30
        self.assertEqual(self.bank.schedule_payment(6, "a", 400, 14), "payment2")   # due 20
        self.assertEqual(self.bank.deposit(35, "a", 0), 200)   # due20 then due30
        self.assertEqual(self.bank.top_spenders(36, 1), ["a(800)"])


if __name__ == "__main__":
    unittest.main()

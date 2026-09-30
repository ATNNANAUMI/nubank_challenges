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


class Level2Tests(unittest.TestCase):
    """10 tests for Level 2. All have the same score. Do not modify this file."""

    failureException = Exception

    def setUp(self):
        self.bank = BankingSystemImpl()

    @timeout(0.4)
    def test_level_2_case_01_empty_ranking(self):
        self.assertEqual(self.bank.top_spenders(1, 3), [])

    @timeout(0.4)
    def test_level_2_case_02_single_spender(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 1000), 1000)
        self.assertEqual(self.bank.pay(3, "acc1", 400), 600)
        self.assertEqual(self.bank.top_spenders(4, 1), ["acc1(400)"])

    @timeout(0.4)
    def test_level_2_case_03_zero_spenders_alpha_order(self):
        self.assertTrue(self.bank.create_account(1, "b"))
        self.assertTrue(self.bank.create_account(2, "a"))
        self.assertTrue(self.bank.create_account(3, "c"))
        self.assertEqual(self.bank.top_spenders(4, 3), ["a(0)", "b(0)", "c(0)"])

    @timeout(0.4)
    def test_level_2_case_04_ordering_by_spend(self):
        for i, acc in enumerate(["acc1", "acc2", "acc3"], start=1):
            self.assertTrue(self.bank.create_account(i, acc))
            self.assertEqual(self.bank.deposit(10 + i, acc, 5000), 5000)
        self.assertEqual(self.bank.pay(20, "acc1", 100), 4900)
        self.assertEqual(self.bank.pay(21, "acc2", 300), 4700)
        self.assertEqual(self.bank.pay(22, "acc3", 200), 4800)
        self.assertEqual(self.bank.top_spenders(23, 3),
                         ["acc2(300)", "acc3(200)", "acc1(100)"])

    @timeout(0.4)
    def test_level_2_case_05_tie_broken_alphabetically(self):
        for i, acc in enumerate(["z", "a", "m"], start=1):
            self.assertTrue(self.bank.create_account(i, acc))
            self.assertEqual(self.bank.deposit(10 + i, acc, 1000), 1000)
            self.assertEqual(self.bank.pay(20 + i, acc, 500), 500)
        self.assertEqual(self.bank.top_spenders(30, 3), ["a(500)", "m(500)", "z(500)"])

    @timeout(0.4)
    def test_level_2_case_06_n_larger_than_accounts(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 1000), 1000)
        self.assertEqual(self.bank.pay(3, "acc1", 100), 900)
        self.assertEqual(self.bank.top_spenders(4, 10), ["acc1(100)"])

    @timeout(0.4)
    def test_level_2_case_07_n_smaller_than_accounts(self):
        for i, (acc, spend) in enumerate(
                [("acc1", 100), ("acc2", 500), ("acc3", 300)], start=1):
            self.assertTrue(self.bank.create_account(i, acc))
            self.assertEqual(self.bank.deposit(10 + i, acc, 1000), 1000)
            self.assertEqual(self.bank.pay(20 + i, acc, spend), 1000 - spend)
        self.assertEqual(self.bank.top_spenders(30, 2), ["acc2(500)", "acc3(300)"])

    @timeout(0.4)
    def test_level_2_case_08_accumulated_spend(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 1000), 1000)
        self.assertEqual(self.bank.pay(3, "acc1", 100), 900)
        self.assertEqual(self.bank.pay(4, "acc1", 250), 650)
        self.assertEqual(self.bank.top_spenders(5, 1), ["acc1(350)"])

    @timeout(0.4)
    def test_level_2_case_09_failed_pay_does_not_count(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 100), 100)
        self.assertIsNone(self.bank.pay(3, "acc1", 500))
        self.assertEqual(self.bank.pay(4, "acc1", 100), 0)
        self.assertEqual(self.bank.top_spenders(5, 1), ["acc1(100)"])

    @timeout(0.4)
    def test_level_2_case_10_mixed(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertTrue(self.bank.create_account(2, "acc2"))
        self.assertEqual(self.bank.deposit(3, "acc1", 2000), 2000)
        self.assertEqual(self.bank.deposit(4, "acc2", 2000), 2000)
        self.assertEqual(self.bank.pay(5, "acc1", 700), 1300)
        self.assertEqual(self.bank.pay(6, "acc2", 700), 1300)
        self.assertEqual(self.bank.pay(7, "acc1", 100), 1200)
        self.assertEqual(self.bank.top_spenders(8, 2), ["acc1(800)", "acc2(700)"])


if __name__ == "__main__":
    unittest.main()

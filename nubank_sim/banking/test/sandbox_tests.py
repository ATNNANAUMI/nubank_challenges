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


class SandboxTests(unittest.TestCase):
    """Playground - edit freely. These do not affect scoring."""

    failureException = Exception

    def setUp(self):
        self.bank = BankingSystemImpl()

    @timeout(0.4)
    def test_sample(self):
        self.assertTrue(self.bank.create_account(1, "acc1"))
        self.assertEqual(self.bank.deposit(2, "acc1", 1000), 1000)
        self.assertEqual(self.bank.pay(3, "acc1", 400), 600)


if __name__ == "__main__":
    unittest.main()

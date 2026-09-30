import inspect, os, sys
frame = inspect.currentframe()
if frame is None:
    exit()
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(frame)))
sys.path.insert(0, current_dir)

from timeout_decorator import timeout
import unittest
from cloud.cloud_storage_system_impl import CloudStorageSystemImpl


class Level1Tests(unittest.TestCase):
    """10 tests for Level 1. All have the same score. Do not modify this file."""

    failureException = Exception

    def setUp(self):  # type: ignore
        self.cloud = CloudStorageSystemImpl()

    @timeout(0.4)
    def test_level_1_case_01_add_file(self):
        self.assertTrue(self.cloud.add_file(1, "a.txt", 100))
        self.assertTrue(self.cloud.add_file(2, "b.txt", 200))

    @timeout(0.4)
    def test_level_1_case_02_add_duplicate_file(self):
        self.assertTrue(self.cloud.add_file(1, "a.txt", 100))
        self.assertFalse(self.cloud.add_file(2, "a.txt", 50))

    @timeout(0.4)
    def test_level_1_case_03_get_file_size_returns_size(self):
        self.assertTrue(self.cloud.add_file(1, "a.txt", 100))
        self.assertEqual(self.cloud.get_file_size(2, "a.txt"), 100)

    @timeout(0.4)
    def test_level_1_case_04_get_file_size_missing_file(self):
        self.assertIsNone(self.cloud.get_file_size(1, "a.txt"))
        self.assertTrue(self.cloud.add_file(2, "a.txt", 50))
        self.assertEqual(self.cloud.get_file_size(3, "a.txt"), 50)

    @timeout(0.4)
    def test_level_1_case_05_delete_file_returns_size(self):
        self.assertTrue(self.cloud.add_file(1, "a.txt", 100))
        self.assertEqual(self.cloud.delete_file(2, "a.txt"), 100)
        self.assertIsNone(self.cloud.get_file_size(3, "a.txt"))

    @timeout(0.4)
    def test_level_1_case_06_delete_missing_file(self):
        self.assertIsNone(self.cloud.delete_file(1, "a.txt"))

    @timeout(0.4)
    def test_level_1_case_07_delete_then_readd(self):
        self.assertTrue(self.cloud.add_file(1, "a.txt", 100))
        self.assertEqual(self.cloud.delete_file(2, "a.txt"), 100)
        self.assertTrue(self.cloud.add_file(3, "a.txt", 50))
        self.assertEqual(self.cloud.get_file_size(4, "a.txt"), 50)

    @timeout(0.4)
    def test_level_1_case_08_multiple_files_independent(self):
        self.assertTrue(self.cloud.add_file(1, "a.txt", 100))
        self.assertTrue(self.cloud.add_file(2, "b.txt", 200))
        self.assertEqual(self.cloud.get_file_size(3, "a.txt"), 100)
        self.assertEqual(self.cloud.get_file_size(4, "b.txt"), 200)
        self.assertEqual(self.cloud.delete_file(5, "a.txt"), 100)
        self.assertEqual(self.cloud.get_file_size(6, "b.txt"), 200)

    @timeout(0.4)
    def test_level_1_case_09_zero_size_file(self):
        self.assertTrue(self.cloud.add_file(1, "empty.txt", 0))
        self.assertEqual(self.cloud.get_file_size(2, "empty.txt"), 0)
        self.assertEqual(self.cloud.delete_file(3, "empty.txt"), 0)

    @timeout(0.4)
    def test_level_1_case_10_mixed_operations(self):
        self.assertTrue(self.cloud.add_file(1, "x", 10))
        self.assertFalse(self.cloud.add_file(2, "x", 20))
        self.assertIsNone(self.cloud.delete_file(3, "y"))
        self.assertTrue(self.cloud.add_file(4, "y", 5))
        self.assertEqual(self.cloud.get_file_size(5, "y"), 5)
        self.assertEqual(self.cloud.delete_file(6, "x"), 10)
        self.assertIsNone(self.cloud.get_file_size(7, "x"))
        self.assertEqual(self.cloud.delete_file(8, "y"), 5)
        self.assertIsNone(self.cloud.get_file_size(9, "y"))


if __name__ == "__main__":
    unittest.main()

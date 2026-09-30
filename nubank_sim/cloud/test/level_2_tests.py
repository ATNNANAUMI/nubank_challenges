import inspect, os, sys
frame = inspect.currentframe()
if frame is None:
    exit()
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(frame)))
sys.path.insert(0, current_dir)

from timeout_decorator import timeout
import unittest
from cloud.cloud_storage_system_impl import CloudStorageSystemImpl


class Level2Tests(unittest.TestCase):
    """10 tests for Level 2. All have the same score. Do not modify this file."""

    failureException = Exception

    def setUp(self):
        self.cloud = CloudStorageSystemImpl()

    @timeout(0.4)
    def test_level_2_case_01_empty_ranking(self):
        self.assertEqual(self.cloud.get_n_largest(1, "", 3), [])

    @timeout(0.4)
    def test_level_2_case_02_single_match(self):
        self.assertTrue(self.cloud.add_file(1, "a", 100))
        self.assertEqual(self.cloud.get_n_largest(2, "a", 1), ["a(100)"])

    @timeout(0.4)
    def test_level_2_case_03_prefix_filters_non_matching(self):
        self.assertTrue(self.cloud.add_file(1, "apple", 10))
        self.assertTrue(self.cloud.add_file(2, "banana", 20))
        self.assertEqual(self.cloud.get_n_largest(3, "a", 5), ["apple(10)"])

    @timeout(0.4)
    def test_level_2_case_04_ordering_by_size(self):
        self.assertTrue(self.cloud.add_file(1, "a1", 100))
        self.assertTrue(self.cloud.add_file(2, "a2", 300))
        self.assertTrue(self.cloud.add_file(3, "a3", 200))
        self.assertEqual(
            self.cloud.get_n_largest(4, "a", 3), ["a2(300)", "a3(200)", "a1(100)"]
        )

    @timeout(0.4)
    def test_level_2_case_05_tie_broken_alphabetically(self):
        self.assertTrue(self.cloud.add_file(1, "c", 50))
        self.assertTrue(self.cloud.add_file(2, "a", 50))
        self.assertTrue(self.cloud.add_file(3, "b", 50))
        self.assertEqual(
            self.cloud.get_n_largest(4, "", 3), ["a(50)", "b(50)", "c(50)"]
        )

    @timeout(0.4)
    def test_level_2_case_06_n_larger_than_matches(self):
        self.assertTrue(self.cloud.add_file(1, "z1", 10))
        self.assertEqual(self.cloud.get_n_largest(2, "z", 10), ["z1(10)"])

    @timeout(0.4)
    def test_level_2_case_07_n_smaller_than_matches(self):
        self.assertTrue(self.cloud.add_file(1, "m1", 100))
        self.assertTrue(self.cloud.add_file(2, "m2", 300))
        self.assertTrue(self.cloud.add_file(3, "m3", 200))
        self.assertEqual(self.cloud.get_n_largest(4, "m", 2), ["m2(300)", "m3(200)"])

    @timeout(0.4)
    def test_level_2_case_08_empty_prefix_matches_all(self):
        self.assertTrue(self.cloud.add_file(1, "a", 10))
        self.assertTrue(self.cloud.add_file(2, "b", 30))
        self.assertTrue(self.cloud.add_file(3, "c", 20))
        self.assertEqual(
            self.cloud.get_n_largest(4, "", 3), ["b(30)", "c(20)", "a(10)"]
        )

    @timeout(0.4)
    def test_level_2_case_09_deleted_file_excluded(self):
        self.assertTrue(self.cloud.add_file(1, "d1", 100))
        self.assertTrue(self.cloud.add_file(2, "d2", 50))
        self.assertEqual(self.cloud.delete_file(3, "d1"), 100)
        self.assertEqual(self.cloud.get_n_largest(4, "d", 5), ["d2(50)"])

    @timeout(0.4)
    def test_level_2_case_10_mixed_prefixes(self):
        self.assertTrue(self.cloud.add_file(1, "docA", 10))
        self.assertTrue(self.cloud.add_file(2, "docB", 40))
        self.assertTrue(self.cloud.add_file(3, "imgA", 90))
        self.assertEqual(
            self.cloud.get_n_largest(4, "doc", 2), ["docB(40)", "docA(10)"]
        )
        self.assertEqual(self.cloud.get_n_largest(5, "img", 1), ["imgA(90)"])


if __name__ == "__main__":
    unittest.main()

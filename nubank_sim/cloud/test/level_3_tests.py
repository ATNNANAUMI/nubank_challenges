import inspect, os, sys
frame = inspect.currentframe()
if frame is None:
    exit()
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(frame)))
sys.path.insert(0, current_dir)

from timeout_decorator import timeout
import unittest
from cloud.cloud_storage_system_impl import CloudStorageSystemImpl


class Level3Tests(unittest.TestCase):
    """10 tests for Level 3. All have the same score. Do not modify this file."""

    failureException = Exception

    def setUp(self):
        self.cloud = CloudStorageSystemImpl()

    @timeout(0.4)
    def test_level_3_case_01_add_user(self):
        self.assertTrue(self.cloud.add_user(1, "u1", 1000))
        self.assertTrue(self.cloud.add_user(2, "u2", 500))

    @timeout(0.4)
    def test_level_3_case_02_add_duplicate_user(self):
        self.assertTrue(self.cloud.add_user(1, "u1", 1000))
        self.assertFalse(self.cloud.add_user(2, "u1", 500))

    @timeout(0.4)
    def test_level_3_case_03_add_file_by_returns_remaining_capacity(self):
        self.assertTrue(self.cloud.add_user(1, "u1", 1000))
        self.assertEqual(self.cloud.add_file_by(2, "u1", "f1", 300), 700)
        self.assertEqual(self.cloud.add_file_by(3, "u1", "f2", 200), 500)

    @timeout(0.4)
    def test_level_3_case_04_add_file_by_missing_user(self):
        self.assertIsNone(self.cloud.add_file_by(1, "nouser", "f1", 100))

    @timeout(0.4)
    def test_level_3_case_05_add_file_by_capacity_enforced(self):
        self.assertTrue(self.cloud.add_user(1, "u1", 100))
        self.assertEqual(self.cloud.add_file_by(2, "u1", "f1", 50), 50)
        self.assertIsNone(self.cloud.add_file_by(3, "u1", "f2", 60))
        self.assertEqual(self.cloud.add_file_by(4, "u1", "f2", 50), 0)

    @timeout(0.4)
    def test_level_3_case_06_add_file_by_duplicate_name_same_user(self):
        self.assertTrue(self.cloud.add_user(1, "u1", 1000))
        self.assertEqual(self.cloud.add_file_by(2, "u1", "f1", 100), 900)
        self.assertIsNone(self.cloud.add_file_by(3, "u1", "f1", 50))

    @timeout(0.4)
    def test_level_3_case_07_same_filename_different_users_allowed(self):
        self.assertTrue(self.cloud.add_user(1, "u1", 1000))
        self.assertTrue(self.cloud.add_user(2, "u2", 1000))
        self.assertEqual(self.cloud.add_file_by(3, "u1", "shared.txt", 100), 900)
        self.assertEqual(self.cloud.add_file_by(4, "u2", "shared.txt", 200), 800)

    @timeout(0.4)
    def test_level_3_case_08_delete_file_by_frees_capacity(self):
        self.assertTrue(self.cloud.add_user(1, "u1", 1000))
        self.assertEqual(self.cloud.add_file_by(2, "u1", "f1", 300), 700)
        self.assertEqual(self.cloud.delete_file_by(3, "u1", "f1"), 1000)
        self.assertEqual(self.cloud.add_file_by(4, "u1", "f2", 1000), 0)

    @timeout(0.4)
    def test_level_3_case_09_delete_file_by_corner_cases(self):
        self.assertIsNone(self.cloud.delete_file_by(1, "nouser", "f1"))
        self.assertTrue(self.cloud.add_user(2, "u1", 1000))
        self.assertIsNone(self.cloud.delete_file_by(3, "u1", "missing"))

    @timeout(0.4)
    def test_level_3_case_10_ranking_across_owned_and_ownerless_files(self):
        self.assertTrue(self.cloud.add_file(1, "anon1", 500))
        self.assertTrue(self.cloud.add_user(2, "u1", 1000))
        self.assertEqual(self.cloud.add_file_by(3, "u1", "u1file", 700), 300)
        self.assertEqual(
            self.cloud.get_n_largest(4, "", 2), ["u1file(700)", "anon1(500)"]
        )


if __name__ == "__main__":
    unittest.main()

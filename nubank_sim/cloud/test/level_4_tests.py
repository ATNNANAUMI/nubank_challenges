import inspect, os, sys
frame = inspect.currentframe()
if frame is None:
    exit()
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(frame)))
sys.path.insert(0, current_dir)

from timeout_decorator import timeout
import unittest
from cloud.cloud_storage_system_impl import CloudStorageSystemImpl


class Level4Tests(unittest.TestCase):
    """10 tests for Level 4. All have the same score. Do not modify this file."""

    failureException = Exception

    def setUp(self):
        self.cloud = CloudStorageSystemImpl()

    @timeout(0.4)
    def test_level_4_case_01_merge_sums_capacity_and_usage(self):
        self.assertTrue(self.cloud.add_user(1, "a", 1000))
        self.assertTrue(self.cloud.add_user(2, "b", 500))
        self.assertEqual(self.cloud.add_file_by(3, "a", "f1", 200), 800)
        self.assertEqual(self.cloud.add_file_by(4, "b", "f2", 100), 400)
        self.assertTrue(self.cloud.merge_user(5, "a", "b"))
        self.assertEqual(self.cloud.add_file_by(6, "a", "f3", 1200), 0)
        self.assertIsNone(self.cloud.add_file_by(7, "b", "f4", 10))

    @timeout(0.4)
    def test_level_4_case_02_merge_renames_colliding_filenames(self):
        self.assertTrue(self.cloud.add_user(1, "a", 1000))
        self.assertTrue(self.cloud.add_user(2, "b", 1000))
        self.assertEqual(self.cloud.add_file_by(3, "a", "report", 100), 900)
        self.assertEqual(self.cloud.add_file_by(4, "b", "report", 50), 950)
        self.assertTrue(self.cloud.merge_user(5, "a", "b"))
        self.assertEqual(
            self.cloud.get_n_largest(6, "report", 5),
            ["report(100)", "report (merged)(50)"],
        )

    @timeout(0.4)
    def test_level_4_case_03_merge_corner_cases(self):
        self.assertTrue(self.cloud.add_user(1, "a", 100))
        self.assertFalse(self.cloud.merge_user(2, "a", "a"))     # same user
        self.assertFalse(self.cloud.merge_user(3, "a", "x"))     # missing target
        self.assertFalse(self.cloud.merge_user(4, "x", "a"))     # missing source
        self.assertFalse(self.cloud.merge_user(5, "x", "y"))     # both missing

    @timeout(0.4)
    def test_level_4_case_04_merge_reassigns_files(self):
        self.assertTrue(self.cloud.add_user(1, "a", 1000))
        self.assertTrue(self.cloud.add_user(2, "b", 1000))
        self.assertEqual(self.cloud.add_file_by(3, "b", "f1", 300), 700)
        self.assertTrue(self.cloud.merge_user(4, "a", "b"))
        self.assertEqual(self.cloud.delete_file_by(5, "a", "f1"), 2000)
        self.assertIsNone(self.cloud.delete_file_by(6, "b", "f1"))

    @timeout(0.4)
    def test_level_4_case_05_backup_and_restore_basic(self):
        self.assertTrue(self.cloud.add_user(1, "a", 1000))
        self.assertEqual(self.cloud.add_file_by(2, "a", "f1", 300), 700)
        self.assertEqual(self.cloud.backup_user(3, "a"), 1)
        self.assertEqual(self.cloud.add_file_by(4, "a", "f2", 200), 500)
        self.assertEqual(self.cloud.delete_file_by(5, "a", "f1"), 800)
        self.assertEqual(self.cloud.get_n_largest(6, "f", 5), ["f2(200)"])
        self.assertEqual(self.cloud.restore_user(7, "a"), 1)
        self.assertEqual(self.cloud.get_n_largest(8, "f", 5), ["f1(300)"])

    @timeout(0.4)
    def test_level_4_case_06_backup_missing_user(self):
        self.assertIsNone(self.cloud.backup_user(1, "nouser"))

    @timeout(0.4)
    def test_level_4_case_07_restore_without_backup(self):
        self.assertTrue(self.cloud.add_user(1, "a", 1000))
        self.assertIsNone(self.cloud.restore_user(2, "a"))

    @timeout(0.4)
    def test_level_4_case_08_restore_missing_user(self):
        self.assertIsNone(self.cloud.restore_user(1, "nouser"))

    @timeout(0.4)
    def test_level_4_case_09_backup_overwritten_by_new_backup(self):
        self.assertTrue(self.cloud.add_user(1, "a", 1000))
        self.assertEqual(self.cloud.add_file_by(2, "a", "f1", 100), 900)
        self.assertEqual(self.cloud.backup_user(3, "a"), 1)
        self.assertEqual(self.cloud.add_file_by(4, "a", "f2", 100), 800)
        self.assertEqual(self.cloud.backup_user(5, "a"), 2)
        self.assertEqual(self.cloud.delete_file_by(6, "a", "f1"), 900)
        self.assertEqual(self.cloud.restore_user(7, "a"), 2)
        self.assertEqual(
            self.cloud.get_n_largest(8, "f", 5), ["f1(100)", "f2(100)"]
        )

    @timeout(0.4)
    def test_level_4_case_10_full_scenario(self):
        self.assertTrue(self.cloud.add_user(1, "a", 1000))
        self.assertTrue(self.cloud.add_user(2, "b", 500))
        self.assertEqual(self.cloud.add_file_by(3, "a", "x", 200), 800)
        self.assertEqual(self.cloud.add_file_by(4, "b", "y", 100), 400)
        self.assertEqual(self.cloud.backup_user(5, "a"), 1)
        self.assertTrue(self.cloud.merge_user(6, "a", "b"))
        self.assertEqual(self.cloud.add_file_by(7, "a", "z", 1200), 0)
        self.assertEqual(self.cloud.restore_user(8, "a"), 1)
        self.assertEqual(self.cloud.get_n_largest(9, "", 5), ["x(200)"])
        self.assertEqual(self.cloud.add_file_by(10, "a", "w", 800), 0)


if __name__ == "__main__":
    unittest.main()

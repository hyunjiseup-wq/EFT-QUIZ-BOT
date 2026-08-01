import tempfile
import unittest
from pathlib import Path

import database
import load_test


class LoadTestToolTests(unittest.TestCase):
    def test_small_load_run_is_isolated_and_consistent(self):
        operating_path = database.DB_PATH
        temp_root = Path(tempfile.gettempdir())
        directories_before = set(temp_root.glob("tarkov-quiz-load-*"))

        result = load_test.run_load_test(
            participants=50,
            attempts_per_user=2,
            concurrent_reads=10,
        )

        self.assertEqual(database.DB_PATH, operating_path)
        self.assertEqual(result.participants, 50)
        self.assertEqual(result.attempts, 100)
        self.assertGreaterEqual(result.leaderboard_rows, 50)
        self.assertGreater(result.database_bytes, 0)
        self.assertEqual(
            set(temp_root.glob("tarkov-quiz-load-*")),
            directories_before,
        )

    def test_load_run_rejects_unsafe_sizes(self):
        with self.assertRaises(ValueError):
            load_test.run_load_test(participants=0)
        with self.assertRaises(ValueError):
            load_test.run_load_test(participants=1)
        with self.assertRaises(ValueError):
            load_test.run_load_test(participants=1, attempts_per_user=21)


if __name__ == "__main__":
    unittest.main()

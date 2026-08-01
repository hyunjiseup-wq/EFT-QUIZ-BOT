import asyncio
import tempfile
import unittest
from pathlib import Path

import database
import load_test
from quiz_session import QuizSession, active_sessions


class LoadTestToolTests(unittest.TestCase):
    def test_small_load_run_is_isolated_and_consistent(self):
        operating_path = database.DB_PATH
        temp_root = Path(tempfile.gettempdir())
        directories_before = set(temp_root.glob("tarkov-quiz-load-*"))

        result = load_test.run_load_test(
            participants=50,
            attempts_per_user=2,
            concurrent_reads=10,
            session_capacity=10,
        )

        self.assertEqual(database.DB_PATH, operating_path)
        self.assertEqual(result.participants, 50)
        self.assertEqual(result.attempts, 100)
        self.assertGreaterEqual(result.leaderboard_rows, 50)
        self.assertGreater(result.database_bytes, 0)
        self.assertEqual(result.concurrent_reads, 10)
        self.assertEqual(result.concurrent_sessions, 10)
        self.assertFalse(active_sessions)
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
        with self.assertRaises(ValueError):
            load_test.run_load_test(session_capacity=0)

    def test_session_load_rejects_nonempty_registry_without_mutating_it(self):
        existing = QuizSession(
            mode="pvp",
            guild_id=1,
            user_id=1,
            username="기존 세션",
            channel_id=1,
            questions=[{"id": 1}],
        )
        active_sessions[(1, 1)] = existing
        try:
            with self.assertRaisesRegex(RuntimeError, "빈 활성 세션"):
                asyncio.run(load_test._run_session_load(2))
            self.assertIs(active_sessions[(1, 1)], existing)
        finally:
            active_sessions.clear()


if __name__ == "__main__":
    unittest.main()

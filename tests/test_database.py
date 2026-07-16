import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import database


class DatabaseTests(unittest.TestCase):
    def test_record_result_keeps_best_and_accumulates_totals(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "leaderboard.db"
            with patch.object(database, "DB_PATH", path):
                database.init_db()
                database.record_result(10, 1, "테스터", 100, 4, 5)
                database.record_result(10, 1, "테스터", 80, 3, 5)

                self.assertEqual(
                    database.get_user_record(10, 1),
                    ("테스터", 100, 80, 2, 7, 10),
                )

    def test_records_are_isolated_by_guild(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "leaderboard.db"
            with patch.object(database, "DB_PATH", path):
                database.init_db()
                database.record_result(10, 1, "서버10", 100, 4, 5)
                database.record_result(20, 1, "서버20", 80, 3, 5)

                self.assertEqual(database.get_user_record(10, 1)[0], "서버10")
                self.assertEqual(database.get_user_record(20, 1)[0], "서버20")
                self.assertEqual(database.reset_leaderboard(10), 1)
                self.assertIsNone(database.get_user_record(10, 1))
                self.assertIsNotNone(database.get_user_record(20, 1))

    def test_init_db_migrates_legacy_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.db"
            with closing(sqlite3.connect(path)) as connection:
                connection.execute(
                    """
                    CREATE TABLE leaderboard (
                        user_id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        best_score INTEGER NOT NULL DEFAULT 0,
                        last_score INTEGER NOT NULL DEFAULT 0,
                        total_correct INTEGER NOT NULL DEFAULT 0,
                        total_questions INTEGER NOT NULL DEFAULT 0,
                        attempts INTEGER NOT NULL DEFAULT 0,
                        last_played_at TEXT
                    )
                    """
                )
                connection.execute(
                    """
                    INSERT INTO leaderboard
                        (user_id, username, best_score, last_score, total_correct,
                         total_questions, attempts, last_played_at)
                    VALUES ('1', '레거시', 100, 100, 4, 5, 1, '2026-01-01T00:00:00+00:00')
                    """
                )
                connection.commit()

            with patch.object(database, "DB_PATH", path):
                database.init_db()

            with closing(sqlite3.connect(path)) as connection:
                columns = {row[1] for row in connection.execute("PRAGMA table_info(leaderboard)")}
                legacy = connection.execute(
                    "SELECT guild_id, best_achieved_at FROM leaderboard"
                ).fetchone()
            self.assertIn("guild_id", columns)
            self.assertIn("best_achieved_at", columns)
            self.assertEqual(legacy, ("0", "2026-01-01T00:00:00+00:00"))


if __name__ == "__main__":
    unittest.main()

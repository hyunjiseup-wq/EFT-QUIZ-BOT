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
                database.record_result(10, "pvp", 1, "테스터", 100, 4, 5)
                database.record_result(10, "pvp", 1, "테스터", 80, 3, 5)

                self.assertEqual(
                    database.get_user_record(10, "pvp", 1),
                    ("테스터", 100, 80, 2, 7, 10),
                )

    def test_records_are_isolated_by_guild(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "leaderboard.db"
            with patch.object(database, "DB_PATH", path):
                database.init_db()
                database.record_result(10, "pvp", 1, "서버10", 100, 4, 5)
                database.record_result(20, "pvp", 1, "서버20", 80, 3, 5)

                self.assertEqual(database.get_user_record(10, "pvp", 1)[0], "서버10")
                self.assertEqual(database.get_user_record(20, "pvp", 1)[0], "서버20")
                self.assertEqual(database.reset_leaderboard(10), 1)
                self.assertIsNone(database.get_user_record(10, "pvp", 1))
                self.assertIsNotNone(database.get_user_record(20, "pvp", 1))

    def test_records_are_isolated_by_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "leaderboard.db"
            with patch.object(database, "DB_PATH", path):
                database.init_db()
                database.record_result(10, "pvp", 1, "테스터", 100, 4, 5)
                database.record_result(10, "pve", 1, "테스터", 80, 3, 5)

                self.assertEqual(database.get_user_record(10, "pvp", 1)[1], 100)
                self.assertEqual(database.get_user_record(10, "pve", 1)[1], 80)
                self.assertEqual(len(database.get_leaderboard(10, "pvp")), 1)
                self.assertEqual(len(database.get_leaderboard(10, "pve")), 1)

    def test_public_stats_count_unique_users_and_all_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "leaderboard.db"
            with patch.object(database, "DB_PATH", path):
                database.init_db()
                database.record_result(10, "pvp", 1, "한모드", 100, 4, 5)
                database.record_result(10, "pvp", 1, "한모드", 120, 5, 5)
                database.record_result(10, "pve", 1, "한모드", 80, 3, 5)
                database.record_result(10, "pve", 2, "두번째", 60, 2, 5)

                stats = database.get_public_stats(10)

            self.assertEqual(stats["total_participants"], 2)
            self.assertEqual(stats["total_attempts"], 4)
            self.assertEqual(stats["modes"]["pvp"], {"participants": 1, "attempts": 2})
            self.assertEqual(stats["modes"]["pve"], {"participants": 2, "attempts": 2})

    def test_hidden_reward_candidates_use_detailed_attempt_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "leaderboard.db"
            with patch.object(database, "DB_PATH", path):
                database.init_db()
                database.record_result(10, "pvp", 1, "성장형", 100, 4, 5)
                database.record_result(10, "pvp", 1, "성장형", 300, 5, 5)
                database.record_result(10, "pvp", 2, "올라운더", 10, 1, 5)
                database.record_result(10, "pve", 2, "올라운더", 20, 2, 5)

                report = database.get_hidden_reward_candidates(
                    10,
                    "2020-01-01T00:00:00+00:00",
                )

            self.assertEqual(report["participants"], 2)
            self.assertEqual(report["attempts"], 4)
            self.assertEqual(report["growth"][0]["username"], "성장형")
            self.assertEqual(report["growth"][0]["improvement"], 200)
            self.assertEqual(report["underdogs"][0]["username"], "올라운더")
            self.assertEqual(report["dual_mode"][0]["username"], "올라운더")

    def test_reset_removes_detailed_attempt_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "leaderboard.db"
            with patch.object(database, "DB_PATH", path):
                database.init_db()
                database.record_result(10, "pvp", 1, "삭제대상", 100, 4, 5)

                database.reset_leaderboard(10)
                report = database.get_hidden_reward_candidates(
                    10,
                    "2020-01-01T00:00:00+00:00",
                )

            self.assertEqual(report["participants"], 0)
            self.assertEqual(report["attempts"], 0)

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
                    "SELECT guild_id, mode, best_achieved_at FROM leaderboard"
                ).fetchone()
            self.assertIn("guild_id", columns)
            self.assertIn("mode", columns)
            self.assertIn("best_achieved_at", columns)
            self.assertEqual(legacy, ("0", "legacy", "2026-01-01T00:00:00+00:00"))
            with closing(sqlite3.connect(path)) as connection:
                attempts_table = connection.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type = 'table' AND name = 'quiz_attempts'
                    """
                ).fetchone()
            self.assertEqual(attempts_table, ("quiz_attempts",))


if __name__ == "__main__":
    unittest.main()

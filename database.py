import sqlite3
import threading
from contextlib import closing
from datetime import datetime, timezone

from config import DB_PATH

_lock = threading.Lock()


def init_db():
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        columns = {row[1]: row for row in conn.execute("PRAGMA table_info(leaderboard)")}
        if columns and "guild_id" not in columns:
            # 구버전 기록에는 어느 서버에서 생성됐는지 정보가 없다. 삭제하지 않고
            # guild_id=0인 레거시 영역에 보존하되 실제 서버 랭킹에는 섞지 않는다.
            conn.execute("ALTER TABLE leaderboard RENAME TO leaderboard_legacy")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leaderboard (
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                best_score INTEGER NOT NULL DEFAULT 0,
                last_score INTEGER NOT NULL DEFAULT 0,
                total_correct INTEGER NOT NULL DEFAULT 0,
                total_questions INTEGER NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_played_at TEXT,
                best_achieved_at TEXT,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )
        if columns and "guild_id" not in columns:
            legacy_columns = {
                row[1] for row in conn.execute("PRAGMA table_info(leaderboard_legacy)")
            }
            best_time = (
                "best_achieved_at" if "best_achieved_at" in legacy_columns else "last_played_at"
            )
            conn.execute(
                f"""
                INSERT INTO leaderboard
                    (guild_id, user_id, username, best_score, last_score, total_correct,
                     total_questions, attempts, last_played_at, best_achieved_at)
                SELECT '0', user_id, username, best_score, last_score, total_correct,
                       total_questions, attempts, last_played_at,
                       COALESCE({best_time}, last_played_at)
                FROM leaderboard_legacy
                """
            )
            conn.execute("DROP TABLE leaderboard_legacy")

        # 초기 서버별 스키마에도 이 컬럼이 없을 가능성을 고려한 소규모 마이그레이션.
        current_columns = {row[1] for row in conn.execute("PRAGMA table_info(leaderboard)")}
        if "best_achieved_at" not in current_columns:
            conn.execute("ALTER TABLE leaderboard ADD COLUMN best_achieved_at TEXT")
        conn.commit()


def record_result(guild_id: int, user_id: int, username: str, score: int, correct: int, total: int):
    """퀴즈 완료 시 결과를 저장한다.

    - best_score: 최고 기록만 유지
    - best_achieved_at: 최고 기록 경신 시 갱신하여 동점이면 먼저 달성한 사용자를 우선
    - total_correct / total_questions: 전 세션 누적
    """
    now = datetime.now(timezone.utc).isoformat()
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO leaderboard
                (guild_id, user_id, username, best_score, last_score, total_correct,
                 total_questions, attempts, last_played_at, best_achieved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET
                username = excluded.username,
                best_score = MAX(best_score, excluded.best_score),
                best_achieved_at = CASE
                    WHEN excluded.best_score > best_score THEN excluded.best_achieved_at
                    ELSE best_achieved_at
                END,
                last_score = excluded.last_score,
                total_correct = total_correct + excluded.total_correct,
                total_questions = total_questions + excluded.total_questions,
                attempts = attempts + 1,
                last_played_at = excluded.last_played_at
            """,
            (str(guild_id), str(user_id), username, score, score, correct, total, now, now),
        )
        conn.commit()


def get_leaderboard(guild_id: int, limit: int = 10):
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            """
            SELECT username, best_score, attempts, total_correct, total_questions
            FROM leaderboard
            WHERE guild_id = ?
            ORDER BY best_score DESC, best_achieved_at ASC
            LIMIT ?
            """,
            (str(guild_id), limit),
        )
        return cur.fetchall()


def reset_leaderboard(guild_id: int) -> int:
    """해당 서버의 응시 기록을 삭제하고 삭제된 행 수를 반환한다."""
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("DELETE FROM leaderboard WHERE guild_id = ?", (str(guild_id),))
        conn.commit()
        return cur.rowcount


def get_user_record(guild_id: int, user_id: int):
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            """
            SELECT username, best_score, last_score, attempts, total_correct, total_questions
            FROM leaderboard WHERE guild_id = ? AND user_id = ?
            """,
            (str(guild_id), str(user_id)),
        )
        return cur.fetchone()

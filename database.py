import sqlite3
import threading
from contextlib import closing
from datetime import datetime, timezone

from config import DB_PATH

_lock = threading.Lock()


def init_db():
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leaderboard (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                best_score INTEGER NOT NULL DEFAULT 0,
                last_score INTEGER NOT NULL DEFAULT 0,
                total_correct INTEGER NOT NULL DEFAULT 0,
                total_questions INTEGER NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_played_at TEXT,
                best_achieved_at TEXT
            )
            """
        )
        # 구버전 DB에는 best_achieved_at 컬럼이 없으므로 명시적으로 확인 후 추가한다.
        # 모든 OperationalError를 무시하면 실제 DB 손상이나 권한 오류까지 숨길 수 있다.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(leaderboard)")}
        if "best_achieved_at" not in columns:
            conn.execute("ALTER TABLE leaderboard ADD COLUMN best_achieved_at TEXT")
        conn.commit()


def record_result(user_id: int, username: str, score: int, correct: int, total: int):
    """퀴즈 완료 시 결과를 저장한다.

    - best_score: 최고 기록만 유지 (경신 시 best_achieved_at 갱신 → 동점 시 먼저 달성한 사람이 랭킹 위)
    - total_correct / total_questions: 전 세션 누적
    """
    now = datetime.now(timezone.utc).isoformat()
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO leaderboard
                (user_id, username, best_score, last_score, total_correct, total_questions,
                 attempts, last_played_at, best_achieved_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
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
            (str(user_id), username, score, score, correct, total, now, now),
        )
        conn.commit()


def get_leaderboard(limit: int = 10):
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            """
            SELECT username, best_score, attempts, total_correct, total_questions
            FROM leaderboard
            ORDER BY best_score DESC, best_achieved_at ASC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()


def reset_leaderboard() -> int:
    """전체 응시 기록을 삭제하고 삭제된 행 수를 반환한다 (관리자 전용 명령어에서 사용)."""
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("DELETE FROM leaderboard")
        conn.commit()
        return cur.rowcount


def get_user_record(user_id: int):
    with _lock, closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            """
            SELECT username, best_score, last_score, attempts, total_correct, total_questions
            FROM leaderboard WHERE user_id = ?
            """,
            (str(user_id),),
        )
        return cur.fetchone()

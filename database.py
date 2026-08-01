import sqlite3
import threading
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timezone

from config import DB_PATH

_lock = threading.Lock()
SQLITE_BUSY_TIMEOUT_MS = 30_000
SCHEMA_VERSION = 2
DASHBOARD_KINDS = {"quiz", "supervisor"}


def _connect() -> sqlite3.Connection:
    """동시 요청이 몰려도 즉시 database locked로 실패하지 않는 연결을 만든다."""
    conn = sqlite3.connect(DB_PATH, timeout=SQLITE_BUSY_TIMEOUT_MS / 1000)
    conn.execute(f"PRAGMA busy_timeout = {SQLITE_BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock, closing(_connect()) as conn:
        stored_version = conn.execute("PRAGMA user_version").fetchone()[0]
        if stored_version > SCHEMA_VERSION:
            raise RuntimeError(
                "이 DB는 더 새로운 봇에서 생성되었습니다. "
                f"DB 스키마 버전 {stored_version}, 지원 버전 {SCHEMA_VERSION}"
            )
        # WAL은 읽기가 쓰기를 막지 않으므로 랭킹 조회와 결과 저장이 몰릴 때 유리하다.
        conn.execute("PRAGMA journal_mode = WAL")
        columns = {row[1]: row for row in conn.execute("PRAGMA table_info(leaderboard)")}
        if columns and "guild_id" not in columns:
            # 구버전 기록에는 어느 서버에서 생성됐는지 정보가 없다. 삭제하지 않고
            # guild_id=0인 레거시 영역에 보존하되 실제 서버 랭킹에는 섞지 않는다.
            conn.execute("ALTER TABLE leaderboard RENAME TO leaderboard_legacy")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leaderboard (
                guild_id TEXT NOT NULL,
                mode TEXT NOT NULL DEFAULT 'legacy',
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                best_score INTEGER NOT NULL DEFAULT 0,
                last_score INTEGER NOT NULL DEFAULT 0,
                total_correct INTEGER NOT NULL DEFAULT 0,
                total_questions INTEGER NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_played_at TEXT,
                best_achieved_at TEXT,
                PRIMARY KEY (guild_id, mode, user_id)
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
        # 중간 버전의 서버별 스키마는 컬럼만 추가하면 기존 행이 NULL로 남는다.
        # 동점 순위에서 NULL이 가장 먼저 정렬되지 않도록 마지막 플레이 시각으로 보정한다.
        conn.execute(
            """
            UPDATE leaderboard
            SET best_achieved_at = last_played_at
            WHERE best_achieved_at IS NULL AND last_played_at IS NOT NULL
            """
        )

        current_columns = {row[1] for row in conn.execute("PRAGMA table_info(leaderboard)")}
        if "mode" not in current_columns:
            # 모드 분리 이전 기록은 삭제하지 않고 legacy 영역에 보존한다.
            conn.execute("ALTER TABLE leaderboard RENAME TO leaderboard_without_mode")
            conn.execute(
                """
                CREATE TABLE leaderboard (
                    guild_id TEXT NOT NULL,
                    mode TEXT NOT NULL DEFAULT 'legacy',
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    best_score INTEGER NOT NULL DEFAULT 0,
                    last_score INTEGER NOT NULL DEFAULT 0,
                    total_correct INTEGER NOT NULL DEFAULT 0,
                    total_questions INTEGER NOT NULL DEFAULT 0,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_played_at TEXT,
                    best_achieved_at TEXT,
                    PRIMARY KEY (guild_id, mode, user_id)
                )
                """
            )
            conn.execute(
                """
                INSERT INTO leaderboard
                    (guild_id, mode, user_id, username, best_score, last_score,
                     total_correct, total_questions, attempts, last_played_at,
                     best_achieved_at)
                SELECT guild_id, 'legacy', user_id, username, best_score, last_score,
                       total_correct, total_questions, attempts, last_played_at,
                       best_achieved_at
                FROM leaderboard_without_mode
                """
            )
            conn.execute("DROP TABLE leaderboard_without_mode")

        # 개별 완주 이력은 히든 상품 후보(성장 폭, 최저점, 참여 일수 등)를
        # 계산하기 위해 사용한다. 기존 leaderboard 집계는 그대로 유지한다.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                mode TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                score INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                timed_out_count INTEGER NOT NULL DEFAULT 0,
                duration_seconds REAL NOT NULL DEFAULT 0,
                completed_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_quiz_attempts_guild_completed
            ON quiz_attempts (guild_id, completed_at)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_quiz_attempts_guild_user
            ON quiz_attempts (guild_id, user_id, completed_at)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_leaderboard_ranking
            ON leaderboard (guild_id, mode, best_score DESC, best_achieved_at ASC)
            """
        )
        # 고정 권한이 없거나 메시지가 오래되어 최근 기록 밖으로 밀려도 기존 대시보드를
        # 정확히 다시 찾을 수 있도록 종류별 Discord 메시지 위치를 보존한다.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dashboard_messages (
                guild_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (guild_id, kind)
            )
            """
        )
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()


def get_dashboard_message(guild_id: int, kind: str) -> tuple[int, int] | None:
    """저장된 대시보드의 (채널 ID, 메시지 ID)를 반환한다."""
    if kind not in DASHBOARD_KINDS:
        raise ValueError(f"알 수 없는 대시보드 종류: {kind}")
    with closing(_connect()) as conn:
        row = conn.execute(
            """
            SELECT channel_id, message_id
            FROM dashboard_messages
            WHERE guild_id = ? AND kind = ?
            """,
            (str(guild_id), kind),
        ).fetchone()
    if row is None:
        return None
    return int(row[0]), int(row[1])


def save_dashboard_message(
    guild_id: int,
    kind: str,
    channel_id: int,
    message_id: int,
) -> None:
    """종류별 최신 대시보드 메시지 위치를 원자적으로 저장한다."""
    if kind not in DASHBOARD_KINDS:
        raise ValueError(f"알 수 없는 대시보드 종류: {kind}")
    now = datetime.now(timezone.utc).isoformat()
    with _lock, closing(_connect()) as conn:
        conn.execute(
            """
            INSERT INTO dashboard_messages
                (guild_id, kind, channel_id, message_id, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guild_id, kind) DO UPDATE SET
                channel_id = excluded.channel_id,
                message_id = excluded.message_id,
                updated_at = excluded.updated_at
            """,
            (str(guild_id), kind, str(channel_id), str(message_id), now),
        )
        conn.commit()


def record_result(
    guild_id: int,
    mode: str,
    user_id: int,
    username: str,
    score: int,
    correct: int,
    total: int,
    *,
    timed_out_count: int = 0,
    duration_seconds: float = 0,
):
    """퀴즈 완료 시 결과를 저장한다.

    - best_score: 최고 기록만 유지
    - best_achieved_at: 최고 기록 경신 시 갱신하여 동점이면 먼저 달성한 사용자를 우선
    - total_correct / total_questions: 전 세션 누적
    """
    now = datetime.now(timezone.utc).isoformat()
    with _lock, closing(_connect()) as conn:
        conn.execute(
            """
            INSERT INTO leaderboard
                (guild_id, mode, user_id, username, best_score, last_score, total_correct,
                 total_questions, attempts, last_played_at, best_achieved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(guild_id, mode, user_id) DO UPDATE SET
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
            (
                str(guild_id),
                mode,
                str(user_id),
                username,
                score,
                score,
                correct,
                total,
                now,
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO quiz_attempts
                (guild_id, mode, user_id, username, score, correct_count,
                 total_questions, timed_out_count, duration_seconds, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(guild_id),
                mode,
                str(user_id),
                username,
                score,
                correct,
                total,
                timed_out_count,
                max(0, float(duration_seconds)),
                now,
            ),
        )
        conn.commit()


def get_leaderboard(guild_id: int, mode: str, limit: int = 10):
    # WAL 모드에서는 읽기끼리 직렬화할 필요가 없다.
    with closing(_connect()) as conn:
        cur = conn.execute(
            """
            SELECT username, best_score, attempts, total_correct, total_questions
            FROM leaderboard
            WHERE guild_id = ? AND mode = ?
            ORDER BY best_score DESC,
                     best_achieved_at IS NULL ASC,
                     best_achieved_at ASC
            LIMIT ?
            """,
            (str(guild_id), mode, limit),
        )
        return cur.fetchall()


def reset_leaderboard(guild_id: int, mode: str | None = None) -> int:
    """해당 서버의 집계 및 개별 완주 이력을 삭제하고 집계 행 수를 반환한다."""
    with _lock, closing(_connect()) as conn:
        if mode is None:
            cur = conn.execute("DELETE FROM leaderboard WHERE guild_id = ?", (str(guild_id),))
            conn.execute("DELETE FROM quiz_attempts WHERE guild_id = ?", (str(guild_id),))
        else:
            cur = conn.execute(
                "DELETE FROM leaderboard WHERE guild_id = ? AND mode = ?",
                (str(guild_id), mode),
            )
            conn.execute(
                "DELETE FROM quiz_attempts WHERE guild_id = ? AND mode = ?",
                (str(guild_id), mode),
            )
        conn.commit()
        return cur.rowcount


def get_user_record(guild_id: int, mode: str, user_id: int):
    with closing(_connect()) as conn:
        cur = conn.execute(
            """
            SELECT username, best_score, last_score, attempts, total_correct, total_questions
            FROM leaderboard WHERE guild_id = ? AND mode = ? AND user_id = ?
            """,
            (str(guild_id), mode, str(user_id)),
        )
        return cur.fetchone()


def get_public_stats(guild_id: int) -> dict:
    """기존 집계 기록을 포함한 서버 공개 참가 현황을 반환한다."""
    guild = str(guild_id)
    with closing(_connect()) as conn:
        total_participants = conn.execute(
            """
            SELECT COUNT(DISTINCT user_id)
            FROM leaderboard
            WHERE guild_id = ? AND mode IN ('pvp', 'pve')
            """,
            (guild,),
        ).fetchone()[0]
        total_attempts = conn.execute(
            """
            SELECT COALESCE(SUM(attempts), 0)
            FROM leaderboard
            WHERE guild_id = ? AND mode IN ('pvp', 'pve')
            """,
            (guild,),
        ).fetchone()[0]
        mode_rows = conn.execute(
            """
            SELECT mode, COUNT(*), COALESCE(SUM(attempts), 0)
            FROM leaderboard
            WHERE guild_id = ? AND mode IN ('pvp', 'pve')
            GROUP BY mode
            """,
            (guild,),
        ).fetchall()

    modes = {
        "pvp": {"participants": 0, "attempts": 0},
        "pve": {"participants": 0, "attempts": 0},
    }
    for mode, participants, attempts in mode_rows:
        modes[mode] = {"participants": participants, "attempts": attempts}
    return {
        "total_participants": total_participants,
        "total_attempts": total_attempts,
        "modes": modes,
    }


def get_hidden_reward_candidates(
    guild_id: int,
    since: str,
    limit: int = 5,
) -> dict:
    """기간 내 개별 완주 이력으로 관리자용 히든 상품 후보를 계산한다."""
    users: dict[str, dict] = defaultdict(
        lambda: {
            "username": "",
            "attempts": 0,
            "active_days": set(),
            "modes": set(),
            "first_score": None,
            "later_best": None,
            "best_score": 0,
            "score_total": 0,
            "lowest_sincere_score": None,
        }
    )
    row_count = 0
    with closing(_connect()) as conn:
        cursor = conn.execute(
            """
            SELECT user_id, username, mode, score, correct_count, total_questions,
                   timed_out_count, completed_at
            FROM quiz_attempts
            WHERE guild_id = ? AND completed_at >= ?
            ORDER BY completed_at ASC, id ASC
            """,
            (str(guild_id), since),
        )
        for user_id, username, mode, score, correct, total, timed_out, completed_at in cursor:
            row_count += 1
            user = users[user_id]
            user["username"] = username
            if user["attempts"] == 0:
                user["first_score"] = score
            else:
                previous_best = user["later_best"]
                user["later_best"] = (
                    score if previous_best is None else max(previous_best, score)
                )
            user["attempts"] += 1
            user["best_score"] = max(user["best_score"], score)
            user["score_total"] += score
            user["active_days"].add(completed_at[:10])
            user["modes"].add(mode)
            if correct >= 1 and timed_out <= total / 2:
                previous_low = user["lowest_sincere_score"]
                user["lowest_sincere_score"] = (
                    score if previous_low is None else min(previous_low, score)
                )

    summaries = []
    for user_id, user in users.items():
        attempts = user["attempts"]
        first_score = user["first_score"]
        later_best = user["later_best"]
        summaries.append(
            {
                "user_id": user_id,
                "username": user["username"],
                "attempts": attempts,
                "active_days": len(user["active_days"]),
                "modes": set(user["modes"]),
                "first_score": first_score,
                "best_score": user["best_score"],
                "lowest_sincere_score": user["lowest_sincere_score"],
                "improvement": later_best - first_score if attempts >= 2 else None,
                "average_score": user["score_total"] / attempts,
            }
        )

    most_attempts = sorted(
        summaries,
        key=lambda item: (-item["attempts"], -item["active_days"], item["username"]),
    )[:limit]
    most_days = sorted(
        summaries,
        key=lambda item: (-item["active_days"], -item["attempts"], item["username"]),
    )[:limit]
    underdogs = sorted(
        (item for item in summaries if item["lowest_sincere_score"] is not None),
        key=lambda item: (
            item["lowest_sincere_score"],
            -item["attempts"],
            item["username"],
        ),
    )[:limit]
    growth = sorted(
        (
            item
            for item in summaries
            if item["improvement"] is not None and item["improvement"] > 0
        ),
        key=lambda item: (-item["improvement"], -item["attempts"], item["username"]),
    )[:limit]
    dual_mode = sorted(
        (item for item in summaries if {"pvp", "pve"} <= item["modes"]),
        key=lambda item: (-item["attempts"], -item["active_days"], item["username"]),
    )[:limit]

    return {
        "participants": len(users),
        "attempts": row_count,
        "most_attempts": most_attempts,
        "most_days": most_days,
        "underdogs": underdogs,
        "growth": growth,
        "dual_mode": dual_mode,
    }

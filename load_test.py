"""운영 DB를 사용하지 않는 타르코프 퀴즈봇 합성 부하 검사."""

from __future__ import annotations

import argparse
import sqlite3
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import database

LOAD_TEST_GUILD_ID = 8_500


@dataclass(frozen=True)
class LoadTestResult:
    participants: int
    attempts: int
    leaderboard_rows: int
    database_bytes: int
    seed_seconds: float
    report_seconds: float
    concurrent_read_seconds: float


def _bounded_integer(value: str, *, minimum: int, maximum: int) -> int:
    parsed = int(value)
    if not minimum <= parsed <= maximum:
        raise argparse.ArgumentTypeError(
            f"{minimum}~{maximum} 범위의 정수여야 합니다."
        )
    return parsed


def _build_rows(participants: int, attempts_per_user: int):
    now = datetime.now(timezone.utc)
    attempts = []
    aggregates: dict[tuple[str, str], dict] = {}

    for user_number in range(1, participants + 1):
        user_id = str(user_number)
        username = f"부하테스트-{user_number:05d}"
        primary_mode = "pvp" if user_number % 2 else "pve"
        for attempt_number in range(attempts_per_user):
            if user_number % 10 == 0 and attempt_number == attempts_per_user - 1:
                mode = "pve" if primary_mode == "pvp" else "pvp"
            else:
                mode = primary_mode
            score = (user_number * 37 + attempt_number * 113) % 1_721
            correct = 1 + (user_number + attempt_number) % 30
            timed_out = (user_number + attempt_number) % 4
            completed = now - timedelta(
                days=(user_number + attempt_number) % 30,
                seconds=attempt_number,
            )
            completed_at = completed.isoformat()
            attempts.append(
                (
                    str(LOAD_TEST_GUILD_ID),
                    mode,
                    user_id,
                    username,
                    score,
                    correct,
                    30,
                    timed_out,
                    240 + attempt_number,
                    completed_at,
                )
            )

            key = (mode, user_id)
            aggregate = aggregates.get(key)
            if aggregate is None:
                aggregates[key] = {
                    "username": username,
                    "best_score": score,
                    "last_score": score,
                    "total_correct": correct,
                    "total_questions": 30,
                    "attempts": 1,
                    "last_played_at": completed_at,
                    "best_achieved_at": completed_at,
                }
                continue
            if score > aggregate["best_score"]:
                aggregate["best_score"] = score
                aggregate["best_achieved_at"] = completed_at
            aggregate["last_score"] = score
            aggregate["total_correct"] += correct
            aggregate["total_questions"] += 30
            aggregate["attempts"] += 1
            aggregate["last_played_at"] = max(
                aggregate["last_played_at"], completed_at
            )

    leaderboard = [
        (
            str(LOAD_TEST_GUILD_ID),
            mode,
            user_id,
            values["username"],
            values["best_score"],
            values["last_score"],
            values["total_correct"],
            values["total_questions"],
            values["attempts"],
            values["last_played_at"],
            values["best_achieved_at"],
        )
        for (mode, user_id), values in aggregates.items()
    ]
    return leaderboard, attempts


def _seed_database(path: Path, participants: int, attempts_per_user: int) -> tuple[int, int]:
    leaderboard, attempts = _build_rows(participants, attempts_per_user)
    with closing(sqlite3.connect(path)) as connection:
        connection.executemany(
            """
            INSERT INTO leaderboard
                (guild_id, mode, user_id, username, best_score, last_score,
                 total_correct, total_questions, attempts, last_played_at,
                 best_achieved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            leaderboard,
        )
        connection.executemany(
            """
            INSERT INTO quiz_attempts
                (guild_id, mode, user_id, username, score, correct_count,
                 total_questions, timed_out_count, duration_seconds, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            attempts,
        )
        connection.commit()
    return len(leaderboard), len(attempts)


def run_load_test(
    participants: int = 8_500,
    attempts_per_user: int = 3,
    *,
    concurrent_reads: int = 200,
) -> LoadTestResult:
    if not 2 <= participants <= 100_000:
        raise ValueError("participants는 2~100000 범위여야 합니다.")
    if not 1 <= attempts_per_user <= 20:
        raise ValueError("attempts_per_user는 1~20 범위여야 합니다.")
    if not 1 <= concurrent_reads <= 10_000:
        raise ValueError("concurrent_reads는 1~10000 범위여야 합니다.")

    original_path = database.DB_PATH
    with tempfile.TemporaryDirectory(
        prefix="tarkov-quiz-load-", ignore_cleanup_errors=True
    ) as directory:
        load_path = Path(directory) / "synthetic-load.db"
        if load_path.resolve() == original_path.resolve():
            raise RuntimeError("부하 검사 DB가 운영 DB와 같아 실행을 중단합니다.")

        try:
            database.DB_PATH = load_path
            database.init_db()

            started = time.perf_counter()
            leaderboard_rows, attempt_rows = _seed_database(
                load_path, participants, attempts_per_user
            )
            seed_seconds = time.perf_counter() - started

            started = time.perf_counter()
            stats = database.get_public_stats(LOAD_TEST_GUILD_ID)
            pvp_ranking = database.get_leaderboard(LOAD_TEST_GUILD_ID, "pvp", 10)
            pve_ranking = database.get_leaderboard(LOAD_TEST_GUILD_ID, "pve", 10)
            report = database.get_hidden_reward_candidates(
                LOAD_TEST_GUILD_ID,
                "2000-01-01T00:00:00+00:00",
                5,
            )
            report_seconds = time.perf_counter() - started

            expected_attempts = participants * attempts_per_user
            if stats["total_participants"] != participants:
                raise AssertionError("공개 통계 참가자 수가 합성 데이터와 다릅니다.")
            if stats["total_attempts"] != expected_attempts:
                raise AssertionError("공개 통계 완주 횟수가 합성 데이터와 다릅니다.")
            if report["participants"] != participants:
                raise AssertionError("히든 후보 참가자 수가 합성 데이터와 다릅니다.")
            if report["attempts"] != expected_attempts:
                raise AssertionError("히든 후보 완주 횟수가 합성 데이터와 다릅니다.")
            if not pvp_ranking or not pve_ranking:
                raise AssertionError("PvP/PvE 랭킹 중 하나가 비어 있습니다.")

            started = time.perf_counter()
            with ThreadPoolExecutor(max_workers=min(32, concurrent_reads)) as executor:
                futures = [
                    executor.submit(
                        database.get_leaderboard,
                        LOAD_TEST_GUILD_ID,
                        "pvp" if index % 2 else "pve",
                        10,
                    )
                    for index in range(concurrent_reads)
                ]
                for future in futures:
                    if not future.result(timeout=30):
                        raise AssertionError("동시 랭킹 조회 결과가 비어 있습니다.")
            concurrent_read_seconds = time.perf_counter() - started
            database_bytes = sum(
                candidate.stat().st_size
                for candidate in load_path.parent.glob(f"{load_path.name}*")
            )

            return LoadTestResult(
                participants=participants,
                attempts=attempt_rows,
                leaderboard_rows=leaderboard_rows,
                database_bytes=database_bytes,
                seed_seconds=seed_seconds,
                report_seconds=report_seconds,
                concurrent_read_seconds=concurrent_read_seconds,
            )
        finally:
            database.DB_PATH = original_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="운영 DB와 분리된 임시 DB에서 퀴즈봇 대규모 집계를 검증합니다."
    )
    parser.add_argument(
        "--participants",
        type=lambda value: _bounded_integer(value, minimum=2, maximum=100_000),
        default=8_500,
        help="합성 참가자 수 (기본 8500)",
    )
    parser.add_argument(
        "--attempts",
        type=lambda value: _bounded_integer(value, minimum=1, maximum=20),
        default=3,
        help="참가자당 완주 횟수 (기본 3)",
    )
    args = parser.parse_args()
    result = run_load_test(args.participants, args.attempts)
    print("합성 부하 검사 통과")
    print(f"참가자: {result.participants:,}명")
    print(f"완주 이력: {result.attempts:,}건")
    print(f"랭킹 행: {result.leaderboard_rows:,}행")
    print(f"임시 DB 크기: {result.database_bytes / 1024 / 1024:.2f} MiB")
    print(f"데이터 생성: {result.seed_seconds:.3f}초")
    print(f"통계·랭킹·히든 후보: {result.report_seconds:.3f}초")
    print(f"동시 랭킹 200회: {result.concurrent_read_seconds:.3f}초")


if __name__ == "__main__":
    main()

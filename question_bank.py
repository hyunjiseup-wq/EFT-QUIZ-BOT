"""문제 데이터 로딩, 검증, 세션 출제를 담당하는 순수 Python 모듈."""

from __future__ import annotations

import json
import random
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

CATEGORIES = (
    "스토리",
    "퀘스트",
    "맵",
    "보스·AI",
    "상인",
    "무기",
    "탄약",
    "장비",
    "의료·식량",
    "하이드아웃",
    "스킬",
    "시스템",
)

REQUIRED_FIELDS = (
    "id",
    "difficulty",
    "category",
    "question",
    "choices",
    "answer",
    "explanation",
)
QUESTION_MODES = ("common", "pvp", "pve")


class QuestionDataError(ValueError):
    """문제 파일을 안전하게 사용할 수 없을 때 발생한다."""

    def __init__(self, errors: Sequence[str]):
        self.errors = tuple(errors)
        preview = "\n".join(f"- {error}" for error in self.errors[:10])
        if len(self.errors) > 10:
            preview += f"\n- 그 외 {len(self.errors) - 10}건"
        super().__init__(f"문제 데이터 검증에 실패했습니다:\n{preview}")


def load_questions(path: str | Path) -> list[dict]:
    """UTF-8 JSON을 읽고 중복 필드와 잘못된 최상위 구조를 거부한다."""
    source = Path(path)

    def unique_object(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            if key in result:
                raise QuestionDataError([f"중복된 JSON 필드: {source} ({key})"])
            result[key] = value
        return result

    try:
        with source.open(encoding="utf-8") as file:
            questions = json.load(file, object_pairs_hook=unique_object)
    except OSError as exc:
        raise QuestionDataError([f"문제 파일을 읽을 수 없음: {source} ({exc})"]) from exc
    except UnicodeDecodeError as exc:
        raise QuestionDataError([f"문제 파일은 UTF-8 인코딩이어야 함: {source}"]) from exc
    except json.JSONDecodeError as exc:
        raise QuestionDataError(
            [f"JSON 문법 오류: {source}:{exc.lineno}:{exc.colno} ({exc.msg})"]
        ) from exc

    if not isinstance(questions, list):
        raise QuestionDataError(["questions.json의 최상위 값은 배열이어야 함"])
    return questions


def is_question_enabled(question: Mapping) -> bool:
    """생략된 enabled는 활성으로 취급하고, 명시된 값은 True만 허용한다."""
    return question.get("enabled", True) is True


def validate_questions(questions: Sequence[object], session_counts: Mapping[str, int]) -> list[str]:
    """문제 형식과 출제 가능한 문제 수를 검사하고 오류 목록을 반환한다."""
    errors: list[str] = []
    seen_ids: set[int] = set()
    seen_texts: set[str] = set()
    difficulty_counts = {difficulty: 0 for difficulty in session_counts}

    for difficulty, required_count in session_counts.items():
        if (
            not isinstance(required_count, int)
            or isinstance(required_count, bool)
            or required_count <= 0
        ):
            errors.append(f"난이도 '{difficulty}' 출제 수량은 1 이상의 정수여야 함")

    for position, raw_question in enumerate(questions, start=1):
        if not isinstance(raw_question, dict):
            errors.append(f"{position}번째 항목: 객체가 아님")
            continue

        question = raw_question
        qid = question.get("id")
        label = f"id {qid}" if qid is not None else f"{position}번째 항목"

        enabled = question.get("enabled", True)
        if not isinstance(enabled, bool):
            errors.append(f"{label}: enabled는 true 또는 false여야 함")
        if enabled is False:
            reason = question.get("disabled_reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(
                    f"{label}: 출제 보류 문제에는 비어 있지 않은 disabled_reason이 필요함"
                )

        missing = [field for field in REQUIRED_FIELDS if field not in question]
        if missing:
            errors.append(f"{label}: 필수 필드 누락 ({', '.join(missing)})")

        if not isinstance(qid, int) or isinstance(qid, bool):
            errors.append(f"{label}: id는 정수여야 함")
        elif qid in seen_ids:
            errors.append(f"id {qid}: 중복된 id")
        else:
            seen_ids.add(qid)

        text = question.get("question")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"{label}: 문제 지문이 비어 있거나 문자열이 아님")
        elif text.strip() in seen_texts:
            errors.append(f"{label}: 중복된 문제 지문")
        else:
            seen_texts.add(text.strip())

        difficulty = question.get("difficulty")
        if not isinstance(difficulty, str) or difficulty not in session_counts:
            errors.append(f"{label}: 알 수 없는 난이도 '{difficulty}'")
        elif is_question_enabled(question):
            difficulty_counts[difficulty] += 1

        mode = question.get("mode", "common")
        if not isinstance(mode, str) or mode not in QUESTION_MODES:
            errors.append(
                f"{label}: 알 수 없는 mode '{mode}' "
                f"(허용: {', '.join(QUESTION_MODES)})"
            )

        category = question.get("category")
        if category not in CATEGORIES:
            errors.append(f"{label}: 알 수 없는 파트 '{category}'")

        choices = question.get("choices")
        if not isinstance(choices, list):
            errors.append(f"{label}: choices는 배열이어야 함")
            choices = []
        elif len(choices) != 4:
            errors.append(f"{label}: 보기가 4개가 아님 ({len(choices)}개)")

        if choices:
            if any(not isinstance(choice, str) or not choice.strip() for choice in choices):
                errors.append(f"{label}: 모든 보기는 비어 있지 않은 문자열이어야 함")
            elif len({choice.strip() for choice in choices}) != len(choices):
                errors.append(f"{label}: 중복된 보기 존재")

        answer = question.get("answer")
        if (
            not isinstance(answer, int)
            or isinstance(answer, bool)
            or not 0 <= answer < len(choices)
        ):
            errors.append(f"{label}: answer 인덱스가 잘못됨 ({answer})")

        explanation = question.get("explanation")
        if not isinstance(explanation, str) or not explanation.strip():
            errors.append(f"{label}: explanation은 비어 있지 않은 문자열이어야 함")

        volatile = question.get("volatile", False)
        if not isinstance(volatile, bool):
            errors.append(f"{label}: volatile는 true 또는 false여야 함")
        if volatile is True:
            note = question.get("volatile_note")
            if not isinstance(note, str) or not note.strip():
                errors.append(f"{label}: volatile 문제에는 비어 있지 않은 volatile_note가 필요함")

        # 선택적 근거 기록. 형식 검증일 뿐, 링크 내용의 사실성/최신성을 보증하지 않는다.
        if "reviewed_at" in question or "sources" in question:
            reviewed_at = question.get("reviewed_at")
            try:
                valid_date = (
                    isinstance(reviewed_at, str)
                    and date.fromisoformat(reviewed_at).isoformat() == reviewed_at
                )
            except ValueError:
                valid_date = False
            if not valid_date:
                errors.append(f"{label}: reviewed_at은 YYYY-MM-DD 날짜여야 함")

            sources = question.get("sources")
            valid_sources = isinstance(sources, list) and bool(sources)
            if valid_sources:
                for source in sources:
                    if not isinstance(source, str) or any(c.isspace() for c in source):
                        valid_sources = False
                        break
                    try:
                        parsed = urlsplit(source)
                        if (
                            parsed.scheme != "https"
                            or not parsed.hostname
                            or parsed.username is not None
                            or parsed.password is not None
                        ):
                            valid_sources = False
                    except ValueError:
                        valid_sources = False
            if not valid_sources:
                errors.append(f"{label}: sources는 비어 있지 않은 HTTPS URL 배열이어야 함")

    for difficulty, required_count in session_counts.items():
        available = difficulty_counts[difficulty]
        if (
            isinstance(required_count, int)
            and not isinstance(required_count, bool)
            and available < required_count
        ):
            errors.append(f"난이도 '{difficulty}' 문제 부족: {available}개/필요 {required_count}개")

    # 전체 수량이 충분해도 특정 모드의 출제 풀만 부족할 수 있다. 그 경우 봇 시작 시점이
    # 아니라 해당 모드로 퀴즈를 시작하는 순간에야 실패하므로, 모드별로도 미리 검사한다.
    for mode in ("pvp", "pve"):
        mode_counts = {difficulty: 0 for difficulty in session_counts}
        for raw_question in questions:
            if not isinstance(raw_question, dict):
                continue
            if not is_question_enabled(raw_question):
                continue
            if raw_question.get("mode", "common") not in ("common", mode):
                continue
            difficulty = raw_question.get("difficulty")
            if isinstance(difficulty, str) and difficulty in mode_counts:
                mode_counts[difficulty] += 1

        for difficulty, required_count in session_counts.items():
            available = mode_counts[difficulty]
            if (
                isinstance(required_count, int)
                and not isinstance(required_count, bool)
                and available < required_count
            ):
                errors.append(
                    f"{mode.upper()} 모드 난이도 '{difficulty}' 문제 부족: "
                    f"{available}개/필요 {required_count}개"
                )

    return errors


def load_validated_questions(path: str | Path, session_counts: Mapping[str, int]) -> list[dict]:
    """보류 문항까지 검증한 뒤 활성 문항만 반환하며, 오류가 있으면 시작을 중단한다."""
    questions = load_questions(path)
    errors = validate_questions(questions, session_counts)
    if errors:
        raise QuestionDataError(errors)
    return [question for question in questions if is_question_enabled(question)]


def group_by_difficulty(questions: Sequence[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for question in questions:
        if not is_question_enabled(question):
            continue
        grouped.setdefault(question["difficulty"], []).append(question)
    return grouped


def filter_questions_for_mode(
    questions: Sequence[dict],
    mode: str,
) -> list[dict]:
    """활성 문항 중 공통 문제와 요청한 게임 모드 전용 문제만 반환한다."""
    if mode not in {"pvp", "pve"}:
        raise ValueError("mode는 'pvp' 또는 'pve'여야 합니다.")
    return [
        question
        for question in questions
        if is_question_enabled(question)
        and question.get("mode", "common") in {"common", mode}
    ]


def select_session_questions(
    questions_by_difficulty: Mapping[str, Sequence[dict]],
    session_counts: Mapping[str, int],
    *,
    rng=None,
) -> list[dict]:
    """설정된 난이도별 수량을 중복 없이 뽑은 뒤 전체 순서를 섞는다."""
    randomizer = rng or random
    selected: list[dict] = []

    for difficulty, count in session_counts.items():
        pool = [
            question
            for question in questions_by_difficulty.get(difficulty, ())
            if is_question_enabled(question)
        ]
        if len(pool) < count:
            raise QuestionDataError(
                [f"난이도 '{difficulty}' 문제 부족: {len(pool)}개/필요 {count}개"]
            )
        selected.extend(randomizer.sample(list(pool), count))

    randomizer.shuffle(selected)
    return selected

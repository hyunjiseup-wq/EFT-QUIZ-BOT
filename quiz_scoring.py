from dataclasses import dataclass

import config
from quiz_session import QuizSession


@dataclass(frozen=True)
class ScoredResponse:
    question: dict
    is_correct: bool
    chosen_text: str | None
    timed_out: bool


def score_answer(session: QuizSession, display_index: int) -> ScoredResponse:
    """화면의 보기 인덱스를 원본 보기로 변환하고 세션 점수를 한 번 반영한다."""
    order = session.current_shuffled_choices
    if order is None:
        raise RuntimeError("현재 문제의 보기 순서가 준비되지 않았습니다.")
    if not 0 <= display_index < len(order):
        raise ValueError(f"보기 인덱스가 범위를 벗어났습니다: {display_index}")

    question = session.current_question
    chosen_original_index = order[display_index]
    choices = question["choices"]
    if not 0 <= chosen_original_index < len(choices):
        raise ValueError(
            f"원본 보기 인덱스가 범위를 벗어났습니다: {chosen_original_index}"
        )

    is_correct = chosen_original_index == question["answer"]
    difficulty = question["difficulty"]
    session.per_difficulty[difficulty][1] += 1
    if is_correct:
        session.score += config.POINTS[difficulty]
        session.correct_count += 1
        session.per_difficulty[difficulty][0] += 1

    return ScoredResponse(
        question=question,
        is_correct=is_correct,
        chosen_text=choices[chosen_original_index],
        timed_out=False,
    )


def score_timeout(session: QuizSession) -> ScoredResponse:
    """현재 문제를 시간 초과로 기록하되 점수와 정답 수는 변경하지 않는다."""
    question = session.current_question
    difficulty = question["difficulty"]
    session.per_difficulty[difficulty][1] += 1
    session.timed_out_count += 1
    return ScoredResponse(
        question=question,
        is_correct=False,
        chosen_text=None,
        timed_out=True,
    )

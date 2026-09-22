"""questions.json 점검 도구.

사용법:
  python check_questions.py                  # 형식 검증 + 난이도/파트별 문제 수 통계
  python check_questions.py --volatile       # 패치 변동형 문제 목록과 기록된 정답 출력
  python check_questions.py --disabled       # 출제 보류 문항과 사유 출력
  python check_questions.py --category 탄약  # 특정 파트의 문제 목록 출력

게임 패치가 나오면 --volatile 로 변동형 문제를 확인하고,
정답이 바뀐 문제의 choices/answer/explanation을 questions.json에서 수정한 뒤
다시 이 스크립트로 형식 검증을 하고 봇을 재시작하세요.
"""

import sys

import config
from question_bank import (
    CATEGORIES,
    QUESTION_MODES,
    QuestionDataError,
    filter_questions_for_mode,
    is_question_enabled,
    load_questions,
    validate_questions,
)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    questions = load_questions(config.QUESTIONS_PATH)
    errors = validate_questions(questions, config.SESSION_COUNTS)
    if errors:
        raise QuestionDataError(errors)

    enabled = [q for q in questions if is_question_enabled(q)]
    disabled = [q for q in questions if not is_question_enabled(q)]
    print(f"총 {len(questions)}문제 (활성 {len(enabled)} · 출제 보류 {len(disabled)})")
    print(
        "모드별 보관 구성: "
        + " · ".join(
            f"{mode} {sum(q.get('mode', 'common') == mode for q in questions)}문제"
            for mode in QUESTION_MODES
        )
    )
    for mode in ("pvp", "pve"):
        playable = filter_questions_for_mode(questions, mode)
        print(f"  {mode.upper()} 출제 가능: {len(playable)}문제 (공통 포함)")
    by_diff = {}
    for q in questions:
        by_diff.setdefault(q.get("difficulty"), []).append(q)
    for diff, need in config.SESSION_COUNTS.items():
        pool = sum(is_question_enabled(q) for q in by_diff.get(diff, []))
        label = config.DIFFICULTY_LABEL.get(diff, diff)
        status = "OK" if pool >= need else "부족! (문제 추가 필요)"
        print(f"  {label}({diff}): 활성 {pool}문제 (세션당 {need}개 출제) {status}")

    print("\n파트별 보관 구성 (보류 포함):")
    by_cat = {}
    for q in questions:
        by_cat.setdefault(q.get("category"), []).append(q)
    for cat in CATEGORIES:
        pool = by_cat.get(cat, [])
        diff_counts = {}
        for q in pool:
            diff_counts[q["difficulty"]] = diff_counts.get(q["difficulty"], 0) + 1
        detail = " ".join(
            f"{config.DIFFICULTY_LABEL[d]}{diff_counts[d]}"
            for d in config.SESSION_COUNTS
            if d in diff_counts
        )
        print(f"  {cat}: {len(pool)}문제 ({detail})")

    if "--category" in sys.argv:
        idx = sys.argv.index("--category")
        target = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        print(f"\n[{target}] 파트 문제 목록:")
        for q in by_cat.get(target, []):
            label = config.DIFFICULTY_LABEL.get(q["difficulty"], q["difficulty"])
            mark = " 🔁" if q.get("volatile") else ""
            if not is_question_enabled(q):
                mark += " [출제 보류]"
            print(f"  {q['id']:3d} [{label}]{mark} {q['question']}")

    volatile = [q for q in questions if q.get("volatile")]
    print(f"\n패치 변동형(volatile) 문제: {len(volatile)}개")
    reviewed = [q for q in questions if q.get("reviewed_at") and q.get("sources")]
    print(f"근거·검토일 기록: {len(reviewed)}개 (사실성·최신성 자동 검증 아님)")
    if "--volatile" in sys.argv:
        for q in volatile:
            label = config.DIFFICULTY_LABEL.get(q["difficulty"], q["difficulty"])
            print(f"\n[id {q['id']} · {label}] {q['question']}")
            status = "활성" if is_question_enabled(q) else "출제 보류"
            print(f"  상태: {status}")
            print(f"  기록된 정답: {q['choices'][q['answer']]}")
            if not is_question_enabled(q):
                print(f"  보류 사유: {q['disabled_reason']}")
            if q.get("volatile_note"):
                print(f"  점검 메모: {q['volatile_note']}")
            if q.get("reviewed_at"):
                print(f"  검토일: {q['reviewed_at']}")
                for source in q["sources"]:
                    print(f"  근거: {source}")

    if "--disabled" in sys.argv:
        for q in disabled:
            print(f"\n[id {q['id']} · 출제 보류] {q['question']}")
            print(f"  사유: {q['disabled_reason']}")

    print("\n형식 검증 통과")


if __name__ == "__main__":
    try:
        main()
    except QuestionDataError as exc:
        print(exc)
        sys.exit(1)

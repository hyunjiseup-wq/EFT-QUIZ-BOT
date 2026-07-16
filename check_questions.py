"""questions.json 점검 도구.

사용법:
  python check_questions.py                  # 형식 검증 + 난이도/파트별 문제 수 통계
  python check_questions.py --volatile       # 패치 변동형 문제 목록과 현재 정답 출력
  python check_questions.py --category 탄약  # 특정 파트의 문제 목록 출력

게임 패치가 나오면 --volatile 로 변동형 문제를 확인하고,
정답이 바뀐 문제의 choices/answer/explanation을 questions.json에서 수정한 뒤
다시 이 스크립트로 형식 검증을 하고 봇을 재시작하세요.
"""
import sys

import config
from question_bank import CATEGORIES, QuestionDataError, load_questions, validate_questions


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    questions = load_questions(config.QUESTIONS_PATH)
    errors = validate_questions(questions, config.SESSION_COUNTS)
    if errors:
        raise QuestionDataError(errors)

    print(f"총 {len(questions)}문제")
    by_diff = {}
    for q in questions:
        by_diff.setdefault(q.get("difficulty"), []).append(q)
    for diff, need in config.SESSION_COUNTS.items():
        pool = len(by_diff.get(diff, []))
        label = config.DIFFICULTY_LABEL.get(diff, diff)
        status = "OK" if pool >= need else "부족! (문제 추가 필요)"
        print(f"  {label}({diff}): {pool}문제 (세션당 {need}개 출제) {status}")

    print("\n파트별 구성:")
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
            for d in config.SESSION_COUNTS if d in diff_counts
        )
        print(f"  {cat}: {len(pool)}문제 ({detail})")

    if "--category" in sys.argv:
        idx = sys.argv.index("--category")
        target = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        print(f"\n[{target}] 파트 문제 목록:")
        for q in by_cat.get(target, []):
            label = config.DIFFICULTY_LABEL.get(q["difficulty"], q["difficulty"])
            mark = " 🔁" if q.get("volatile") else ""
            print(f"  {q['id']:3d} [{label}]{mark} {q['question']}")

    volatile = [q for q in questions if q.get("volatile")]
    print(f"\n패치 변동형(volatile) 문제: {len(volatile)}개")
    if "--volatile" in sys.argv:
        for q in volatile:
            label = config.DIFFICULTY_LABEL.get(q["difficulty"], q["difficulty"])
            print(f"\n[id {q['id']} · {label}] {q['question']}")
            print(f"  현재 정답: {q['choices'][q['answer']]}")
            if q.get("volatile_note"):
                print(f"  점검 메모: {q['volatile_note']}")

    print("\n형식 검증 통과")


if __name__ == "__main__":
    try:
        main()
    except QuestionDataError as exc:
        print(exc)
        sys.exit(1)

import json
import random
import tempfile
import unittest
from pathlib import Path

from config import SESSION_COUNTS
from question_bank import (
    QuestionDataError,
    filter_questions_for_mode,
    group_by_difficulty,
    load_questions,
    select_session_questions,
    validate_questions,
)


def make_question(qid: int, difficulty: str = "general") -> dict:
    return {
        "id": qid,
        "difficulty": difficulty,
        "category": "시스템",
        "question": f"문제 {qid}",
        "choices": ["정답", "오답 1", "오답 2", "오답 3"],
        "answer": 0,
        "explanation": "해설",
    }


class QuestionBankTests(unittest.TestCase):
    def test_real_bank_600_sessions_keep_difficulty_counts_unique_ids_and_mode_isolation(self):
        questions = load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        self.assertEqual(validate_questions(questions, SESSION_COUNTS), [])
        rng = random.Random(20260922)
        total = sum(SESSION_COUNTS.values())
        for mode in ("pvp", "pve"):
            pool = group_by_difficulty(filter_questions_for_mode(questions, mode))
            for draw in range(300):
                with self.subTest(mode=mode, draw=draw):
                    selected = select_session_questions(pool, SESSION_COUNTS, rng=rng)
                    self.assertEqual(len(selected), total)
                    self.assertEqual(len({q["id"] for q in selected}), total)
                    self.assertTrue(
                        all(q.get("mode", "common") in {"common", mode} for q in selected)
                    )
                    for difficulty, count in SESSION_COUNTS.items():
                        self.assertEqual(
                            sum(q["difficulty"] == difficulty for q in selected), count
                        )

    def test_review_metadata_is_optional_but_requires_date_and_https_sources_together(self):
        question = make_question(1)
        self.assertEqual(validate_questions([question], {"general": 1}), [])
        reviewed = {
            **question,
            "reviewed_at": "2026-09-22",
            "sources": ["https://telegra.ph/Patch-1151-09-15-2"],
        }
        self.assertEqual(validate_questions([reviewed], {"general": 1}), [])
        for field in ("reviewed_at", "sources"):
            with self.subTest(missing=field):
                incomplete = {key: value for key, value in reviewed.items() if key != field}
                self.assertTrue(validate_questions([incomplete], {"general": 1}))

    def test_review_metadata_rejects_invalid_dates_and_sources(self):
        reviewed = {
            **make_question(1),
            "reviewed_at": "2026-09-22",
            "sources": ["https://telegra.ph/Patch-1151-09-15-2"],
        }
        for value in (None, True, 20260922, "2026-02-30", "22/09/2026", "20260922"):
            with self.subTest(date=value):
                errors = validate_questions([{**reviewed, "reviewed_at": value}], {"general": 1})
                self.assertTrue(any("reviewed_at" in error for error in errors))
        for value in (
            None, [], "https://example.com", [42], [""], ["http://example.com"],
            ["https:///missing-host"], ["https://[bad"], ["https://user:secret@example.com"],
            ["https://example.com/with space"],
        ):
            with self.subTest(sources=value):
                errors = validate_questions([{**reviewed, "sources": value}], {"general": 1})
                self.assertTrue(any("sources" in error for error in errors))

    def test_september_patch_questions_keep_corrected_scope_and_provenance(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        # 회귀 검사는 원전의 사실성을 증명하지 않는다. 검토한 수정 범위만 고정한다.
        expected_answer_fragments = {
            44: "사격", 80: "대상 캐릭터", 138: "로그", 164: "볼트액션",
            211: "두 진영", 242: "가까이", 244: "거치 화기와 지뢰 제거",
            273: "12.7x108mm", 339: "타길라의 그림자", 403: "경향",
            406: "플레이트 캐리어", 450: "보상 해금", 457: "Arena에서",
            459: "시즌 캐릭터", 460: "집계에서는 제외", 461: "25명·15명·10명",
            462: "수리 키트", 463: "Fence·Ref", 464: "방어 성능 제거",
        }
        for qid, fragment in expected_answer_fragments.items():
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertIn(fragment, question["choices"][question["answer"]])
                self.assertEqual(question["reviewed_at"], "2026-09-22")
                self.assertTrue(question["sources"])
        self.assertIn("Power Station", questions[130]["question"])
        self.assertIn("전술 의상", questions[457]["explanation"])
        self.assertIn("장비 상자 교환에는 사용할 수 없습니다", questions[450]["explanation"])
        self.assertNotIn("10~15%", questions[403]["choices"][0])
        pve_ids = {q["id"] for q in filter_questions_for_mode(list(questions.values()), "pve")}
        self.assertTrue({459, 460, 461}.isdisjoint(pve_ids))
        self.assertTrue({462, 463, 464}.issubset(pve_ids))

    def test_revalidated_questions_keep_current_answer_and_bounded_scope(self):
        questions_path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {question["id"]: question for question in load_questions(questions_path)}

        painkiller = questions[413]
        self.assertEqual(painkiller["choices"][painkiller["answer"]], "골든 스타 밤")

        terminal = questions[442]
        self.assertIn("제시된 네 맵 중", terminal["explanation"])

        smallest_map = questions[446]
        self.assertTrue(smallest_map["question"].startswith("다음 네 맵 중"))
        self.assertEqual(smallest_map["choices"][smallest_map["answer"]], "팩토리")

    def test_exception_corrections_keep_scope_and_sources(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        # 원전 사실성 자동 검증이 아니라 이번에 고친 예외·범위의 회귀 방지다.
        question_scopes = {
            29: "귀", 41: "비배신자", 61: "호환 헬멧", 94: "1칸(1x1)",
            156: "팔·다리·복부", 157: "총탄의 직접 피해", 438: "매칭",
        }
        for qid, scope in question_scopes.items():
            with self.subTest(qid=qid):
                self.assertIn(scope, questions[qid]["question"])
        for qid in (29, 41, 61, 94, 118, 156, 157, 220, 314, 389, 390, 415, 424, 438):
            with self.subTest(provenance=qid):
                self.assertEqual(questions[qid]["reviewed_at"], "2026-09-22")
                self.assertTrue(questions[qid]["sources"])
        for fragment in ("은신처 제작품", "퀘스트 보상", "Run Through"):
            self.assertIn(fragment, questions[118]["explanation"])
        self.assertIn("출혈", questions[157]["explanation"])
        self.assertIn("퀘스트에 지정된", questions[314]["choices"][questions[314]["answer"]])
        self.assertNotIn("카파 필수", questions[314]["explanation"])
        self.assertIn("최고 레벨 구성원", questions[438]["explanation"])

    def test_malfunction_questions_ask_boundaries_not_overlapping_ranges(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        for qid, scope, answer in ((389, "경계값", "93"), (390, "상한", "5%")):
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertIn(scope, question["question"])
                self.assertEqual(question["choices"][question["answer"]], answer)
                self.assertTrue(question["volatile"])
                for choice in question["choices"]:
                    self.assertNotIn("초과", choice)
                    self.assertNotIn("이하", choice)

    def test_medical_questions_compare_one_measure_only(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        comparison = questions[415]
        self.assertIn("1회 사용당 최대 HP 회복량", comparison["question"])
        self.assertEqual(comparison["choices"][comparison["answer"]], "85 → 60")
        self.assertEqual(len(set(comparison["choices"])), 4)
        for choice in comparison["choices"]:
            self.assertRegex(choice, r"^\d+ → \d+$")
        surgery = questions[424]
        self.assertIn("최대 HP 감소 페널티", surgery["choices"][surgery["answer"]])
        self.assertNotIn("완전한 체력으로 복구", surgery["explanation"])

    def test_mode_filter_includes_common_and_requested_mode_only(self):
        common = make_question(1)
        pvp = {**make_question(2), "mode": "pvp"}
        pve = {**make_question(3), "mode": "pve"}

        self.assertEqual(
            [q["id"] for q in filter_questions_for_mode([common, pvp, pve], "pvp")],
            [1, 2],
        )
        self.assertEqual(
            [q["id"] for q in filter_questions_for_mode([common, pvp, pve], "pve")],
            [1, 3],
        )

    def test_validation_rejects_unknown_mode(self):
        question = {**make_question(1), "mode": "arena"}

        errors = validate_questions([question], {"general": 1})

        self.assertTrue(any("알 수 없는 mode" in error for error in errors))

    def test_validation_reports_shortage_in_one_mode_only(self):
        # 전체 2문제로 수량은 충족되지만, PvE 풀에는 1문제뿐이라 PvE만 부족해야 한다.
        questions = [
            {**make_question(1), "mode": "pvp"},
            {**make_question(2), "mode": "common"},
        ]

        errors = validate_questions(questions, {"general": 2})

        self.assertTrue(any("PVE 모드 난이도 'general' 문제 부족" in error for error in errors))
        self.assertFalse(any("PVP 모드" in error for error in errors))
        self.assertFalse(
            any(error.startswith("난이도 'general' 문제 부족") for error in errors)
        )

    def test_valid_questions_have_no_errors(self):
        questions = [make_question(1), make_question(2)]

        self.assertEqual(validate_questions(questions, {"general": 2}), [])

    def test_validation_finds_duplicate_id_and_shortage(self):
        questions = [make_question(1), make_question(1)]

        errors = validate_questions(questions, {"general": 2, "hard": 1})

        self.assertTrue(any("중복된 id" in error for error in errors))
        self.assertTrue(any("'hard' 문제 부족" in error for error in errors))

    def test_validation_rejects_non_positive_session_count(self):
        errors = validate_questions([make_question(1)], {"general": 0})

        self.assertTrue(any("1 이상의 정수" in error for error in errors))

    def test_selection_respects_counts_without_duplicate_ids(self):
        questions = [make_question(i) for i in range(1, 6)]
        questions += [make_question(i, "hard") for i in range(6, 10)]

        selected = select_session_questions(
            group_by_difficulty(questions),
            {"general": 3, "hard": 2},
            rng=random.Random(7),
        )

        self.assertEqual(len(selected), 5)
        self.assertEqual(len({question["id"] for question in selected}), 5)
        self.assertEqual(
            {
                difficulty: sum(q["difficulty"] == difficulty for q in selected)
                for difficulty in ("general", "hard")
            },
            {"general": 3, "hard": 2},
        )

    def test_selection_rejects_an_undersized_pool(self):
        with self.assertRaises(QuestionDataError):
            select_session_questions({"general": [make_question(1)]}, {"general": 2})

    def test_loader_rejects_non_array_root(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.json"
            path.write_text(json.dumps({"id": 1}), encoding="utf-8")

            with self.assertRaises(QuestionDataError):
                load_questions(path)


if __name__ == "__main__":
    unittest.main()

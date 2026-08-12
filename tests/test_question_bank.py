import json
import random
import tempfile
import unittest
from pathlib import Path

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

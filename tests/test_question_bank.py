import json
import random
import tempfile
import unittest
from pathlib import Path

from question_bank import (
    QuestionDataError,
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
    def test_valid_questions_have_no_errors(self):
        questions = [make_question(1), make_question(2)]

        self.assertEqual(validate_questions(questions, {"general": 2}), [])

    def test_validation_finds_duplicate_id_and_shortage(self):
        questions = [make_question(1), make_question(1)]

        errors = validate_questions(questions, {"general": 2, "hard": 1})

        self.assertTrue(any("중복된 id" in error for error in errors))
        self.assertTrue(any("'hard' 문제 부족" in error for error in errors))

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
            {difficulty: sum(q["difficulty"] == difficulty for q in selected)
             for difficulty in ("general", "hard")},
            {"general": 3, "hard": 2},
        )

    def test_selection_rejects_an_undersized_pool(self):
        with self.assertRaises(QuestionDataError):
            select_session_questions(
                {"general": [make_question(1)]}, {"general": 2}
            )

    def test_loader_rejects_non_array_root(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.json"
            path.write_text(json.dumps({"id": 1}), encoding="utf-8")

            with self.assertRaises(QuestionDataError):
                load_questions(path)


if __name__ == "__main__":
    unittest.main()

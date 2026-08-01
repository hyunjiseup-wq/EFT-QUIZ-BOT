import unittest
from unittest.mock import patch

import quiz_scoring
from quiz_session import QuizSession


def make_session() -> QuizSession:
    question = {
        "difficulty": "general",
        "question": "테스트 문제",
        "choices": ["정답", "오답 1", "오답 2", "오답 3"],
        "answer": 0,
        "explanation": "해설",
    }
    return QuizSession(
        mode="pvp",
        guild_id=10,
        user_id=1,
        username="테스터",
        channel_id=20,
        questions=[question],
    )


class QuizScoringTests(unittest.TestCase):
    def test_correct_answer_updates_all_score_counters(self):
        session = make_session()
        session.current_shuffled_choices = [2, 0, 3, 1]

        with patch.dict(quiz_scoring.config.POINTS, {"general": 100}):
            result = quiz_scoring.score_answer(session, 1)

        self.assertTrue(result.is_correct)
        self.assertEqual(result.chosen_text, "정답")
        self.assertEqual(session.score, 100)
        self.assertEqual(session.correct_count, 1)
        self.assertEqual(session.per_difficulty["general"], [1, 1])

    def test_wrong_answer_only_increments_answered_counter(self):
        session = make_session()
        session.current_shuffled_choices = [2, 0, 3, 1]

        result = quiz_scoring.score_answer(session, 0)

        self.assertFalse(result.is_correct)
        self.assertEqual(result.chosen_text, "오답 2")
        self.assertEqual(session.score, 0)
        self.assertEqual(session.correct_count, 0)
        self.assertEqual(session.per_difficulty["general"], [0, 1])

    def test_timeout_updates_attempt_and_timeout_only(self):
        session = make_session()

        result = quiz_scoring.score_timeout(session)

        self.assertTrue(result.timed_out)
        self.assertIsNone(result.chosen_text)
        self.assertEqual(session.score, 0)
        self.assertEqual(session.correct_count, 0)
        self.assertEqual(session.timed_out_count, 1)
        self.assertEqual(session.per_difficulty["general"], [0, 1])

    def test_missing_choice_mapping_is_rejected_before_mutation(self):
        session = make_session()

        with self.assertRaisesRegex(RuntimeError, "보기 순서"):
            quiz_scoring.score_answer(session, 0)

        self.assertEqual(session.score, 0)
        self.assertEqual(session.per_difficulty["general"], [0, 0])

    def test_invalid_choice_index_is_rejected_before_mutation(self):
        session = make_session()
        session.current_shuffled_choices = [0, 1, 2, 3]

        with self.assertRaisesRegex(ValueError, "보기 인덱스"):
            quiz_scoring.score_answer(session, 4)

        self.assertEqual(session.score, 0)
        self.assertEqual(session.per_difficulty["general"], [0, 0])


if __name__ == "__main__":
    unittest.main()

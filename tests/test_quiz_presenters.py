import unittest
from unittest.mock import Mock, patch

import quiz_presenters
from quiz_session import QuizSession


def make_session() -> QuizSession:
    question = {
        "difficulty": "general",
        "question": "테스트 문제",
        "choices": ["A 보기", "B 보기", "C 보기", "D 보기"],
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


class QuizPresenterTests(unittest.TestCase):
    def test_question_embed_uses_and_records_shuffled_choice_order(self):
        session = make_session()
        find_quiz_emoji = Mock(return_value=None)

        with patch.object(
            quiz_presenters.random,
            "shuffle",
            side_effect=lambda order: order.reverse(),
        ):
            embed = quiz_presenters.build_question_embed(
                session,
                mode_labels={"pvp": "PvP", "pve": "PvE"},
                find_quiz_emoji=find_quiz_emoji,
            )

        self.assertEqual(session.current_shuffled_choices, [3, 2, 1, 0])
        self.assertEqual(
            [field.value for field in embed.fields],
            ["D 보기", "C 보기", "B 보기", "A 보기"],
        )
        self.assertEqual(embed.title, "PvP 문제 1 / 1")
        self.assertNotIn("점", embed.footer.text)

    def test_final_embed_contains_public_result_summary(self):
        session = make_session()
        session.score = 100
        session.correct_count = 1
        decorate_embed = Mock(
            side_effect=lambda embed, title, *_args, **_kwargs: setattr(
                embed, "title", title
            )
        )

        embed = quiz_presenters.build_final_embed(
            session,
            mode_labels={"pvp": "PvP", "pve": "PvE"},
            decorate_embed=decorate_embed,
        )

        values = {field.name: field.value for field in embed.fields}
        self.assertEqual(values["총점"], "100점")
        self.assertEqual(values["모드"], "PvP")
        self.assertEqual(values["정답 수"], "1 / 1")
        self.assertIn("/pvp퀴즈랭킹", embed.footer.text)

    def test_result_text_does_not_reveal_correctness(self):
        icon_text = Mock(side_effect=lambda _guild, _name, fallback: fallback)

        submitted = quiz_presenters.build_result_text(
            False, None, quiz_icon_text=icon_text
        )
        timed_out = quiz_presenters.build_result_text(
            True, None, quiz_icon_text=icon_text
        )

        self.assertNotIn("정답", submitted)
        self.assertNotIn("오답", submitted)
        self.assertIn("시간 초과", timed_out)


if __name__ == "__main__":
    unittest.main()

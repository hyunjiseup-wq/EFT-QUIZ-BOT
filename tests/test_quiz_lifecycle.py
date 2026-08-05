import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import quiz_lifecycle
from quiz_session import QuizSession, active_sessions

QUESTION = {
    "difficulty": "general",
    "question": "테스트 문제",
    "choices": ["정답", "오답1", "오답2", "오답3"],
    "answer": 0,
    "explanation": "테스트 해설",
}


def make_interaction(user_id: int = 1):
    interaction = Mock()
    interaction.guild_id = 10
    interaction.channel_id = 20
    interaction.user = SimpleNamespace(id=user_id, display_name=f"테스터{user_id}")
    interaction.client = Mock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    interaction.original_response = AsyncMock(return_value=f"message-{user_id}")
    return interaction


def make_session(user_id: int = 1) -> QuizSession:
    return QuizSession(
        mode="pvp",
        guild_id=10,
        user_id=user_id,
        username=f"테스터{user_id}",
        channel_id=20,
        questions=[QUESTION],
    )


def alert_text(_guild_id, _name, fallback, text):
    return f"{fallback} {text}"


def start_kwargs(**overrides):
    values = {
        "quiz_channel_ids": (20, 21),
        "max_active_sessions": 250,
        "build_questions": Mock(return_value=[QUESTION]),
        "build_question_embed": Mock(return_value="question-embed"),
        "answer_view_factory": Mock(return_value=SimpleNamespace(stop=Mock())),
        "start_admin_log": AsyncMock(),
        "quiz_alert_text": alert_text,
        "logger": Mock(),
    }
    values.update(overrides)
    return values


class QuizLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_abort_cleans_session_even_if_admin_log_fails(self):
        session = make_session()
        logger = Mock()

        with patch.dict(active_sessions, {(10, 1): session}, clear=True):
            aborted = await quiz_lifecycle.abort_quiz_session(
                session,
                finalize_admin_log=AsyncMock(side_effect=RuntimeError("log failed")),
                reason="답변 처리 오류",
                logger=logger,
            )

            self.assertNotIn((10, 1), active_sessions)

        self.assertTrue(aborted)
        self.assertTrue(session.finished)
        logger.exception.assert_called_once()

    async def test_stale_session_is_reclaimed_before_new_start(self):
        stale = make_session()
        stale.finished = True
        interaction = make_interaction()

        with patch.dict(active_sessions, {(10, 1): stale}, clear=True):
            session = await quiz_lifecycle.start_quiz(
                interaction, "pvp", **start_kwargs()
            )

            self.assertIsNotNone(session)
            self.assertIs(active_sessions[(10, 1)], session)
            self.assertIsNot(active_sessions[(10, 1)], stale)

    async def test_concurrent_start_reserves_session_before_first_await_finishes(self):
        first = make_interaction()
        second = make_interaction()
        send_started = asyncio.Event()
        release_send = asyncio.Event()

        async def delayed_send(**_kwargs):
            send_started.set()
            await release_send.wait()

        first.response.send_message.side_effect = delayed_send

        with patch.dict(active_sessions, {}, clear=True):
            first_task = asyncio.create_task(
                quiz_lifecycle.start_quiz(first, "pvp", **start_kwargs())
            )
            await send_started.wait()

            second_result = await quiz_lifecycle.start_quiz(
                second, "pvp", **start_kwargs()
            )
            release_send.set()
            first_result = await first_task

            self.assertIsNotNone(first_result)
            self.assertIsNone(second_result)
            self.assertIs(active_sessions[(10, 1)], first_result)

        second.response.send_message.assert_awaited_once()
        self.assertIn("이미 진행 중", second.response.send_message.await_args.args[0])

    async def test_unexpected_first_message_failure_stops_view_and_cleans_session(self):
        interaction = make_interaction()
        interaction.original_response.side_effect = RuntimeError("response unavailable")
        interaction.response.is_done.return_value = True
        interaction.edit_original_response = AsyncMock()
        view = SimpleNamespace(stop=Mock())

        with patch.dict(active_sessions, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "response unavailable"):
                await quiz_lifecycle.start_quiz(
                    interaction,
                    "pvp",
                    **start_kwargs(answer_view_factory=Mock(return_value=view)),
                )

            self.assertNotIn((10, 1), active_sessions)

        view.stop.assert_called_once_with()
        interaction.edit_original_response.assert_awaited_once_with(
            content="퀴즈 시작에 실패했어요. 잠시 후 다시 시도해주세요.",
            embed=None,
            view=None,
        )

    async def test_admin_log_failure_does_not_abort_started_quiz(self):
        interaction = make_interaction()
        logger = Mock()

        with patch.dict(active_sessions, {}, clear=True):
            session = await quiz_lifecycle.start_quiz(
                interaction,
                "pvp",
                **start_kwargs(
                    start_admin_log=AsyncMock(side_effect=RuntimeError("log failed")),
                    logger=logger,
                ),
            )

            self.assertIs(active_sessions[(10, 1)], session)
            self.assertFalse(session.finished)

        logger.exception.assert_called_once()

    async def test_guild_limit_rejects_before_building_questions(self):
        current = make_session(user_id=2)
        interaction = make_interaction()
        build_questions = Mock(return_value=[QUESTION])

        with patch.dict(active_sessions, {(10, 2): current}, clear=True):
            result = await quiz_lifecycle.start_quiz(
                interaction,
                "pvp",
                **start_kwargs(
                    max_active_sessions=1,
                    build_questions=build_questions,
                ),
            )

        self.assertIsNone(result)
        build_questions.assert_not_called()

    async def test_other_server_quiz_channel_is_allowed(self):
        """다른 서버의 설정 채널에서도 퀴즈를 시작할 수 있어야 한다."""
        interaction = make_interaction()
        interaction.guild_id = 11
        interaction.channel_id = 21

        with patch.dict(active_sessions, {}, clear=True):
            session = await quiz_lifecycle.start_quiz(
                interaction, "pvp", **start_kwargs()
            )

            self.assertIsNotNone(session)
            self.assertIs(active_sessions[(11, 1)], session)

    async def test_unconfigured_channel_is_rejected_with_this_guild_channel(self):
        interaction = make_interaction()
        interaction.channel_id = 99
        build_questions = Mock(return_value=[QUESTION])
        interaction.client.get_channel = Mock(
            side_effect=lambda channel_id: {
                20: SimpleNamespace(guild=SimpleNamespace(id=10)),
                21: SimpleNamespace(guild=SimpleNamespace(id=11)),
            }.get(channel_id)
        )

        with patch.dict(active_sessions, {}, clear=True):
            result = await quiz_lifecycle.start_quiz(
                interaction,
                "pvp",
                **start_kwargs(build_questions=build_questions),
            )

        self.assertIsNone(result)
        build_questions.assert_not_called()
        notice = interaction.response.send_message.await_args.args[0]
        self.assertIn("<#20>", notice)
        self.assertNotIn("<#21>", notice)

    async def test_rejection_without_channel_for_this_guild_guides_to_admin(self):
        interaction = make_interaction()
        interaction.guild_id = 12
        interaction.channel_id = 99
        interaction.client.get_channel = Mock(return_value=None)

        with patch.dict(active_sessions, {}, clear=True):
            result = await quiz_lifecycle.start_quiz(
                interaction, "pvp", **start_kwargs()
            )

        self.assertIsNone(result)
        notice = interaction.response.send_message.await_args.args[0]
        self.assertIn("설정되어 있지 않아요", notice)

    async def test_give_up_cleans_session_even_if_admin_log_fails(self):
        session = make_session()
        session.message = SimpleNamespace(edit=AsyncMock())
        interaction = make_interaction()
        logger = Mock()

        with patch.dict(active_sessions, {(10, 1): session}, clear=True):
            result = await quiz_lifecycle.give_up_quiz(
                interaction,
                finalize_admin_log=AsyncMock(
                    side_effect=RuntimeError("admin log unavailable")
                ),
                quiz_alert_text=alert_text,
                quiz_icon_text=lambda _guild, _name, fallback: fallback,
                logger=logger,
            )

            self.assertNotIn((10, 1), active_sessions)

        self.assertTrue(result)
        self.assertTrue(session.finished)
        session.message.edit.assert_awaited_once_with(
            content="🚪 퀴즈를 포기했어요.", embed=None, view=None
        )
        interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        interaction.edit_original_response.assert_awaited_once()
        interaction.response.send_message.assert_not_awaited()
        logger.exception.assert_called_once()

    async def test_give_up_reclaims_inactive_registered_session(self):
        session = make_session()
        session.finished = True
        interaction = make_interaction()

        with patch.dict(active_sessions, {(10, 1): session}, clear=True):
            result = await quiz_lifecycle.give_up_quiz(
                interaction,
                finalize_admin_log=AsyncMock(),
                quiz_alert_text=alert_text,
                quiz_icon_text=Mock(),
                logger=Mock(),
            )

            self.assertNotIn((10, 1), active_sessions)

        self.assertFalse(result)
        interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        self.assertIn(
            "이미 종료",
            interaction.edit_original_response.await_args.kwargs["content"],
        )


if __name__ == "__main__":
    unittest.main()

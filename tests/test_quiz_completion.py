import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord

import quiz_completion
from quiz_session import QuizSession, active_sessions


def make_session(question_count: int = 1) -> QuizSession:
    question = {
        "difficulty": "general",
        "question": "테스트 문제",
        "choices": ["정답", "오답1", "오답2", "오답3"],
        "answer": 0,
        "explanation": "해설",
    }
    return QuizSession(
        mode="pvp",
        guild_id=10,
        user_id=1,
        username="테스터",
        channel_id=20,
        questions=[question] * question_count,
    )


def make_interaction():
    interaction = Mock()
    interaction.response.is_done.return_value = True
    interaction.edit_original_response = AsyncMock()
    interaction.original_response = AsyncMock(return_value="updated-message")
    return interaction


class QuizCompletionTests(unittest.IsolatedAsyncioTestCase):
    async def test_message_http_failure_aborts_and_cleans_session(self):
        session = make_session()
        response = Mock(status=404, reason="Not Found", headers={})
        error = discord.HTTPException(response, "expired")
        interaction = make_interaction()
        interaction.edit_original_response.side_effect = error
        finalize_admin_log = AsyncMock()

        with patch.dict(active_sessions, {(10, 1): session}, clear=True):
            updated = await quiz_completion.edit_session_message(
                session,
                interaction,
                finalize_admin_log=finalize_admin_log,
                logger=Mock(),
                content="다음 문제",
            )

            self.assertFalse(updated)
            self.assertNotIn((10, 1), active_sessions)

        self.assertTrue(session.finished)
        finalize_admin_log.assert_awaited_once_with(
            session,
            aborted=True,
            reason="메시지 수정 실패로 중단",
        )

    async def test_message_failure_cleans_session_when_admin_log_finalizer_fails(self):
        session = make_session()
        response = Mock(status=404, reason="Not Found", headers={})
        interaction = make_interaction()
        interaction.edit_original_response.side_effect = discord.HTTPException(
            response, "expired"
        )
        finalize_admin_log = AsyncMock(side_effect=RuntimeError("log failed"))
        logger = Mock()

        with patch.dict(active_sessions, {(10, 1): session}, clear=True):
            updated = await quiz_completion.edit_session_message(
                session,
                interaction,
                finalize_admin_log=finalize_admin_log,
                logger=logger,
                content="다음 문제",
            )

            self.assertFalse(updated)
            self.assertNotIn((10, 1), active_sessions)

        self.assertTrue(session.finished)
        logger.exception.assert_called_once()

    async def test_missing_timeout_message_aborts_and_cleans_session(self):
        session = make_session()
        finalize_admin_log = AsyncMock()

        with patch.dict(active_sessions, {(10, 1): session}, clear=True):
            updated = await quiz_completion.edit_session_message(
                session,
                None,
                finalize_admin_log=finalize_admin_log,
                logger=Mock(),
                content="다음 문제",
            )

            self.assertFalse(updated)
            self.assertNotIn((10, 1), active_sessions)

        finalize_admin_log.assert_awaited_once_with(
            session,
            aborted=True,
            reason="세션 메시지 없음으로 중단",
        )

    async def test_final_result_is_saved_before_success_cleanup(self):
        session = make_session()
        interaction = make_interaction()
        finalize_admin_log = AsyncMock()
        build_final_embed = Mock(return_value="final-embed")

        with (
            patch.dict(active_sessions, {(10, 1): session}, clear=True),
            patch.object(
                quiz_completion.asyncio,
                "to_thread",
                new=AsyncMock(return_value=None),
            ) as to_thread,
        ):
            await quiz_completion.advance_or_finish(
                interaction,
                session,
                "제출 완료",
                build_final_embed=build_final_embed,
                build_question_embed=Mock(),
                answer_view_factory=Mock(),
                finalize_admin_log=finalize_admin_log,
                quiz_icon_text=Mock(),
                logger=Mock(),
            )

            self.assertNotIn((10, 1), active_sessions)

        self.assertTrue(session.finished)
        to_thread.assert_awaited_once()
        self.assertIs(to_thread.await_args.args[0], quiz_completion.database.record_result)
        interaction.edit_original_response.assert_awaited_once_with(
            content="제출 완료",
            embed="final-embed",
            view=None,
        )
        finalize_admin_log.assert_awaited_once_with(session, aborted=False)

    async def test_finalizer_failure_still_cleans_completed_session(self):
        session = make_session()
        interaction = make_interaction()
        finalize_admin_log = AsyncMock(side_effect=RuntimeError("log failed"))
        logger = Mock()

        with (
            patch.dict(active_sessions, {(10, 1): session}, clear=True),
            patch.object(
                quiz_completion.asyncio,
                "to_thread",
                new=AsyncMock(return_value=None),
            ),
        ):
            await quiz_completion.advance_or_finish(
                interaction,
                session,
                "제출 완료",
                build_final_embed=Mock(return_value="final-embed"),
                build_question_embed=Mock(),
                answer_view_factory=Mock(),
                finalize_admin_log=finalize_admin_log,
                quiz_icon_text=Mock(),
                logger=logger,
            )

            self.assertNotIn((10, 1), active_sessions)

        self.assertTrue(session.finished)
        logger.exception.assert_called_once()

    async def test_database_failure_shows_warning_and_aborts_log(self):
        session = make_session()
        interaction = make_interaction()
        finalize_admin_log = AsyncMock()

        with (
            patch.dict(active_sessions, {(10, 1): session}, clear=True),
            patch.object(
                quiz_completion.asyncio,
                "to_thread",
                new=AsyncMock(side_effect=RuntimeError("db failure")),
            ),
        ):
            await quiz_completion.advance_or_finish(
                interaction,
                session,
                "제출 완료",
                build_final_embed=Mock(return_value="final-embed"),
                build_question_embed=Mock(),
                answer_view_factory=Mock(),
                finalize_admin_log=finalize_admin_log,
                quiz_icon_text=Mock(
                    side_effect=lambda _guild, _name, fallback: fallback
                ),
                logger=Mock(),
            )

            self.assertNotIn((10, 1), active_sessions)

        message = interaction.edit_original_response.await_args.kwargs["content"]
        self.assertIn("기록 저장에 실패", message)
        finalize_admin_log.assert_awaited_once_with(
            session,
            aborted=True,
            reason="기록 저장 실패",
        )

    async def test_next_question_keeps_session_active(self):
        session = make_session(question_count=2)
        interaction = make_interaction()
        next_view = SimpleNamespace(stop=Mock())
        answer_view_factory = Mock(return_value=next_view)
        finalize_admin_log = AsyncMock()

        with patch.dict(active_sessions, {(10, 1): session}, clear=True):
            await quiz_completion.advance_or_finish(
                interaction,
                session,
                "제출 완료",
                build_final_embed=Mock(),
                build_question_embed=Mock(return_value="next-embed"),
                answer_view_factory=answer_view_factory,
                finalize_admin_log=finalize_admin_log,
                quiz_icon_text=Mock(),
                logger=Mock(),
            )

            self.assertIs(active_sessions[(10, 1)], session)

        self.assertEqual(session.index, 1)
        self.assertFalse(session.finished)
        interaction.edit_original_response.assert_awaited_once_with(
            content="제출 완료",
            embed="next-embed",
            view=next_view,
        )
        next_view.stop.assert_not_called()
        finalize_admin_log.assert_not_awaited()

    async def test_saved_completion_stays_complete_when_result_message_is_unavailable(self):
        for failure in ("edit", "fetch", "missing"):
            with self.subTest(failure=failure):
                session = make_session()
                interaction = None if failure == "missing" else make_interaction()
                if interaction is not None:
                    response = Mock(status=404, reason="Not Found", headers={})
                    target = (
                        interaction.edit_original_response if failure == "edit"
                        else interaction.original_response
                    )
                    target.side_effect = discord.HTTPException(response, "expired")
                finalize = AsyncMock()
                with (
                    patch.dict(active_sessions, {(10, 1): session}, clear=True),
                    patch.object(quiz_completion.asyncio, "to_thread", new=AsyncMock()) as save,
                ):
                    await quiz_completion.advance_or_finish(
                        interaction, session, "완료",
                        build_final_embed=Mock(), build_question_embed=Mock(),
                        answer_view_factory=Mock(), finalize_admin_log=finalize,
                        quiz_icon_text=Mock(), logger=Mock(),
                    )
                    self.assertNotIn((10, 1), active_sessions)
                save.assert_awaited_once()
                finalize.assert_awaited_once_with(session, aborted=False)
                self.assertTrue(session.finished)

    async def test_storage_failure_reason_survives_result_message_http_failure(self):
        session = make_session()
        interaction = make_interaction()
        response = Mock(status=404, reason="Not Found", headers={})
        interaction.edit_original_response.side_effect = discord.HTTPException(response, "expired")
        finalize = AsyncMock()
        with (
            patch.dict(active_sessions, {(10, 1): session}, clear=True),
            patch.object(
                quiz_completion.asyncio, "to_thread",
                new=AsyncMock(side_effect=RuntimeError("db failure")),
            ) as save,
        ):
            await quiz_completion.advance_or_finish(
                interaction, session, "완료",
                build_final_embed=Mock(), build_question_embed=Mock(),
                answer_view_factory=Mock(), finalize_admin_log=finalize,
                quiz_icon_text=Mock(), logger=Mock(),
            )
            self.assertNotIn((10, 1), active_sessions)
        save.assert_awaited_once()
        finalize.assert_awaited_once_with(session, aborted=True, reason="기록 저장 실패")

    async def test_unexpected_result_message_error_still_finalizes_storage_outcome(self):
        for stored in (True, False):
            with self.subTest(stored=stored):
                session = make_session()
                interaction = make_interaction()
                interaction.edit_original_response.side_effect = RuntimeError("message failure")
                finalize = AsyncMock()
                with (
                    patch.dict(active_sessions, {(10, 1): session}, clear=True),
                    patch.object(
                        quiz_completion.asyncio, "to_thread",
                        new=AsyncMock(side_effect=None if stored else RuntimeError("db failure")),
                    ),
                ):
                    with self.assertRaisesRegex(RuntimeError, "message failure"):
                        await quiz_completion.advance_or_finish(
                            interaction, session, "완료",
                            build_final_embed=Mock(), build_question_embed=Mock(),
                            answer_view_factory=Mock(), finalize_admin_log=finalize,
                            quiz_icon_text=Mock(), logger=Mock(),
                        )
                    self.assertNotIn((10, 1), active_sessions)
                if stored:
                    finalize.assert_awaited_once_with(session, aborted=False)
                else:
                    finalize.assert_awaited_once_with(
                        session, aborted=True, reason="기록 저장 실패"
                    )
                self.assertTrue(session.finished)

    async def test_next_question_message_failure_stops_new_view(self):
        session = make_session(question_count=2)
        interaction = make_interaction()
        response = Mock(status=404, reason="Not Found", headers={})
        interaction.edit_original_response.side_effect = discord.HTTPException(
            response, "expired"
        )
        next_view = SimpleNamespace(stop=Mock())
        finalize_admin_log = AsyncMock()

        with patch.dict(active_sessions, {(10, 1): session}, clear=True):
            await quiz_completion.advance_or_finish(
                interaction,
                session,
                "제출 완료",
                build_final_embed=Mock(),
                build_question_embed=Mock(return_value="next-embed"),
                answer_view_factory=Mock(return_value=next_view),
                finalize_admin_log=finalize_admin_log,
                quiz_icon_text=Mock(),
                logger=Mock(),
            )

            self.assertNotIn((10, 1), active_sessions)

        self.assertTrue(session.finished)
        next_view.stop.assert_called_once_with()
        finalize_admin_log.assert_awaited_once_with(
            session,
            aborted=True,
            reason="메시지 수정 실패로 중단",
        )


if __name__ == "__main__":
    unittest.main()

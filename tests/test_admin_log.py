import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord

import admin_log
from quiz_session import QuizSession


class AdminLogTests(unittest.TestCase):
    def test_embed_description_never_exceeds_safe_limit(self):
        session = QuizSession(
            mode="pvp",
            guild_id=10,
            user_id=1,
            username="테스터",
            channel_id=20,
            questions=[],
        )
        session.admin_log_lines.append("가" * 5000)
        decorate_embed = Mock()

        embed = admin_log.build_admin_embed(
            session,
            "진행 중",
            discord.Color.blurple(),
            mode_labels={"pvp": "PvP", "pve": "PvE"},
            decorate_embed=decorate_embed,
        )

        self.assertLessEqual(len(embed.description), 3900)
        self.assertTrue(embed.description.startswith("(이전 기록 생략)"))
        decorate_embed.assert_called_once()


class AdminLogAsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_delayed_creation_keeps_answers_and_flushes_final_state(self):
        question = {
            "difficulty": "general",
            "question": "생성 대기 중 답변",
            "choices": ["정답", "오답1", "오답2", "오답3"],
            "answer": 0,
            "explanation": "해설",
        }
        session = QuizSession(
            mode="pvp",
            guild_id=10,
            user_id=1,
            username="테스터",
            channel_id=20,
            questions=[question] * 30,
        )
        send_started = asyncio.Event()
        release_send = asyncio.Event()
        message = SimpleNamespace(edit=AsyncMock())

        async def delayed_send(**_kwargs):
            send_started.set()
            await release_send.wait()
            return message

        channel = SimpleNamespace(send=AsyncMock(side_effect=delayed_send))
        client = SimpleNamespace(get_channel=Mock(return_value=channel))
        helpers = {
            "mode_labels": {"pvp": "PvP", "pve": "PvE"},
            "decorate_embed": Mock(),
            "quiz_icon_text": lambda _guild, _name, fallback: fallback,
            "logger": Mock(),
        }

        with patch.object(admin_log.config, "ADMIN_LOG_CHANNEL_ID", 30):
            await admin_log.start_admin_log(client, session, **helpers)
        await asyncio.wait_for(send_started.wait(), timeout=1)
        session.per_difficulty["general"] = [0, 1]
        await admin_log.update_admin_log(
            session,
            question,
            False,
            False,
            "오답1",
            **helpers,
        )
        await admin_log.finalize_admin_log(session, aborted=False, **helpers)

        self.assertGreaterEqual(len(session.admin_log_lines), 2)
        self.assertFalse(session.admin_log_task.done())
        self.assertEqual(admin_log.pending_admin_log_count(), 1)
        self.assertEqual(admin_log.pending_admin_log_count(10), 1)
        self.assertEqual(admin_log.pending_admin_log_count(999), 0)

        release_send.set()
        await session.admin_log_task
        await asyncio.sleep(0)

        channel.send.assert_awaited_once()
        message.edit.assert_awaited_once()
        final_embed = message.edit.await_args.kwargs["embed"]
        self.assertEqual(final_embed.fields[0].value, "🟢 완료")
        self.assertIsNone(session.admin_log_message)
        self.assertEqual(admin_log.pending_admin_log_count(), 0)
        self.assertEqual(admin_log.pending_admin_log_count(10), 0)


if __name__ == "__main__":
    unittest.main()

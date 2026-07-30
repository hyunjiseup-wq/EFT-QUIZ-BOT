import unittest
from unittest.mock import AsyncMock, Mock

import bot


class BotHelpersTests(unittest.IsolatedAsyncioTestCase):
    def test_leaderboard_line_labels_accumulated_results(self):
        line = bot.format_leaderboard_line("🥇", "테스터", 100, 2, 7, 10)

        self.assertEqual(
            line,
            "🥇 **테스터** — 최고 100점 (누적 정답 7/10, 2회 도전)",
        )

    async def test_edit_session_message_uses_followup_edit_after_defer(self):
        session = Mock()
        interaction = Mock()
        interaction.response.is_done.return_value = True
        interaction.edit_original_response = AsyncMock()
        interaction.original_response = AsyncMock(return_value="updated-message")

        updated = await bot.edit_session_message(
            session,
            interaction,
            content="다음 문제",
            view=None,
        )

        self.assertTrue(updated)
        interaction.edit_original_response.assert_awaited_once_with(
            content="다음 문제",
            view=None,
        )
        interaction.response.edit_message.assert_not_called()
        self.assertEqual(session.message, "updated-message")


if __name__ == "__main__":
    unittest.main()

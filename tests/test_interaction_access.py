import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import interaction_access


class FakeMember:
    def __init__(self, *, administrator: bool):
        self.id = 1
        self.guild_permissions = SimpleNamespace(administrator=administrator)


def make_interaction(*, administrator: bool, response_done: bool = False):
    response = SimpleNamespace(
        is_done=Mock(return_value=response_done),
        send_message=AsyncMock(),
    )
    return SimpleNamespace(
        id=123456789,
        guild=SimpleNamespace(id=10),
        guild_id=10,
        user=FakeMember(administrator=administrator),
        response=response,
        followup=SimpleNamespace(send=AsyncMock()),
    )


class InteractionAccessTests(unittest.IsolatedAsyncioTestCase):
    async def test_administrator_is_allowed_without_response(self):
        interaction = make_interaction(administrator=True)

        with patch.object(interaction_access.discord, "Member", FakeMember):
            allowed = await interaction_access.require_guild_admin(
                interaction,
                quiz_alert_text=Mock(),
            )

        self.assertTrue(allowed)
        interaction.response.send_message.assert_not_awaited()

    async def test_non_administrator_receives_ephemeral_denial(self):
        interaction = make_interaction(administrator=False)
        alert_text = Mock(return_value="관리자 전용")

        with patch.object(interaction_access.discord, "Member", FakeMember):
            allowed = await interaction_access.require_guild_admin(
                interaction,
                quiz_alert_text=alert_text,
            )

        self.assertFalse(allowed)
        interaction.response.send_message.assert_awaited_once_with(
            "관리자 전용",
            ephemeral=True,
        )

    async def test_direct_message_context_is_denied(self):
        interaction = make_interaction(administrator=True)
        interaction.guild = None

        with patch.object(interaction_access.discord, "Member", FakeMember):
            allowed = await interaction_access.require_guild_admin(
                interaction,
                quiz_alert_text=Mock(return_value="차단"),
            )

        self.assertFalse(allowed)
        interaction.response.send_message.assert_awaited_once_with(
            "차단",
            ephemeral=True,
        )

    async def test_error_report_uses_followup_after_response(self):
        interaction = make_interaction(administrator=True, response_done=True)
        logger = Mock()

        await interaction_access.report_interaction_error(
            interaction,
            RuntimeError("failure"),
            context="test:button",
            quiz_icon_text=Mock(return_value="⚠️"),
            logger=logger,
        )

        interaction.response.send_message.assert_not_awaited()
        interaction.followup.send.assert_awaited_once()
        message = interaction.followup.send.await_args.args[0]
        self.assertIn("오류 번호 `23456789`", message)
        logger.error.assert_called_once()

    async def test_error_report_uses_initial_response_when_available(self):
        interaction = make_interaction(administrator=True, response_done=False)

        await interaction_access.report_interaction_error(
            interaction,
            ValueError("failure"),
            context="test:command",
            quiz_icon_text=Mock(return_value="⚠️"),
            logger=Mock(),
        )

        interaction.response.send_message.assert_awaited_once()
        interaction.followup.send.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()

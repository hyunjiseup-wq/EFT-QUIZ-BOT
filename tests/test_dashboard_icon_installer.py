import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord

import dashboard_icon_installer


def make_interaction(*, permissions=True, emojis=None, emoji_limit=50):
    guild = SimpleNamespace(
        id=10,
        me=SimpleNamespace(
            guild_permissions=SimpleNamespace(
                create_expressions=permissions,
                manage_expressions=permissions,
            )
        ),
        emojis=list(emojis or []),
        emoji_limit=emoji_limit,
        create_custom_emoji=AsyncMock(),
    )
    return SimpleNamespace(
        guild=guild,
        guild_id=10,
        user="관리자",
        response=SimpleNamespace(
            send_message=AsyncMock(),
            defer=AsyncMock(),
        ),
        followup=SimpleNamespace(send=AsyncMock()),
    )


class DashboardIconInstallerTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_bot_permission_stops_before_upload(self):
        interaction = make_interaction(permissions=False)

        await dashboard_icon_installer.install_dashboard_icons(
            interaction,
            refresh_dashboards=AsyncMock(),
            quiz_alert_text=Mock(return_value="권한 부족"),
            logger=Mock(),
        )

        interaction.response.send_message.assert_awaited_once_with(
            "권한 부족",
            ephemeral=True,
        )
        interaction.response.defer.assert_not_awaited()
        interaction.guild.create_custom_emoji.assert_not_awaited()

    async def test_slot_shortage_stops_before_upload(self):
        interaction = make_interaction()

        with (
            patch.object(
                dashboard_icon_installer,
                "validate_quiz_icon_assets",
                return_value=[],
            ),
            patch.object(
                dashboard_icon_installer,
                "missing_quiz_emoji_names",
                return_value=["one", "two"],
            ),
            patch.object(
                dashboard_icon_installer,
                "available_static_emoji_slots",
                return_value=1,
            ),
        ):
            await dashboard_icon_installer.install_dashboard_icons(
                interaction,
                refresh_dashboards=AsyncMock(),
                quiz_alert_text=Mock(return_value="슬롯 부족"),
                logger=Mock(),
            )

        interaction.response.send_message.assert_awaited_once_with(
            "슬롯 부족",
            ephemeral=True,
        )
        interaction.guild.create_custom_emoji.assert_not_awaited()

    async def test_existing_icons_are_reused_and_missing_icons_created(self):
        existing = SimpleNamespace(name="tq_correct", animated=False)
        created = SimpleNamespace(name="tq_warning", animated=False)
        interaction = make_interaction(emojis=[existing])
        interaction.guild.create_custom_emoji.return_value = created
        refresh_dashboards = AsyncMock(return_value=(["퀴즈", "감독"], []))

        with (
            patch.dict(
                dashboard_icon_installer.QUIZ_EMOJI_ASSETS,
                {"tq_correct": "correct.png", "tq_warning": "warning.png"},
                clear=True,
            ),
            patch.object(
                dashboard_icon_installer,
                "validate_quiz_icon_assets",
                return_value=[],
            ),
        ):
            await dashboard_icon_installer.install_dashboard_icons(
                interaction,
                refresh_dashboards=refresh_dashboards,
                quiz_alert_text=Mock(),
                logger=Mock(),
            )

        interaction.guild.create_custom_emoji.assert_awaited_once()
        refresh_dashboards.assert_awaited_once()
        summary = interaction.followup.send.await_args.args[0]
        self.assertIn("신규 등록 **1개**", summary)
        self.assertIn("기존 재사용 **1개**", summary)
        self.assertIn("퀴즈 · 감독", summary)

    async def test_http_failure_is_reported_and_remaining_uploads_continue(self):
        interaction = make_interaction()
        response = Mock(status=500, reason="Server Error", headers={})
        interaction.guild.create_custom_emoji.side_effect = [
            discord.HTTPException(response, "failed"),
            SimpleNamespace(name="tq_warning", animated=False),
        ]

        with (
            patch.dict(
                dashboard_icon_installer.QUIZ_EMOJI_ASSETS,
                {"tq_correct": "correct.png", "tq_warning": "warning.png"},
                clear=True,
            ),
            patch.object(
                dashboard_icon_installer,
                "validate_quiz_icon_assets",
                return_value=[],
            ),
        ):
            await dashboard_icon_installer.install_dashboard_icons(
                interaction,
                refresh_dashboards=AsyncMock(return_value=([], [])),
                quiz_alert_text=Mock(),
                logger=Mock(),
            )

        self.assertEqual(interaction.guild.create_custom_emoji.await_count, 2)
        summary = interaction.followup.send.await_args.args[0]
        self.assertIn("신규 등록 **1개**", summary)
        self.assertIn("tq_correct(HTTP 500)", summary)


if __name__ == "__main__":
    unittest.main()

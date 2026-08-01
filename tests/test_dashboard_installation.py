import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import discord

import dashboard_installation


def make_interaction(channel=None):
    return SimpleNamespace(
        guild_id=10,
        channel_id=20,
        channel=channel,
        response=SimpleNamespace(
            send_message=AsyncMock(),
            defer=AsyncMock(),
        ),
        followup=SimpleNamespace(send=AsyncMock()),
    )


def make_channel():
    return SimpleNamespace(history=Mock(), send=AsyncMock())


class DashboardInstallationTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_channel_is_rejected_before_defer(self):
        interaction = make_interaction(channel=SimpleNamespace())
        upsert = AsyncMock()

        await dashboard_installation.install_dashboard_message(
            interaction,
            upsert_dashboard=upsert,
            copy=dashboard_installation.QUIZ_DASHBOARD_COPY,
            quiz_alert_text=Mock(return_value="설치 불가"),
            quiz_icon_text=Mock(),
            logger=Mock(),
        )

        interaction.response.send_message.assert_awaited_once_with(
            "설치 불가",
            ephemeral=True,
        )
        interaction.response.defer.assert_not_awaited()
        upsert.assert_not_awaited()

    async def test_created_dashboard_returns_jump_link(self):
        channel = make_channel()
        interaction = make_interaction(channel)
        dashboard = SimpleNamespace(jump_url="https://discord.test/dashboard")

        await dashboard_installation.install_dashboard_message(
            interaction,
            upsert_dashboard=AsyncMock(return_value=(dashboard, True)),
            copy=dashboard_installation.QUIZ_DASHBOARD_COPY,
            quiz_alert_text=Mock(),
            quiz_icon_text=Mock(return_value="✅"),
            logger=Mock(),
        )

        interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        message = interaction.followup.send.await_args.args[0]
        self.assertIn("이 채널에 설치했습니다", message)
        self.assertIn(dashboard.jump_url, message)

    async def test_updated_supervisor_dashboard_uses_update_copy(self):
        channel = make_channel()
        interaction = make_interaction(channel)
        dashboard = SimpleNamespace(jump_url="https://discord.test/supervisor")

        await dashboard_installation.install_dashboard_message(
            interaction,
            upsert_dashboard=AsyncMock(return_value=(dashboard, False)),
            copy=dashboard_installation.SUPERVISOR_DASHBOARD_COPY,
            quiz_alert_text=Mock(),
            quiz_icon_text=Mock(return_value="✅"),
            logger=Mock(),
        )

        message = interaction.followup.send.await_args.args[0]
        self.assertIn("기존 감독 대시보드를 최신 내용으로 갱신", message)
        self.assertIn(dashboard.jump_url, message)

    async def test_forbidden_error_returns_permission_guidance(self):
        interaction = make_interaction(make_channel())
        response = Mock(status=403, reason="Forbidden", headers={})

        await dashboard_installation.install_dashboard_message(
            interaction,
            upsert_dashboard=AsyncMock(
                side_effect=discord.Forbidden(response, "forbidden")
            ),
            copy=dashboard_installation.QUIZ_DASHBOARD_COPY,
            quiz_alert_text=Mock(return_value="권한 안내"),
            quiz_icon_text=Mock(),
            logger=Mock(),
        )

        interaction.followup.send.assert_awaited_once_with(
            "권한 안내",
            ephemeral=True,
        )

    async def test_http_error_is_logged_and_returns_retry_guidance(self):
        interaction = make_interaction(make_channel())
        response = Mock(status=500, reason="Server Error", headers={})
        logger = Mock()

        await dashboard_installation.install_dashboard_message(
            interaction,
            upsert_dashboard=AsyncMock(
                side_effect=discord.HTTPException(response, "failed")
            ),
            copy=dashboard_installation.SUPERVISOR_DASHBOARD_COPY,
            quiz_alert_text=Mock(return_value="재시도 안내"),
            quiz_icon_text=Mock(),
            logger=logger,
        )

        logger.exception.assert_called_once()
        interaction.followup.send.assert_awaited_once_with(
            "재시도 안내",
            ephemeral=True,
        )


if __name__ == "__main__":
    unittest.main()

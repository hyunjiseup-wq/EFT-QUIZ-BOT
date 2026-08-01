import logging
from collections.abc import Callable
from dataclasses import dataclass

import discord


@dataclass(frozen=True)
class DashboardInstallCopy:
    log_label: str
    invalid_channel: str
    permission_error: str
    http_error: str
    created: str
    updated: str
    success_template: str


QUIZ_DASHBOARD_COPY = DashboardInstallCopy(
    log_label="퀴즈",
    invalid_channel="이 채널에는 대시보드를 설치할 수 없어요.",
    permission_error=(
        "대시보드를 설치하려면 이 채널의 **메시지 기록 보기**와 "
        "**메시지 보내기** 권한이 필요합니다."
    ),
    http_error=(
        "디스코드 요청 오류로 대시보드를 설치하지 못했습니다. "
        "잠시 후 다시 시도해주세요."
    ),
    created="대시보드를 이 채널에 설치했습니다.",
    updated="기존 대시보드를 최신 내용으로 갱신했습니다.",
    success_template=(
        "{icon} {result} 필요하면 [메시지로 이동]({jump_url})해 고정해주세요."
    ),
)

SUPERVISOR_DASHBOARD_COPY = DashboardInstallCopy(
    log_label="감독",
    invalid_channel="이 채널에는 감독 대시보드를 설치할 수 없어요.",
    permission_error=(
        "감독 대시보드를 설치하려면 이 채널의 **메시지 기록 보기**와 "
        "**메시지 보내기** 권한이 필요합니다."
    ),
    http_error="디스코드 요청 오류로 감독 대시보드를 설치하지 못했습니다.",
    created="감독 대시보드를 이 채널에 설치했습니다.",
    updated="기존 감독 대시보드를 최신 내용으로 갱신했습니다.",
    success_template="{icon} {result} [메시지로 이동]({jump_url})",
)


async def install_dashboard_message(
    interaction: discord.Interaction,
    *,
    upsert_dashboard: Callable,
    copy: DashboardInstallCopy,
    quiz_alert_text: Callable,
    quiz_icon_text: Callable,
    logger: logging.Logger,
):
    channel = interaction.channel
    if channel is None or not hasattr(channel, "history") or not hasattr(channel, "send"):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                copy.invalid_channel,
            ),
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)
    try:
        dashboard, created = await upsert_dashboard(channel)
    except discord.Forbidden:
        await interaction.followup.send(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                copy.permission_error,
            ),
            ephemeral=True,
        )
        return
    except discord.HTTPException:
        logger.exception(
            "%s 대시보드 설치/갱신 실패 (channel=%s)",
            copy.log_label,
            interaction.channel_id,
        )
        await interaction.followup.send(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                copy.http_error,
            ),
            ephemeral=True,
        )
        return

    icon = quiz_icon_text(interaction.guild_id, "tq_correct", "✅")
    result = copy.created if created else copy.updated
    await interaction.followup.send(
        copy.success_template.format(
            icon=icon,
            result=result,
            jump_url=dashboard.jump_url,
        ),
        ephemeral=True,
    )

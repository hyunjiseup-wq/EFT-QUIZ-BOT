import logging
from collections.abc import Callable

import discord

import config
from quiz_icons import (
    QUIZ_EMOJI_ASSETS,
    QUIZ_ICON_DIR,
    available_static_emoji_slots,
    missing_quiz_emoji_names,
    validate_quiz_icon_assets,
)


async def refresh_configured_dashboards(
    client: discord.Client,
    guild: discord.Guild,
    emojis: list[discord.Emoji],
    *,
    upsert_dashboard: Callable,
    upsert_supervisor_dashboard: Callable,
    logger: logging.Logger,
) -> tuple[list[str], list[str]]:
    """아이콘 등록 후 같은 서버의 설정된 대시보드 메시지를 갱신한다."""
    refreshed = []
    failed = []
    targets = (
        ("퀴즈", config.QUIZ_CHANNEL_ID, upsert_dashboard),
        ("감독", config.ADMIN_LOG_CHANNEL_ID, upsert_supervisor_dashboard),
    )
    for label, channel_id, updater in targets:
        if not channel_id:
            continue
        channel = client.get_channel(channel_id)
        if channel is None:
            try:
                channel = await client.fetch_channel(channel_id)
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                logger.exception("%s 대시보드 아이콘 갱신용 채널 조회 실패", label)
                failed.append(label)
                continue
        if getattr(getattr(channel, "guild", None), "id", None) != guild.id:
            continue
        try:
            await updater(channel, emojis=emojis)
        except (discord.Forbidden, discord.HTTPException):
            logger.exception("%s 대시보드 아이콘 적용 실패", label)
            failed.append(label)
        else:
            refreshed.append(label)
    return refreshed, failed


async def install_dashboard_icons(
    interaction: discord.Interaction,
    *,
    refresh_dashboards: Callable,
    quiz_alert_text: Callable,
    logger: logging.Logger,
):
    guild = interaction.guild
    bot_member = guild.me
    bot_permissions = bot_member.guild_permissions if bot_member else None
    if not (
        bot_permissions
        and (bot_permissions.create_expressions or bot_permissions.manage_expressions)
    ):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "아이콘을 등록하려면 봇 역할에 **표현물 만들기** 또는 "
                "**이모지 및 스티커 관리** 권한이 필요합니다.",
            ),
            ephemeral=True,
        )
        return

    asset_errors = validate_quiz_icon_assets()
    if asset_errors:
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "아이콘 파일 검증에 실패해 설치를 중단했습니다: "
                + ", ".join(asset_errors),
            ),
            ephemeral=True,
        )
        return

    emojis = list(guild.emojis)
    missing_names = missing_quiz_emoji_names(emojis)
    available_slots = available_static_emoji_slots(guild)
    if len(missing_names) > available_slots:
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                f"퀴즈 아이콘은 **{len(missing_names)}개**가 더 필요하지만 일반 이모지 "
                f"슬롯은 **{available_slots}개**만 남아 있어요. 서버 이모지 슬롯을 "
                "확보한 뒤 다시 실행해주세요.",
            ),
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)
    by_name = {emoji.name: emoji for emoji in emojis}
    created = []
    reused = []
    failed = []

    for emoji_name, filename in QUIZ_EMOJI_ASSETS.items():
        if emoji_name in by_name:
            reused.append(emoji_name)
            continue

        image = (QUIZ_ICON_DIR / filename).read_bytes()
        if len(image) > 256 * 1024:
            failed.append(f"{emoji_name}(256KB 초과)")
            continue
        try:
            emoji = await guild.create_custom_emoji(
                name=emoji_name,
                image=image,
                reason=f"{interaction.user}님의 퀴즈 대시보드 아이콘 설치",
            )
        except discord.Forbidden:
            failed.append(f"{emoji_name}(권한 부족)")
            break
        except discord.HTTPException as error:
            logger.exception("대시보드 커스텀 이모지 등록 실패: %s", emoji_name)
            failed.append(f"{emoji_name}(HTTP {error.status})")
            continue

        created.append(emoji_name)
        emojis.append(emoji)
        by_name[emoji_name] = emoji

    refreshed, refresh_failed = await refresh_dashboards(guild, emojis)
    success_icon = str(by_name.get("tq_correct") or "✅")
    lines = [
        f"{success_icon} 신규 등록 **{len(created)}개** · "
        f"기존 재사용 **{len(reused)}개**"
    ]
    if refreshed:
        lines.append(f"대시보드 갱신: **{' · '.join(refreshed)}**")
    if failed:
        lines.append("등록 실패: " + ", ".join(failed))
    if refresh_failed:
        lines.append("대시보드 갱신 실패: " + ", ".join(refresh_failed))
    if not refreshed and not refresh_failed:
        lines.append(
            "설정된 대시보드 채널이 없어 아이콘만 등록했습니다. "
            "각 채널에서 설치 명령을 실행하면 적용됩니다."
        )
    lines.append("같은 이름의 서버 이모지는 삭제하거나 덮어쓰지 않습니다.")
    await interaction.followup.send("\n".join(lines), ephemeral=True)

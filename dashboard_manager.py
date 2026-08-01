import inspect
import logging

import discord


def is_dashboard_message(
    message: discord.Message,
    bot_user: discord.ClientUser | None,
    marker: str,
    legacy_markers: tuple[str, ...] = (),
    expected_custom_id: str | None = None,
) -> bool:
    """이전 footer 또는 고유 버튼 ID를 가진 봇 대시보드인지 판별한다."""
    if message.author != bot_user or not message.embeds:
        return False
    if message.embeds[0].footer.text in (marker, *legacy_markers):
        return True
    if expected_custom_id is None:
        return False
    components = getattr(message, "components", ())
    if not isinstance(components, (list, tuple)):
        return False
    return any(
        getattr(component, "custom_id", None) == expected_custom_id
        for row in components
        for component in getattr(row, "children", ())
    )


async def find_dashboard_message(
    channel,
    bot_user: discord.ClientUser | None,
    marker: str,
    preferred_message_id: int | None = None,
    legacy_markers: tuple[str, ...] = (),
    expected_custom_id: str | None = None,
) -> discord.Message | None:
    """저장 ID, 고정 메시지, 최근 기록 순으로 기존 대시보드를 찾는다."""
    if preferred_message_id and hasattr(channel, "fetch_message"):
        try:
            message = await channel.fetch_message(preferred_message_id)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass
        else:
            if is_dashboard_message(
                message,
                bot_user,
                marker,
                legacy_markers,
                expected_custom_id,
            ):
                return message

    if hasattr(channel, "pins"):
        async for message in channel.pins(limit=50):
            if is_dashboard_message(
                message,
                bot_user,
                marker,
                legacy_markers,
                expected_custom_id,
            ):
                return message

    async for message in channel.history(limit=100):
        if is_dashboard_message(
            message,
            bot_user,
            marker,
            legacy_markers,
            expected_custom_id,
        ):
            return message
    return None


async def ensure_dashboard_pinned(
    message,
    label: str,
    logger: logging.Logger,
) -> bool:
    """대시보드가 기록에 묻히지 않도록 고정하며, 권한 부족은 실행을 막지 않는다."""
    if getattr(message, "pinned", False) is True:
        return True

    pin = getattr(message, "pin", None)
    if pin is None:
        return False
    try:
        result = pin(reason=f"타르코프 퀴즈 {label} 대시보드 자동 고정")
        if not inspect.isawaitable(result):
            return False
        await result
    except discord.Forbidden:
        logger.warning(
            "%s 대시보드를 고정하지 못했습니다. 봇의 '메시지 관리' 권한을 확인하세요.",
            label,
        )
        return False
    except discord.HTTPException as error:
        logger.warning("%s 대시보드 고정 실패: %s", label, error)
        return False
    return True


def channel_dashboard_emojis(channel) -> list[discord.Emoji]:
    """Mock/부분 채널에서도 안전하게 서버 이모지 캐시를 꺼낸다."""
    guild = getattr(channel, "guild", None)
    emojis = getattr(guild, "emojis", None)
    return list(emojis) if isinstance(emojis, (list, tuple)) else []

import inspect
import logging

import discord


def is_dashboard_message(
    message: discord.Message,
    bot_user: discord.ClientUser | None,
    marker: str,
) -> bool:
    """봇이 만든 대시보드인지 footer marker로 판별한다."""
    return bool(
        message.author == bot_user
        and message.embeds
        and message.embeds[0].footer.text == marker
    )


async def find_dashboard_message(
    channel,
    bot_user: discord.ClientUser | None,
    marker: str,
) -> discord.Message | None:
    """고정 메시지를 우선하고, 없으면 최근 메시지에서 기존 대시보드를 찾는다."""
    if hasattr(channel, "pins"):
        async for message in channel.pins(limit=50):
            if is_dashboard_message(message, bot_user, marker):
                return message

    async for message in channel.history(limit=100):
        if is_dashboard_message(message, bot_user, marker):
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

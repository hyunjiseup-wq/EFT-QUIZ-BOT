"""여러 서버에 흩어진 설정 채널 중 특정 서버의 채널을 찾는 도우미.

퀴즈 채널과 감독 채널은 서버마다 다르므로 설정값은 채널 ID 목록이다.
채널 ID는 전역에서 유일하므로 "허용 여부"는 목록 포함 여부로 판단하고,
"어느 채널로 보낼지"는 서버 기준으로 골라야 한다.
"""

import logging
from collections.abc import Iterable, Sequence

import discord

# 존재하지 않거나 봇이 접근할 수 없는 ID를 매 세션마다 다시 조회하지 않도록 기억한다.
_unresolvable_channel_ids: set[int] = set()


def _channel_guild_id(channel) -> int | None:
    return getattr(getattr(channel, "guild", None), "id", None)


def forget_unresolvable_channels() -> None:
    """재접속 등으로 캐시가 갱신됐을 때 실패 기록을 비운다."""
    _unresolvable_channel_ids.clear()


def guild_channel_id(
    client: discord.Client,
    channel_ids: Sequence[int],
    guild_id: int | None,
) -> int | None:
    """캐시에 있는 채널만 보고 해당 서버에 설정된 채널 ID를 반환한다."""
    for channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        if channel is not None and _channel_guild_id(channel) == guild_id:
            return channel_id
    return None


async def resolve_channel(
    client: discord.Client,
    channel_id: int,
    logger: logging.Logger,
    *,
    label: str,
):
    """캐시 우선으로 채널을 찾고, 없으면 한 번만 API로 조회한다."""
    channel = client.get_channel(channel_id)
    if channel is not None:
        return channel
    if channel_id in _unresolvable_channel_ids:
        return None
    try:
        return await client.fetch_channel(channel_id)
    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
        _unresolvable_channel_ids.add(channel_id)
        logger.warning(
            "%s 채널을 찾을 수 없습니다. 봇이 초대된 서버의 채널 ID인지 확인하세요. "
            "(channel=%s)",
            label,
            channel_id,
        )
        return None


async def fetch_guild_channel(
    client: discord.Client,
    channel_ids: Iterable[int],
    guild_id: int | None,
    logger: logging.Logger,
    *,
    label: str,
):
    """해당 서버에 설정된 채널 객체를 찾는다. 없으면 None."""
    uncached: list[int] = []
    for channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        if channel is None:
            uncached.append(channel_id)
        elif _channel_guild_id(channel) == guild_id:
            return channel

    for channel_id in uncached:
        channel = await resolve_channel(client, channel_id, logger, label=label)
        if channel is not None and _channel_guild_id(channel) == guild_id:
            return channel
    return None


def split_by_guild(
    client: discord.Client,
    channel_ids: Iterable[int],
    guild_id: int | None,
) -> tuple[list, list[int], list[int]]:
    """설정 채널을 (이 서버 채널, 다른 서버 ID, 조회 실패 ID)로 나눈다."""
    in_guild = []
    other_guild: list[int] = []
    unreachable: list[int] = []
    for channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        if channel is None:
            unreachable.append(channel_id)
        elif _channel_guild_id(channel) == guild_id:
            in_guild.append(channel)
        else:
            other_guild.append(channel_id)
    return in_guild, other_guild, unreachable

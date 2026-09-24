"""여러 서버에 흩어진 설정 채널 중 특정 서버의 채널을 찾는 도우미.

퀴즈 채널과 감독 채널은 서버마다 다르므로 설정값은 채널 ID 목록이다.
채널 ID는 전역에서 유일하므로 "허용 여부"는 목록 포함 여부로 판단하고,
"어느 채널로 보낼지"는 서버 기준으로 골라야 한다.
"""

import logging
import time
from collections.abc import Iterable, Sequence

import discord

# 존재하지 않거나 봇이 접근할 수 없는 ID를 매 세션마다 다시 조회하지 않도록 기억한다.
_unresolvable_channel_ids: set[int] = set()
# 서버 오류는 영구적인 채널 접근 실패가 아니다. 요청 폭주를 막고 다음 호출에서 재시도한다.
_transient_retry_after: dict[int, float] = {}
CHANNEL_RETRY_SECONDS = 30.0


def _channel_guild_id(channel) -> int | None:
    return getattr(getattr(channel, "guild", None), "id", None)


def forget_unresolvable_channels() -> None:
    """재접속 등으로 캐시가 갱신됐을 때 실패 기록을 비운다."""
    _unresolvable_channel_ids.clear()
    _transient_retry_after.clear()


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
    """캐시 우선 조회. 권한/삭제 오류는 기억하고 일시 HTTP 오류는 유예 후 재조회한다."""
    channel = client.get_channel(channel_id)
    if channel is not None:
        _unresolvable_channel_ids.discard(channel_id)
        _transient_retry_after.pop(channel_id, None)
        return channel
    if channel_id in _unresolvable_channel_ids:
        return None
    if time.monotonic() < _transient_retry_after.get(channel_id, 0.0):
        return None
    _transient_retry_after.pop(channel_id, None)
    try:
        return await client.fetch_channel(channel_id)
    except (discord.Forbidden, discord.NotFound):
        _unresolvable_channel_ids.add(channel_id)
        logger.warning(
            "%s 채널을 찾을 수 없습니다. 봇이 초대된 서버의 채널 ID인지 확인하세요. "
            "(channel=%s)",
            label,
            channel_id,
        )
        return None
    except discord.HTTPException as error:
        _transient_retry_after[channel_id] = time.monotonic() + CHANNEL_RETRY_SECONDS
        logger.warning(
            "%s 채널 조회 HTTP 오류. %.0f초 이후 다음 요청에서 재시도합니다. "
            "(channel=%s, status=%s)",
            label,
            CHANNEL_RETRY_SECONDS,
            channel_id,
            error.status,
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

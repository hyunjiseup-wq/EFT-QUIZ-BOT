import asyncio
import logging
from collections.abc import Callable, Mapping

import discord

import config
from quiz_session import QuizSession

ADMIN_LOG_TIMEOUT = 2.0


async def get_admin_channel(client: discord.Client, logger: logging.Logger):
    if not config.ADMIN_LOG_CHANNEL_ID:
        return None
    channel = client.get_channel(config.ADMIN_LOG_CHANNEL_ID)
    if channel is None:
        try:
            channel = await client.fetch_channel(config.ADMIN_LOG_CHANNEL_ID)
        except discord.HTTPException:
            logger.warning(
                "관리자 로그 채널을 찾을 수 없습니다. ADMIN_LOG_CHANNEL_ID를 확인하세요."
            )
            return None
    return channel


def build_admin_embed(
    session: QuizSession,
    status_line: str,
    color: discord.Color,
    *,
    mode_labels: Mapping[str, str],
    decorate_embed: Callable,
) -> discord.Embed:
    # 임베드 description 한도(4096자)를 고려해 넘치면 오래된 기록부터 자른다.
    lines = list(session.admin_log_lines)
    description = "\n".join(lines)
    while len(description) > 3900 and len(lines) > 1:
        lines.pop(0)
        description = "(이전 기록 생략)\n" + "\n".join(lines)
    if len(description) > 3900:
        marker = "(이전 기록 생략)\n"
        description = marker + description[-(3900 - len(marker)) :]
    embed = discord.Embed(
        description=description if lines else "(진행 기록 없음)",
        color=color,
    )
    decorate_embed(
        embed,
        f"[{mode_labels[session.mode]}] {session.username}",
        "tq_sessions",
        "🎮",
        guild_id=session.guild_id,
    )
    answered = sum(counts[1] for counts in session.per_difficulty.values())
    embed.add_field(name="상태", value=status_line, inline=True)
    embed.add_field(name="점수", value=f"{session.score}점", inline=True)
    embed.add_field(name="정답", value=f"{session.correct_count}/{answered}", inline=True)
    breakdown = " · ".join(
        f"{config.DIFFICULTY_LABEL[d]} {c}/{t}"
        for d, (c, t) in session.per_difficulty.items()
        if t
    )
    embed.add_field(name="난이도별", value=breakdown or "-", inline=False)
    return embed


async def start_admin_log(
    client: discord.Client,
    session: QuizSession,
    *,
    mode_labels: Mapping[str, str],
    decorate_embed: Callable,
    quiz_icon_text: Callable,
    logger: logging.Logger,
):
    channel = await get_admin_channel(client, logger)
    if channel is None:
        return
    status = f"{quiz_icon_text(session.guild_id, 'tq_sessions', '🟡')} 진행 중"
    embed = build_admin_embed(
        session,
        status,
        discord.Color.blurple(),
        mode_labels=mode_labels,
        decorate_embed=decorate_embed,
    )
    try:
        session.admin_log_message = await asyncio.wait_for(
            channel.send(embed=embed),
            timeout=ADMIN_LOG_TIMEOUT,
        )
    except TimeoutError:
        logger.warning("관리자 로그 생성 시간 초과; 퀴즈 진행은 계속합니다.")
    except discord.HTTPException as error:
        logger.warning("관리자 로그 생성 실패; 퀴즈 진행은 계속합니다: %s", error)


async def update_admin_log(
    session: QuizSession,
    question: dict,
    is_correct: bool,
    timed_out: bool,
    chosen_text: str | None = None,
    *,
    mode_labels: Mapping[str, str],
    decorate_embed: Callable,
    quiz_icon_text: Callable,
    logger: logging.Logger,
):
    if session.admin_log_message is None:
        return
    if timed_out:
        mark = quiz_icon_text(session.guild_id, "tq_timeout", "⏰")
    elif is_correct:
        mark = quiz_icon_text(session.guild_id, "tq_correct", "✅")
    else:
        mark = quiz_icon_text(session.guild_id, "tq_incorrect", "❌")
    diff_label = config.DIFFICULTY_LABEL[question["difficulty"]]
    session.admin_log_lines.append(
        f"`{session.index + 1:02d}` {mark} [{diff_label}] {question['question'][:40]}"
    )
    if timed_out or not is_correct:
        answer_text = question["choices"][question["answer"]]
        if chosen_text:
            session.admin_log_lines.append(
                f"　└ 응답: {chosen_text[:40]} → 정답: **{answer_text[:40]}**"
            )
        else:
            session.admin_log_lines.append(f"　└ 정답: **{answer_text[:40]}**")
        explanation = question.get("explanation")
        if explanation:
            intel_icon = quiz_icon_text(session.guild_id, "tq_tutorial", "💡")
            session.admin_log_lines.append(f"　└ {intel_icon} {explanation[:150]}")

    # 모든 답변은 메모리에 남기되 Discord API 편집은 묶어서 수행한다.
    answered = sum(counts[1] for counts in session.per_difficulty.values())
    if answered >= session.total or answered % config.ADMIN_LOG_UPDATE_EVERY:
        return

    status = f"{quiz_icon_text(session.guild_id, 'tq_sessions', '🟡')} 진행 중"
    embed = build_admin_embed(
        session,
        status,
        discord.Color.blurple(),
        mode_labels=mode_labels,
        decorate_embed=decorate_embed,
    )
    try:
        await asyncio.wait_for(
            session.admin_log_message.edit(embed=embed),
            timeout=ADMIN_LOG_TIMEOUT,
        )
    except TimeoutError:
        logger.warning("관리자 로그 갱신 시간 초과; 퀴즈 진행은 계속합니다.")
        session.admin_log_message = None
    except discord.HTTPException as error:
        logger.warning("관리자 로그 갱신 실패: %s", error)
        session.admin_log_message = None


async def finalize_admin_log(
    session: QuizSession,
    aborted: bool,
    reason: str = "",
    *,
    mode_labels: Mapping[str, str],
    decorate_embed: Callable,
    quiz_icon_text: Callable,
    logger: logging.Logger,
):
    if session.admin_log_message is None:
        return
    if aborted:
        exit_icon = quiz_icon_text(session.guild_id, "tq_exit", "⚪")
        status = f"{exit_icon} 중단됨{f' ({reason})' if reason else ''}"
        color = discord.Color.light_grey()
    else:
        status = f"{quiz_icon_text(session.guild_id, 'tq_complete', '🟢')} 완료"
        color = discord.Color.green()
    embed = build_admin_embed(
        session,
        status,
        color,
        mode_labels=mode_labels,
        decorate_embed=decorate_embed,
    )
    try:
        await asyncio.wait_for(
            session.admin_log_message.edit(embed=embed),
            timeout=ADMIN_LOG_TIMEOUT,
        )
    except TimeoutError:
        logger.warning(
            "최종 관리자 로그 갱신 시간 초과 (guild=%s, user=%s, aborted=%s)",
            session.guild_id,
            session.user_id,
            aborted,
        )
    except discord.HTTPException as error:
        logger.warning(
            "최종 관리자 로그 갱신 실패 (guild=%s, user=%s, aborted=%s): %s",
            session.guild_id,
            session.user_id,
            aborted,
            error,
        )
    session.admin_log_message = None

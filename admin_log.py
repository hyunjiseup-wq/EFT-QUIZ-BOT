import asyncio
import logging
from collections.abc import Callable, Mapping

import discord

import config
from quiz_session import QuizSession


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


def _admin_log_status(session: QuizSession, quiz_icon_text: Callable):
    if session.admin_log_finalized:
        if session.admin_log_aborted:
            exit_icon = quiz_icon_text(session.guild_id, "tq_exit", "⚪")
            suffix = (
                f" ({session.admin_log_final_reason})"
                if session.admin_log_final_reason
                else ""
            )
            return f"{exit_icon} 중단됨{suffix}", discord.Color.light_grey()
        complete_icon = quiz_icon_text(session.guild_id, "tq_complete", "🟢")
        return f"{complete_icon} 완료", discord.Color.green()
    active_icon = quiz_icon_text(session.guild_id, "tq_sessions", "🟡")
    return f"{active_icon} 진행 중", discord.Color.blurple()


async def _flush_admin_log(
    session: QuizSession,
    *,
    mode_labels: Mapping[str, str],
    decorate_embed: Callable,
    quiz_icon_text: Callable,
    logger: logging.Logger,
) -> None:
    """Discord 레이트리밋은 기다리되 대기 중 변경은 최신 상태로 병합한다."""
    channel = session.admin_log_channel
    if channel is None and session.admin_log_message is None:
        return

    try:
        while True:
            revision = session.admin_log_revision
            status, color = _admin_log_status(session, quiz_icon_text)
            embed = build_admin_embed(
                session,
                status,
                color,
                mode_labels=mode_labels,
                decorate_embed=decorate_embed,
            )
            if session.admin_log_message is None:
                session.admin_log_message = await channel.send(embed=embed)
            else:
                await session.admin_log_message.edit(embed=embed)

            if session.admin_log_revision == revision:
                if session.admin_log_finalized:
                    session.admin_log_message = None
                return
    except asyncio.CancelledError:
        raise
    except (discord.HTTPException, TimeoutError) as error:
        logger.warning(
            "관리자 로그 비동기 갱신 실패 (guild=%s, user=%s): %s",
            session.guild_id,
            session.user_id,
            error,
        )
        if session.admin_log_finalized:
            session.admin_log_message = None
    except Exception:
        logger.exception(
            "관리자 로그 비동기 처리 오류 (guild=%s, user=%s)",
            session.guild_id,
            session.user_id,
        )


def _ensure_admin_log_flush(
    session: QuizSession,
    *,
    mode_labels: Mapping[str, str],
    decorate_embed: Callable,
    quiz_icon_text: Callable,
    logger: logging.Logger,
) -> None:
    if session.admin_log_channel is None and session.admin_log_message is None:
        return
    task = session.admin_log_task
    if task is not None and not task.done():
        return
    session.admin_log_task = asyncio.create_task(
        _flush_admin_log(
            session,
            mode_labels=mode_labels,
            decorate_embed=decorate_embed,
            quiz_icon_text=quiz_icon_text,
            logger=logger,
        )
    )


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
    session.admin_log_channel = channel
    session.admin_log_revision += 1
    _ensure_admin_log_flush(
        session,
        mode_labels=mode_labels,
        decorate_embed=decorate_embed,
        quiz_icon_text=quiz_icon_text,
        logger=logger,
    )


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
    session.admin_log_revision += 1

    # 모든 답변은 메모리에 남기되 Discord API 편집은 묶어서 수행한다.
    answered = sum(counts[1] for counts in session.per_difficulty.values())
    if answered >= session.total or answered % config.ADMIN_LOG_UPDATE_EVERY:
        return
    _ensure_admin_log_flush(
        session,
        mode_labels=mode_labels,
        decorate_embed=decorate_embed,
        quiz_icon_text=quiz_icon_text,
        logger=logger,
    )


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
    session.admin_log_finalized = True
    session.admin_log_aborted = aborted
    session.admin_log_final_reason = reason
    session.admin_log_revision += 1
    _ensure_admin_log_flush(
        session,
        mode_labels=mode_labels,
        decorate_embed=decorate_embed,
        quiz_icon_text=quiz_icon_text,
        logger=logger,
    )

import asyncio
import logging
import time
from collections.abc import Callable

import discord

import database
from quiz_session import QuizSession, cleanup_session


async def edit_session_message(
    session: QuizSession,
    interaction,
    *,
    finalize_admin_log: Callable,
    logger: logging.Logger,
    **message_kwargs,
) -> bool:
    """세션 메시지를 수정하고 복구 불가능한 HTTP 오류에서는 세션을 정리한다."""
    try:
        if interaction is not None:
            if interaction.response.is_done():
                await interaction.edit_original_response(**message_kwargs)
            else:
                await interaction.response.edit_message(**message_kwargs)
            session.message = await interaction.original_response()
        elif session.message:
            await session.message.edit(**message_kwargs)
        else:
            return False
        return True
    except discord.HTTPException as error:
        # ephemeral 메시지는 인터랙션 토큰이 만료되면 더 이상 수정할 수 없다.
        logger.warning("세션 메시지 수정 실패 (user=%s): %s", session.user_id, error)
        await finalize_admin_log(
            session,
            aborted=True,
            reason="메시지 수정 실패로 중단",
        )
        cleanup_session(session)
        return False


async def advance_or_finish(
    interaction,
    session: QuizSession,
    result_text: str,
    *,
    build_final_embed: Callable,
    build_question_embed: Callable,
    answer_view_factory: Callable,
    finalize_admin_log: Callable,
    quiz_icon_text: Callable,
    logger: logging.Logger,
):
    session.index += 1

    if session.index >= session.total:
        embed = build_final_embed(session)
        # SQLite 쓰기가 Discord 이벤트 루프를 막지 않도록 작업 스레드에서 실행한다.
        try:
            await asyncio.to_thread(
                database.record_result,
                session.guild_id,
                session.mode,
                session.user_id,
                session.username,
                session.score,
                session.correct_count,
                session.total,
                timed_out_count=session.timed_out_count,
                duration_seconds=time.monotonic() - session.started_at_monotonic,
            )
        except Exception:
            logger.exception(
                "퀴즈 결과 저장 실패 (guild=%s, user=%s)",
                session.guild_id,
                session.user_id,
            )
            await edit_session_message(
                session,
                interaction,
                finalize_admin_log=finalize_admin_log,
                logger=logger,
                content=(
                    f"{quiz_icon_text(session.guild_id, 'tq_warning', '⚠️')} "
                    "퀴즈는 완료됐지만 기록 저장에 실패했습니다. 관리자에게 문의해주세요."
                ),
                embed=embed,
                view=None,
            )
            await finalize_admin_log(
                session,
                aborted=True,
                reason="기록 저장 실패",
            )
            cleanup_session(session)
            return

        updated = await edit_session_message(
            session,
            interaction,
            finalize_admin_log=finalize_admin_log,
            logger=logger,
            content=result_text,
            embed=embed,
            view=None,
        )
        if updated:
            await finalize_admin_log(session, aborted=False)
        cleanup_session(session)
        return

    next_embed = build_question_embed(session)
    next_view = answer_view_factory(session)
    updated = await edit_session_message(
        session,
        interaction,
        finalize_admin_log=finalize_admin_log,
        logger=logger,
        content=result_text,
        embed=next_embed,
        view=next_view,
    )
    if not updated:
        next_view.stop()

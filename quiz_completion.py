import asyncio
import logging
import time
from collections.abc import Callable

import discord

import database
from quiz_session import QuizSession, cleanup_session


async def _finalize_and_cleanup(
    session: QuizSession,
    *,
    finalize_admin_log: Callable,
    logger: logging.Logger,
    aborted: bool,
    reason: str = "",
) -> None:
    """관리자 로그 마감 실패와 무관하게 세션을 레지스트리에서 제거한다."""
    try:
        if reason:
            await finalize_admin_log(session, aborted=aborted, reason=reason)
        else:
            await finalize_admin_log(session, aborted=aborted)
    except Exception:
        logger.exception(
            "세션 최종 관리자 로그 정리 실패 (guild=%s, user=%s, aborted=%s)",
            session.guild_id,
            session.user_id,
            aborted,
        )
    finally:
        cleanup_session(session)


async def edit_session_message(
    session: QuizSession,
    interaction,
    *,
    finalize_admin_log: Callable,
    logger: logging.Logger,
    finalize_on_failure: bool = True,
    **message_kwargs,
) -> bool:
    """메시지를 수정한다. 완료 처리는 실패 시 정리를 호출자가 맡을 수 있다."""
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
            logger.warning(
                "수정할 세션 메시지가 없습니다 (guild=%s, user=%s)",
                session.guild_id,
                session.user_id,
            )
            if finalize_on_failure:
                await _finalize_and_cleanup(
                    session,
                    finalize_admin_log=finalize_admin_log,
                    logger=logger,
                    aborted=True,
                    reason="세션 메시지 없음으로 중단",
                )
            return False
        return True
    except discord.HTTPException as error:
        # ephemeral 메시지는 인터랙션 토큰이 만료되면 더 이상 수정할 수 없다.
        logger.warning("세션 메시지 수정 실패 (user=%s): %s", session.user_id, error)
        if finalize_on_failure:
            await _finalize_and_cleanup(
                session,
                finalize_admin_log=finalize_admin_log,
                logger=logger,
                aborted=True,
                reason="메시지 수정 실패로 중단",
            )
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
            try:
                await edit_session_message(
                    session,
                    interaction,
                    finalize_admin_log=finalize_admin_log,
                    logger=logger,
                    finalize_on_failure=False,
                    content=(
                        f"{quiz_icon_text(session.guild_id, 'tq_warning', '⚠️')} "
                        "퀴즈는 완료됐지만 기록 저장에 실패했습니다. 관리자에게 문의해주세요."
                    ),
                    embed=embed,
                    view=None,
                )
            finally:
                await _finalize_and_cleanup(
                    session,
                    finalize_admin_log=finalize_admin_log,
                    logger=logger,
                    aborted=True,
                    reason="기록 저장 실패",
                )
            return

        # DB 저장 성공은 결과 화면 전달 성공과 별개다. 화면 실패로 완주를 중단 처리하지 않는다.
        try:
            await edit_session_message(
                session,
                interaction,
                finalize_admin_log=finalize_admin_log,
                logger=logger,
                finalize_on_failure=False,
                content=result_text,
                embed=embed,
                view=None,
            )
        finally:
            await _finalize_and_cleanup(
                session,
                finalize_admin_log=finalize_admin_log,
                logger=logger,
                aborted=False,
            )
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

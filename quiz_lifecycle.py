import logging
from collections.abc import Callable

import discord

from quiz_session import (
    QuizSession,
    active_sessions,
    cleanup_session,
    count_active_sessions,
)


async def abort_quiz_session(
    session: QuizSession,
    *,
    finalize_admin_log: Callable,
    reason: str,
    logger: logging.Logger,
) -> bool:
    """예상 밖 처리 오류가 난 활성 세션을 한 번만 중단하고 정리한다."""
    async with session.transition_lock:
        if session.finished:
            return False
        try:
            await finalize_admin_log(session, aborted=True, reason=reason)
        except Exception:
            logger.exception(
                "오류 세션 관리자 로그 정리 실패 (guild=%s, user=%s)",
                session.guild_id,
                session.user_id,
            )
        finally:
            cleanup_session(session)
    return True


async def start_quiz(
    interaction: discord.Interaction,
    mode: str,
    *,
    quiz_channel_id: int,
    max_active_sessions: int,
    build_questions: Callable[[str], list[dict]],
    build_question_embed: Callable[[QuizSession], discord.Embed],
    answer_view_factory: Callable[[QuizSession], discord.ui.View],
    start_admin_log: Callable,
    quiz_alert_text: Callable,
    logger: logging.Logger,
) -> QuizSession | None:
    """새 세션을 등록하고 첫 화면 전송 실패 시 등록을 되돌린다."""
    if quiz_channel_id and interaction.channel_id != quiz_channel_id:
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_notice_quiz",
                "🎯",
                f"퀴즈는 <#{quiz_channel_id}> 채널에서만 시작할 수 있어요!",
            ),
            ephemeral=True,
        )
        return None

    key = (interaction.guild_id, interaction.user.id)
    existing = active_sessions.get(key)
    if existing is not None:
        if existing.is_active():
            await interaction.response.send_message(
                quiz_alert_text(
                    interaction.guild_id,
                    "tq_warning",
                    "⚠️",
                    "이미 진행 중인 퀴즈가 있어요! `/타르코프퀴즈포기`로 종료하거나 "
                    "기존 퀴즈를 끝내주세요.",
                ),
                ephemeral=True,
            )
            return None
        # 예외 종료 뒤 레지스트리에 남은 세션은 새 시작을 막지 않도록 회수한다.
        cleanup_session(existing)

    guild_active_count = count_active_sessions(interaction.guild_id)
    if guild_active_count >= max_active_sessions:
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "현재 동시 응시자가 많아 새 퀴즈를 잠시 시작할 수 없어요. "
                "진행 중인 응시자가 끝난 뒤 다시 시도해주세요.",
            ),
            ephemeral=True,
        )
        logger.warning(
            "서버 동시 세션 상한 도달 (guild=%s, active=%s, limit=%s)",
            interaction.guild_id,
            guild_active_count,
            max_active_sessions,
        )
        return None

    session = QuizSession(
        mode=mode,
        guild_id=interaction.guild_id,
        user_id=interaction.user.id,
        username=interaction.user.display_name,
        channel_id=interaction.channel_id,
        questions=build_questions(mode),
    )
    embed = build_question_embed(session)
    view = answer_view_factory(session)

    # 이 지점까지 await가 없으므로 동일 이벤트 루프에서 중복 확인과 등록은 원자적이다.
    active_sessions[key] = session
    try:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        session.message = await interaction.original_response()
    except BaseException as error:
        view.stop()
        cleanup_session(session)
        if isinstance(error, Exception):
            logger.exception("퀴즈 시작 메시지 전송 실패 (user=%s)", session.user_id)
            # 첫 응답은 전송됐지만 원본 조회만 실패한 경우 남은 버튼을 비활성화한다.
            try:
                if interaction.response.is_done():
                    await interaction.edit_original_response(
                        content="퀴즈 시작에 실패했어요. 잠시 후 다시 시도해주세요.",
                        embed=None,
                        view=None,
                    )
            except Exception:
                logger.warning(
                    "실패한 퀴즈 시작 화면 회수 불가 (guild=%s, user=%s)",
                    session.guild_id,
                    session.user_id,
                )
        raise

    # 관리자 관전 로그는 보조 기능이다. 예상 밖 오류도 응시 세션을 중단시키지 않는다.
    try:
        await start_admin_log(interaction.client, session)
    except Exception:
        logger.exception(
            "관리자 로그 시작 실패; 퀴즈는 계속합니다 (guild=%s, user=%s)",
            session.guild_id,
            session.user_id,
        )
    return session


async def give_up_quiz(
    interaction: discord.Interaction,
    *,
    finalize_admin_log: Callable,
    quiz_alert_text: Callable,
    quiz_icon_text: Callable,
    logger: logging.Logger,
) -> bool:
    """현재 사용자의 세션을 중단하며 부가 작업 실패와 무관하게 정리한다."""
    session = active_sessions.get((interaction.guild_id, interaction.user.id))
    if session is None:
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_notice_quiz",
                "🎯",
                "진행 중인 퀴즈가 없어요.",
            ),
            ephemeral=True,
        )
        return False

    # 관리자 로그 마감과 기존 화면 편집 전에 최초 응답을 확보한다.
    await interaction.response.defer(ephemeral=True)

    async with session.transition_lock:
        if not session.is_active():
            cleanup_session(session)
            await interaction.edit_original_response(
                content=quiz_alert_text(
                    interaction.guild_id,
                    "tq_complete",
                    "🏁",
                    "이미 종료된 퀴즈예요.",
                ),
            )
            return False
        try:
            await finalize_admin_log(session, aborted=True, reason="응시자 포기")
        except Exception:
            logger.exception(
                "포기 세션 관리자 로그 정리 실패 (guild=%s, user=%s)",
                session.guild_id,
                session.user_id,
            )
        finally:
            cleanup_session(session)

    # 남아있는 퀴즈 화면의 버튼 제거 시도. 실패해도 세션은 이미 정리됐다.
    if session.message:
        try:
            await session.message.edit(
                content=(
                    f"{quiz_icon_text(session.guild_id, 'tq_exit', '🚪')} "
                    "퀴즈를 포기했어요."
                ),
                embed=None,
                view=None,
            )
        except discord.HTTPException as error:
            logger.warning(
                "포기한 퀴즈 화면 정리 실패 (guild=%s, user=%s): %s",
                session.guild_id,
                session.user_id,
                error,
            )

    await interaction.edit_original_response(
        content=quiz_alert_text(
            interaction.guild_id,
            "tq_exit",
            "🚪",
            "퀴즈를 포기했어요. `/pvp퀴즈` 또는 `/pve퀴즈`로 다시 도전할 수 있어요!",
        ),
    )
    return True

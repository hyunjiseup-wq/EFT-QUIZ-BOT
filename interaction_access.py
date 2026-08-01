import logging
from collections.abc import Callable

import discord

ADMIN_COMMAND_MESSAGE = "이 명령어는 서버 관리자만 사용할 수 있어요."


def is_guild_admin(interaction: discord.Interaction) -> bool:
    """실제 서버 Member이며 관리자 권한이 있는 요청만 허용한다."""
    return bool(
        interaction.guild
        and isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    )


async def require_guild_admin(
    interaction: discord.Interaction,
    *,
    quiz_alert_text: Callable,
    denied_message: str = ADMIN_COMMAND_MESSAGE,
) -> bool:
    """관리자가 아니면 비공개 안내를 보내고 False를 반환한다."""
    if is_guild_admin(interaction):
        return True
    await interaction.response.send_message(
        quiz_alert_text(
            interaction.guild_id,
            "tq_warning",
            "⚠️",
            denied_message,
        ),
        ephemeral=True,
    )
    return False


async def report_interaction_error(
    interaction: discord.Interaction,
    error: Exception,
    *,
    context: str,
    quiz_icon_text: Callable,
    logger: logging.Logger,
):
    """처리되지 않은 인터랙션 오류를 기록하고 추적 가능한 오류 번호를 안내한다."""
    original = getattr(error, "original", error)
    error_id = str(interaction.id)[-8:]
    logger.error(
        "Discord 인터랙션 처리 실패 (error_id=%s, context=%s, user=%s)",
        error_id,
        context,
        interaction.user.id,
        exc_info=(type(original), original, original.__traceback__),
    )
    warning_icon = quiz_icon_text(interaction.guild_id, "tq_warning", "⚠️")
    message = (
        f"{warning_icon} 요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요. "
        f"계속되면 관리자에게 오류 번호 `{error_id}`를 알려주세요."
    )
    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException:
        logger.warning("Discord 오류 안내 메시지 전송 실패 (error_id=%s)", error_id)

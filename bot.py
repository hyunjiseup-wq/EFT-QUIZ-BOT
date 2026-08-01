import asyncio
import logging
import random
import time
from datetime import datetime, timedelta, timezone

import discord

import config
import database
from dashboard_manager import (
    channel_dashboard_emojis,
    ensure_dashboard_pinned,
    find_dashboard_message,
)
from question_bank import (
    filter_questions_for_mode,
    group_by_difficulty,
    load_validated_questions,
    select_session_questions,
)
from quiz_icons import (
    QUIZ_EMOJI_ASSETS,
    QUIZ_ICON_DIR,
    apply_dashboard_emojis,
    available_static_emoji_slots,
    missing_quiz_emoji_names,
    validate_quiz_icon_assets,
)
from quiz_session import (
    QuizSession,
    active_sessions,
    cleanup_session,
    count_active_sessions,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tarkov_quiz")

intents = discord.Intents.default()
ADMIN_LOG_TIMEOUT = 2.0


class QuizBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        # on_ready는 재연결 시마다 반복될 수 있으므로 명령어 동기화는 여기서 1회만 수행한다.
        database.init_db()
        # timeout=None + 고정 custom_id를 사용하는 뷰를 등록하면 봇 재시작 뒤에도
        # 기존 대시보드 메시지의 버튼 인터랙션을 계속 받을 수 있다.
        self.add_view(QuizDashboardView())
        self.add_view(SupervisorDashboardView())
        try:
            synced = await self.tree.sync()
        except discord.HTTPException:
            # 명령어는 Discord에 이미 등록되어 있을 수 있다. 일시적인 API 장애 때문에
            # 퀴즈 봇 전체가 시작하지 못하는 상황은 피하고 다음 재시작 때 다시 시도한다.
            log.exception("슬래시 명령어 동기화 실패; 기존 등록 명령어로 봇을 계속 실행합니다.")
        else:
            log.info("슬래시 명령어 %s개 동기화 완료", len(synced))


bot = QuizBot(intents=intents)

ALL_QUESTIONS = load_validated_questions(config.QUESTIONS_PATH, config.SESSION_COUNTS)

# 난이도별로 문제를 미리 그룹화 (매 세션마다 이 풀에서 랜덤 추출)
QUESTIONS_BY_MODE = {
    mode: group_by_difficulty(filter_questions_for_mode(ALL_QUESTIONS, mode))
    for mode in ("pvp", "pve")
}
MODE_LABELS = {"pvp": "PvP", "pve": "PvE"}
DASHBOARD_MARKER = "타르코프 퀴즈 대시보드 · v1"
SUPERVISOR_DASHBOARD_MARKER = "타르코프 퀴즈 감독 대시보드 · v1"


def find_quiz_emoji(
    emoji_name: str,
    *,
    guild_id: int | None = None,
    emojis: list[discord.Emoji] | tuple[discord.Emoji, ...] | None = None,
) -> discord.Emoji | None:
    """서버 캐시나 전달받은 목록에서 퀴즈 전용 이모지를 찾는다."""
    if emojis is None and guild_id:
        guild = bot.get_guild(guild_id)
        emojis = guild.emojis if guild else None
    if not emojis:
        return None
    return discord.utils.get(emojis, name=emoji_name)


def quiz_icon_text(guild_id: int | None, emoji_name: str, fallback: str) -> str:
    """알림 본문용 커스텀 이모지 문자열. 미설치 서버는 기본 이모지를 쓴다."""
    emoji = find_quiz_emoji(emoji_name, guild_id=guild_id)
    return str(emoji) if emoji else fallback


def quiz_alert_text(
    guild_id: int | None,
    emoji_name: str,
    fallback: str,
    text: str,
) -> str:
    return f"{quiz_icon_text(guild_id, emoji_name, fallback)} {text}"


def decorate_embed(
    embed: discord.Embed,
    title: str,
    emoji_name: str,
    fallback: str,
    *,
    guild_id: int | None = None,
    emojis: list[discord.Emoji] | tuple[discord.Emoji, ...] | None = None,
) -> discord.Embed:
    """커스텀 아이콘은 썸네일로, 미설치 시 기본 이모지는 제목에 표시한다."""
    emoji = find_quiz_emoji(emoji_name, guild_id=guild_id, emojis=emojis)
    if emoji:
        embed.title = title
        embed.set_thumbnail(url=str(emoji.url))
    else:
        embed.title = f"{fallback} {title}"
    return embed


def build_session_questions(mode: str) -> list:
    """난이도별로 config.SESSION_COUNTS 개수만큼 문제 풀에서 랜덤 추출 후, 전체 순서를 섞어 반환."""
    return select_session_questions(QUESTIONS_BY_MODE[mode], config.SESSION_COUNTS)


def build_dashboard_embed(
    emojis: list[discord.Emoji] | tuple[discord.Emoji, ...] | None = None,
) -> discord.Embed:
    """퀴즈 채널에 고정해 둘 공개 대시보드 메시지를 만든다."""
    embed = discord.Embed(
        description=(
            "플레이할 모드를 선택하세요. 퀴즈 화면은 **본인에게만** 보이며,\n"
            "문제마다 제한시간 안에 보기 버튼을 눌러 답하면 됩니다."
        ),
        color=discord.Color.dark_teal(),
    )
    decorate_embed(embed, "타르코프 지식 퀴즈", "tq_notice_quiz", "🎯", emojis=emojis)
    embed.add_field(
        name="퀴즈 구성",
        value=(
            f"전체 문제 풀 **{len(ALL_QUESTIONS)}문제** "
            f"(PvP {sum(len(pool) for pool in QUESTIONS_BY_MODE['pvp'].values())} · "
            f"PvE {sum(len(pool) for pool in QUESTIONS_BY_MODE['pve'].values())}) · "
            f"1회 **{config.TOTAL_QUESTIONS}문제** · "
            f"문제당 **{config.QUESTION_TIME_LIMIT}초**"
        ),
        inline=False,
    )
    embed.add_field(
        name="모드 안내",
        value=(
            "**PvP** — 공통 + 현재 PvP로 분류된 시즌 문항\n"
            "**PvE** — 공통 + PvE Zone 전용 문제"
        ),
        inline=False,
    )
    embed.add_field(
        name="처음이신가요?",
        value="아래 **튜토리얼** 버튼에서 진행 방식과 주의사항을 확인하세요.",
        inline=False,
    )
    embed.set_footer(text=DASHBOARD_MARKER)
    return embed


def build_tutorial_embed(guild_id: int | None = None) -> discord.Embed:
    """대시보드에서 본인에게만 보여줄 간단한 이용 안내."""
    embed = discord.Embed(
        description="대시보드에서 모드를 고르면 즉시 개인 퀴즈가 시작됩니다.",
        color=discord.Color.blurple(),
    )
    decorate_embed(
        embed,
        "타르코프 퀴즈 튜토리얼",
        "tq_tutorial",
        "📘",
        guild_id=guild_id,
    )
    embed.add_field(
        name="1. 모드 선택",
        value=(
            "**PvP 퀴즈**는 공통 지식과 현재 PvP로 분류된 시즌 문항을,\n"
            "**PvE 퀴즈**는 공통 지식과 PvE Zone 전용 문제를 출제합니다."
        ),
        inline=False,
    )
    embed.add_field(
        name="2. 문제 풀이",
        value=(
            f"한 번에 {config.TOTAL_QUESTIONS}문제가 출제되며 문제당 "
            f"{config.QUESTION_TIME_LIMIT}초입니다. 시간 초과는 오답 처리됩니다."
        ),
        inline=False,
    )
    embed.add_field(
        name="3. 결과와 정답",
        value=(
            "진행 중에는 정오답·점수·정답을 공개하지 않습니다. "
            "모든 문제를 풀면 최종 점수와 정답 수가 저장됩니다."
        ),
        inline=False,
    )
    embed.add_field(
        name="4. 중단·기록 확인",
        value=(
            "중단하려면 `/타르코프퀴즈포기`, 개인 기록은 `/pvp퀴즈기록` 또는 "
            "`/pve퀴즈기록`을 사용하세요. 포기한 퀴즈는 기록되지 않습니다."
        ),
        inline=False,
    )
    embed.set_footer(text="튜토리얼은 본인에게만 표시됩니다.")
    return embed


def build_supervisor_dashboard_embed(
    emojis: list[discord.Emoji] | tuple[discord.Emoji, ...] | None = None,
) -> discord.Embed:
    """감독 채널에 고정해 둘 관리자 전용 대시보드."""
    embed = discord.Embed(
        description=(
            "참가 현황과 랭킹을 확인하고 히든 상품 후보를 검토하는 관리자용 패널입니다.\n"
            "응시자의 문제별 정오답은 이 채널에 생성되는 관전 로그에서 확인하세요."
        ),
        color=discord.Color.dark_purple(),
    )
    decorate_embed(
        embed,
        "타르코프 퀴즈 감독 대시보드",
        "tq_sessions",
        "🛰️",
        emojis=emojis,
    )
    embed.add_field(
        name="공개 운영 현황",
        value="서버 참가자·완주 횟수, PvP/PvE 랭킹, 현재 활성 세션",
        inline=False,
    )
    embed.add_field(
        name="히든 상품 검토",
        value=(
            "최근 30일 기준 최다 완주 · 참여 일수 · 성장 · 언더독 · "
            "PvP/PvE 올라운더 후보"
        ),
        inline=False,
    )
    embed.add_field(
        name="권한",
        value="아래 버튼은 서버 관리자만 사용할 수 있습니다.",
        inline=False,
    )
    embed.set_footer(text=SUPERVISOR_DASHBOARD_MARKER)
    return embed


async def report_interaction_error(
    interaction: discord.Interaction,
    error: Exception,
    *,
    context: str,
):
    """슬래시 명령과 영구 버튼에서 공통으로 사용하는 최종 오류 응답."""
    original = getattr(error, "original", error)
    error_id = str(interaction.id)[-8:]
    log.error(
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
        log.warning("Discord 오류 안내 메시지 전송 실패 (error_id=%s)", error_id)


class QuizDashboardView(discord.ui.View):
    """재시작 후에도 작동하는 공개 퀴즈 진입점."""

    def __init__(self, emojis: list[discord.Emoji] | None = None):
        super().__init__(timeout=None)
        apply_dashboard_emojis(self, emojis)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item,
    ):
        await report_interaction_error(
            interaction,
            error,
            context=f"dashboard:{getattr(item, 'custom_id', 'unknown')}",
        )

    @discord.ui.button(
        label="PvP 퀴즈 시작",
        emoji="⚔️",
        style=discord.ButtonStyle.danger,
        custom_id="tarkov_quiz:pvp:start",
        row=0,
    )
    async def start_pvp(self, interaction: discord.Interaction, button: discord.ui.Button):
        await start_quiz(interaction, "pvp")

    @discord.ui.button(
        label="PvE 퀴즈 시작",
        emoji="🛡️",
        style=discord.ButtonStyle.success,
        custom_id="tarkov_quiz:pve:start",
        row=0,
    )
    async def start_pve(self, interaction: discord.Interaction, button: discord.ui.Button):
        await start_quiz(interaction, "pve")

    @discord.ui.button(
        label="튜토리얼",
        emoji="📘",
        style=discord.ButtonStyle.primary,
        custom_id="tarkov_quiz:tutorial",
        row=0,
    )
    async def tutorial(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=build_tutorial_embed(interaction.guild_id),
            ephemeral=True,
        )

    @discord.ui.button(
        label="PvP 랭킹",
        emoji="🏆",
        style=discord.ButtonStyle.secondary,
        custom_id="tarkov_quiz:pvp:ranking",
        row=1,
    )
    async def pvp_ranking(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await show_leaderboard(interaction, "pvp", ephemeral=True)

    @discord.ui.button(
        label="PvE 랭킹",
        emoji="🏆",
        style=discord.ButtonStyle.secondary,
        custom_id="tarkov_quiz:pve:ranking",
        row=1,
    )
    async def pve_ranking(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await show_leaderboard(interaction, "pve", ephemeral=True)

    @discord.ui.button(
        label="내 PvP 기록",
        emoji="📊",
        style=discord.ButtonStyle.secondary,
        custom_id="tarkov_quiz:pvp:record",
        row=1,
    )
    async def pvp_record(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_my_record(interaction, "pvp")

    @discord.ui.button(
        label="내 PvE 기록",
        emoji="📊",
        style=discord.ButtonStyle.secondary,
        custom_id="tarkov_quiz:pve:record",
        row=1,
    )
    async def pve_record(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_my_record(interaction, "pve")


class SupervisorDashboardView(discord.ui.View):
    """감독 채널에서만 사용하는 관리자용 영구 대시보드."""

    def __init__(self, emojis: list[discord.Emoji] | None = None):
        super().__init__(timeout=None)
        apply_dashboard_emojis(self, emojis)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        is_admin = (
            interaction.guild
            and isinstance(interaction.user, discord.Member)
            and interaction.user.guild_permissions.administrator
        )
        if not is_admin:
            await interaction.response.send_message(
                quiz_alert_text(
                    interaction.guild_id,
                    "tq_warning",
                    "⚠️",
                    "감독 대시보드는 서버 관리자만 사용할 수 있어요.",
                ),
                ephemeral=True,
            )
            return False
        if (
            config.ADMIN_LOG_CHANNEL_ID
            and interaction.channel_id != config.ADMIN_LOG_CHANNEL_ID
        ):
            await interaction.response.send_message(
                quiz_alert_text(
                    interaction.guild_id,
                    "tq_notice_quiz",
                    "🎯",
                    f"감독 기능은 <#{config.ADMIN_LOG_CHANNEL_ID}> 채널에서만 사용할 수 있어요.",
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item,
    ):
        await report_interaction_error(
            interaction,
            error,
            context=f"supervisor:{getattr(item, 'custom_id', 'unknown')}",
        )

    @discord.ui.button(
        label="참가 현황",
        emoji="📈",
        style=discord.ButtonStyle.primary,
        custom_id="tarkov_quiz:supervisor:stats",
        row=0,
    )
    async def participation(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await show_public_stats(interaction)

    @discord.ui.button(
        label="히든 후보 30일",
        emoji="🎁",
        style=discord.ButtonStyle.success,
        custom_id="tarkov_quiz:supervisor:rewards",
        row=0,
    )
    async def rewards(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_hidden_reward_candidates(interaction, 30)

    @discord.ui.button(
        label="활성 세션",
        emoji="🎮",
        style=discord.ButtonStyle.secondary,
        custom_id="tarkov_quiz:supervisor:sessions",
        row=0,
    )
    async def sessions(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_count = count_active_sessions(interaction.guild_id)
        pvp_count = count_active_sessions(interaction.guild_id, "pvp")
        pve_count = count_active_sessions(interaction.guild_id, "pve")
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_sessions",
                "🎮",
                f"현재 활성 세션 **{total_count}개** "
                f"(PvP {pvp_count} · PvE {pve_count})",
            ),
            ephemeral=True,
        )

    @discord.ui.button(
        label="PvP 랭킹",
        emoji="🏆",
        style=discord.ButtonStyle.secondary,
        custom_id="tarkov_quiz:supervisor:pvp-ranking",
        row=1,
    )
    async def pvp_ranking(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await show_leaderboard(interaction, "pvp", ephemeral=True)

    @discord.ui.button(
        label="PvE 랭킹",
        emoji="🏆",
        style=discord.ButtonStyle.secondary,
        custom_id="tarkov_quiz:supervisor:pve-ranking",
        row=1,
    )
    async def pve_ranking(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await show_leaderboard(interaction, "pve", ephemeral=True)


def build_question_embed(session: QuizSession) -> discord.Embed:
    q = session.current_question

    # 매번 보기 순서를 섞어서 정답 위치 암기를 방지
    order = list(range(len(q["choices"])))
    random.shuffle(order)
    session.current_shuffled_choices = order

    # 난이도/배점은 응시자에게 비공개 (관리자 관전 로그에서만 표시)
    embed = discord.Embed(
        title=f"{MODE_LABELS[session.mode]} 문제 {session.index + 1} / {session.total}",
        description=q["question"],
        color=discord.Color.dark_gold(),
    )
    emoji = find_quiz_emoji("tq_notice_quiz", guild_id=session.guild_id)
    if emoji:
        embed.set_thumbnail(url=str(emoji.url))
    labels = ["🇦", "🇧", "🇨", "🇩"]
    for i, orig_idx in enumerate(order):
        embed.add_field(name=labels[i], value=q["choices"][orig_idx], inline=False)
    # 진행 중 점수를 보여주면 직전 문제의 정오답이 드러나므로 표시하지 않는다
    embed.set_footer(text=f"제한시간 {config.QUESTION_TIME_LIMIT}초")
    return embed


def build_result_text(timed_out: bool, guild_id: int | None = None) -> str:
    # 응시자에게는 정답/오답 여부와 정답을 공개하지 않는다 (관전 로그에서만 확인 가능).
    if timed_out:
        return (
            f"{quiz_icon_text(guild_id, 'tq_timeout', '⏰')} "
            "시간 초과! 다음 문제로 넘어갑니다."
        )
    return (
        f"{quiz_icon_text(guild_id, 'tq_submitted', '📨')} "
        "답변이 제출되었습니다."
    )


class AnswerButton(discord.ui.Button):
    def __init__(self, label: str, display_index: int):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.display_index = display_index

    async def callback(self, interaction: discord.Interaction):
        view: AnswerView = self.view
        await view.handle_answer(interaction, self.display_index)


class AnswerView(discord.ui.View):
    def __init__(self, session: QuizSession):
        super().__init__(timeout=config.QUESTION_TIME_LIMIT)
        self.session = session
        self.question_index = session.index
        labels = ["🇦", "🇧", "🇨", "🇩"]
        for i in range(4):
            self.add_item(AnswerButton(labels[i], i))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.session.user_id:
            await interaction.response.send_message(
                quiz_alert_text(
                    interaction.guild_id,
                    "tq_warning",
                    "⚠️",
                    "이 퀴즈는 당신의 세션이 아니에요!",
                ),
                ephemeral=True,
            )
            return False
        return True

    async def handle_answer(self, interaction: discord.Interaction, display_index: int):
        # 관리자 로그 API가 느리더라도 Discord의 3초 인터랙션 응답 제한을 넘기지 않는다.
        # defer에 실패한 경우에는 뷰의 제한시간 처리가 계속될 수 있도록 stop보다 먼저 호출한다.
        await interaction.response.defer()
        # 답변을 받는 즉시 뷰를 정지시켜 on_timeout이 뒤늦게 실행되어
        # 문제가 이중으로 진행되는 것을 차단
        self.stop()

        session = self.session
        async with session.transition_lock:
            if not session.is_active() or session.index != self.question_index:
                return

            q = session.current_question
            order = session.current_shuffled_choices
            chosen_original_idx = order[display_index]
            is_correct = chosen_original_idx == q["answer"]

            diff = q["difficulty"]
            session.per_difficulty[diff][1] += 1
            if is_correct:
                session.score += config.POINTS[diff]
                session.correct_count += 1
                session.per_difficulty[diff][0] += 1

            result_text = build_result_text(timed_out=False, guild_id=session.guild_id)

            await update_admin_log(
                session,
                q,
                is_correct,
                timed_out=False,
                chosen_text=q["choices"][chosen_original_idx],
            )
            await advance_or_finish(interaction, session, result_text)

    async def on_timeout(self):
        session = self.session
        async with session.transition_lock:
            # 이미 답변 처리됐거나 다음 문제로 넘어간 경우 아무것도 하지 않음
            if not session.is_active() or session.index != self.question_index:
                return

            q = session.current_question
            diff = q["difficulty"]
            session.per_difficulty[diff][1] += 1
            session.timed_out_count += 1
            result_text = build_result_text(timed_out=True, guild_id=session.guild_id)

            await update_admin_log(session, q, False, timed_out=True)
            await advance_or_finish(None, session, result_text)


async def edit_session_message(session: QuizSession, interaction, **kwargs) -> bool:
    """응시자 세션 메시지를 수정한다. 실패(토큰 만료 등) 시 False를 반환하고 세션을 정리한다."""
    try:
        if interaction is not None:
            if interaction.response.is_done():
                await interaction.edit_original_response(**kwargs)
            else:
                await interaction.response.edit_message(**kwargs)
            session.message = await interaction.original_response()
        elif session.message:
            await session.message.edit(**kwargs)
        else:
            return False
        return True
    except discord.HTTPException as e:
        # ephemeral 메시지는 최초 인터랙션 토큰이 만료(약 15분)되면 봇이 임의로 수정할 수 없음
        log.warning(f"세션 메시지 수정 실패 (user={session.user_id}): {e}")
        await finalize_admin_log(session, aborted=True, reason="메시지 수정 실패로 중단")
        cleanup_session(session)
        return False


async def advance_or_finish(interaction, session: QuizSession, result_text: str):
    session.index += 1

    if session.index >= session.total:
        embed = build_final_embed(session)
        # DB 쓰기는 스레드로 분리해 이벤트 루프 블로킹 방지
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
            log.exception(
                "퀴즈 결과 저장 실패 (guild=%s, user=%s)", session.guild_id, session.user_id
            )
            await edit_session_message(
                session,
                interaction,
                content=(
                    f"{quiz_icon_text(session.guild_id, 'tq_warning', '⚠️')} "
                    "퀴즈는 완료됐지만 기록 저장에 실패했습니다. 관리자에게 문의해주세요."
                ),
                embed=embed,
                view=None,
            )
            await finalize_admin_log(session, aborted=True, reason="기록 저장 실패")
            cleanup_session(session)
            return

        updated = await edit_session_message(
            session, interaction, content=result_text, embed=embed, view=None
        )
        if updated:
            await finalize_admin_log(session, aborted=False)
        cleanup_session(session)
        return

    next_embed = build_question_embed(session)
    next_view = AnswerView(session)
    ok = await edit_session_message(
        session, interaction, content=result_text, embed=next_embed, view=next_view
    )
    if not ok:
        next_view.stop()


def build_final_embed(session: QuizSession) -> discord.Embed:
    embed = discord.Embed(
        description=f"**{session.username}**님의 결과입니다.",
        color=discord.Color.green(),
    )
    decorate_embed(
        embed,
        "퀴즈 완료!",
        "tq_complete",
        "🏁",
        guild_id=session.guild_id,
    )
    embed.add_field(name="총점", value=f"{session.score}점", inline=True)
    embed.add_field(name="모드", value=MODE_LABELS[session.mode], inline=True)
    embed.add_field(name="정답 수", value=f"{session.correct_count} / {session.total}", inline=True)
    embed.set_footer(
        text=f"/{session.mode}퀴즈랭킹 명령어로 서버 랭킹을 확인해보세요."
    )
    return embed


# ---------------------------------------------------------------------------
# 관리자 관전 로그
# 세션당 메시지 1개를 생성 후 계속 edit하는 방식.
# (문제마다 새 메시지를 보내면 응시자 1명당 30개 메시지가 쌓여
#  동시 응시 시 채널 도배 + 디스코드 레이트리밋 문제가 발생하기 때문)
# ---------------------------------------------------------------------------


async def get_admin_channel(client: discord.Client):
    if not config.ADMIN_LOG_CHANNEL_ID:
        return None
    channel = client.get_channel(config.ADMIN_LOG_CHANNEL_ID)
    if channel is None:
        try:
            channel = await client.fetch_channel(config.ADMIN_LOG_CHANNEL_ID)
        except discord.HTTPException:
            log.warning("관리자 로그 채널을 찾을 수 없습니다. ADMIN_LOG_CHANNEL_ID를 확인하세요.")
            return None
    return channel


def build_admin_embed(
    session: QuizSession, status_line: str, color: discord.Color
) -> discord.Embed:
    # 임베드 description 한도(4096자)를 고려해, 넘치면 오래된 기록부터 잘라낸다
    lines = list(session.admin_log_lines)
    description = "\n".join(lines)
    while len(description) > 3900 and len(lines) > 1:
        lines.pop(0)
        description = "(이전 기록 생략)\n" + "\n".join(lines)
    embed = discord.Embed(
        description=description if lines else "(진행 기록 없음)",
        color=color,
    )
    decorate_embed(
        embed,
        f"[{MODE_LABELS[session.mode]}] {session.username}",
        "tq_sessions",
        "🎮",
        guild_id=session.guild_id,
    )
    answered = sum(counts[1] for counts in session.per_difficulty.values())
    embed.add_field(name="상태", value=status_line, inline=True)
    embed.add_field(name="점수", value=f"{session.score}점", inline=True)
    embed.add_field(name="정답", value=f"{session.correct_count}/{answered}", inline=True)
    # 난이도별 현황은 응시자에게는 비공개, 관전 로그에서만 표시
    breakdown = " · ".join(
        f"{config.DIFFICULTY_LABEL[d]} {c}/{t}" for d, (c, t) in session.per_difficulty.items() if t
    )
    embed.add_field(name="난이도별", value=breakdown or "-", inline=False)
    return embed


async def start_admin_log(client: discord.Client, session: QuizSession):
    channel = await get_admin_channel(client)
    if channel is None:
        return
    status = f"{quiz_icon_text(session.guild_id, 'tq_sessions', '🟡')} 진행 중"
    embed = build_admin_embed(session, status, discord.Color.blurple())
    try:
        session.admin_log_message = await asyncio.wait_for(
            channel.send(embed=embed),
            timeout=ADMIN_LOG_TIMEOUT,
        )
    except TimeoutError:
        log.warning("관리자 로그 생성 시간 초과; 퀴즈 진행은 계속합니다.")
    except discord.HTTPException as error:
        log.warning("관리자 로그 생성 실패; 퀴즈 진행은 계속합니다: %s", error)


async def update_admin_log(
    session: QuizSession,
    q: dict,
    is_correct: bool,
    timed_out: bool,
    chosen_text: str | None = None,
):
    if session.admin_log_message is None:
        return
    if timed_out:
        mark = quiz_icon_text(session.guild_id, "tq_timeout", "⏰")
    elif is_correct:
        mark = quiz_icon_text(session.guild_id, "tq_correct", "✅")
    else:
        mark = quiz_icon_text(session.guild_id, "tq_incorrect", "❌")
    diff_label = config.DIFFICULTY_LABEL[q["difficulty"]]
    session.admin_log_lines.append(
        f"`{session.index + 1:02d}` {mark} [{diff_label}] {q['question'][:40]}"
    )
    # 오답/시간초과 문항은 응시자 문의("왜 오답이냐") 대응을 위해
    # 고른 보기 · 정답 · 해설을 관전 로그에 함께 남긴다 (응시자에게는 비공개)
    if timed_out or not is_correct:
        answer_text = q["choices"][q["answer"]]
        if chosen_text:
            session.admin_log_lines.append(
                f"　└ 응답: {chosen_text[:40]} → 정답: **{answer_text[:40]}**"
            )
        else:
            session.admin_log_lines.append(f"　└ 정답: **{answer_text[:40]}**")
        explanation = q.get("explanation")
        if explanation:
            intel_icon = quiz_icon_text(session.guild_id, "tq_tutorial", "💡")
            session.admin_log_lines.append(f"　└ {intel_icon} {explanation[:150]}")

    # 모든 답변은 메모리에 남기되 Discord API 편집은 묶어서 수행한다.
    # 마지막 문제는 finalize_admin_log가 최종 상태와 함께 한 번만 갱신한다.
    answered = sum(counts[1] for counts in session.per_difficulty.values())
    if answered >= session.total or answered % config.ADMIN_LOG_UPDATE_EVERY:
        return

    status = f"{quiz_icon_text(session.guild_id, 'tq_sessions', '🟡')} 진행 중"
    embed = build_admin_embed(session, status, discord.Color.blurple())
    try:
        await asyncio.wait_for(
            session.admin_log_message.edit(embed=embed),
            timeout=ADMIN_LOG_TIMEOUT,
        )
    except TimeoutError:
        log.warning("관리자 로그 갱신 시간 초과; 퀴즈 진행은 계속합니다.")
        session.admin_log_message = None
    except discord.HTTPException as e:
        log.warning(f"관리자 로그 갱신 실패: {e}")
        session.admin_log_message = None  # 이후 갱신 시도 중단


async def finalize_admin_log(session: QuizSession, aborted: bool, reason: str = ""):
    if session.admin_log_message is None:
        return
    if aborted:
        exit_icon = quiz_icon_text(session.guild_id, "tq_exit", "⚪")
        status = f"{exit_icon} 중단됨{f' ({reason})' if reason else ''}"
        color = discord.Color.light_grey()
    else:
        status = f"{quiz_icon_text(session.guild_id, 'tq_complete', '🟢')} 완료"
        color = discord.Color.green()
    embed = build_admin_embed(session, status, color)
    try:
        await asyncio.wait_for(
            session.admin_log_message.edit(embed=embed),
            timeout=ADMIN_LOG_TIMEOUT,
        )
    except TimeoutError:
        log.warning(
            "최종 관리자 로그 갱신 시간 초과 (guild=%s, user=%s, aborted=%s)",
            session.guild_id,
            session.user_id,
            aborted,
        )
    except discord.HTTPException as error:
        log.warning(
            "최종 관리자 로그 갱신 실패 (guild=%s, user=%s, aborted=%s): %s",
            session.guild_id,
            session.user_id,
            aborted,
            error,
        )
    session.admin_log_message = None


# ---------------------------------------------------------------------------
# 슬래시 명령어
# ---------------------------------------------------------------------------


@bot.event
async def on_ready():
    log.info(f"{bot.user}로 로그인 완료")
    await ensure_configured_dashboard()
    await ensure_supervisor_dashboard()


async def start_quiz(interaction: discord.Interaction, mode: str):
    if config.QUIZ_CHANNEL_ID and interaction.channel_id != config.QUIZ_CHANNEL_ID:
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_notice_quiz",
                "🎯",
                f"퀴즈는 <#{config.QUIZ_CHANNEL_ID}> 채널에서만 시작할 수 있어요!",
            ),
            ephemeral=True,
        )
        return

    key = (interaction.guild_id, interaction.user.id)
    if key in active_sessions:
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
        return

    guild_active_count = count_active_sessions(interaction.guild_id)
    if guild_active_count >= config.MAX_ACTIVE_SESSIONS_PER_GUILD:
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
        log.warning(
            "서버 동시 세션 상한 도달 (guild=%s, active=%s, limit=%s)",
            interaction.guild_id,
            guild_active_count,
            config.MAX_ACTIVE_SESSIONS_PER_GUILD,
        )
        return

    questions = build_session_questions(mode)

    session = QuizSession(
        mode=mode,
        guild_id=interaction.guild_id,
        user_id=interaction.user.id,
        username=interaction.user.display_name,
        channel_id=interaction.channel_id,
        questions=questions,
    )
    active_sessions[key] = session

    embed = build_question_embed(session)
    view = AnswerView(session)
    try:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        session.message = await interaction.original_response()
    except discord.HTTPException:
        view.stop()
        cleanup_session(session)
        log.exception("퀴즈 시작 메시지 전송 실패 (user=%s)", session.user_id)
        raise

    await start_admin_log(interaction.client, session)


@bot.tree.command(
    name="pvp퀴즈",
    description=f"PvP 기준 타르코프 퀴즈를 시작합니다 ({config.TOTAL_QUESTIONS}문제)",
)
@discord.app_commands.guild_only()
async def start_pvp_quiz(interaction: discord.Interaction):
    await start_quiz(interaction, "pvp")


@bot.tree.command(
    name="pve퀴즈",
    description=f"PvE Zone 기준 타르코프 퀴즈를 시작합니다 ({config.TOTAL_QUESTIONS}문제)",
)
@discord.app_commands.guild_only()
async def start_pve_quiz(interaction: discord.Interaction):
    await start_quiz(interaction, "pve")


@bot.tree.command(
    name="타르코프퀴즈포기", description="진행 중인 퀴즈를 포기합니다 (기록에 저장되지 않음)"
)
@discord.app_commands.guild_only()
async def give_up_cmd(interaction: discord.Interaction):
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
        return

    async with session.transition_lock:
        if not session.is_active():
            await interaction.response.send_message(
                quiz_alert_text(
                    interaction.guild_id,
                    "tq_complete",
                    "🏁",
                    "이미 종료된 퀴즈예요.",
                ),
                ephemeral=True,
            )
            return
        await finalize_admin_log(session, aborted=True, reason="응시자 포기")
        cleanup_session(session)

    # 남아있는 퀴즈 화면의 버튼 제거 시도 (실패해도 무방)
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
        except discord.HTTPException:
            pass

    await interaction.response.send_message(
        quiz_alert_text(
            interaction.guild_id,
            "tq_exit",
            "🚪",
            "퀴즈를 포기했어요. `/pvp퀴즈` 또는 `/pve퀴즈`로 다시 도전할 수 있어요!",
        ),
        ephemeral=True,
    )


async def show_leaderboard(
    interaction: discord.Interaction, mode: str, *, ephemeral: bool = False
):
    await interaction.response.defer(ephemeral=ephemeral)
    rows = await asyncio.to_thread(
        database.get_leaderboard, interaction.guild_id, mode, 10
    )
    if not rows:
        await interaction.edit_original_response(
            content=quiz_alert_text(
                interaction.guild_id,
                "tq_notice_quiz",
                "🎯",
                "아직 기록이 없어요. 먼저 퀴즈에 도전해보세요!",
            )
        )
        return

    embed = discord.Embed(
        color=discord.Color.gold(),
    )
    decorate_embed(
        embed,
        f"{MODE_LABELS[mode]} 퀴즈 랭킹 TOP 10",
        f"tq_{mode}_rank",
        "🏆",
        guild_id=interaction.guild_id,
    )
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (username, best_score, attempts, correct, total) in enumerate(rows):
        prefix = medals[i] if i < 3 else f"{i + 1}."
        lines.append(
            format_leaderboard_line(
                prefix, username, best_score, attempts, correct, total
            )
        )
    embed.description = "\n".join(lines)
    await interaction.edit_original_response(embed=embed)


@bot.tree.command(name="pvp퀴즈랭킹", description="PvP 퀴즈 서버 랭킹을 확인합니다")
@discord.app_commands.guild_only()
async def pvp_leaderboard_cmd(interaction: discord.Interaction):
    await show_leaderboard(interaction, "pvp")


@bot.tree.command(name="pve퀴즈랭킹", description="PvE 퀴즈 서버 랭킹을 확인합니다")
@discord.app_commands.guild_only()
async def pve_leaderboard_cmd(interaction: discord.Interaction):
    await show_leaderboard(interaction, "pve")


def build_public_stats_embed(
    stats: dict,
    guild_id: int | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        description="서버의 PvP·PvE 퀴즈 누적 완주 기록입니다.",
        color=discord.Color.teal(),
    )
    decorate_embed(
        embed,
        "타르코프 퀴즈 참가 현황",
        "tq_participation",
        "📈",
        guild_id=guild_id,
    )
    embed.add_field(
        name="전체 참가자",
        value=f"**{stats['total_participants']}명**",
        inline=True,
    )
    embed.add_field(
        name="총 완주",
        value=f"**{stats['total_attempts']}회**",
        inline=True,
    )
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    for mode in ("pvp", "pve"):
        mode_stats = stats["modes"][mode]
        embed.add_field(
            name=MODE_LABELS[mode],
            value=(
                f"참가자 **{mode_stats['participants']}명**\n"
                f"완주 **{mode_stats['attempts']}회**"
            ),
            inline=True,
        )
    embed.set_footer(text="포기한 퀴즈는 참가·완주 통계에 포함되지 않습니다.")
    return embed


@bot.tree.command(
    name="퀴즈참가현황",
    description="서버의 퀴즈 참가자 수와 모드별 누적 완주 횟수를 확인합니다",
)
@discord.app_commands.guild_only()
async def quiz_participation_stats_cmd(interaction: discord.Interaction):
    await show_public_stats(interaction)


async def show_public_stats(
    interaction: discord.Interaction, *, ephemeral: bool = False
):
    await interaction.response.defer(ephemeral=ephemeral)
    stats = await asyncio.to_thread(database.get_public_stats, interaction.guild_id)
    await interaction.edit_original_response(
        embed=build_public_stats_embed(stats, interaction.guild_id)
    )


async def upsert_dashboard(
    channel,
    *,
    emojis: list[discord.Emoji] | None = None,
) -> tuple[discord.Message, bool]:
    """채널의 대시보드를 만들거나 최신 내용으로 갱신한다.

    반환값의 bool은 새 메시지를 만들었으면 True다.
    """
    dashboard = await find_dashboard_message(channel, bot.user, DASHBOARD_MARKER)
    resolved_emojis = channel_dashboard_emojis(channel) if emojis is None else emojis
    view = QuizDashboardView(resolved_emojis)
    embed = build_dashboard_embed(resolved_emojis)
    if dashboard is None:
        dashboard = await channel.send(embed=embed, view=view)
        await ensure_dashboard_pinned(dashboard, "퀴즈", log)
        return dashboard, True

    await dashboard.edit(embed=embed, view=view)
    await ensure_dashboard_pinned(dashboard, "퀴즈", log)
    return dashboard, False


async def upsert_supervisor_dashboard(
    channel,
    *,
    emojis: list[discord.Emoji] | None = None,
) -> tuple[discord.Message, bool]:
    """감독 채널의 관리자 대시보드를 만들거나 갱신한다."""
    dashboard = await find_dashboard_message(
        channel, bot.user, SUPERVISOR_DASHBOARD_MARKER
    )
    resolved_emojis = channel_dashboard_emojis(channel) if emojis is None else emojis
    view = SupervisorDashboardView(resolved_emojis)
    embed = build_supervisor_dashboard_embed(resolved_emojis)
    if dashboard is None:
        dashboard = await channel.send(
            embed=embed,
            view=view,
        )
        await ensure_dashboard_pinned(dashboard, "감독", log)
        return dashboard, True

    await dashboard.edit(embed=embed, view=view)
    await ensure_dashboard_pinned(dashboard, "감독", log)
    return dashboard, False


async def ensure_configured_dashboard():
    """설정된 퀴즈 채널에 대시보드가 있도록 시작 시 한 번 보장한다."""
    if not config.QUIZ_CHANNEL_ID or getattr(bot, "_dashboard_ready", False):
        return

    channel = bot.get_channel(config.QUIZ_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(config.QUIZ_CHANNEL_ID)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            log.exception(
                "QUIZ_CHANNEL_ID 채널을 불러오지 못해 대시보드를 설치하지 못했습니다. "
                "(channel=%s)",
                config.QUIZ_CHANNEL_ID,
            )
            return

    if not hasattr(channel, "history") or not hasattr(channel, "send"):
        log.error(
            "QUIZ_CHANNEL_ID가 메시지를 보낼 수 없는 채널입니다. (channel=%s)",
            config.QUIZ_CHANNEL_ID,
        )
        return

    try:
        dashboard, created = await upsert_dashboard(channel)
    except discord.Forbidden:
        log.exception(
            "퀴즈 채널 권한 부족으로 대시보드를 설치하지 못했습니다. "
            "'채널 보기', '메시지 기록 보기', '메시지 보내기' 권한을 확인하세요. "
            "(channel=%s)",
            config.QUIZ_CHANNEL_ID,
        )
        return
    except discord.HTTPException:
        log.exception(
            "디스코드 요청 오류로 대시보드를 설치하지 못했습니다. (channel=%s)",
            config.QUIZ_CHANNEL_ID,
        )
        return

    bot._dashboard_ready = True
    action = "자동 설치" if created else "자동 갱신"
    log.info("퀴즈 대시보드 %s 완료: %s", action, dashboard.jump_url)


async def ensure_supervisor_dashboard():
    """설정된 관리자 로그 채널에 감독 대시보드가 있도록 보장한다."""
    if not config.ADMIN_LOG_CHANNEL_ID or getattr(
        bot, "_supervisor_dashboard_ready", False
    ):
        return

    channel = bot.get_channel(config.ADMIN_LOG_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(config.ADMIN_LOG_CHANNEL_ID)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            log.exception(
                "ADMIN_LOG_CHANNEL_ID 채널을 불러오지 못해 감독 대시보드를 "
                "설치하지 못했습니다. (channel=%s)",
                config.ADMIN_LOG_CHANNEL_ID,
            )
            return

    if not hasattr(channel, "history") or not hasattr(channel, "send"):
        log.error(
            "ADMIN_LOG_CHANNEL_ID가 메시지를 보낼 수 없는 채널입니다. (channel=%s)",
            config.ADMIN_LOG_CHANNEL_ID,
        )
        return

    try:
        dashboard, created = await upsert_supervisor_dashboard(channel)
    except discord.Forbidden:
        log.exception(
            "감독 채널 권한 부족으로 대시보드를 설치하지 못했습니다. "
            "'채널 보기', '메시지 기록 보기', '메시지 보내기' 권한을 확인하세요. "
            "(channel=%s)",
            config.ADMIN_LOG_CHANNEL_ID,
        )
        return
    except discord.HTTPException:
        log.exception(
            "디스코드 요청 오류로 감독 대시보드를 설치하지 못했습니다. (channel=%s)",
            config.ADMIN_LOG_CHANNEL_ID,
        )
        return

    bot._supervisor_dashboard_ready = True
    action = "자동 설치" if created else "자동 갱신"
    log.info("감독 대시보드 %s 완료: %s", action, dashboard.jump_url)


async def refresh_configured_dashboards(
    guild: discord.Guild,
    emojis: list[discord.Emoji],
) -> tuple[list[str], list[str]]:
    """아이콘 등록 후 같은 서버의 설정된 대시보드 메시지를 즉시 갱신한다."""
    refreshed = []
    failed = []
    targets = (
        ("퀴즈", config.QUIZ_CHANNEL_ID, upsert_dashboard),
        ("감독", config.ADMIN_LOG_CHANNEL_ID, upsert_supervisor_dashboard),
    )
    for label, channel_id, updater in targets:
        if not channel_id:
            continue
        channel = bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                log.exception("%s 대시보드 아이콘 갱신용 채널 조회 실패", label)
                failed.append(label)
                continue
        if getattr(getattr(channel, "guild", None), "id", None) != guild.id:
            continue
        try:
            await updater(channel, emojis=emojis)
        except (discord.Forbidden, discord.HTTPException):
            log.exception("%s 대시보드 아이콘 적용 실패", label)
            failed.append(label)
        else:
            refreshed.append(label)
    return refreshed, failed


@bot.tree.command(
    name="대시보드아이콘설치",
    description="[관리자 전용] 타르코프 테마 대시보드 아이콘을 서버에 등록합니다",
)
@discord.app_commands.default_permissions(administrator=True)
@discord.app_commands.guild_only()
async def install_dashboard_icons_cmd(interaction: discord.Interaction):
    guild = interaction.guild
    if not (
        guild
        and isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    ):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "이 명령어는 서버 관리자만 사용할 수 있어요.",
            ),
            ephemeral=True,
        )
        return

    bot_member = guild.me
    bot_permissions = bot_member.guild_permissions if bot_member else None
    if not (
        bot_permissions
        and (bot_permissions.create_expressions or bot_permissions.manage_expressions)
    ):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "아이콘을 등록하려면 봇 역할에 **표현물 만들기** 또는 "
                "**이모지 및 스티커 관리** 권한이 필요합니다.",
            ),
            ephemeral=True,
        )
        return

    asset_errors = validate_quiz_icon_assets()
    if asset_errors:
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "아이콘 파일 검증에 실패해 설치를 중단했습니다: "
                + ", ".join(asset_errors),
            ),
            ephemeral=True,
        )
        return

    emojis = list(guild.emojis)
    missing_names = missing_quiz_emoji_names(emojis)
    available_slots = available_static_emoji_slots(guild)
    if len(missing_names) > available_slots:
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                f"퀴즈 아이콘은 **{len(missing_names)}개**가 더 필요하지만 일반 이모지 "
                f"슬롯은 **{available_slots}개**만 남아 있어요. 서버 이모지 슬롯을 "
                "확보한 뒤 다시 실행해주세요.",
            ),
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)
    by_name = {emoji.name: emoji for emoji in emojis}
    created = []
    reused = []
    failed = []

    for emoji_name, filename in QUIZ_EMOJI_ASSETS.items():
        if emoji_name in by_name:
            reused.append(emoji_name)
            continue

        image = (QUIZ_ICON_DIR / filename).read_bytes()
        if len(image) > 256 * 1024:
            failed.append(f"{emoji_name}(256KB 초과)")
            continue
        try:
            emoji = await guild.create_custom_emoji(
                name=emoji_name,
                image=image,
                reason=f"{interaction.user}님의 퀴즈 대시보드 아이콘 설치",
            )
        except discord.Forbidden:
            failed.append(f"{emoji_name}(권한 부족)")
            break
        except discord.HTTPException as error:
            log.exception("대시보드 커스텀 이모지 등록 실패: %s", emoji_name)
            failed.append(f"{emoji_name}(HTTP {error.status})")
            continue

        created.append(emoji_name)
        emojis.append(emoji)
        by_name[emoji_name] = emoji

    refreshed, refresh_failed = await refresh_configured_dashboards(guild, emojis)
    success_icon = str(by_name.get("tq_correct") or "✅")
    lines = [
        f"{success_icon} 신규 등록 **{len(created)}개** · "
        f"기존 재사용 **{len(reused)}개**"
    ]
    if refreshed:
        lines.append(f"대시보드 갱신: **{' · '.join(refreshed)}**")
    if failed:
        lines.append("등록 실패: " + ", ".join(failed))
    if refresh_failed:
        lines.append("대시보드 갱신 실패: " + ", ".join(refresh_failed))
    if not refreshed and not refresh_failed:
        lines.append(
            "설정된 대시보드 채널이 없어 아이콘만 등록했습니다. "
            "각 채널에서 설치 명령을 실행하면 적용됩니다."
        )
    lines.append("같은 이름의 서버 이모지는 삭제하거나 덮어쓰지 않습니다.")
    await interaction.followup.send("\n".join(lines), ephemeral=True)


@bot.tree.command(
    name="퀴즈대시보드설치",
    description="[관리자 전용] 현재 채널에 퀴즈 대시보드를 설치하거나 갱신합니다",
)
@discord.app_commands.default_permissions(administrator=True)
@discord.app_commands.guild_only()
async def install_dashboard_cmd(interaction: discord.Interaction):
    if not (
        interaction.guild
        and isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    ):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "이 명령어는 서버 관리자만 사용할 수 있어요.",
            ),
            ephemeral=True,
        )
        return

    channel = interaction.channel
    if channel is None or not hasattr(channel, "history") or not hasattr(channel, "send"):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "이 채널에는 대시보드를 설치할 수 없어요.",
            ),
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)
    try:
        dashboard, created = await upsert_dashboard(channel)
        if created:
            result = "대시보드를 이 채널에 설치했습니다."
        else:
            result = "기존 대시보드를 최신 내용으로 갱신했습니다."
    except discord.Forbidden:
        await interaction.followup.send(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "대시보드를 설치하려면 이 채널의 **메시지 기록 보기**와 "
                "**메시지 보내기** 권한이 필요합니다.",
            ),
            ephemeral=True,
        )
        return
    except discord.HTTPException:
        log.exception("퀴즈 대시보드 설치/갱신 실패 (channel=%s)", interaction.channel_id)
        await interaction.followup.send(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "디스코드 요청 오류로 대시보드를 설치하지 못했습니다. "
                "잠시 후 다시 시도해주세요.",
            ),
            ephemeral=True,
        )
        return

    await interaction.followup.send(
        f"{quiz_icon_text(interaction.guild_id, 'tq_correct', '✅')} {result} "
        f"필요하면 [메시지로 이동]({dashboard.jump_url})해 고정해주세요.",
        ephemeral=True,
    )


@bot.tree.command(
    name="감독대시보드설치",
    description="[관리자 전용] 현재 채널에 감독 대시보드를 설치하거나 갱신합니다",
)
@discord.app_commands.default_permissions(administrator=True)
@discord.app_commands.guild_only()
async def install_supervisor_dashboard_cmd(interaction: discord.Interaction):
    if not (
        interaction.guild
        and isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    ):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "이 명령어는 서버 관리자만 사용할 수 있어요.",
            ),
            ephemeral=True,
        )
        return

    channel = interaction.channel
    if channel is None or not hasattr(channel, "history") or not hasattr(channel, "send"):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "이 채널에는 감독 대시보드를 설치할 수 없어요.",
            ),
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)
    try:
        dashboard, created = await upsert_supervisor_dashboard(channel)
        result = (
            "감독 대시보드를 이 채널에 설치했습니다."
            if created
            else "기존 감독 대시보드를 최신 내용으로 갱신했습니다."
        )
    except discord.Forbidden:
        await interaction.followup.send(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "감독 대시보드를 설치하려면 이 채널의 **메시지 기록 보기**와 "
                "**메시지 보내기** 권한이 필요합니다.",
            ),
            ephemeral=True,
        )
        return
    except discord.HTTPException:
        log.exception("감독 대시보드 설치/갱신 실패 (channel=%s)", interaction.channel_id)
        await interaction.followup.send(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "디스코드 요청 오류로 감독 대시보드를 설치하지 못했습니다.",
            ),
            ephemeral=True,
        )
        return

    await interaction.followup.send(
        f"{quiz_icon_text(interaction.guild_id, 'tq_correct', '✅')} {result} "
        f"[메시지로 이동]({dashboard.jump_url})",
        ephemeral=True,
    )


def format_reward_candidates(items: list[dict], kind: str) -> str:
    if not items:
        return "조건을 충족한 참가자가 없습니다."

    lines = []
    for index, item in enumerate(items, start=1):
        mention = f"<@{item['user_id']}>"
        if kind == "attempts":
            detail = f"{item['attempts']}회 · {item['active_days']}일 참여"
        elif kind == "days":
            detail = f"{item['active_days']}일 · {item['attempts']}회 완주"
        elif kind == "underdog":
            detail = (
                f"유효 최저 {item['lowest_sincere_score']}점 · "
                f"평균 {item['average_score']:.0f}점"
            )
        elif kind == "growth":
            detail = (
                f"+{item['improvement']}점 · "
                f"첫 {item['first_score']} → 최고 {item['best_score']}"
            )
        else:
            detail = f"PvP·PvE 완주 · 총 {item['attempts']}회"
        lines.append(f"`{index}.` {mention} — {detail}")
    return "\n".join(lines)


def build_hidden_reward_embed(
    report: dict,
    period_days: int,
    guild_id: int | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        description=(
            f"최근 **{period_days}일** 개별 완주 기록 기준\n"
            f"참가자 **{report['participants']}명** · 완주 **{report['attempts']}회**"
        ),
        color=discord.Color.purple(),
    )
    decorate_embed(
        embed,
        "히든 상품 후보 검토",
        "tq_reward",
        "🎁",
        guild_id=guild_id,
    )
    embed.add_field(
        name=f"{quiz_icon_text(guild_id, 'tq_complete', '🏃')} 최다 완주",
        value=format_reward_candidates(report["most_attempts"], "attempts"),
        inline=False,
    )
    embed.add_field(
        name=f"{quiz_icon_text(guild_id, 'tq_calendar', '📅')} 꾸준한 생존자",
        value=format_reward_candidates(report["most_days"], "days"),
        inline=False,
    )
    embed.add_field(
        name=f"{quiz_icon_text(guild_id, 'tq_participation', '📈')} 성장상",
        value=format_reward_candidates(report["growth"], "growth"),
        inline=False,
    )
    embed.add_field(
        name=f"{quiz_icon_text(guild_id, 'tq_underdog', '🩹')} 언더독 검토",
        value=format_reward_candidates(report["underdogs"], "underdog"),
        inline=False,
    )
    embed.add_field(
        name=f"{quiz_icon_text(guild_id, 'tq_pvp_start', '⚔️')} 올라운더",
        value=format_reward_candidates(report["dual_mode"], "dual"),
        inline=False,
    )
    embed.set_footer(
        text=(
            "세부 후보는 이 기능 배포 후 완주 기록부터 계산됩니다. "
            "언더독은 1문제 이상 정답·시간 초과 절반 이하만 포함합니다."
        )
    )
    return embed


async def show_hidden_reward_candidates(
    interaction: discord.Interaction,
    period_days: int,
    *,
    ephemeral: bool = False,
):
    await interaction.response.defer(ephemeral=ephemeral)
    since = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()
    report = await asyncio.to_thread(
        database.get_hidden_reward_candidates,
        interaction.guild_id,
        since,
        5,
    )
    await interaction.edit_original_response(
        embed=build_hidden_reward_embed(report, period_days, interaction.guild_id)
    )


@bot.tree.command(
    name="히든상품후보",
    description="[관리자 전용] 최근 퀴즈 기록에서 히든 상품 후보를 확인합니다",
)
@discord.app_commands.describe(기간일="집계할 최근 기간(기본 30일, 최대 365일)")
@discord.app_commands.default_permissions(administrator=True)
@discord.app_commands.guild_only()
async def hidden_reward_candidates_cmd(
    interaction: discord.Interaction,
    기간일: discord.app_commands.Range[int, 1, 365] = 30,
):
    if not (
        interaction.guild
        and isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    ):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "이 명령어는 서버 관리자만 사용할 수 있어요.",
            ),
            ephemeral=True,
        )
        return

    if (
        config.ADMIN_LOG_CHANNEL_ID
        and interaction.channel_id != config.ADMIN_LOG_CHANNEL_ID
    ):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_notice_quiz",
                "🎯",
                f"히든 상품 후보는 관리자 검토 채널 "
                f"<#{config.ADMIN_LOG_CHANNEL_ID}>에서 확인해주세요.",
            ),
            ephemeral=True,
        )
        return

    await show_hidden_reward_candidates(interaction, 기간일)


def format_leaderboard_line(
    prefix: str,
    username: str,
    best_score: int,
    attempts: int,
    total_correct: int,
    total_questions: int,
) -> str:
    """최고 점수와 전체 도전 누적 통계를 혼동하지 않도록 랭킹 한 줄을 만든다."""
    return (
        f"{prefix} **{username}** — 최고 {best_score}점 "
        f"(누적 정답 {total_correct}/{total_questions}, {attempts}회 도전)"
    )


class ResetConfirmView(discord.ui.View):
    """랭킹 초기화는 되돌릴 수 없으므로 확인 버튼을 한 번 거친다."""

    def __init__(self, guild_id: int, invoker_id: int):
        super().__init__(timeout=30)
        self.guild_id = guild_id
        self.invoker_id = invoker_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.invoker_id

    @discord.ui.button(label="초기화 실행", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.defer()
        deleted = await asyncio.to_thread(database.reset_leaderboard, self.guild_id)
        log.info(f"랭킹 초기화: {interaction.user} (기록 {deleted}건 삭제)")
        await interaction.edit_original_response(
            content=(
                f"{quiz_icon_text(self.guild_id, 'tq_reset', '🗑️')} "
                f"랭킹이 초기화되었습니다. (응시 기록 {deleted}건 삭제)"
            ),
            view=None,
        )

    @discord.ui.button(label="취소", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(
            content=quiz_alert_text(
                self.guild_id,
                "tq_exit",
                "🚪",
                "초기화를 취소했어요.",
            ),
            view=None,
        )


@bot.tree.command(
    name="타르코프퀴즈랭킹초기화",
    description="[관리자 전용] 퀴즈 랭킹과 전체 응시 기록을 삭제합니다",
)
@discord.app_commands.default_permissions(administrator=True)
@discord.app_commands.guild_only()
async def reset_leaderboard_cmd(interaction: discord.Interaction):
    # default_permissions는 서버 설정에서 바뀔 수 있으므로 런타임에서 한 번 더 확인
    if not (
        interaction.guild
        and isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    ):
        await interaction.response.send_message(
            quiz_alert_text(
                interaction.guild_id,
                "tq_warning",
                "⚠️",
                "이 명령어는 서버 관리자만 사용할 수 있어요.",
            ),
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"{quiz_icon_text(interaction.guild_id, 'tq_warning', '⚠️')} "
        "**전체 응시 기록과 랭킹이 삭제됩니다.** 되돌릴 수 없어요. 진행할까요?",
        view=ResetConfirmView(interaction.guild_id, interaction.user.id),
        ephemeral=True,
    )


async def show_my_record(interaction: discord.Interaction, mode: str):
    await interaction.response.defer(ephemeral=True)
    row = await asyncio.to_thread(
        database.get_user_record, interaction.guild_id, mode, interaction.user.id
    )
    if not row:
        await interaction.edit_original_response(
            content=quiz_alert_text(
                interaction.guild_id,
                "tq_notice_quiz",
                "🎯",
                "아직 퀴즈 기록이 없어요!",
            )
        )
        return
    username, best_score, last_score, attempts, correct, total = row
    embed = discord.Embed(
        color=discord.Color.blue(),
    )
    decorate_embed(
        embed,
        f"{username}님의 {MODE_LABELS[mode]} 기록",
        f"tq_{mode}_record",
        "📊",
        guild_id=interaction.guild_id,
    )
    embed.add_field(name="최고 점수", value=str(best_score))
    embed.add_field(name="최근 점수", value=str(last_score))
    embed.add_field(name="도전 횟수", value=str(attempts))
    embed.add_field(name="누적 정답", value=f"{correct}/{total}")
    await interaction.edit_original_response(embed=embed)


@bot.tree.command(name="pvp퀴즈기록", description="내 PvP 퀴즈 기록을 확인합니다")
@discord.app_commands.guild_only()
async def pvp_record_cmd(interaction: discord.Interaction):
    await show_my_record(interaction, "pvp")


@bot.tree.command(name="pve퀴즈기록", description="내 PvE 퀴즈 기록을 확인합니다")
@discord.app_commands.guild_only()
async def pve_record_cmd(interaction: discord.Interaction):
    await show_my_record(interaction, "pve")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: discord.app_commands.AppCommandError,
):
    """처리되지 않은 슬래시 명령/대시보드 오류를 기록하고 사용자에게 응답한다."""
    await report_interaction_error(
        interaction,
        error,
        context=f"command:{getattr(interaction.command, 'qualified_name', 'unknown')}",
    )


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
    bot.run(config.DISCORD_TOKEN)

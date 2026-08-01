import asyncio
import logging
from datetime import datetime, timedelta, timezone

import discord

import admin_log
import config
import dashboard_icon_installer
import dashboard_installation
import database
import interaction_access
import quiz_completion
import quiz_icons
import quiz_lifecycle
import quiz_presenters
import quiz_scoring
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
from quiz_icons import apply_dashboard_emojis
from quiz_reports import (
    build_hidden_reward_embed,
    build_leaderboard_embed,
    build_public_stats_embed,
    build_user_record_embed,
)
from quiz_session import (
    QuizSession,
    count_active_sessions,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tarkov_quiz")

intents = discord.Intents.default()


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

# 기존 외부 참조와 테스트 호환을 유지하는 quiz_icons 재노출 이름.
QUIZ_EMOJI_ASSETS = quiz_icons.QUIZ_EMOJI_ASSETS
QUIZ_ICON_DIR = quiz_icons.QUIZ_ICON_DIR
# 기존 외부 참조와 테스트 호환을 유지하는 활성 세션 레지스트리 재노출 이름.
active_sessions = quiz_lifecycle.active_sessions
available_static_emoji_slots = quiz_icons.available_static_emoji_slots
missing_quiz_emoji_names = quiz_icons.missing_quiz_emoji_names
validate_quiz_icon_assets = quiz_icons.validate_quiz_icon_assets


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
    await interaction_access.report_interaction_error(
        interaction,
        error,
        context=context,
        quiz_icon_text=quiz_icon_text,
        logger=log,
    )


async def require_guild_admin(
    interaction: discord.Interaction,
    denied_message: str = interaction_access.ADMIN_COMMAND_MESSAGE,
) -> bool:
    return await interaction_access.require_guild_admin(
        interaction,
        quiz_alert_text=quiz_alert_text,
        denied_message=denied_message,
    )


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
        if not await require_guild_admin(
            interaction,
            "감독 대시보드는 서버 관리자만 사용할 수 있어요.",
        ):
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
    return quiz_presenters.build_question_embed(
        session,
        mode_labels=MODE_LABELS,
        find_quiz_emoji=find_quiz_emoji,
    )


def build_result_text(timed_out: bool, guild_id: int | None = None) -> str:
    return quiz_presenters.build_result_text(
        timed_out,
        guild_id,
        quiz_icon_text=quiz_icon_text,
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

    async def _abort_after_processing_error(self, reason: str) -> None:
        aborted = await quiz_lifecycle.abort_quiz_session(
            self.session,
            finalize_admin_log=finalize_admin_log,
            reason=reason,
            logger=log,
        )
        if not aborted or self.session.message is None:
            return
        try:
            await self.session.message.edit(
                content=(
                    f"{quiz_icon_text(self.session.guild_id, 'tq_warning', '⚠️')} "
                    "퀴즈 처리 오류로 세션을 종료했어요. 다시 시작해주세요."
                ),
                embed=None,
                view=None,
            )
        except discord.HTTPException as error:
            log.warning(
                "오류 종료된 퀴즈 화면 정리 실패 (guild=%s, user=%s): %s",
                self.session.guild_id,
                self.session.user_id,
                error,
            )

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item,
    ):
        self.stop()
        await self._abort_after_processing_error("답변 처리 오류")
        await report_interaction_error(
            interaction,
            error,
            context=f"answer:{getattr(item, 'custom_id', 'unknown')}",
        )

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

            scored = quiz_scoring.score_answer(session, display_index)
            result_text = build_result_text(timed_out=False, guild_id=session.guild_id)

            await update_admin_log(
                session,
                scored.question,
                scored.is_correct,
                timed_out=False,
                chosen_text=scored.chosen_text,
            )
            await advance_or_finish(interaction, session, result_text)

    async def on_timeout(self):
        session = self.session
        try:
            async with session.transition_lock:
                # 이미 답변 처리됐거나 다음 문제로 넘어간 경우 아무것도 하지 않음
                if not session.is_active() or session.index != self.question_index:
                    return

                scored = quiz_scoring.score_timeout(session)
                result_text = build_result_text(timed_out=True, guild_id=session.guild_id)

                await update_admin_log(
                    session,
                    scored.question,
                    scored.is_correct,
                    timed_out=scored.timed_out,
                )
                await advance_or_finish(None, session, result_text)
        except Exception:
            log.exception(
                "퀴즈 시간 초과 처리 실패 (guild=%s, user=%s)",
                session.guild_id,
                session.user_id,
            )
            await self._abort_after_processing_error("시간 초과 처리 오류")


async def edit_session_message(session: QuizSession, interaction, **kwargs) -> bool:
    return await quiz_completion.edit_session_message(
        session,
        interaction,
        finalize_admin_log=finalize_admin_log,
        logger=log,
        **kwargs,
    )


async def advance_or_finish(interaction, session: QuizSession, result_text: str):
    await quiz_completion.advance_or_finish(
        interaction,
        session,
        result_text,
        build_final_embed=build_final_embed,
        build_question_embed=build_question_embed,
        answer_view_factory=AnswerView,
        finalize_admin_log=finalize_admin_log,
        quiz_icon_text=quiz_icon_text,
        logger=log,
    )


def build_final_embed(session: QuizSession) -> discord.Embed:
    return quiz_presenters.build_final_embed(
        session,
        mode_labels=MODE_LABELS,
        decorate_embed=decorate_embed,
    )


# ---------------------------------------------------------------------------
# 관리자 관전 로그
# 세션당 메시지 1개를 생성 후 계속 edit하는 방식.
# (문제마다 새 메시지를 보내면 응시자 1명당 30개 메시지가 쌓여
#  동시 응시 시 채널 도배 + 디스코드 레이트리밋 문제가 발생하기 때문)
# ---------------------------------------------------------------------------


async def start_admin_log(client: discord.Client, session: QuizSession):
    await admin_log.start_admin_log(
        client,
        session,
        mode_labels=MODE_LABELS,
        decorate_embed=decorate_embed,
        quiz_icon_text=quiz_icon_text,
        logger=log,
    )


async def update_admin_log(
    session: QuizSession,
    q: dict,
    is_correct: bool,
    timed_out: bool,
    chosen_text: str | None = None,
):
    await admin_log.update_admin_log(
        session,
        q,
        is_correct,
        timed_out,
        chosen_text,
        mode_labels=MODE_LABELS,
        decorate_embed=decorate_embed,
        quiz_icon_text=quiz_icon_text,
        logger=log,
    )


async def finalize_admin_log(session: QuizSession, aborted: bool, reason: str = ""):
    await admin_log.finalize_admin_log(
        session,
        aborted,
        reason,
        mode_labels=MODE_LABELS,
        decorate_embed=decorate_embed,
        quiz_icon_text=quiz_icon_text,
        logger=log,
    )


# ---------------------------------------------------------------------------
# 슬래시 명령어
# ---------------------------------------------------------------------------


@bot.event
async def on_ready():
    log.info(f"{bot.user}로 로그인 완료")
    await ensure_configured_dashboard()
    await ensure_supervisor_dashboard()


async def start_quiz(interaction: discord.Interaction, mode: str):
    await quiz_lifecycle.start_quiz(
        interaction,
        mode,
        quiz_channel_id=config.QUIZ_CHANNEL_ID,
        max_active_sessions=config.MAX_ACTIVE_SESSIONS_PER_GUILD,
        build_questions=build_session_questions,
        build_question_embed=build_question_embed,
        answer_view_factory=AnswerView,
        start_admin_log=start_admin_log,
        quiz_alert_text=quiz_alert_text,
        logger=log,
    )


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
    await quiz_lifecycle.give_up_quiz(
        interaction,
        finalize_admin_log=finalize_admin_log,
        quiz_alert_text=quiz_alert_text,
        quiz_icon_text=quiz_icon_text,
        logger=log,
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

    embed = build_leaderboard_embed(
        rows, mode, MODE_LABELS[mode], interaction.guild_id, decorate_embed
    )
    await interaction.edit_original_response(embed=embed)


@bot.tree.command(name="pvp퀴즈랭킹", description="PvP 퀴즈 서버 랭킹을 확인합니다")
@discord.app_commands.guild_only()
async def pvp_leaderboard_cmd(interaction: discord.Interaction):
    await show_leaderboard(interaction, "pvp")


@bot.tree.command(name="pve퀴즈랭킹", description="PvE 퀴즈 서버 랭킹을 확인합니다")
@discord.app_commands.guild_only()
async def pve_leaderboard_cmd(interaction: discord.Interaction):
    await show_leaderboard(interaction, "pve")


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
        embed=build_public_stats_embed(
            stats, interaction.guild_id, MODE_LABELS, decorate_embed
        )
    )


def _dashboard_scope(channel) -> tuple[int, int] | None:
    guild_id = getattr(getattr(channel, "guild", None), "id", None)
    channel_id = getattr(channel, "id", None)
    if not isinstance(guild_id, int) or not isinstance(channel_id, int):
        return None
    return guild_id, channel_id


async def _load_dashboard_message_id(channel, kind: str) -> int | None:
    scope = _dashboard_scope(channel)
    if scope is None:
        return None
    guild_id, channel_id = scope
    try:
        stored = await asyncio.to_thread(database.get_dashboard_message, guild_id, kind)
    except Exception:
        log.exception("저장된 %s 대시보드 위치 조회 실패 (guild=%s)", kind, guild_id)
        return None
    if stored is None or stored[0] != channel_id:
        return None
    return stored[1]


async def _save_dashboard_message(channel, dashboard, kind: str) -> None:
    scope = _dashboard_scope(channel)
    message_id = getattr(dashboard, "id", None)
    if scope is None or not isinstance(message_id, int):
        return
    guild_id, channel_id = scope
    try:
        await asyncio.to_thread(
            database.save_dashboard_message,
            guild_id,
            kind,
            channel_id,
            message_id,
        )
    except Exception:
        # 레지스트리는 중복 방지용 보조 정보다. 저장 실패로 대시보드 자체를 막지 않는다.
        log.exception("%s 대시보드 위치 저장 실패 (guild=%s)", kind, guild_id)


async def upsert_dashboard(
    channel,
    *,
    emojis: list[discord.Emoji] | None = None,
) -> tuple[discord.Message, bool]:
    """채널의 대시보드를 만들거나 최신 내용으로 갱신한다.

    반환값의 bool은 새 메시지를 만들었으면 True다.
    """
    preferred_message_id = await _load_dashboard_message_id(channel, "quiz")
    dashboard = await find_dashboard_message(
        channel,
        bot.user,
        DASHBOARD_MARKER,
        preferred_message_id,
    )
    resolved_emojis = channel_dashboard_emojis(channel) if emojis is None else emojis
    view = QuizDashboardView(resolved_emojis)
    embed = build_dashboard_embed(resolved_emojis)
    if dashboard is None:
        dashboard = await channel.send(embed=embed, view=view)
        await ensure_dashboard_pinned(dashboard, "퀴즈", log)
        await _save_dashboard_message(channel, dashboard, "quiz")
        return dashboard, True

    await dashboard.edit(embed=embed, view=view)
    await ensure_dashboard_pinned(dashboard, "퀴즈", log)
    await _save_dashboard_message(channel, dashboard, "quiz")
    return dashboard, False


async def upsert_supervisor_dashboard(
    channel,
    *,
    emojis: list[discord.Emoji] | None = None,
) -> tuple[discord.Message, bool]:
    """감독 채널의 관리자 대시보드를 만들거나 갱신한다."""
    preferred_message_id = await _load_dashboard_message_id(channel, "supervisor")
    dashboard = await find_dashboard_message(
        channel,
        bot.user,
        SUPERVISOR_DASHBOARD_MARKER,
        preferred_message_id,
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
        await _save_dashboard_message(channel, dashboard, "supervisor")
        return dashboard, True

    await dashboard.edit(embed=embed, view=view)
    await ensure_dashboard_pinned(dashboard, "감독", log)
    await _save_dashboard_message(channel, dashboard, "supervisor")
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
    return await dashboard_icon_installer.refresh_configured_dashboards(
        bot,
        guild,
        emojis,
        upsert_dashboard=upsert_dashboard,
        upsert_supervisor_dashboard=upsert_supervisor_dashboard,
        logger=log,
    )


@bot.tree.command(
    name="대시보드아이콘설치",
    description="[관리자 전용] 타르코프 테마 대시보드 아이콘을 서버에 등록합니다",
)
@discord.app_commands.default_permissions(administrator=True)
@discord.app_commands.guild_only()
async def install_dashboard_icons_cmd(interaction: discord.Interaction):
    if not await require_guild_admin(interaction):
        return
    await dashboard_icon_installer.install_dashboard_icons(
        interaction,
        refresh_dashboards=refresh_configured_dashboards,
        quiz_alert_text=quiz_alert_text,
        logger=log,
    )


@bot.tree.command(
    name="퀴즈대시보드설치",
    description="[관리자 전용] 현재 채널에 퀴즈 대시보드를 설치하거나 갱신합니다",
)
@discord.app_commands.default_permissions(administrator=True)
@discord.app_commands.guild_only()
async def install_dashboard_cmd(interaction: discord.Interaction):
    if not await require_guild_admin(interaction):
        return
    await dashboard_installation.install_dashboard_message(
        interaction,
        upsert_dashboard=upsert_dashboard,
        copy=dashboard_installation.QUIZ_DASHBOARD_COPY,
        quiz_alert_text=quiz_alert_text,
        quiz_icon_text=quiz_icon_text,
        logger=log,
    )


@bot.tree.command(
    name="감독대시보드설치",
    description="[관리자 전용] 현재 채널에 감독 대시보드를 설치하거나 갱신합니다",
)
@discord.app_commands.default_permissions(administrator=True)
@discord.app_commands.guild_only()
async def install_supervisor_dashboard_cmd(interaction: discord.Interaction):
    if not await require_guild_admin(interaction):
        return
    await dashboard_installation.install_dashboard_message(
        interaction,
        upsert_dashboard=upsert_supervisor_dashboard,
        copy=dashboard_installation.SUPERVISOR_DASHBOARD_COPY,
        quiz_alert_text=quiz_alert_text,
        quiz_icon_text=quiz_icon_text,
        logger=log,
    )


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
        embed=build_hidden_reward_embed(
            report,
            period_days,
            interaction.guild_id,
            decorate_embed,
            quiz_icon_text,
        )
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
    if not await require_guild_admin(interaction):
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
    if not await require_guild_admin(interaction):
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
    embed = build_user_record_embed(
        row, mode, MODE_LABELS[mode], interaction.guild_id, decorate_embed
    )
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


def run_bot() -> None:
    if not config.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
    # logging.basicConfig가 이미 루트 핸들러를 구성했으므로 discord.py의 기본 핸들러를
    # 추가하지 않는다. 둘을 함께 쓰면 discord 로그가 두 번 출력될 수 있다.
    bot.run(config.DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    run_bot()

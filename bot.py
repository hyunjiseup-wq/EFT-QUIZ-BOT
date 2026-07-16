import asyncio
import random
import logging
from dataclasses import dataclass, field

import discord
from discord.ext import commands

import config
import database
from question_bank import (
    group_by_difficulty,
    load_validated_questions,
    select_session_questions,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tarkov_quiz")

intents = discord.Intents.default()


class QuizBot(commands.Bot):
    async def setup_hook(self):
        # on_ready는 재연결 시마다 반복 호출될 수 있으므로, 명령어 동기화는 setup_hook에서 1회만 수행
        database.init_db()
        synced = await self.tree.sync()
        log.info(f"슬래시 명령어 {len(synced)}개 동기화 완료")


bot = QuizBot(command_prefix="!", intents=intents)

ALL_QUESTIONS = load_validated_questions(
    config.QUESTIONS_PATH, config.SESSION_COUNTS
)

# 난이도별로 문제를 미리 그룹화 (매 세션마다 이 풀에서 랜덤 추출)
QUESTIONS_BY_DIFFICULTY = group_by_difficulty(ALL_QUESTIONS)


def build_session_questions() -> list:
    """난이도별로 config.SESSION_COUNTS 개수만큼 문제 풀에서 랜덤 추출 후, 전체 순서를 섞어 반환."""
    return select_session_questions(
        QUESTIONS_BY_DIFFICULTY, config.SESSION_COUNTS
    )


# user_id -> QuizSession
active_sessions: dict[int, "QuizSession"] = {}


@dataclass
class QuizSession:
    user_id: int
    username: str
    channel_id: int
    questions: list = field(default_factory=list)
    index: int = 0
    score: int = 0
    correct_count: int = 0
    per_difficulty: dict = field(
        default_factory=lambda: {d: [0, 0] for d in config.SESSION_COUNTS}
    )
    message: discord.InteractionMessage = None  # 응시자용 ephemeral 원본 메시지 (edit용)
    current_shuffled_choices: list = None  # 보기 표시 순서 (원본 인덱스 배열)
    finished: bool = False
    # 관리자 관전 로그: 세션당 메시지 1개를 계속 수정(edit)하여 채널 도배/레이트리밋 방지
    admin_log_message: discord.Message = None
    admin_log_lines: list = field(default_factory=list)
    # 버튼 응답과 제한시간 만료가 동시에 도착해도 한 문제를 한 번만 처리한다.
    transition_lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    @property
    def total(self):
        return len(self.questions)

    @property
    def current_question(self):
        return self.questions[self.index]

    def is_active(self) -> bool:
        """세션이 아직 유효하고 진행 중인지 (이중 진행 방지용 가드)"""
        return (
            not self.finished
            and self.index < self.total
            and active_sessions.get(self.user_id) is self
        )


def cleanup_session(session: QuizSession):
    session.finished = True
    if active_sessions.get(session.user_id) is session:
        active_sessions.pop(session.user_id, None)


def build_question_embed(session: QuizSession) -> discord.Embed:
    q = session.current_question

    # 매번 보기 순서를 섞어서 정답 위치 암기를 방지
    order = list(range(len(q["choices"])))
    random.shuffle(order)
    session.current_shuffled_choices = order

    # 난이도/배점은 응시자에게 비공개 (관리자 관전 로그에서만 표시)
    embed = discord.Embed(
        title=f"문제 {session.index + 1} / {session.total}",
        description=q["question"],
        color=discord.Color.dark_gold(),
    )
    labels = ["🇦", "🇧", "🇨", "🇩"]
    for i, orig_idx in enumerate(order):
        embed.add_field(name=labels[i], value=q["choices"][orig_idx], inline=False)
    # 진행 중 점수를 보여주면 직전 문제의 정오답이 드러나므로 표시하지 않는다
    embed.set_footer(text=f"제한시간 {config.QUESTION_TIME_LIMIT}초")
    return embed


def build_result_text(timed_out: bool) -> str:
    # 응시자에게는 정답/오답 여부와 정답을 공개하지 않는다 (관전 로그에서만 확인 가능).
    if timed_out:
        return "⏰ 시간 초과! 다음 문제로 넘어갑니다."
    return "📨 답변이 제출되었습니다."


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
            await interaction.response.send_message("이 퀴즈는 당신의 세션이 아니에요!", ephemeral=True)
            return False
        return True

    async def handle_answer(self, interaction: discord.Interaction, display_index: int):
        # 답변을 받는 즉시 뷰를 정지시켜 on_timeout이 뒤늦게 실행되어
        # 문제가 이중으로 진행되는 것을 차단
        self.stop()

        session = self.session
        async with session.transition_lock:
            if not session.is_active() or session.index != self.question_index:
                await interaction.response.defer()
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

            result_text = build_result_text(timed_out=False)

            await update_admin_log(
                session, q, is_correct, timed_out=False,
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
            result_text = build_result_text(timed_out=True)

            await update_admin_log(session, q, False, timed_out=True)
            await advance_or_finish(None, session, result_text)


async def edit_session_message(session: QuizSession, interaction, **kwargs) -> bool:
    """응시자 세션 메시지를 수정한다. 실패(토큰 만료 등) 시 False를 반환하고 세션을 정리한다."""
    try:
        if interaction is not None:
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
        await asyncio.to_thread(
            database.record_result,
            session.user_id, session.username, session.score,
            session.correct_count, session.total,
        )
        await finalize_admin_log(session, aborted=False)
        await edit_session_message(session, interaction, content=result_text, embed=embed, view=None)
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
        title="🏁 퀴즈 완료!",
        description=f"**{session.username}**님의 결과입니다.",
        color=discord.Color.green(),
    )
    embed.add_field(name="총점", value=f"{session.score}점", inline=True)
    embed.add_field(name="정답 수", value=f"{session.correct_count} / {session.total}", inline=True)
    embed.set_footer(text="/타르코프퀴즈랭킹 명령어로 서버 랭킹을 확인해보세요.")
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


def build_admin_embed(session: QuizSession, status_line: str, color: discord.Color) -> discord.Embed:
    # 임베드 description 한도(4096자)를 고려해, 넘치면 오래된 기록부터 잘라낸다
    lines = list(session.admin_log_lines)
    description = "\n".join(lines)
    while len(description) > 3900 and len(lines) > 1:
        lines.pop(0)
        description = "(이전 기록 생략)\n" + "\n".join(lines)
    embed = discord.Embed(
        title=f"🎮 {session.username}",
        description=description if lines else "(진행 기록 없음)",
        color=color,
    )
    answered = sum(counts[1] for counts in session.per_difficulty.values())
    embed.add_field(name="상태", value=status_line, inline=True)
    embed.add_field(name="점수", value=f"{session.score}점", inline=True)
    embed.add_field(name="정답", value=f"{session.correct_count}/{answered}", inline=True)
    # 난이도별 현황은 응시자에게는 비공개, 관전 로그에서만 표시
    breakdown = " · ".join(
        f"{config.DIFFICULTY_LABEL[d]} {c}/{t}"
        for d, (c, t) in session.per_difficulty.items() if t
    )
    embed.add_field(name="난이도별", value=breakdown or "-", inline=False)
    return embed


async def start_admin_log(client: discord.Client, session: QuizSession):
    channel = await get_admin_channel(client)
    if channel is None:
        return
    embed = build_admin_embed(session, "🟡 진행 중", discord.Color.blurple())
    try:
        session.admin_log_message = await channel.send(embed=embed)
    except discord.Forbidden:
        log.warning("관리자 로그 채널에 메시지를 보낼 권한이 없습니다.")


async def update_admin_log(
    session: QuizSession, q: dict, is_correct: bool, timed_out: bool,
    chosen_text: str | None = None,
):
    if session.admin_log_message is None:
        return
    mark = "⏰" if timed_out else ("✅" if is_correct else "❌")
    diff_label = config.DIFFICULTY_LABEL[q["difficulty"]]
    session.admin_log_lines.append(
        f"`{session.index + 1:02d}` {mark} [{diff_label}] {q['question'][:40]}"
    )
    # 오답/시간초과 문항은 응시자 문의("왜 오답이냐") 대응을 위해
    # 고른 보기 · 정답 · 해설을 관전 로그에 함께 남긴다 (응시자에게는 비공개)
    if timed_out or not is_correct:
        answer_text = q["choices"][q["answer"]]
        if chosen_text:
            session.admin_log_lines.append(f"　└ 응답: {chosen_text[:40]} → 정답: **{answer_text[:40]}**")
        else:
            session.admin_log_lines.append(f"　└ 정답: **{answer_text[:40]}**")
        explanation = q.get("explanation")
        if explanation:
            session.admin_log_lines.append(f"　└ 💡 {explanation[:150]}")
    embed = build_admin_embed(session, "🟡 진행 중", discord.Color.blurple())
    try:
        await session.admin_log_message.edit(embed=embed)
    except discord.HTTPException as e:
        log.warning(f"관리자 로그 갱신 실패: {e}")
        session.admin_log_message = None  # 이후 갱신 시도 중단


async def finalize_admin_log(session: QuizSession, aborted: bool, reason: str = ""):
    if session.admin_log_message is None:
        return
    if aborted:
        status = f"⚪ 중단됨{f' ({reason})' if reason else ''}"
        color = discord.Color.light_grey()
    else:
        status = "🟢 완료"
        color = discord.Color.green()
    embed = build_admin_embed(session, status, color)
    try:
        await session.admin_log_message.edit(embed=embed)
    except discord.HTTPException:
        pass
    session.admin_log_message = None


# ---------------------------------------------------------------------------
# 슬래시 명령어
# ---------------------------------------------------------------------------

@bot.event
async def on_ready():
    log.info(f"{bot.user}로 로그인 완료")


@bot.tree.command(
    name="타르코프퀴즈시작",
    description=f"이스케이프 프롬 타르코프 지식 퀴즈를 시작합니다 ({config.TOTAL_QUESTIONS}문제, 객관식)",
)
async def start_quiz(interaction: discord.Interaction):
    if config.QUIZ_CHANNEL_ID and interaction.channel_id != config.QUIZ_CHANNEL_ID:
        await interaction.response.send_message(
            f"퀴즈는 <#{config.QUIZ_CHANNEL_ID}> 채널에서만 시작할 수 있어요!",
            ephemeral=True,
        )
        return

    if interaction.user.id in active_sessions:
        await interaction.response.send_message(
            "이미 진행 중인 퀴즈가 있어요! `/타르코프퀴즈포기`로 종료하거나 기존 퀴즈를 끝내주세요.",
            ephemeral=True,
        )
        return

    questions = build_session_questions()

    session = QuizSession(
        user_id=interaction.user.id,
        username=interaction.user.display_name,
        channel_id=interaction.channel_id,
        questions=questions,
    )
    active_sessions[interaction.user.id] = session

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


@bot.tree.command(name="타르코프퀴즈포기", description="진행 중인 퀴즈를 포기합니다 (기록에 저장되지 않음)")
async def give_up_cmd(interaction: discord.Interaction):
    session = active_sessions.get(interaction.user.id)
    if session is None:
        await interaction.response.send_message("진행 중인 퀴즈가 없어요.", ephemeral=True)
        return

    await finalize_admin_log(session, aborted=True, reason="응시자 포기")
    cleanup_session(session)

    # 남아있는 퀴즈 화면의 버튼 제거 시도 (실패해도 무방)
    if session.message:
        try:
            await session.message.edit(content="🚪 퀴즈를 포기했어요.", embed=None, view=None)
        except discord.HTTPException:
            pass

    await interaction.response.send_message(
        "퀴즈를 포기했어요. `/타르코프퀴즈시작`으로 다시 도전할 수 있어요!", ephemeral=True
    )


@bot.tree.command(name="타르코프퀴즈랭킹", description="타르코프 퀴즈 서버 랭킹을 확인합니다")
async def leaderboard_cmd(interaction: discord.Interaction):
    rows = await asyncio.to_thread(database.get_leaderboard, 10)
    if not rows:
        await interaction.response.send_message("아직 기록이 없어요. 먼저 퀴즈에 도전해보세요!", ephemeral=True)
        return

    embed = discord.Embed(title="🏆 타르코프 퀴즈 랭킹 TOP 10", color=discord.Color.gold())
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (username, best_score, attempts, correct, total) in enumerate(rows):
        prefix = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"{prefix} **{username}** — {best_score}점 (정답 {correct}/{total}, {attempts}회 도전)")
    embed.description = "\n".join(lines)
    await interaction.response.send_message(embed=embed)


class ResetConfirmView(discord.ui.View):
    """랭킹 초기화는 되돌릴 수 없으므로 확인 버튼을 한 번 거친다."""

    def __init__(self, invoker_id: int):
        super().__init__(timeout=30)
        self.invoker_id = invoker_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.invoker_id

    @discord.ui.button(label="초기화 실행", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        deleted = await asyncio.to_thread(database.reset_leaderboard)
        log.info(f"랭킹 초기화: {interaction.user} (기록 {deleted}건 삭제)")
        await interaction.response.edit_message(
            content=f"🗑️ 랭킹이 초기화되었습니다. (응시 기록 {deleted}건 삭제)", view=None
        )

    @discord.ui.button(label="취소", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="초기화를 취소했어요.", view=None)


@bot.tree.command(name="타르코프퀴즈랭킹초기화", description="[관리자 전용] 퀴즈 랭킹과 전체 응시 기록을 삭제합니다")
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
            "이 명령어는 서버 관리자만 사용할 수 있어요.", ephemeral=True
        )
        return

    await interaction.response.send_message(
        "⚠️ **전체 응시 기록과 랭킹이 삭제됩니다.** 되돌릴 수 없어요. 진행할까요?",
        view=ResetConfirmView(interaction.user.id),
        ephemeral=True,
    )


@bot.tree.command(name="타르코프퀴즈기록", description="내 타르코프 퀴즈 기록을 확인합니다")
async def my_record_cmd(interaction: discord.Interaction):
    row = await asyncio.to_thread(database.get_user_record, interaction.user.id)
    if not row:
        await interaction.response.send_message("아직 퀴즈 기록이 없어요!", ephemeral=True)
        return
    username, best_score, last_score, attempts, correct, total = row
    embed = discord.Embed(title=f"{username}님의 기록", color=discord.Color.blue())
    embed.add_field(name="최고 점수", value=str(best_score))
    embed.add_field(name="최근 점수", value=str(last_score))
    embed.add_field(name="도전 횟수", value=str(attempts))
    embed.add_field(name="누적 정답", value=f"{correct}/{total}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
    bot.run(config.DISCORD_TOKEN)

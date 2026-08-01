import random
from collections.abc import Callable, Mapping

import discord

import config
from quiz_session import QuizSession

CHOICE_LABELS = ("🇦", "🇧", "🇨", "🇩")


def build_question_embed(
    session: QuizSession,
    *,
    mode_labels: Mapping[str, str],
    find_quiz_emoji: Callable,
) -> discord.Embed:
    question = session.current_question

    # 매번 보기 순서를 섞어서 정답 위치 암기를 방지한다.
    order = list(range(len(question["choices"])))
    random.shuffle(order)
    session.current_shuffled_choices = order

    # 난이도·배점은 응시자에게 비공개이며 관리자 관전 로그에서만 표시한다.
    embed = discord.Embed(
        title=f"{mode_labels[session.mode]} 문제 {session.index + 1} / {session.total}",
        description=question["question"],
        color=discord.Color.dark_gold(),
    )
    emoji = find_quiz_emoji("tq_notice_quiz", guild_id=session.guild_id)
    if emoji:
        embed.set_thumbnail(url=str(emoji.url))
    for label, original_index in zip(CHOICE_LABELS, order, strict=True):
        embed.add_field(
            name=label,
            value=question["choices"][original_index],
            inline=False,
        )
    # 진행 중 점수는 직전 문제의 정오답을 노출할 수 있으므로 표시하지 않는다.
    embed.set_footer(text=f"제한시간 {config.QUESTION_TIME_LIMIT}초")
    return embed


def build_result_text(
    timed_out: bool,
    guild_id: int | None,
    *,
    quiz_icon_text: Callable,
) -> str:
    # 응시자에게 정답 여부와 정답은 공개하지 않고 관전 로그에만 남긴다.
    if timed_out:
        return (
            f"{quiz_icon_text(guild_id, 'tq_timeout', '⏰')} "
            "시간 초과! 다음 문제로 넘어갑니다."
        )
    return (
        f"{quiz_icon_text(guild_id, 'tq_submitted', '📨')} "
        "답변이 제출되었습니다."
    )


def build_final_embed(
    session: QuizSession,
    *,
    mode_labels: Mapping[str, str],
    decorate_embed: Callable,
) -> discord.Embed:
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
    embed.add_field(name="모드", value=mode_labels[session.mode], inline=True)
    embed.add_field(
        name="정답 수",
        value=f"{session.correct_count} / {session.total}",
        inline=True,
    )
    embed.set_footer(
        text=f"/{session.mode}퀴즈랭킹 명령어로 서버 랭킹을 확인해보세요."
    )
    return embed

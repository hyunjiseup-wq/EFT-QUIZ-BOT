import discord


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


def build_leaderboard_embed(
    rows: list[tuple],
    mode: str,
    mode_label: str,
    guild_id: int,
    decorate_embed,
) -> discord.Embed:
    embed = discord.Embed(color=discord.Color.gold())
    decorate_embed(
        embed,
        f"{mode_label} 퀴즈 랭킹 TOP 10",
        f"tq_{mode}_rank",
        "🏆",
        guild_id=guild_id,
    )
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for index, (username, best_score, attempts, correct, total) in enumerate(rows):
        prefix = medals[index] if index < 3 else f"{index + 1}."
        lines.append(
            format_leaderboard_line(
                prefix, username, best_score, attempts, correct, total
            )
        )
    embed.description = "\n".join(lines)
    return embed


def build_public_stats_embed(
    stats: dict,
    guild_id: int | None,
    mode_labels: dict[str, str],
    decorate_embed,
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
            name=mode_labels[mode],
            value=(
                f"참가자 **{mode_stats['participants']}명**\n"
                f"완주 **{mode_stats['attempts']}회**"
            ),
            inline=True,
        )
    embed.set_footer(text="포기한 퀴즈는 참가·완주 통계에 포함되지 않습니다.")
    return embed


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
    guild_id: int | None,
    decorate_embed,
    quiz_icon_text,
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
    fields = (
        ("tq_complete", "🏃", "최다 완주", "most_attempts", "attempts"),
        ("tq_calendar", "📅", "꾸준한 생존자", "most_days", "days"),
        ("tq_participation", "📈", "성장상", "growth", "growth"),
        ("tq_underdog", "🩹", "언더독 검토", "underdogs", "underdog"),
        ("tq_pvp_start", "⚔️", "올라운더", "dual_mode", "dual"),
    )
    for emoji_name, fallback, label, report_key, kind in fields:
        embed.add_field(
            name=f"{quiz_icon_text(guild_id, emoji_name, fallback)} {label}",
            value=format_reward_candidates(report[report_key], kind),
            inline=False,
        )
    embed.set_footer(
        text=(
            "세부 후보는 이 기능 배포 후 완주 기록부터 계산됩니다. "
            "언더독은 1문제 이상 정답·시간 초과 절반 이하만 포함합니다."
        )
    )
    return embed


def build_user_record_embed(
    row: tuple,
    mode: str,
    mode_label: str,
    guild_id: int,
    decorate_embed,
) -> discord.Embed:
    username, best_score, last_score, attempts, correct, total = row
    embed = discord.Embed(color=discord.Color.blue())
    decorate_embed(
        embed,
        f"{username}님의 {mode_label} 기록",
        f"tq_{mode}_record",
        "📊",
        guild_id=guild_id,
    )
    embed.add_field(name="최고 점수", value=str(best_score))
    embed.add_field(name="최근 점수", value=str(last_score))
    embed.add_field(name="도전 횟수", value=str(attempts))
    embed.add_field(name="누적 정답", value=f"{correct}/{total}")
    return embed

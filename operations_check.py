"""관리자용 퀴즈봇 운영 상태 점검 결과 구성."""

from __future__ import annotations

from dataclasses import dataclass

import discord


@dataclass(frozen=True)
class CheckResult:
    level: str
    title: str
    detail: str


LEVEL_ICONS = {"ok": "✅", "warning": "⚠️", "error": "❌"}


def _channel_check(bot, guild, channel_id: int, *, supervisor: bool) -> CheckResult:
    label = "감독 채널" if supervisor else "퀴즈 채널"
    if not channel_id:
        detail = (
            "미설정 — 관전 로그와 감독 대시보드가 비활성화됩니다."
            if supervisor
            else "미설정 — 모든 채널에서 퀴즈 시작이 허용됩니다."
        )
        return CheckResult("warning", label, detail)

    channel = bot.get_channel(channel_id)
    if channel is None or getattr(getattr(channel, "guild", None), "id", None) != guild.id:
        return CheckResult("error", label, f"<#{channel_id}> 채널을 현재 서버에서 찾지 못했습니다.")
    if not hasattr(channel, "permissions_for"):
        return CheckResult("error", label, f"<#{channel_id}>은 메시지 채널이 아닙니다.")

    bot_member = getattr(guild, "me", None)
    if bot_member is None:
        return CheckResult("error", label, "서버의 봇 멤버 정보를 확인하지 못했습니다.")
    permissions = channel.permissions_for(bot_member)
    required = {
        "채널 보기": getattr(permissions, "view_channel", False),
        "메시지 보내기": getattr(permissions, "send_messages", False),
        "메시지 기록 보기": getattr(permissions, "read_message_history", False),
    }
    missing = [name for name, allowed in required.items() if not allowed]
    if missing:
        return CheckResult(
            "error",
            label,
            f"<#{channel_id}> 봇 권한 부족: {', '.join(missing)}",
        )

    if supervisor:
        default_role = getattr(guild, "default_role", None)
        if default_role is not None:
            public_permissions = channel.permissions_for(default_role)
            if getattr(public_permissions, "view_channel", False):
                return CheckResult(
                    "warning",
                    label,
                    f"<#{channel_id}> 접근 가능. 다만 @everyone에게 채널이 보입니다.",
                )
    return CheckResult("ok", label, f"<#{channel_id}> 접근 및 필수 권한 정상")


def _dashboard_check(
    db_status: dict,
    quiz_channel_id: int,
    admin_channel_id: int,
) -> CheckResult:
    expected = {
        "quiz": quiz_channel_id,
        "supervisor": admin_channel_id,
    }
    missing = []
    mismatched = []
    dashboards = db_status["dashboards"]
    configured = 0
    for kind, channel_id in expected.items():
        if not channel_id:
            continue
        configured += 1
        stored = dashboards.get(kind)
        if stored is None:
            missing.append(kind)
        elif stored[0] != channel_id:
            mismatched.append(kind)

    if mismatched:
        return CheckResult(
            "error",
            "대시보드 등록",
            f"설정 채널과 등록 위치가 다름: {', '.join(mismatched)}",
        )
    if missing:
        return CheckResult(
            "warning",
            "대시보드 등록",
            f"DB에 메시지 위치가 없음: {', '.join(missing)} — 재시작 또는 설치 명령 필요",
        )
    if configured == 0:
        return CheckResult("warning", "대시보드 등록", "설정된 대시보드 채널이 없습니다.")
    return CheckResult("ok", "대시보드 등록", f"설정된 {configured}개 위치가 DB와 일치")


def collect_operations_checks(
    *,
    bot,
    guild,
    db_status: dict | None,
    db_error: bool,
    quiz_channel_id: int,
    admin_channel_id: int,
    total_questions: int,
    pvp_pool_size: int,
    pve_pool_size: int,
    active_session_count: int,
    max_active_sessions: int,
    missing_icons: list[str],
    total_icons: int,
) -> list[CheckResult]:
    checks: list[CheckResult] = []
    if db_error or db_status is None:
        checks.append(CheckResult("error", "데이터베이스", "상태 조회 실패 — 봇 로그 확인 필요"))
    else:
        schema_ok = (
            db_status["schema_version"] == db_status["expected_schema_version"]
        )
        integrity_ok = db_status["integrity_ok"]
        level = "ok" if schema_ok and integrity_ok else "error"
        checks.append(
            CheckResult(
                level,
                "데이터베이스",
                (
                    f"스키마 v{db_status['schema_version']}"
                    f"/지원 v{db_status['expected_schema_version']} · "
                    f"무결성 {'정상' if integrity_ok else '오류'} · "
                    f"랭킹 {db_status['leaderboard_rows']:,}행 · "
                    f"상세 응시 {db_status['attempt_rows']:,}행"
                ),
            )
        )

    checks.append(
        CheckResult(
            "ok",
            "문제 풀",
            f"전체 {total_questions:,}문제 · PvP {pvp_pool_size:,} · PvE {pve_pool_size:,}",
        )
    )
    session_level = "warning" if active_session_count >= max_active_sessions * 0.9 else "ok"
    checks.append(
        CheckResult(
            session_level,
            "활성 세션",
            f"{active_session_count:,}/{max_active_sessions:,}개 사용 중",
        )
    )
    checks.append(_channel_check(bot, guild, quiz_channel_id, supervisor=False))
    checks.append(_channel_check(bot, guild, admin_channel_id, supervisor=True))

    if db_error or db_status is None:
        checks.append(CheckResult("error", "대시보드 등록", "DB 조회 실패로 확인할 수 없습니다."))
    else:
        checks.append(_dashboard_check(db_status, quiz_channel_id, admin_channel_id))

    if missing_icons:
        checks.append(
            CheckResult(
                "warning",
                "전용 아이콘",
                f"{len(missing_icons)}개 미설치 — 기본 이모지로 동작합니다.",
            )
        )
    else:
        checks.append(CheckResult("ok", "전용 아이콘", f"{total_icons}개 모두 설치됨"))
    return checks


def build_operations_check_embed(checks: list[CheckResult]) -> discord.Embed:
    errors = sum(check.level == "error" for check in checks)
    warnings = sum(check.level == "warning" for check in checks)
    if errors:
        summary = f"오류 {errors}개 · 경고 {warnings}개 — 이벤트 시작 전 오류를 해결하세요."
        color = discord.Color.red()
    elif warnings:
        summary = f"치명적 오류 없음 · 경고 {warnings}개 — 운영 설정을 확인하세요."
        color = discord.Color.orange()
    else:
        summary = "모든 운영 점검 항목이 정상입니다."
        color = discord.Color.green()

    embed = discord.Embed(description=summary, color=color)
    for check in checks:
        embed.add_field(
            name=f"{LEVEL_ICONS[check.level]} {check.title}",
            value=check.detail,
            inline=False,
        )
    embed.set_footer(text="읽기 전용 점검 · 결과는 명령어 실행자에게만 표시됩니다.")
    return embed

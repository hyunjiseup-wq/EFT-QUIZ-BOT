import hashlib
from pathlib import Path

import discord

QUIZ_ICON_DIR = Path(__file__).resolve().parent / "assets" / "dashboard_icons"
QUIZ_EMOJI_ASSETS = {
    "tq_pvp_start": "pvp_start.png",
    "tq_pve_start": "pve_start.png",
    "tq_tutorial": "tutorial.png",
    "tq_pvp_rank": "pvp_rank.png",
    "tq_pve_rank": "pve_rank.png",
    "tq_pvp_record": "pvp_record.png",
    "tq_pve_record": "pve_record.png",
    "tq_participation": "participation.png",
    "tq_reward": "reward.png",
    "tq_sessions": "sessions.png",
    "tq_notice_quiz": "notice_quiz.png",
    "tq_warning": "warning.png",
    "tq_submitted": "submitted.png",
    "tq_complete": "complete.png",
    "tq_correct": "correct.png",
    "tq_incorrect": "incorrect.png",
    "tq_timeout": "timeout.png",
    "tq_exit": "exit.png",
    "tq_reset": "reset.png",
    "tq_calendar": "calendar.png",
    "tq_underdog": "underdog.png",
}
QUIZ_ICON_SHA256 = {
    "calendar.png": "0481e76efcd408bb24a835333cee5d033c0d6f9db7630ec446925f16b1ee19df",
    "complete.png": "8137edfb30417495b63a920ffd7b7d454204c1caf65215662a77bcefcc092e53",
    "correct.png": "b7e0432c1d490918a82b2cbc259cda962ce742787075874a360c189619e9c568",
    "exit.png": "83107da52b4c4efb51d0774b458d253e2e9a7996b3d7c5db5bd0dc24532d2fab",
    "incorrect.png": "8babcb093764bcf94dce9cb34174a6250d482b6e709c885fa9fbf304206d7dcf",
    "notice_quiz.png": "56ff63b5eda5bd2faebfc82df684c9c1de3f69fa0b183e93c25b77700512856b",
    "participation.png": "4e2c0d6c3607439adbe6ba1326a46300ec86615cd82007f03d77677f6647855d",
    "pve_rank.png": "1a04f51a30b1816a0051376e641d6a7e1870baf2e6bdf4a081efcaa20b9ee822",
    "pve_record.png": "a71da9457ba02d88f9ecab5f7b6d4ab339d135269648f8723b9e3b2e58f615ac",
    "pve_start.png": "33394f11a98d59229fe3a297a4f043bc0f773254009b04d011458d15ca8cd30e",
    "pvp_rank.png": "0a83e8ed4a68e25baf6b09177f967b7b5e696983d4f84fc480a6e7080d13503a",
    "pvp_record.png": "25ed6f294d6814ad7d9db85b714503625e2e68a244cba6f18e69d6d13ac1757a",
    "pvp_start.png": "4e6f4c6e06f46c6cc20c72710ce9e666b360c1e02887eab30ed4fcdac5da0778",
    "reset.png": "5603be87e9b06cc4ffd56bfd36bceff5bd5b08eb5b657040f05660674473123a",
    "reward.png": "20a13c76d830ed7334c7b2a92f31a7c043ecf6364e33c21401c1b6e1650e137e",
    "sessions.png": "7408cead4dc38492b195b76acbda8fabcbf4da3aba197e62e2945e311649508c",
    "submitted.png": "abee2b63966e1e0d115a0757450104498df987587f895c503897af9ac9b9a145",
    "timeout.png": "8c7c2925c4f104f24504f5d2ec4f9e2d1fe789c1c15dbb84ea202cdcfec3467f",
    "tutorial.png": "8fcf2367a58dfc37a2636cae990eb764fe05f2ed7127bfff98835b6caa34e961",
    "underdog.png": "e168e70b28d4ea7abf50ee0731d41cd7f1e5830a43fb6ef5b64d928be1bfbc9f",
    "warning.png": "103803b61dc038fd2f4a4625b7b61e8811b30da90406fc66f46ba73aa4d70fae",
}
DASHBOARD_EMOJI_BY_CUSTOM_ID = {
    "tarkov_quiz:pvp:start": "tq_pvp_start",
    "tarkov_quiz:pve:start": "tq_pve_start",
    "tarkov_quiz:tutorial": "tq_tutorial",
    "tarkov_quiz:pvp:ranking": "tq_pvp_rank",
    "tarkov_quiz:pve:ranking": "tq_pve_rank",
    "tarkov_quiz:pvp:record": "tq_pvp_record",
    "tarkov_quiz:pve:record": "tq_pve_record",
    "tarkov_quiz:supervisor:stats": "tq_participation",
    "tarkov_quiz:supervisor:rewards": "tq_reward",
    "tarkov_quiz:supervisor:sessions": "tq_sessions",
    "tarkov_quiz:supervisor:pvp-ranking": "tq_pvp_rank",
    "tarkov_quiz:supervisor:pve-ranking": "tq_pve_rank",
}


def apply_dashboard_emojis(
    view: discord.ui.View,
    emojis: list[discord.Emoji] | tuple[discord.Emoji, ...] | None,
) -> None:
    """서버에 등록된 전용 이모지가 있으면 버튼의 기본 이모지를 교체한다."""
    if not emojis:
        return

    by_name = {emoji.name: emoji for emoji in emojis}
    for item in view.children:
        emoji_name = DASHBOARD_EMOJI_BY_CUSTOM_ID.get(getattr(item, "custom_id", None))
        if emoji_name and emoji_name in by_name:
            item.emoji = by_name[emoji_name]


def missing_quiz_emoji_names(
    emojis: list[discord.Emoji] | tuple[discord.Emoji, ...],
) -> list[str]:
    """현재 서버에 등록되지 않은 퀴즈 UI 이모지 이름을 선언 순서대로 반환한다."""
    existing_names = {emoji.name for emoji in emojis}
    return [name for name in QUIZ_EMOJI_ASSETS if name not in existing_names]


def available_static_emoji_slots(guild: discord.Guild) -> int:
    """일반 이미지형 커스텀 이모지를 추가할 수 있는 남은 슬롯 수를 계산한다."""
    used = sum(not emoji.animated for emoji in guild.emojis)
    return max(guild.emoji_limit - used, 0)


def validate_quiz_icon_assets(icon_dir: Path = QUIZ_ICON_DIR) -> list[str]:
    """아이콘 파일 목록과 고정 SHA-256 해시가 일치하는지 검사한다."""
    errors = []
    expected_files = set(QUIZ_EMOJI_ASSETS.values())
    if expected_files != set(QUIZ_ICON_SHA256):
        errors.append("아이콘 목록과 SHA-256 manifest 파일 목록이 일치하지 않습니다.")

    for filename in sorted(expected_files):
        path = icon_dir / filename
        if not path.is_file():
            errors.append(f"{filename}: 파일 누락")
            continue
        expected_hash = QUIZ_ICON_SHA256.get(filename)
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected_hash != actual_hash:
            errors.append(f"{filename}: SHA-256 불일치")
    return errors

import os
import re
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _positive_int_env(name: str, default: int) -> int:
    """양의 정수 환경변수를 읽고 잘못된 값이면 안전한 기본값을 사용한다."""
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        print(f"[경고] {name}이 올바른 숫자가 아니어서 기본값 {default}을 사용합니다.")
        return default
    if value <= 0:
        print(f"[경고] {name}은 1 이상이어야 해서 기본값 {default}을 사용합니다.")
        return default
    return value


def _project_path(env_name: str, default_name: str) -> Path:
    """환경변수 경로를 절대경로로 변환한다.

    상대경로가 들어오면 실행 위치가 아니라 프로젝트 루트를 기준으로 해석한다.
    """
    configured = os.getenv(env_name)
    path = Path(configured).expanduser() if configured else BASE_DIR / default_name
    if not path.is_absolute():
        path = BASE_DIR / path
    return path.resolve()


def _channel_ids_env(name: str) -> tuple[int, ...]:
    """Discord 채널 ID 목록을 읽는다.

    서버마다 채널이 다르므로 쉼표(또는 공백)로 구분해 여러 개를 넣을 수 있다.
    0과 빈 값은 미설정이고, 잘못된 항목은 그 항목만 건너뛰어 나머지 설정은 살린다.
    """
    channel_ids: list[int] = []
    for token in re.split(r"[,\s]+", os.getenv(name, "").strip()):
        if not token:
            continue
        try:
            value = int(token)
        except ValueError:
            print(f"[경고] {name}의 '{token}'은 숫자가 아니어서 무시합니다.")
            continue
        if value < 0:
            print(f"[경고] {name}의 '{token}'은 0 이상이어야 해서 무시합니다.")
            continue
        if value and value not in channel_ids:
            channel_ids.append(value)
    return tuple(channel_ids)


# 디스코드 봇 토큰 (.env 파일에서 로드)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

# 관리자 전용 "관전 로그" 채널 ID (서버마다 하나씩, 쉼표로 구분)
# - 응시자에게는 ephemeral(본인만 보임)로 퀴즈가 진행되므로,
#   관리자가 모든 응시자의 진행 상황을 볼 수 있도록 이 채널에 세션당 로그 메시지 1개를 남깁니다.
# - 관전 로그와 감독 대시보드는 세션이 열린 서버에 설정된 채널로 갑니다.
# - 값이 비어있거나 잘못된 경우 관리자 로그 기능만 비활성화되고 봇은 정상 동작합니다.
ADMIN_LOG_CHANNEL_IDS = _channel_ids_env("ADMIN_LOG_CHANNEL_ID")

# 퀴즈 시작을 허용할 채널 ID (서버마다 하나씩, 쉼표로 구분)
# - 여기 적힌 채널에서만 /pvp퀴즈, /pve퀴즈와 이용자 대시보드를 사용할 수 있습니다.
# - 비어 있으면(미설정) 모든 서버의 모든 채널에서 시작할 수 있습니다.
QUIZ_CHANNEL_IDS = _channel_ids_env("QUIZ_CHANNEL_ID")

# 난이도별 배점
POINTS = {
    "general": 10,
    "medium": 20,
    "hard": 40,
    "expert": 70,
}

DIFFICULTY_LABEL = {
    "general": "일반",
    "medium": "중간",
    "hard": "어려움",
    "expert": "고난이도",
}

# 문제당 제한 시간(초)
QUESTION_TIME_LIMIT = 20

# 이벤트 공지 직후 과도한 동시 시작으로 메모리와 Discord API가 포화되는 것을 막는다.
# 전체 서버 인원 제한이 아니라 한 서버에서 동시에 진행 중인 세션 수 제한이다.
MAX_ACTIVE_SESSIONS_PER_GUILD = _positive_int_env("MAX_ACTIVE_SESSIONS_PER_GUILD", 250)

# 관리자 관전 로그는 모든 답변 내용을 메모리에 쌓되, Discord 메시지는 N문제마다 묶어서 갱신한다.
ADMIN_LOG_UPDATE_EVERY = _positive_int_env("ADMIN_LOG_UPDATE_EVERY", 5)

# 한 판(세션)에서 난이도별로 문제 풀에서 랜덤으로 뽑을 문제 수
# questions.json에 각 난이도별로 이 숫자 이상의 문제가 있어야 중복 없이 뽑힙니다.
SESSION_COUNTS = {
    "general": 2,
    "medium": 3,
    "hard": 15,
    "expert": 10,
}

TOTAL_QUESTIONS = sum(SESSION_COUNTS.values())


def validate_settings() -> None:
    """서로 의존하는 퀴즈 설정을 시작 전에 검증한다."""
    difficulties = set(SESSION_COUNTS)
    if set(POINTS) != difficulties or set(DIFFICULTY_LABEL) != difficulties:
        raise ValueError("POINTS, DIFFICULTY_LABEL, SESSION_COUNTS의 난이도 키가 같아야 합니다.")
    if (
        not isinstance(QUESTION_TIME_LIMIT, int)
        or isinstance(QUESTION_TIME_LIMIT, bool)
        or QUESTION_TIME_LIMIT <= 0
    ):
        raise ValueError("QUESTION_TIME_LIMIT은 1 이상의 정수여야 합니다.")
    for difficulty, count in SESSION_COUNTS.items():
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise ValueError(f"SESSION_COUNTS['{difficulty}']는 1 이상의 정수여야 합니다.")
        points = POINTS[difficulty]
        if not isinstance(points, int) or isinstance(points, bool) or points < 0:
            raise ValueError(f"POINTS['{difficulty}']는 0 이상의 정수여야 합니다.")


validate_settings()

# 데이터베이스 파일 경로
DB_PATH = _project_path("QUIZ_DB_PATH", "quiz_leaderboard.db")

# 문제 데이터 경로
QUESTIONS_PATH = _project_path("QUIZ_QUESTIONS_PATH", "questions.json")

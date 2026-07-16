import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _project_path(env_name: str, default_name: str) -> Path:
    """환경변수 경로를 절대경로로 변환한다.

    상대경로가 들어오면 실행 위치가 아니라 프로젝트 루트를 기준으로 해석한다.
    """
    configured = os.getenv(env_name)
    path = Path(configured).expanduser() if configured else BASE_DIR / default_name
    if not path.is_absolute():
        path = BASE_DIR / path
    return path.resolve()

# 디스코드 봇 토큰 (.env 파일에서 로드)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# 관리자 전용 "관전 로그" 채널 ID
# - 응시자에게는 ephemeral(본인만 보임)로 퀴즈가 진행되므로,
#   관리자가 모든 응시자의 진행 상황을 볼 수 있도록 이 채널에 세션당 로그 메시지 1개를 남깁니다.
# - 값이 비어있거나 잘못된 경우 관리자 로그 기능만 비활성화되고 봇은 정상 동작합니다.
try:
    ADMIN_LOG_CHANNEL_ID = int(os.getenv("ADMIN_LOG_CHANNEL_ID", "0"))
except ValueError:
    print("[경고] ADMIN_LOG_CHANNEL_ID가 올바른 숫자가 아닙니다. 관리자 로그 기능을 비활성화합니다.")
    ADMIN_LOG_CHANNEL_ID = 0

# 퀴즈 시작을 허용할 채널 ID
# - 이 채널에서만 /타르코프퀴즈시작 을 사용할 수 있습니다.
# - 0(미설정)이면 모든 채널에서 시작할 수 있습니다.
try:
    QUIZ_CHANNEL_ID = int(os.getenv("QUIZ_CHANNEL_ID", "0"))
except ValueError:
    print("[경고] QUIZ_CHANNEL_ID가 올바른 숫자가 아닙니다. 채널 제한 없이 동작합니다.")
    QUIZ_CHANNEL_ID = 0

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

# 한 판(세션)에서 난이도별로 문제 풀에서 랜덤으로 뽑을 문제 수
# questions.json에 각 난이도별로 이 숫자 이상의 문제가 있어야 중복 없이 뽑힙니다.
SESSION_COUNTS = {
    "general": 2,
    "medium": 3,
    "hard": 15,
    "expert": 10,
}

TOTAL_QUESTIONS = sum(SESSION_COUNTS.values())

# 데이터베이스 파일 경로
DB_PATH = _project_path("QUIZ_DB_PATH", "quiz_leaderboard.db")

# 문제 데이터 경로
QUESTIONS_PATH = _project_path("QUIZ_QUESTIONS_PATH", "questions.json")

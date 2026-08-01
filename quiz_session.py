import asyncio
import time
from dataclasses import dataclass, field

import discord

import config

# (guild_id, user_id) -> QuizSession
active_sessions: dict[tuple[int, int], "QuizSession"] = {}


@dataclass
class QuizSession:
    mode: str
    guild_id: int
    user_id: int
    username: str
    channel_id: int
    questions: list[dict] = field(default_factory=list)
    index: int = 0
    score: int = 0
    correct_count: int = 0
    timed_out_count: int = 0
    started_at_monotonic: float = field(default_factory=time.monotonic)
    per_difficulty: dict[str, list[int]] = field(
        default_factory=lambda: {difficulty: [0, 0] for difficulty in config.SESSION_COUNTS}
    )
    message: discord.InteractionMessage | None = None
    current_shuffled_choices: list[int] | None = None
    finished: bool = False
    admin_log_message: discord.Message | None = None
    admin_log_lines: list[str] = field(default_factory=list)
    transition_lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def current_question(self) -> dict:
        return self.questions[self.index]

    def is_active(self) -> bool:
        """세션이 아직 유효하고 진행 중인지 확인한다."""
        return (
            not self.finished
            and self.index < self.total
            and active_sessions.get((self.guild_id, self.user_id)) is self
        )


def count_active_sessions(guild_id: int, mode: str | None = None) -> int:
    return sum(
        session.guild_id == guild_id
        and session.is_active()
        and (mode is None or session.mode == mode)
        for session in active_sessions.values()
    )


def cleanup_session(session: QuizSession) -> None:
    session.finished = True
    key = (session.guild_id, session.user_id)
    if active_sessions.get(key) is session:
        active_sessions.pop(key, None)

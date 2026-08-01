import unittest
from unittest.mock import Mock

import discord

import admin_log
from quiz_session import QuizSession


class AdminLogTests(unittest.TestCase):
    def test_embed_description_never_exceeds_safe_limit(self):
        session = QuizSession(
            mode="pvp",
            guild_id=10,
            user_id=1,
            username="테스터",
            channel_id=20,
            questions=[],
        )
        session.admin_log_lines.append("가" * 5000)
        decorate_embed = Mock()

        embed = admin_log.build_admin_embed(
            session,
            "진행 중",
            discord.Color.blurple(),
            mode_labels={"pvp": "PvP", "pve": "PvE"},
            decorate_embed=decorate_embed,
        )

        self.assertLessEqual(len(embed.description), 3900)
        self.assertTrue(embed.description.startswith("(이전 기록 생략)"))
        decorate_embed.assert_called_once()


if __name__ == "__main__":
    unittest.main()

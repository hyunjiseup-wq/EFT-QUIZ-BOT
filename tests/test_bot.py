import unittest
from unittest.mock import AsyncMock, Mock, patch

import bot


async def async_iterator(*items):
    for item in items:
        yield item


def empty_async_iterator():
    return async_iterator()


class BotHelpersTests(unittest.IsolatedAsyncioTestCase):
    def test_dashboard_view_is_persistent_and_custom_ids_are_unique(self):
        view = bot.QuizDashboardView()
        custom_ids = [item.custom_id for item in view.children]

        self.assertIsNone(view.timeout)
        self.assertEqual(len(custom_ids), 7)
        self.assertEqual(len(custom_ids), len(set(custom_ids)))

    def test_supervisor_dashboard_is_persistent_and_ids_do_not_overlap(self):
        quiz_ids = {item.custom_id for item in bot.QuizDashboardView().children}
        supervisor = bot.SupervisorDashboardView()
        supervisor_ids = [item.custom_id for item in supervisor.children]

        self.assertIsNone(supervisor.timeout)
        self.assertEqual(len(supervisor_ids), 5)
        self.assertEqual(len(supervisor_ids), len(set(supervisor_ids)))
        self.assertTrue(quiz_ids.isdisjoint(supervisor_ids))

    def test_dashboard_embed_shows_live_quiz_settings(self):
        embed = bot.build_dashboard_embed()
        values = "\n".join(field.value for field in embed.fields)

        self.assertEqual(embed.footer.text, bot.DASHBOARD_MARKER)
        self.assertIn(str(len(bot.ALL_QUESTIONS)), values)
        self.assertIn(str(bot.config.TOTAL_QUESTIONS), values)
        self.assertIn(str(bot.config.QUESTION_TIME_LIMIT), values)

    def test_supervisor_dashboard_embed_has_distinct_marker(self):
        embed = bot.build_supervisor_dashboard_embed()

        self.assertEqual(embed.footer.text, bot.SUPERVISOR_DASHBOARD_MARKER)
        self.assertNotEqual(embed.footer.text, bot.DASHBOARD_MARKER)

    def test_tutorial_explains_both_modes_and_give_up(self):
        embed = bot.build_tutorial_embed()
        values = "\n".join(field.value for field in embed.fields)

        self.assertIn("PvP", values)
        self.assertIn("PvE", values)
        self.assertIn("/타르코프퀴즈포기", values)

    def test_public_stats_embed_separates_unique_users_and_attempts(self):
        stats = {
            "total_participants": 3,
            "total_attempts": 8,
            "modes": {
                "pvp": {"participants": 2, "attempts": 5},
                "pve": {"participants": 2, "attempts": 3},
            },
        }

        embed = bot.build_public_stats_embed(stats)
        values = "\n".join(field.value for field in embed.fields)

        self.assertIn("3명", values)
        self.assertIn("8회", values)
        self.assertIn("5회", values)
        self.assertIn("3회", values)

    def test_hidden_reward_embed_contains_review_categories(self):
        candidate = {
            "user_id": "1",
            "username": "후보",
            "attempts": 4,
            "active_days": 3,
            "first_score": 100,
            "best_score": 300,
            "lowest_sincere_score": 80,
            "improvement": 200,
            "average_score": 180,
        }
        report = {
            "participants": 1,
            "attempts": 4,
            "most_attempts": [candidate],
            "most_days": [candidate],
            "underdogs": [candidate],
            "growth": [candidate],
            "dual_mode": [candidate],
        }

        embed = bot.build_hidden_reward_embed(report, 30)
        names = {field.name for field in embed.fields}

        self.assertIn("🏃 최다 완주", names)
        self.assertIn("📅 꾸준한 생존자", names)
        self.assertIn("📈 성장상", names)
        self.assertIn("🩹 언더독 검토", names)
        self.assertIn("⚔️ 올라운더", names)

    async def test_upsert_dashboard_creates_message_when_none_exists(self):
        channel = Mock()
        channel.pins.return_value = empty_async_iterator()
        channel.history.return_value = empty_async_iterator()
        channel.send = AsyncMock(return_value="new-dashboard")

        message, created = await bot.upsert_dashboard(channel)

        self.assertTrue(created)
        self.assertEqual(message, "new-dashboard")
        channel.send.assert_awaited_once()

    async def test_upsert_dashboard_updates_pinned_message(self):
        existing = Mock()
        existing.author = bot.bot.user
        existing.embeds = [Mock()]
        existing.embeds[0].footer.text = bot.DASHBOARD_MARKER
        existing.edit = AsyncMock()
        channel = Mock()
        channel.pins.return_value = async_iterator(existing)
        channel.history.return_value = empty_async_iterator()

        message, created = await bot.upsert_dashboard(channel)

        self.assertFalse(created)
        self.assertIs(message, existing)
        existing.edit.assert_awaited_once()
        channel.history.assert_not_called()

    async def test_supervisor_dashboard_does_not_replace_quiz_dashboard(self):
        quiz_dashboard = Mock()
        quiz_dashboard.author = bot.bot.user
        quiz_dashboard.embeds = [Mock()]
        quiz_dashboard.embeds[0].footer.text = bot.DASHBOARD_MARKER
        channel = Mock()
        channel.pins.return_value = async_iterator(quiz_dashboard)
        channel.history.return_value = empty_async_iterator()
        channel.send = AsyncMock(return_value="new-supervisor-dashboard")

        message, created = await bot.upsert_supervisor_dashboard(channel)

        self.assertTrue(created)
        self.assertEqual(message, "new-supervisor-dashboard")
        channel.send.assert_awaited_once()

    async def test_leaderboard_defers_before_database_result(self):
        interaction = Mock()
        interaction.guild_id = 10
        interaction.response.defer = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        with patch.object(bot.database, "get_leaderboard", return_value=[]):
            await bot.show_leaderboard(interaction, "pvp", ephemeral=True)

        interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        interaction.edit_original_response.assert_awaited_once_with(
            content="아직 기록이 없어요. 먼저 퀴즈에 도전해보세요!"
        )

    def test_active_session_count_is_isolated_by_guild_and_mode(self):
        pvp = Mock(guild_id=10, mode="pvp")
        pvp.is_active.return_value = True
        pve = Mock(guild_id=10, mode="pve")
        pve.is_active.return_value = True
        other_guild = Mock(guild_id=20, mode="pvp")
        other_guild.is_active.return_value = True

        with patch.dict(
            bot.active_sessions,
            {(10, 1): pvp, (10, 2): pve, (20, 3): other_guild},
            clear=True,
        ):
            self.assertEqual(bot.count_active_sessions(10), 2)
            self.assertEqual(bot.count_active_sessions(10, "pvp"), 1)
            self.assertEqual(bot.count_active_sessions(20), 1)

    async def test_admin_log_updates_are_batched(self):
        question = {
            "difficulty": "general",
            "question": "테스트 문제",
            "choices": ["정답", "오답1", "오답2", "오답3"],
            "answer": 0,
            "explanation": "테스트 해설",
        }
        session = bot.QuizSession(
            mode="pvp",
            guild_id=10,
            user_id=1,
            username="테스터",
            channel_id=20,
            questions=[question] * 30,
        )
        session.admin_log_message = Mock()
        session.admin_log_message.edit = AsyncMock()

        with patch.object(bot.config, "ADMIN_LOG_UPDATE_EVERY", 5):
            session.per_difficulty["general"] = [0, 1]
            await bot.update_admin_log(session, question, False, False, "오답1")
            session.admin_log_message.edit.assert_not_awaited()

            session.per_difficulty["general"] = [0, 5]
            await bot.update_admin_log(session, question, False, False, "오답1")
            session.admin_log_message.edit.assert_awaited_once()

    def test_leaderboard_line_labels_accumulated_results(self):
        line = bot.format_leaderboard_line("🥇", "테스터", 100, 2, 7, 10)

        self.assertEqual(
            line,
            "🥇 **테스터** — 최고 100점 (누적 정답 7/10, 2회 도전)",
        )

    async def test_edit_session_message_uses_followup_edit_after_defer(self):
        session = Mock()
        interaction = Mock()
        interaction.response.is_done.return_value = True
        interaction.edit_original_response = AsyncMock()
        interaction.original_response = AsyncMock(return_value="updated-message")

        updated = await bot.edit_session_message(
            session,
            interaction,
            content="다음 문제",
            view=None,
        )

        self.assertTrue(updated)
        interaction.edit_original_response.assert_awaited_once_with(
            content="다음 문제",
            view=None,
        )
        interaction.response.edit_message.assert_not_called()
        self.assertEqual(session.message, "updated-message")


if __name__ == "__main__":
    unittest.main()

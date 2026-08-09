import struct
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import bot
import dashboard_manager
import quiz_icons
import quiz_reports


async def async_iterator(*items):
    for item in items:
        yield item


def empty_async_iterator():
    return async_iterator()


class SupervisorChannelGateTests(unittest.IsolatedAsyncioTestCase):
    def make_interaction(self, channel_id: int, guild_id: int = 10):
        return SimpleNamespace(
            guild_id=guild_id,
            channel_id=channel_id,
            response=SimpleNamespace(send_message=AsyncMock()),
        )

    async def test_configured_supervisor_channel_passes(self):
        interaction = self.make_interaction(31)

        with patch.object(bot.config, "ADMIN_LOG_CHANNEL_IDS", (30, 31)):
            rejected = await bot.reject_outside_supervisor_channel(interaction, "감독 기능")

        self.assertFalse(rejected)
        interaction.response.send_message.assert_not_awaited()

    async def test_other_channel_is_pointed_at_this_guild_supervisor_channel(self):
        interaction = self.make_interaction(99, guild_id=11)
        channels = {
            30: SimpleNamespace(guild=SimpleNamespace(id=10)),
            31: SimpleNamespace(guild=SimpleNamespace(id=11)),
        }

        with (
            patch.object(bot.config, "ADMIN_LOG_CHANNEL_IDS", (30, 31)),
            patch.object(bot.bot, "get_channel", side_effect=channels.get, create=True),
        ):
            rejected = await bot.reject_outside_supervisor_channel(interaction, "감독 기능")

        self.assertTrue(rejected)
        notice = interaction.response.send_message.await_args.args[0]
        self.assertIn("<#31>", notice)
        self.assertNotIn("<#30>", notice)

    def test_korean_particle_follows_final_consonant(self):
        self.assertEqual(
            "감독 기능"
            + bot.korean_particle("감독 기능", with_final="은", without_final="는"),
            "감독 기능은",
        )
        self.assertEqual(
            "히든 상품 후보"
            + bot.korean_particle("히든 상품 후보", with_final="은", without_final="는"),
            "히든 상품 후보는",
        )


class BotHelpersTests(unittest.IsolatedAsyncioTestCase):
    def test_operations_check_command_is_registered_once(self):
        command_names = [command.name for command in bot.bot.tree.get_commands()]

        self.assertEqual(command_names.count("퀴즈봇상태점검"), 1)

    async def test_setup_hook_keeps_bot_running_when_command_sync_fails(self):
        response = Mock(status=503, reason="Service Unavailable", headers={})
        sync_error = bot.discord.HTTPException(response, "temporary failure")
        fake_bot = SimpleNamespace(
            tree=SimpleNamespace(sync=AsyncMock(side_effect=sync_error)),
            add_view=Mock(),
        )

        with (
            patch.object(bot.database, "init_db") as init_db,
            patch.object(bot.log, "exception") as log_exception,
        ):
            await bot.QuizBot.setup_hook(fake_bot)

        init_db.assert_called_once_with()
        self.assertEqual(fake_bot.add_view.call_count, 2)
        log_exception.assert_called_once()

    def test_run_bot_reuses_root_logging_without_discord_handler(self):
        with (
            patch.object(bot.config, "DISCORD_TOKEN", "test-token"),
            patch.object(bot.bot, "run") as run,
        ):
            bot.run_bot()

        run.assert_called_once_with("test-token", log_handler=None)

    def test_run_bot_rejects_missing_token_before_connecting(self):
        with (
            patch.object(bot.config, "DISCORD_TOKEN", ""),
            patch.object(bot.bot, "run") as run,
            self.assertRaisesRegex(RuntimeError, "DISCORD_TOKEN"),
        ):
            bot.run_bot()

        run.assert_not_called()

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

    def test_dashboard_custom_emoji_mapping_covers_every_button(self):
        custom_ids = {
            item.custom_id for item in bot.QuizDashboardView().children
        } | {
            item.custom_id for item in bot.SupervisorDashboardView().children
        }

        self.assertEqual(custom_ids, set(quiz_icons.DASHBOARD_EMOJI_BY_CUSTOM_ID))
        self.assertTrue(
            set(quiz_icons.DASHBOARD_EMOJI_BY_CUSTOM_ID.values()).issubset(
                bot.QUIZ_EMOJI_ASSETS
            )
        )

    def test_dashboard_icon_assets_are_discord_ready_rgba_pngs(self):
        self.assertEqual(bot.validate_quiz_icon_assets(), [])
        for filename in bot.QUIZ_EMOJI_ASSETS.values():
            path = bot.QUIZ_ICON_DIR / filename
            data = path.read_bytes()
            width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])

            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"), filename)
            self.assertEqual((width, height), (128, 128), filename)
            self.assertEqual(bit_depth, 8, filename)
            self.assertEqual(color_type, 6, filename)  # RGBA
            self.assertLessEqual(len(data), 256 * 1024, filename)

    def test_quiz_icon_slot_preflight_counts_only_static_emojis(self):
        existing = [
            SimpleNamespace(name="tq_pvp_start", animated=False),
            SimpleNamespace(name="animated_other", animated=True),
            SimpleNamespace(name="static_other", animated=False),
        ]
        guild = SimpleNamespace(emojis=existing, emoji_limit=3)

        missing = bot.missing_quiz_emoji_names(existing)

        self.assertNotIn("tq_pvp_start", missing)
        self.assertEqual(len(missing), len(bot.QUIZ_EMOJI_ASSETS) - 1)
        self.assertEqual(bot.available_static_emoji_slots(guild), 1)

    def test_dashboard_view_prefers_registered_custom_emoji(self):
        emoji = bot.discord.PartialEmoji(name="tq_pvp_start", id=123456)
        view = bot.QuizDashboardView([emoji])
        start_button = next(
            item
            for item in view.children
            if item.custom_id == "tarkov_quiz:pvp:start"
        )

        self.assertEqual(start_button.emoji.id, 123456)

    def test_embed_uses_custom_thumbnail_and_removes_fallback_title_icon(self):
        emoji = bot.discord.PartialEmoji(name="tq_complete", id=654321)
        embed = bot.discord.Embed()

        bot.decorate_embed(
            embed,
            "퀴즈 완료!",
            "tq_complete",
            "🏁",
            emojis=[emoji],
        )

        self.assertEqual(embed.title, "퀴즈 완료!")
        self.assertIn("654321", embed.thumbnail.url)

    def test_result_alerts_keep_unicode_fallback_without_server_icons(self):
        self.assertTrue(bot.build_result_text(False).startswith("📨"))
        self.assertTrue(bot.build_result_text(True).startswith("⏰"))

    def test_channel_dashboard_emojis_accepts_discord_tuple_cache(self):
        emoji = bot.discord.PartialEmoji(name="tq_tutorial", id=789)
        channel = SimpleNamespace(guild=SimpleNamespace(emojis=(emoji,)))

        self.assertEqual(dashboard_manager.channel_dashboard_emojis(channel), [emoji])

    def test_dashboard_embed_shows_live_quiz_settings(self):
        embed = bot.build_dashboard_embed()
        values = "\n".join(field.value for field in embed.fields)

        self.assertIsNone(embed.footer.text)
        self.assertIn(str(len(bot.ALL_QUESTIONS)), values)
        self.assertIn(str(bot.config.TOTAL_QUESTIONS), values)
        self.assertIn(str(bot.config.QUESTION_TIME_LIMIT), values)

    def test_supervisor_dashboard_embed_hides_internal_marker(self):
        embed = bot.build_supervisor_dashboard_embed()

        self.assertIsNone(embed.footer.text)

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

        embed = quiz_reports.build_public_stats_embed(
            stats, None, bot.MODE_LABELS, bot.decorate_embed
        )
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

        embed = quiz_reports.build_hidden_reward_embed(
            report, 30, None, bot.decorate_embed, bot.quiz_icon_text
        )
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

    async def test_dashboard_pin_failure_does_not_break_dashboard(self):
        response = Mock(status=403, reason="Forbidden", headers={})
        error = bot.discord.Forbidden(response, "forbidden")
        message = SimpleNamespace(pinned=False, pin=AsyncMock(side_effect=error))

        with patch.object(bot.log, "warning") as log_warning:
            pinned = await dashboard_manager.ensure_dashboard_pinned(
                message, "감독", bot.log
            )

        self.assertFalse(pinned)
        log_warning.assert_called_once()

    async def test_dashboard_is_pinned_when_permission_is_available(self):
        message = SimpleNamespace(pinned=False, pin=AsyncMock())

        pinned = await dashboard_manager.ensure_dashboard_pinned(message, "감독", bot.log)

        self.assertTrue(pinned)
        message.pin.assert_awaited_once_with(reason="타르코프 퀴즈 감독 대시보드 자동 고정")

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

    async def test_upsert_dashboard_migrates_legacy_v1_footer_in_place(self):
        existing = Mock()
        existing.author = bot.bot.user
        existing.pinned = True
        existing.embeds = [Mock()]
        existing.embeds[0].footer.text = bot.LEGACY_DASHBOARD_MARKERS[0]
        existing.edit = AsyncMock()
        channel = Mock()
        channel.pins.return_value = async_iterator(existing)
        channel.history.return_value = empty_async_iterator()
        channel.send = AsyncMock()

        message, created = await bot.upsert_dashboard(channel)

        self.assertFalse(created)
        self.assertIs(message, existing)
        channel.send.assert_not_awaited()
        updated_embed = existing.edit.await_args.kwargs["embed"]
        self.assertIsNone(updated_embed.footer.text)

    async def test_upsert_dashboard_finds_markerless_message_by_button_id(self):
        existing = Mock()
        existing.author = bot.bot.user
        existing.pinned = True
        existing.embeds = [bot.discord.Embed(title="타르코프 지식 퀴즈")]
        existing.components = [
            SimpleNamespace(
                children=[SimpleNamespace(custom_id="tarkov_quiz:pvp:start")]
            )
        ]
        existing.edit = AsyncMock()
        channel = Mock()
        channel.pins.return_value = async_iterator(existing)
        channel.history.return_value = empty_async_iterator()
        channel.send = AsyncMock()

        message, created = await bot.upsert_dashboard(channel)

        self.assertFalse(created)
        self.assertIs(message, existing)
        channel.send.assert_not_awaited()

    async def test_upsert_dashboard_uses_persisted_message_before_history(self):
        existing = Mock()
        existing.id = 999
        existing.author = bot.bot.user
        existing.pinned = True
        existing.embeds = [Mock()]
        existing.embeds[0].footer.text = bot.DASHBOARD_MARKER
        existing.edit = AsyncMock()
        channel = SimpleNamespace(
            id=20,
            guild=SimpleNamespace(id=10, emojis=[]),
            fetch_message=AsyncMock(return_value=existing),
            pins=Mock(return_value=empty_async_iterator()),
            history=Mock(return_value=empty_async_iterator()),
            send=AsyncMock(),
        )

        with (
            patch.object(bot.database, "get_dashboard_message", return_value=(20, 999)),
            patch.object(bot.database, "save_dashboard_message") as save,
        ):
            message, created = await bot.upsert_dashboard(channel)

        self.assertFalse(created)
        self.assertIs(message, existing)
        channel.fetch_message.assert_awaited_once_with(999)
        channel.pins.assert_not_called()
        channel.history.assert_not_called()
        save.assert_called_once_with(10, "quiz", 20, 999)

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

    async def test_supervisor_dashboard_migrates_legacy_v1_footer_in_place(self):
        existing = Mock()
        existing.author = bot.bot.user
        existing.pinned = True
        existing.embeds = [Mock()]
        existing.embeds[0].footer.text = bot.LEGACY_SUPERVISOR_DASHBOARD_MARKERS[0]
        existing.edit = AsyncMock()
        channel = Mock()
        channel.pins.return_value = async_iterator(existing)
        channel.history.return_value = empty_async_iterator()
        channel.send = AsyncMock()

        message, created = await bot.upsert_supervisor_dashboard(channel)

        self.assertFalse(created)
        self.assertIs(message, existing)
        channel.send.assert_not_awaited()
        updated_embed = existing.edit.await_args.kwargs["embed"]
        self.assertIsNone(updated_embed.footer.text)

    async def test_leaderboard_defers_before_database_result(self):
        interaction = Mock()
        interaction.guild_id = 10
        interaction.response.defer = AsyncMock()
        interaction.edit_original_response = AsyncMock()

        with patch.object(bot.database, "get_leaderboard", return_value=[]):
            await bot.show_leaderboard(interaction, "pvp", ephemeral=True)

        interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        interaction.edit_original_response.assert_awaited_once_with(
            content="🎯 아직 기록이 없어요. 먼저 퀴즈에 도전해보세요!"
        )

    async def test_leaderboard_remains_available_at_session_limit(self):
        interaction = Mock()
        interaction.guild_id = 10
        interaction.response.defer = AsyncMock()
        interaction.response.send_message = AsyncMock()
        interaction.edit_original_response = AsyncMock()
        session = Mock(guild_id=10, mode="pvp")
        session.is_active.return_value = True

        with (
            patch.dict(bot.active_sessions, {(10, 1): session}, clear=True),
            patch.object(bot.config, "MAX_ACTIVE_SESSIONS_PER_GUILD", 1),
            patch.object(
                bot.database,
                "get_leaderboard",
                return_value=[("테스터", 100, 1, 4, 5)],
            ),
        ):
            await bot.show_leaderboard(interaction, "pvp", ephemeral=True)

        interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        interaction.response.send_message.assert_not_awaited()
        interaction.edit_original_response.assert_awaited_once()

    async def test_start_quiz_rejects_new_session_at_guild_limit(self):
        interaction = Mock()
        interaction.guild_id = 10
        interaction.channel_id = next(iter(bot.config.QUIZ_CHANNEL_IDS), 20)
        interaction.user = SimpleNamespace(id=2, display_name="신규 참가자")
        interaction.response.send_message = AsyncMock()
        session = Mock(guild_id=10, mode="pvp")
        session.is_active.return_value = True

        with (
            patch.dict(bot.active_sessions, {(10, 1): session}, clear=True),
            patch.object(bot.config, "MAX_ACTIVE_SESSIONS_PER_GUILD", 1),
            patch.object(bot, "build_session_questions") as build_questions,
        ):
            await bot.start_quiz(interaction, "pvp")

        interaction.response.send_message.assert_awaited_once()
        self.assertTrue(interaction.response.send_message.await_args.kwargs["ephemeral"])
        build_questions.assert_not_called()
        self.assertNotIn((10, 2), bot.active_sessions)

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
            await session.admin_log_task
            session.admin_log_message.edit.assert_awaited_once()

    async def test_final_admin_log_timeout_is_reported_and_detached(self):
        session = bot.QuizSession(
            mode="pvp",
            guild_id=10,
            user_id=1,
            username="테스터",
            channel_id=20,
            questions=[],
        )
        session.admin_log_message = SimpleNamespace(
            edit=AsyncMock(side_effect=TimeoutError)
        )

        with patch.object(bot.log, "warning") as log_warning:
            await bot.finalize_admin_log(session, aborted=False)
            await session.admin_log_task

        log_warning.assert_called_once()
        self.assertIsNone(session.admin_log_message)

    def test_leaderboard_line_labels_accumulated_results(self):
        line = quiz_reports.format_leaderboard_line("🥇", "테스터", 100, 2, 7, 10)

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

    async def test_stale_answer_callback_is_ignored_before_scoring(self):
        question = {
            "difficulty": "general",
            "question": "테스트 문제",
            "choices": ["정답", "오답1", "오답2", "오답3"],
            "answer": 0,
            "explanation": "해설",
        }
        session = bot.QuizSession(
            mode="pvp",
            guild_id=10,
            user_id=1,
            username="테스터",
            channel_id=20,
            questions=[question, question],
        )
        view = bot.AnswerView(session)
        session.index = 1
        interaction = Mock()
        interaction.response.defer = AsyncMock()

        with (
            patch.dict(bot.active_sessions, {(10, 1): session}, clear=True),
            patch.object(bot.quiz_scoring, "score_answer") as score_answer,
        ):
            await view.handle_answer(interaction, 0)

        interaction.response.defer.assert_awaited_once()
        score_answer.assert_not_called()
        self.assertEqual(session.score, 0)
        self.assertEqual(session.correct_count, 0)

    async def test_answer_view_error_aborts_session_and_reports_error(self):
        question = {
            "difficulty": "general",
            "question": "테스트 문제",
            "choices": ["정답", "오답1", "오답2", "오답3"],
            "answer": 0,
            "explanation": "해설",
        }
        session = bot.QuizSession(
            mode="pvp",
            guild_id=10,
            user_id=1,
            username="테스터",
            channel_id=20,
            questions=[question],
        )
        session.message = SimpleNamespace(edit=AsyncMock())
        view = bot.AnswerView(session)
        interaction = Mock()
        error = RuntimeError("answer failed")

        with (
            patch.dict(bot.active_sessions, {(10, 1): session}, clear=True),
            patch.object(bot, "finalize_admin_log", new=AsyncMock()) as finalize,
            patch.object(bot, "report_interaction_error", new=AsyncMock()) as report,
        ):
            await view.on_error(interaction, error, SimpleNamespace(custom_id="answer-a"))

            self.assertNotIn((10, 1), bot.active_sessions)

        finalize.assert_awaited_once_with(
            session,
            aborted=True,
            reason="답변 처리 오류",
        )
        session.message.edit.assert_awaited_once()
        report.assert_awaited_once_with(
            interaction,
            error,
            context="answer:answer-a",
        )

    async def test_timeout_error_aborts_session(self):
        question = {
            "difficulty": "general",
            "question": "테스트 문제",
            "choices": ["정답", "오답1", "오답2", "오답3"],
            "answer": 0,
            "explanation": "해설",
        }
        session = bot.QuizSession(
            mode="pvp",
            guild_id=10,
            user_id=1,
            username="테스터",
            channel_id=20,
            questions=[question],
        )
        session.message = SimpleNamespace(edit=AsyncMock())
        view = bot.AnswerView(session)

        with (
            patch.dict(bot.active_sessions, {(10, 1): session}, clear=True),
            patch.object(
                bot,
                "update_admin_log",
                new=AsyncMock(side_effect=RuntimeError("timeout failed")),
            ),
            patch.object(bot, "finalize_admin_log", new=AsyncMock()) as finalize,
            patch.object(bot.log, "exception") as log_exception,
        ):
            await view.on_timeout()

            self.assertNotIn((10, 1), bot.active_sessions)

        finalize.assert_awaited_once_with(
            session,
            aborted=True,
            reason="시간 초과 처리 오류",
        )
        session.message.edit.assert_awaited_once()
        log_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()

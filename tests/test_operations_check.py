import unittest
from types import SimpleNamespace

import operations_check


class FakeChannel:
    def __init__(
        self,
        guild,
        *,
        channel_id=0,
        bot_permissions=(True, True, True),
        everyone_can_view=False,
    ):
        self.id = channel_id
        self.guild = guild
        self.bot_permissions = bot_permissions
        self.everyone_can_view = everyone_can_view

    def permissions_for(self, member):
        if member is self.guild.default_role:
            return SimpleNamespace(view_channel=self.everyone_can_view)
        view, send, history = self.bot_permissions
        return SimpleNamespace(
            view_channel=view,
            send_messages=send,
            read_message_history=history,
        )


class FakeBot:
    def __init__(self, channels):
        self.channels = channels

    def get_channel(self, channel_id):
        return self.channels.get(channel_id)


def healthy_db_status():
    return {
        "integrity_ok": True,
        "schema_version": 2,
        "expected_schema_version": 2,
        "leaderboard_rows": 28,
        "attempt_rows": 3,
        "dashboards": {"quiz": (20, 200), "supervisor": (30, 300)},
    }


class OperationsCheckTests(unittest.TestCase):
    def setUp(self):
        self.guild = SimpleNamespace(id=10, me=object(), default_role=object())
        self.other_guild = SimpleNamespace(id=11, me=object(), default_role=object())
        self.quiz_channel = FakeChannel(self.guild, channel_id=20)
        self.supervisor_channel = FakeChannel(self.guild, channel_id=30)
        # 다른 서버에 설정된 채널은 이 서버 점검 결과를 오염시키면 안 된다.
        self.other_quiz_channel = FakeChannel(
            self.other_guild,
            channel_id=21,
            bot_permissions=(False, False, False),
        )
        self.bot = FakeBot(
            {
                20: self.quiz_channel,
                21: self.other_quiz_channel,
                30: self.supervisor_channel,
            }
        )

    def collect(self, **overrides):
        values = {
            "bot": self.bot,
            "guild": self.guild,
            "db_status": healthy_db_status(),
            "db_error": False,
            "quiz_channel_ids": (20, 21),
            "admin_channel_ids": (30,),
            "total_questions": 446,
            "pvp_pool_size": 444,
            "pve_pool_size": 441,
            "active_session_count": 2,
            "max_active_sessions": 250,
            "pending_admin_logs": 0,
            "missing_icons": [],
            "total_icons": 21,
        }
        values.update(overrides)
        return operations_check.collect_operations_checks(**values)

    def test_all_healthy_checks_are_green(self):
        checks = self.collect()
        embed = operations_check.build_operations_check_embed(checks)
        quiz_detail = next(check.detail for check in checks if check.title == "퀴즈 채널")

        self.assertTrue(all(check.level == "ok" for check in checks))
        self.assertIn("모든 운영 점검", embed.description)
        self.assertEqual(len(embed.fields), len(checks))
        self.assertIn("<#20>", quiz_detail)
        self.assertIn("다른 서버 1곳", quiz_detail)
        self.assertNotIn("<#21>", quiz_detail)

    def test_guild_without_configured_quiz_channel_is_warned(self):
        checks = self.collect(guild=self.other_guild, quiz_channel_ids=(20,))
        warnings = {check.title: check.detail for check in checks if check.level == "warning"}

        self.assertIn("퀴즈 채널", warnings)
        self.assertIn("퀴즈를 시작할 수 없습니다", warnings["퀴즈 채널"])
        self.assertIn("감독 채널", warnings)

    def test_unknown_channel_id_is_reported_as_error(self):
        checks = self.collect(quiz_channel_ids=(20, 999))
        errors = {check.title: check.detail for check in checks if check.level == "error"}

        self.assertIn("퀴즈 채널", errors)
        self.assertIn("999", errors["퀴즈 채널"])

    def test_dashboard_registered_in_any_configured_channel_is_ok(self):
        db_status = healthy_db_status()
        db_status["dashboards"]["quiz"] = (21, 210)

        mismatched = self.collect(db_status=db_status, quiz_channel_ids=(20, 21))
        matched = self.collect(
            db_status=db_status,
            guild=self.other_guild,
            quiz_channel_ids=(20, 21),
            admin_channel_ids=(),
        )

        # 이 서버 대시보드는 이 서버 설정 채널에 있어야 한다.
        self.assertEqual(
            next(check.level for check in mismatched if check.title == "대시보드 등록"),
            "error",
        )
        self.assertEqual(
            next(check.level for check in matched if check.title == "대시보드 등록"),
            "ok",
        )

    def test_public_supervisor_and_missing_assets_are_warnings(self):
        self.supervisor_channel.everyone_can_view = True
        db_status = healthy_db_status()
        db_status["dashboards"].pop("supervisor")

        checks = self.collect(db_status=db_status, missing_icons=["one", "two"])
        warnings = {check.title: check.detail for check in checks if check.level == "warning"}

        self.assertIn("감독 채널", warnings)
        self.assertIn("@everyone", warnings["감독 채널"])
        self.assertIn("대시보드 등록", warnings)
        self.assertIn("전용 아이콘", warnings)

    def test_database_and_channel_failures_are_errors(self):
        self.quiz_channel.bot_permissions = (True, False, False)

        checks = self.collect(db_status=None, db_error=True)
        errors = {check.title: check.detail for check in checks if check.level == "error"}

        self.assertIn("데이터베이스", errors)
        self.assertIn("퀴즈 채널", errors)
        self.assertIn("메시지 보내기", errors["퀴즈 채널"])
        self.assertIn("대시보드 등록", errors)

    def test_admin_log_backlog_warns_before_reaching_session_limit(self):
        warnings = {
            check.title: check.detail
            for check in self.collect(pending_admin_logs=26)
            if check.level == "warning"
        }
        errors = {
            check.title: check.detail
            for check in self.collect(pending_admin_logs=250)
            if check.level == "error"
        }

        self.assertIn("관전 로그 큐", warnings)
        self.assertIn("26개", warnings["관전 로그 큐"])
        self.assertIn("관전 로그 큐", errors)


if __name__ == "__main__":
    unittest.main()

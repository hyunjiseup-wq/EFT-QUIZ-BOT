import importlib
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord

import guild_channels


def fake_channel(guild_id: int, channel_id: int = 0):
    return SimpleNamespace(id=channel_id, guild=SimpleNamespace(id=guild_id))


class ChannelIdEnvTests(unittest.TestCase):
    """서버마다 채널이 다르므로 설정은 채널 ID 목록을 받는다."""

    def load_config(self, raw: str):
        import config

        with patch.dict("os.environ", {"QUIZ_CHANNEL_ID": raw}, clear=False):
            # load_dotenv는 이미 존재하는 환경변수를 덮어쓰지 않는다.
            reloaded = importlib.reload(config)
            channel_ids = reloaded.QUIZ_CHANNEL_IDS
        importlib.reload(config)
        return channel_ids

    def test_comma_separated_ids_are_all_kept(self):
        self.assertEqual(
            self.load_config("1525447869576773702, 1533391768345772082"),
            (1525447869576773702, 1533391768345772082),
        )

    def test_single_id_and_unset_values_still_work(self):
        self.assertEqual(self.load_config("1525447869576773702"), (1525447869576773702,))
        self.assertEqual(self.load_config("0"), ())
        self.assertEqual(self.load_config(""), ())

    def test_invalid_entry_is_skipped_without_dropping_valid_ones(self):
        self.assertEqual(self.load_config("20, 채널ID, -5, 20, 21"), (20, 21))


class GuildChannelLookupTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        guild_channels.forget_unresolvable_channels()

    def test_guild_channel_id_picks_the_channel_of_that_guild(self):
        client = SimpleNamespace(
            get_channel=Mock(
                side_effect={20: fake_channel(10), 21: fake_channel(11)}.get
            )
        )

        self.assertEqual(guild_channels.guild_channel_id(client, (20, 21), 11), 21)
        self.assertIsNone(guild_channels.guild_channel_id(client, (20, 21), 12))

    async def test_uncached_channel_is_fetched_once_and_failure_is_remembered(self):
        response = Mock(status=404, reason="Not Found", headers={})
        client = SimpleNamespace(
            get_channel=Mock(return_value=None),
            fetch_channel=AsyncMock(
                side_effect=discord.NotFound(response, "missing channel")
            ),
        )
        logger = Mock()

        for _ in range(3):
            channel = await guild_channels.fetch_guild_channel(
                client, (20,), 10, logger, label="퀴즈"
            )
            self.assertIsNone(channel)

        client.fetch_channel.assert_awaited_once()
        logger.warning.assert_called_once()

    async def test_cached_channel_of_another_guild_is_not_returned(self):
        client = SimpleNamespace(
            get_channel=Mock(side_effect={30: fake_channel(10)}.get),
            fetch_channel=AsyncMock(),
        )

        channel = await guild_channels.fetch_guild_channel(
            client, (30,), 11, Mock(), label="감독"
        )

        self.assertIsNone(channel)
        client.fetch_channel.assert_not_awaited()

    def test_split_by_guild_separates_other_servers_from_unknown_ids(self):
        client = SimpleNamespace(
            get_channel=Mock(
                side_effect={20: fake_channel(10, 20), 21: fake_channel(11, 21)}.get
            )
        )

        in_guild, other_guild, unreachable = guild_channels.split_by_guild(
            client, (20, 21, 999), 10
        )

        self.assertEqual([channel.id for channel in in_guild], [20])
        self.assertEqual(other_guild, [21])
        self.assertEqual(unreachable, [999])


if __name__ == "__main__":
    unittest.main()

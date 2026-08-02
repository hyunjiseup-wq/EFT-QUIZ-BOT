# Tarkov Knowledge Quiz Bot

*[한국어](README.md)*

A Discord quiz bot that tests knowledge of Escape from Tarkov's mechanics, systems, and lore.
It uses a 4-choice button UI, and `questions.json` currently holds **446 questions**.
Each session randomly draws **General 2 · Medium 3 · Hard 15 · Expert 10 (30 questions total)** from that pool per difficulty
and shuffles the answer order too, so the same player sees a different combination every time they play,
and even if questions leak into the community, their usefulness is limited.

The draw counts can be adjusted in `config.py`'s `SESSION_COUNTS` (though you can't set them higher than the size of each difficulty pool).

## How it works

- The public **player dashboard** provides **Start PvP · Start PvE · Tutorial · mode ranking · personal record** buttons.
  When `QUIZ_CHANNEL_ID` is configured, the bot automatically installs or refreshes it on startup.
  An administrator can also run `/퀴즈대시보드설치` in a channel; running it again updates
  an existing pinned dashboard (or one found in the latest 100 messages) instead of posting a duplicate.
  The bot pins an installed or refreshed dashboard automatically, and its buttons survive restarts.
- A separate **supervisor dashboard** is automatically installed in `ADMIN_LOG_CHANNEL_ID`.
  It provides participation stats, 30-day hidden-reward candidates, active sessions, and PvP/PvE
  rankings. Only server administrators can use its buttons.
- Both dashboards and quiz notifications support 21 original Tarkov-inspired icons from
  `assets/dashboard_icons/` (ten dashboard icons and eleven notification icons).
  An administrator can run `/대시보드아이콘설치` once to upload only missing custom emojis and
  immediately refresh the configured player and supervisor dashboards. Existing emojis with the
  reserved names are reused, never deleted or overwritten; default Unicode emoji remain as fallback.
- `/pvp퀴즈`: Starts a quiz using common questions plus PvP-only questions.
- `/pve퀴즈`: Starts a quiz using common questions plus PvE-only questions.
  The quiz runs in an ephemeral message visible only to the person who ran the command.
  If several people run the command in the same channel at once, each only sees their own screen — no one sees anyone else's progress.
  Setting a channel ID in `.env`'s `QUIZ_CHANNEL_ID` restricts quiz starts to **that channel only**
  (attempts in other channels get redirected there; `0` or unset allows all channels).
- 20-second time limit per question (adjustable via `config.py`'s `QUESTION_TIME_LIMIT`). Timing out counts as wrong and auto-advances to the next question.
- **The question's difficulty/points, whether the answer was right or wrong, and the correct answer/explanation are never shown to the player.**
  Submitting an answer only shows "Submitted" (or a timeout notice on timeout), and no running score is shown during play.
  Correct/incorrect history and per-difficulty breakdowns are only visible in the admin spectator log.
- When all questions are answered, the final score and correct-answer count are shown, and the record is saved.
- `/타르코프퀴즈포기` (give-up): Abandons the quiz in progress (not saved). Use this to quit partway through and start over.
- `/pvp퀴즈랭킹`, `/pve퀴즈랭킹`: Mode-specific server TOP 10 (by best score, public message)
- `/퀴즈참가현황` (participation-stats): Public unique participant count and cumulative
  PvP/PvE completions for the server.
- `/pvp퀴즈기록`, `/pve퀴즈기록`: Check your own mode-specific best/most recent score (ephemeral)
- `/타르코프퀴즈랭킹초기화` (reset-ranking): **Server admin only.** Deletes all records and rankings for the server (behind a confirmation button, cannot be undone).
  Regular users don't see this command at all.
- `/퀴즈대시보드설치` (install-dashboard): **Server admin only.** Installs or refreshes the public dashboard in the current channel.
- `/감독대시보드설치` (install-supervisor-dashboard): **Server admin only.** Installs or refreshes the supervisor dashboard in the current channel.
- `/대시보드아이콘설치` (install-dashboard-icons): **Server admin only.** Uploads any missing
  dashboard icons as server custom emojis and applies them to both dashboards.
- `/퀴즈봇상태점검` (operations-check): **Server admin only.** Performs a read-only check of
  database integrity/schema, question pools, active sessions, the server's pending spectator-log work,
  quiz/supervisor channel permissions and visibility, dashboard registration, and custom icons.
  Only the invoking admin sees it.
- `/히든상품후보 [기간일]` (hidden-reward-candidates): **Server admin only.** Shows candidates
  for most completions, active days, improvement, underdog, and dual-mode participation in the
  admin review channel (30 days by default, up to 365).

Rankings and personal records are isolated by Discord server and PvP/PvE mode. Records created before
mode separation are preserved under `mode=legacy` and do not appear in the new mode rankings.
On first run against a database created
before per-server isolation existed, old rows aren't deleted — they're automatically migrated into a
legacy area with `guild_id=0`. Since the old database never stored a server ID, those records won't show
up in any server's actual ranking.

Each future completion is also stored in `quiz_attempts` with its score, correct answers, timeouts,
duration, and completion time. The existing leaderboard aggregate remains unchanged.
Improvement, underdog, and active-day candidates therefore start accumulating after this feature is
deployed. Underdog review excludes zero-correct runs and runs where more than half the questions timed
out; candidates are never selected automatically and should be reviewed by an administrator.

## ⚠️ Known limitation: the 15-minute interaction token

Discord won't let a bot edit an ephemeral message on its own once roughly 15 minutes have passed since the
original interaction. Pressing a button creates a fresh interaction, so that's fine — but **if a session
sits idle long enough that timeouts keep stacking up**, message updates can start failing past the
15-minute mark. When that happens the bot auto-cleans the session, so just start over with
`/pvp퀴즈` or `/pve퀴즈`.

## ⚠️ A structural Discord limitation — admin spectating

Discord's ephemeral messages **cannot be seen by anyone but the player themselves — not even admins.**
This is a platform-level restriction; it can't be worked around from the bot's code.

So instead, this bot uses a dedicated **admin-only "spectator log" channel**. When a player starts the quiz,
**one log message per player** is created in that channel, and it's edited every time they answer a question,
showing their answer history, live score, and per-difficulty breakdown (marked 🟢/⚪ when they finish/give up).
**Wrong and timed-out answers are logged together with the choice the player picked, the correct answer, and the explanation**,
so if a player asks "why was that wrong?", an admin can answer immediately just by reading the log.
Messages aren't re-sent per question in order to avoid spamming the channel and hitting Discord's rate
limits when many people are playing at once.
Set a channel ID in `.env`'s `ADMIN_LOG_CHANNEL_ID` to enable this
(configure the channel's permissions so only admins can see it).

## Setup

Python **3.10 or newer** is required. This project uses APIs introduced in discord.py 2.6.

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in DISCORD_TOKEN (required), ADMIN_LOG_CHANNEL_ID, QUIZ_CHANNEL_ID in .env
python bot.py
```

### Discord Developer Portal configuration
- Bot permissions: `applications.commands`, `bot` scope. Auto-pinning dashboards requires
  **Manage Messages**; installing custom icons also requires **Create Expressions** or
  **Manage Emojis and Stickers**.
- Channel permissions: allow "View Channel", "Send Messages", "Read Message History", and "Use Slash Commands" in the quiz channel
- Spectator log channel: grant the bot "Send Messages"; hide the channel from regular users

## File structure

```
tarkov_quiz_bot/
├── bot.py                     # Discord button UI, logging, and commands
├── admin_log.py               # Admin spectator-log creation and batched updates
├── interaction_access.py      # Admin checks and shared interaction errors
├── operations_check.py        # Read-only admin operations status checks
├── quiz_session.py            # Session state and active-session registry
├── quiz_icons.py              # UI icon manifest, hashes, and slot checks
├── dashboard_manager.py       # Dashboard lookup, pinning, and emoji-cache helpers
├── dashboard_icon_installer.py # Icon upload, slot checks, and dashboard refresh
├── dashboard_installation.py  # Manual dashboard install, permissions, and errors
├── quiz_lifecycle.py          # Quiz start, give-up, and session cleanup lifecycle
├── quiz_completion.py         # Question transitions, result storage, and failure cleanup
├── quiz_presenters.py         # Question, submission, and final-result presentation
├── quiz_scoring.py            # Choice mapping, scoring, and timeout state changes
├── quiz_reports.py            # Ranking, statistics, and hidden-reward embeds
├── question_bank.py           # Question loading, format validation, per-difficulty draw
├── config.py                  # Token/channel ID/points/absolute path settings
├── database.py                # SQLite leaderboard
├── questions.json             # Question pool data
├── check_questions.py         # Question stats + patch-volatility check CLI
├── load_test.py               # Isolated synthetic load check for 8,500 users
├── assets/dashboard_icons/    # 21 transparent 128px Discord UI icons
├── tests/
│   ├── test_admin_log.py      # Admin spectator-log and embed-limit tests
│   ├── test_dashboard_icon_installer.py # Icon permission, slot, and partial-failure tests
│   ├── test_dashboard_installation.py # Manual install, permission, and HTTP error tests
│   ├── test_interaction_access.py # Admin access and error-response tests
│   ├── test_load_test.py      # Synthetic-load isolation and aggregation tests
│   ├── test_operations_check.py # DB, channel, and dashboard-status tests
│   ├── test_bot.py            # Discord UI, dashboard, and response-flow tests
│   ├── test_quiz_completion.py # Completion, storage-failure, and cleanup tests
│   ├── test_quiz_lifecycle.py # Start, give-up, and concurrent-session tests
│   ├── test_database.py       # DB migration, ranking, and reward-stat tests
│   ├── test_project_config.py # Dependency consistency and duplicate-CI prevention
│   ├── test_quiz_presenters.py # Quiz presentation and information-hiding tests
│   ├── test_quiz_scoring.py   # Correct, wrong, and timed-out scoring tests
│   └── test_question_bank.py  # Question validation, mode filtering, and draw tests
├── pyproject.toml
├── requirements.txt
├── 봇실행.bat                 # Windows launcher; auto-sets up the virtual environment
├── .env.example
└── README.md
```

`.env`, `.venv`, `__pycache__`, and `quiz_leaderboard.db` are local files created or used at
runtime, so they aren't version-controlled. To keep the database outside of OneDrive sync,
point `.env`'s `QUIZ_DB_PATH` at an absolute path.

## Large-event protection

- SQLite starts in WAL mode with a 30-second busy timeout so result writes and ranking reads are
  much less likely to fail with `database is locked` under bursts.
- SQLite `user_version` tracks the database schema (currently v2). If a database is newer than
  the running bot, startup stops before older code can modify it.
- A ranking index is maintained, and hidden-reward candidates are aggregated as a stream rather
  than loading every attempt into memory at once.
- Admin spectator-log rate-limit waits run in the background, and changes accumulated while waiting
  are coalesced into the latest state. Answers are retained before the message exists, edits are
  batched every five questions by default, and completion or give-up is flushed last.
- Concurrent active sessions are capped at 250 per server by default. Existing quizzes continue;
  only new starts wait until capacity becomes available.
- Concurrent starts by the same user reserve the first session before sending, while failed start
  messages and give-up log errors automatically release the session slot.
- Give-up commands reserve an ephemeral response before supervisor-log work, avoiding Discord's
  three-second response timeout. Sessions with a missing completion/timeout message are aborted
  and released automatically.
- Discord uses the existing root logger instead of adding a duplicate handler. CI runs once for a
  pull request and once again after its merge to `main`.
- Quiz and supervisor dashboard message IDs are stored in SQLite. Even without pin permission or
  after a dashboard leaves the latest 100 messages, startup retrieves it directly instead of
  creating a duplicate.
- Dashboard versions are not shown in the UI. Internal button IDs and legacy v1/v2 footers remain
  recognizable, so older messages are updated in place to a footer-free dashboard.
- `python load_test.py` creates 8,500 users and 25,500 attempts in a temporary database, never the
  operating database. It checks public stats, rankings, reward reports, 200 concurrent reads, 250
  reserved sessions, rejection of the 251st start, and complete session cleanup. Use `--sessions`
  to change the session load.

`MAX_ACTIVE_SESSIONS_PER_GUILD` and `ADMIN_LOG_UPDATE_EVERY` can be adjusted in `.env`. The session
limit is the number of quizzes active at the same instant, not the Discord server's member count.

## Adding/editing questions

Add entries to `questions.json` in the following format.

```json
{
  "id": 31,
  "mode": "common",
  "difficulty": "medium",
  "category": "무기",
  "question": "Question text",
  "choices": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
  "answer": 0,
  "explanation": "Explanation of the correct answer (never shown to players; used in the spectator log's wrong-answer record)"
}
```

`mode` may be `common`, `pvp`, or `pve`; if omitted, it defaults to `common`.
PvP quizzes draw from `common+pvp`, while PvE quizzes draw from `common+pve`.
When a rule differs by profile or season, state the applicable profile, season, or patch in the question.

`difficulty` is one of `general` / `medium` / `hard` / `expert`, and point values are adjusted in
`config.py`'s `POINTS` dictionary.

`category` classifies the question's topic and is one of 12 values: **story · quests · maps ·
bosses/AI · traders · weapons · ammo · gear · medical/food · hideout · skills · systems**
(Korean strings in the data; this has no effect on quiz logic and is for management purposes only).
`python check_questions.py` shows the question count per category, and
`python check_questions.py --category 탄약` (for example) lists questions in a specific category.

After adding or editing questions, run `python check_questions.py` to validate format (4 choices,
answer index, duplicates, category names, etc.). The bot only reads `questions.json` at startup,
so **you need to restart the bot after editing.** The bot runs the same validation on startup and
refuses to run with invalid questions.

## Checks and tests

```bash
python check_questions.py
python load_test.py
python -m unittest discover -s tests -v
python -m py_compile admin_log.py bot.py config.py dashboard_icon_installer.py dashboard_installation.py database.py dashboard_manager.py interaction_access.py operations_check.py question_bank.py quiz_completion.py quiz_icons.py quiz_lifecycle.py quiz_presenters.py quiz_reports.py quiz_scoring.py quiz_session.py check_questions.py load_test.py
ruff check .
```

Pushes and pull requests run the same checks automatically on Python 3.10 and 3.13.

For VS Code, the committed `.vscode/settings.json` selects the project's
`.venv\\Scripts\\python.exe` and configures `unittest` discovery.

On Windows, `봇실행.bat` first runs the Python inside `.venv` to check its state. If the original
Python installation was removed and the virtual environment is broken, it deletes that environment
and rebuilds it with whatever Python is currently installed.

> **Batch file encoding note:** `봇실행.bat` is kept in **CP949 + CRLF** for compatibility with
> `cmd.exe` on Korean Windows. Don't re-save it as UTF-8 or add `chcp 65001` inside it.
> `.gitattributes` is also configured to apply the same encoding when the batch file is checked out.

## 🔁 Managing patch-volatile questions

Questions whose answers can change with game patches — unlock levels, facility stats, quest
requirements — carry a `"volatile": true` flag and a `"volatile_note"` review note (this has no
effect on bot behavior).

When a game patch drops:

1. `python check_questions.py --volatile` — lists volatile questions and their current answers
2. Cross-check against patch notes/wiki and update the `choices` / `answer` / `explanation` of any question whose answer changed
3. Run `python check_questions.py` to validate format, then restart the bot

Tag any newly written question with `volatile` too if its content could be affected by future patches.
Things like boss spawn maps that only change temporarily during events are written against their
standard/permanent placement.

## Notes

Tarkov has kept receiving patches even after its full 1.0 release in late 2025, so questions are built
mostly around structural knowledge that patches rarely touch (factions, hideout concepts, the secure
container, insurance, etc.) and story content. The ammo damage/penetration questions (id 178–201) were
written from the wiki's [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics) table and are
all flagged `volatile` — after a balance patch, check them with `python check_questions.py --volatile`
and update against the wiki table.

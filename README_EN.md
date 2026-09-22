# Tarkov Knowledge Quiz Bot

*[한국어](README.md)*

A Discord quiz bot that tests knowledge of Escape from Tarkov's mechanics, systems, and lore.
It uses a 4-choice button UI, and `questions.json` currently holds **464 questions**.
Four questions are on hold, leaving 460 active questions. Each session randomly draws
**General 2 · Medium 3 · Hard 15 · Expert 10 (30 questions total)** from the active pool per difficulty
and shuffles the answer order too, so the same player sees a different combination every time they play,
and even if questions leak into the community, their usefulness is limited.

The draw counts can be adjusted in `config.py`'s `SESSION_COUNTS` (though you can't set them higher than the size of each difficulty pool).

## Current operating configuration

| Item | Current value |
|---|---|
| Question bank | 464 total — 449 common · 13 PvP-only · 2 PvE-only |
| Question status | 460 active · 4 on hold (Q95, Q102, Q225, Q226) |
| Playable pools | PvP 458 (`common+pvp`) · PvE 447 (`common+pve`) — active questions only |
| Session draw | General 2 · Medium 3 · Hard 15 · Expert 10 = 30 questions |
| Maximum score | 1,380 points |
| Question timer | 20 seconds per question |
| Concurrency guard | 250 active sessions per server by default |
| Discord UI | One player dashboard · one supervisor dashboard · 21 custom icons |
| Slash commands | 8 player commands · 6 administrator commands = 14 total |
| Storage | Per-server, per-mode SQLite aggregates plus completion history, using WAL |

PvP and PvE are **question-pool tags**, not a claim that every game mechanic differs between the
two modes. The thirteen PvP-only questions cover facts that only apply on the PvP side, including Kord
Breach seasonal rules. The two PvE-only questions cover facts whose answers differ in PvE Zone.
Mechanics shared by permanent PvP profiles and PvE, such as insurance, stay in `common`.

## Commands

### All server members

| Command | Visibility | Function |
|---|---|---|
| `/pvp퀴즈` | Private | Start 30 questions from common + PvP-only pools |
| `/pve퀴즈` | Private | Start 30 questions from common + PvE-only pools |
| `/타르코프퀴즈포기` | Private | End the active session without saving it |
| `/pvp퀴즈랭킹` | Public | Server PvP TOP 10 |
| `/pve퀴즈랭킹` | Public | Server PvE TOP 10 |
| `/퀴즈참가현황` | Public | Unique server participants and cumulative completions by mode |
| `/pvp퀴즈기록` | Private | Your PvP best, latest, and cumulative record |
| `/pve퀴즈기록` | Private | Your PvE best, latest, and cumulative record |

Every server member can view rankings and participation totals. Only personal records and active
quiz screens are ephemeral.

### Server administrators

| Command | Function |
|---|---|
| `/퀴즈대시보드설치` | Install or refresh the player dashboard in the current channel |
| `/감독대시보드설치` | Install or refresh the supervisor dashboard in the current channel |
| `/대시보드아이콘설치` | Upload only missing custom icons and refresh both configured dashboards |
| `/퀴즈봇상태점검` | Read-only DB, pool, session, channel, dashboard, and icon health check |
| `/히든상품후보 [기간일]` | Review completion, activity, growth, underdog, and dual-mode candidates in the supervisor channel |
| `/타르코프퀴즈랭킹초기화` | Delete this server's rankings and all attempts after confirmation |

Administrator commands use both Discord default permissions and a runtime administrator check.
Hidden-reward candidates are review material, not automatic winners, and `/히든상품후보` only runs
in the configured supervisor channel.

Resetting rankings deletes **saved results only**, not active sessions. Those sessions can save new
results on completion. Before an event reset, restrict new starts, check the supervisor dashboard
for active sessions, and back up the production database.

## How it works

- The public **player dashboard** provides **Start PvP · Start PvE · Tutorial · mode ranking · personal record** buttons.
  When `QUIZ_CHANNEL_ID` is configured, the bot automatically installs or refreshes it on startup
  (list one channel per server, separated by commas, when running across several servers).
  An administrator can also run `/퀴즈대시보드설치` in a channel; running it again updates
  the dashboard found via its saved message ID, then pins, then the latest 100 messages.
  It attempts to pin the message; missing permissions or an API error can leave it installed but
  unpinned. Its buttons survive restarts.
- A separate **supervisor dashboard** is automatically installed in `ADMIN_LOG_CHANNEL_ID`.
  It provides participation stats, 30-day hidden-reward candidates, active sessions, and PvP/PvE
  rankings. Only server administrators can use its buttons. This setting also accepts a
  comma-separated list; spectator logs and supervisor features use the channel of the server
  the session was started in.
- Both dashboards and quiz notifications support 21 original Tarkov-inspired icons from
  `assets/dashboard_icons/` (ten dashboard icons and eleven notification icons).
  An administrator can run `/대시보드아이콘설치` once to upload only missing custom emojis and
  immediately refresh the configured player and supervisor dashboards. Existing emojis with the
  reserved names are reused, never deleted or overwritten; default Unicode emoji remain as fallback.
- The quiz runs in an ephemeral message visible only to the person who ran the command.
  If several people run the command in the same channel at once, each only sees their own screen — no one sees anyone else's progress.
  Setting a channel ID in `.env`'s `QUIZ_CHANNEL_ID` restricts quiz starts to **that channel only**
  (attempts in other channels are redirected to the channel configured for that server; `0` or unset
  allows all channels). For several servers, write `QUIZ_CHANNEL_ID=111..., 222...`.
  Use one channel per server: a dashboard's location is stored once per (server, kind), so any extra
  channel in the same server is skipped with a warning in the log.
- 20-second time limit per question (adjustable via `config.py`'s `QUESTION_TIME_LIMIT`). Timing out counts as wrong and auto-advances to the next question.
- **The question's difficulty/points, whether the answer was right or wrong, and the correct answer/explanation are never shown to the player.**
  Submitting an answer only shows "Submitted" (or a timeout notice on timeout), and no running score is shown during play.
  Correct/incorrect history and per-difficulty breakdowns are only visible in the admin spectator log.
- When all questions are answered, the final score and correct-answer count are shown, and the record is saved.
- Rankings use best score. Their correct-answer figure is the cumulative total from every completed
  attempt, not the correct count from the best-scoring session alone.

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
**one log message per session** is created in that channel. Each answer is recorded in memory, but
Discord edits are batched every **five questions** by default, so displayed scores and answer history
may lag. A final update is requested on completion or withdrawal. API failures can leave logs incomplete.
**Wrong and timed-out answers are logged together with the choice the player picked, the correct answer, and the explanation**,
so if a player asks "why was that wrong?", an admin can answer immediately just by reading the log.
Messages aren't re-sent per question in order to avoid spamming the channel and hitting Discord's rate
limits when many people are playing at once.
Set a channel ID in `.env`'s `ADMIN_LOG_CHANNEL_ID` to enable this
(configure the channel's permissions so only admins can see it).
For several servers, list one channel per server, separated by commas. In a server with no
configured channel the quiz still runs normally — only the spectator log is skipped.

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
├── guild_channels.py          # Multi-server quiz/supervisor channel lookup and caching
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
│   ├── test_check_questions.py # Held-question CLI, count, and answer-label tests
│   ├── test_quiz_completion.py # Completion, storage-failure, and cleanup tests
│   ├── test_quiz_lifecycle.py # Start, give-up, and concurrent-session tests
│   ├── test_database.py       # DB migration, ranking, and reward-stat tests
│   ├── test_guild_channels.py # Multi-server channel config, lookup, and isolation tests
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

- Transient channel-lookup HTTP failures suppress requests for that channel for 30 seconds;
  the next lookup after that interval retries. Reconnection or a recovered gateway cache clears
  the delay. Forbidden (403) and missing (404) channels remain suppressed until cache recovery
  or reconnection. This recovers subsequent lookups; it does not replay failed spectator logs.
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

`enabled` defaults to `true`. Set `"enabled": false` with a nonempty `disabled_reason` to keep the
original question and ID while excluding it from both playable pools. Use
`python check_questions.py --disabled` to list held questions and reasons. Only JSON booleans are
accepted, not strings such as `"false"` or numbers such as `0`. Held questions are still structurally
validated, but difficulty minimums count active questions only. After obtaining evidence and reviewing
the question, choices, and explanation, set `enabled` to `true` or remove it to restore eligibility.
Dashboard pool totals count active questions, not every archived record in the JSON file.

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

Pushes to `main` and pull-request creation/updates trigger CI on Python 3.10 and 3.13.
A branch push without a PR does not. CI runs each `tests/test_*.py` in a separate process.
Passing checks verify code and data structure, not the factual accuracy of game content.

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

1. `python check_questions.py --volatile` — lists volatile questions, eligibility, and recorded answers
2. Cross-check against patch notes/wiki and update the `choices` / `answer` / `explanation` of any question whose answer changed
3. Run `python check_questions.py` to validate format, then restart the bot

Tag any newly written question with `volatile` too if its content could be affected by future patches.
Things like boss spawn maps that only change temporarily during events are written against their
standard/permanent placement.

**Latest review: 2026-09-22.** Official 1.1.0, 1.1.5.0, and 1.1.5.1 notes, follow-up announcements,
and indexed wiki content were used to correct ambiguous answers, missing exceptions, and conditions.
Six questions (Q459–Q464) were added, and reviews now cover traders, quests, seasons, Hideout, skills,
medical items, gear, and weapons. The gear review corrected Q289's slots-per-kilogram answer and
Q396's Key case efficiency. Weapon reviews separate magazine loading from firing compatibility,
SVT/AVT firing modes, and overheating/swap conditions. A batch reviewed 26 caliber,
classification, and announcement questions and revised 13, resolving Q125's shotgun ambiguity
and distinguishing game models from real-world variants, and announcements from releases.
Eight further weapon questions clarify condition, night vision, recoil, stance, and melee claims.
RPM alone does not establish recoil difficulty, and melee attacks are not promised to be silent.
All 44 medical/provision, 33 gear, and 53 weapon questions have source records, not latest-client verification.
Another 19 ammunition questions distinguish penetration probability/blunt damage and base/actual damage.
Comparisons now specify their choices and projectile scope; numeric checks used indexed wiki copies, not live measurements.
A further 25 ammunition questions had their answers, option values, and explanations cross-checked and scoped.
All 46 ammunition questions now have source records. A further check of Q369 supports Prapor LL1
sales, distinct from unlocking the trader. Prices, purchase limits, and live ammunition values need separate checks.
Another 22 basic-system/season questions clarify LEDX's purpose, faction selection, separate PMC/Scav
characters, and death/MIA protection exceptions. Seasonal rewards mean unlocked trader offers, not transfer of all gear.
Another 35 trader/basic-quest questions clarify Prapor's Tour unlock, Jaeger's Introduction unlock,
loyalty levels versus reputation, and dedicated quest items versus ordinary handover items.
Jaeger's insurance explanation no longer asserts a return time absent from the released patch notes.
A pre-release announcement did mention a couple of hours; this was not an entirely unsupported claim.
Another 11 quest questions were reviewed. Debut now uses its 1.1 target maps without the old MP-133
handover, and the renamed The Tarkov Import includes its required equipment and maps.
The double-barrel requirement for Cultist kills and room 118 key usage were clarified. Conflicting
kill counts, faction-specific Drip-Out counts, and the Prestige event rollback remain unresolved.
Eight event/unlock questions were also updated. Six Blackout questions explicitly ask about July 2026
records, separating direct key use from entering an already-open room. Collector names the seven
LL4 traders and the separate Fence reputation requirement, not a verified complete unlock checklist.
Q410 and Q429
now ask about **historical wiki reports**, not the current presence of a bug; whether those bugs remain
or have been fixed is still unverified. See the [review record](docs/content-review-2026-09-22.md)
for each batch, evidence, and outstanding checks.
Ten boss/AI questions were cross-checked, with content changes to seven. Home territories are
distinguished from exclusive spawn maps, and Kollontay's locations and Big Pipe's equipment are
qualified. Q358 also explicitly covers the historical Blackout event, not current Labs enemies
or the faction's first appearance. Related map questions Q357 and Q359 also cover that historical
event and distinguish emergency access codes from extraction activation.
The remaining 15 boss/AI questions were cross-checked to distinguish regular night Cultists from
Lighthouse guards, in-raid antidotes from other treatment, and possible loot from guaranteed drops.
The Santa question now explicitly covers the 2025 Kolotun event. All 30 boss/AI questions have
source records, but this is not completed live-client validation.
Another 23 hideout/basic-system questions were cross-checked. Hall of Fame bonus conditions,
Class 0 carriers, original maximum armor durability, and edition/faction exceptions were clarified.
All 29 hideout questions now have source records, not completed live-client validation. The minimap
and kill-feed questions remain unverified because direct evidence of the current base-game UI is lacking.
All 42 story questions were cross-checked, with content changes to 28. Release history and faction
voice descriptions were corrected. Individual objectives are distinguished from chapter completion,
ending narratives from route requirements, and wiki speculation from confirmed lore. Source records
for all story questions do not establish live verification of every branch or game mode.
Another 20 map questions were cross-checked, with content changes to 17. Direct Lab access is
distinguished from transit, entry cards from room keys, and silencing announcements from preventing
Raider spawns. Boss lists do not guarantee simultaneous spawns in every raid. Six map time/capacity
questions were subsequently checked against public tables. Base PMC duration is distinguished from
remaining time, and matching caps from actual populations. Q441 and Q446 now belong only to the PvP
pool, not the PvE co-op/AI population context. Conflicting Interchange and night Factory capacity values
remain unresolved. Two minimap/kill-feed and two trader buyback questions still lack reliable current
answer evidence. Q95, Q102, Q225, and Q226 are now on hold; their original text is archived and is not
marked verified. `volatile` remains an advisory flag; only `enabled: false` excludes a question.
Of 464 questions, **290 are `volatile`**; **460 questions have source/date records**.
This is not a claim that all 464 questions were verified in the latest game client.

Edited questions carry paired `reviewed_at` (review date) and `sources` (HTTPS URL list) fields.
Include both when recording future reviews. `--volatile` displays them and validates their format.
The review date is not the source publication date or an in-game measurement date. Corrections based
on older indexed wiki content are identified separately in the review record. FAMAS G2 (Q458) remains
a question about its announcement, not confirmation of release. Pending bug-state and numeric-value
checks are also listed in the review record.

## Notes

Tarkov has kept receiving patches even after its full 1.0 release in late 2025, so questions are built
mostly around structural knowledge that patches rarely touch (factions, hideout concepts, the secure
container, insurance, etc.) and story content. The ammo damage/penetration questions (id 178–201) were
written from the wiki's [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics) table and are
all flagged `volatile` — after a balance patch, check them with `python check_questions.py --volatile`
and update against the wiki table.

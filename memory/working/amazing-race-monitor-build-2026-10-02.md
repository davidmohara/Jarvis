# Amazing Race Channel Monitor — Build Complete (2026-10-02)

Built the `amazing-race-monitor` skill (David-approved plan at `.claude/plans/... joyful-trinket.md`) for the 2026 Amazing Race event (retreat, within days of 2026-10-02).

## What exists now

- `skills/amazing-race-monitor/SKILL.md` (canonical, owner: knox) + `.claude/skills/amazing-race-monitor/SKILL.md` wrapper — sweep orchestration, fork vision-review prompt template, Slack message formats, rulings, rehearsal checklist, event-night runbook
- `skills/amazing-race-monitor/scripts/` — `poll_channel.py` (Graph device-code auth, channel poll, team/quest parsing, media download incl. ffmpeg video frames), `scoring.py` (standings model), `apply_ruling.py` (ok/override/reject), `dashboard_server.py` (live scoreboard at localhost:7430)
- `skills/amazing-race-monitor/references/quests.json` — all 16 quests, points models, verified item lists (from the retreat docx files; no venue claims from memory)
- Registered: `skills/_index.md` (67 skills), `skills/_manifest.jsonl`, `skills/_manifest-knox.jsonl`
- `data/amazing-race/` (gitignored) — working state; fixtures cleaned after offline verification

## Verified offline (fixtures)

Parsing (incl. rejecting bare "T12 Q4" shorthand → flagged unidentified), per-item scoring (3 items × 5 = 15), duplicate/one-post flagging, bonus candidate detection, ruling round-trip (override 20 → standings update), dashboard start/serve/stop.

## NOT done yet — David's steps before the event

1. Entra app registration "Amazing Race Monitor" (delegated: ChannelMessage.Read.All, Files.Read.All, Team.ReadBasic.All, User.Read; public client). Admin consent may be gated → IT handoff path in SKILL.md setup section
2. Fill `data/amazing-race/config.json` from `references/config.example.json` (tenant_id, client_id)
3. `--setup` device-code auth, `--list-teams`/`--list-channels` to resolve the event Photos channel
4. Rehearsal in a test team/channel (checklist in SKILL.md)
5. Event night: dashboard started, sweep every ~4 min

## Live rehearsal — completed 2026-10-02/03 (Test Channel, Company Retreat - 2026 team)

End-to-end verified against real Teams data: poll, photo download (hostedContents + inline `<img>`, deduped), SharePoint video download via sites/driveItem-by-path ("Shared Documents" library prefix stripped), ffmpeg frame extraction, team/quest parsing, vision review via **general-purpose sub-agent with model: sonnet** (NOT a fork — controller model glm-latest rejects image inputs, logged as err-20261003T002601-FMWBIC), scoring (per-item Quest 9 matched a real "Las Vegas's first telephone" plaque photo → 5 pts), live dashboard, Slack flag DM + "Bonus Point Review Candidate" format message (both sent ok; DM read-back blocked by missing im:history scope on the Jarvis bot — send confirmed by API ts).

Real-data bugs found and fixed in rehearsal: (1) inline `<img>` sources weren't downloaded, (2) `unknownFutureValue` system messages were counted as posts, (3) video SharePoint attachment 401/404 → fixed via Graph sites/drive path, (4) duplicate media from hostedContent+inline double-download → sha256 dedupe, (5) offline_access scope missing → no refresh token → silent re-login hang (fixed + Slack-relayed login codes + HTTP timeouts + flushed output).

## Remaining before the event

1. At event start: switch `channel_id` back to the stashed `event_channel_id` (real Amazing Race channel) and clear rehearsal data (`data/amazing-race/posts.jsonl`, `flags.json`, `media/`, `state.json`, `new-items.json`)
2. Set up the event-night sweep runtime (loop/scheduled task every ~4 min, dashboard daemon up, Mac caffeinated)
3. David confirms the flag DM reached his phone (rehearsal test message marked [REHEARSAL TEST])
4. Vision review always runs on a vision-capable model (sonnet), never a fork

## Key design decisions (user-confirmed)

Graph API over MCP connector; poll every few minutes; AI vision on photos + video frames; private to David only (never posts to Teams channel); Quest base points only (Power/Fortune/Dawn bonuses excluded); creative posts → separate Slack messages titled exactly "Bonus Point Review Candidate"; all Slack via master-slack path (`systems/slack-bot/post.py`); team/quest parsed from message text only (roster xlsx explicitly excluded); live dashboard daemon, not static renders; no evolutions pending-changes logging.

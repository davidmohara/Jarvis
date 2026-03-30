# IES Evolution History

This file logs all system evolutions applied to this IES installation. Each entry records what changed, when, and what personal blocks were preserved.

---

## Format

Each evolution entry follows this structure:

```
## Evolution Name (version) — Applied YYYY-MM-DD

**Evolution ID:** unique-id
**Applied:** ISO timestamp
**Snapshot:** snapshot-id
**Applied by:** user or system

### Files Changed
- List of files modified with action types

### Conflicts
- Any conflicts encountered and how resolved

### Personal Blocks Preserved
- Files with personal blocks and where they were preserved

### Status
- Success or warnings/errors
```

---

## Quinn Strategy Builder — Applied 2026-03-01

**Type:** System evolution
**Applied by:** Manual (David + Jarvis session)

### Summary

Added strategy-building capability to Quinn agent. Fills the creation-phase gap in Quinn's portfolio — previously all Quinn tasks (rocks, alignment, initiatives, leadership-prep) were tracking/reviewing. Strategy Builder is the first generative task: coaches users through rigorous strategy development using the kernel methodology (diagnosis → guiding policy → coherent actions).

### Files Changed

- `skills/quinn-strategy/SKILL.md` — added (new skill, 200 lines)
- `skills/quinn-strategy/references/strategy-framework.md` — added (extended reference, 230+ lines)
- `agents/quinn.md` — merged (Strategy Builder added to Capabilities metadata and Task Portfolio in system block; personal blocks preserved)
- `.claude/skills/quinn-strategy/SKILL.md` — added (shared skill registration)

### Conflicts

None.

### Personal Blocks Preserved

- `agents/quinn.md`: All existing personal blocks preserved (tool bindings, quarterly objectives reference)
- `skills/quinn-strategy/SKILL.md`: Personal blocks contain concrete tool bindings only (M365 MCP, Obsidian, OmniFocus, etc.)
- `.claude/skills/quinn-strategy/SKILL.md`: Personal blocks contain concrete tool bindings only

### Source Material

- *Good Strategy Bad Strategy* by Richard Rumelt (PDF summary)
- Lenny's Newsletter podcast episode with Rumelt (1:49:16 transcript)
- Lenny's Newsletter article on Rumelt's strategy framework

### Notes

- Methodology is Rumelt-derived but skill is branded as generic strategy building — not Rumelt-specific
- "Action agenda" framing used throughout instead of "strategy" — per Rumelt's own recommendation
- Future consideration: workflow version combining strategy building with RAPID decision framework

---

## Error Tracking System — Applied 2026-03-15

**Evolution ID:** 5b830712-192d-42f0-bd1e-65c083ad4278
**Type:** System evolution
**Applied:** 2026-03-15T00:00:00Z
**Applied by:** Manual (David + Jarvis session)

### Summary

Silent error and correction tracking system with pattern analysis and tiered fix proposals. Captures explicit corrections from the executive and self-detected errors during agent execution. Logs are invisible during normal operations; patterns surface through existing review cadences (daily count via Chief, full analysis via Quinn weekly review) and proactive threshold alerting (3+ occurrences). Split ownership: Master captures, Rigby analyzes, Chief/Quinn surface.

### Files Changed

- `systems/error-tracking/error-log.json` — added (structured log with entries array and pattern tracking)
- `systems/error-tracking/schema.md` — added (10 error categories, 10 failure modes, 3 severity levels, pattern structure)
- `.claude/skills/rigby-error-analysis/SKILL.md` — added (pattern detection, statistics, tiered fix proposals)
- `agents/master.md` — merged (Error Capture Protocol added to system block; error analysis routing added to Agent Routing table)
- `agents/rigby.md` — merged (Error Analysis added to Task Portfolio, Data Requirements, and Handoff Behavior in system blocks)
- `SYSTEM.md` — merged (Error Accountability expanded with logging step; Error Tracking System reference section added)
- `workflows/daily-review/steps/step-03-update-system.md` — merged (error count added to System State template; error tracking pull step added)
- `.claude/skills/quinn-weekly-review/SKILL.md` — merged (System Improvement Review step added; System Health section added to weekly report)

### Conflicts

None.

### Personal Blocks Preserved

- `agents/master.md`: All existing personal blocks preserved (Jarvis voice overlay, bridge operations, boot/exit additions, output naming, purge patterns)
- `agents/rigby.md`: All existing personal blocks preserved (release watch task, architecture note)
- `.claude/skills/quinn-weekly-review/SKILL.md`: Personal calibration block preserved

### Architecture Decisions

- **Split ownership over new agent**: Master captures because it sees all interactions. Rigby analyzes because it owns system evolution infrastructure. No new agent needed.
- **Tiered fix proposals**: Tier 1 (auto-propose) for clear-cut fixes like repeated tool misuse. Tier 2 (data-only) for ambiguous patterns requiring executive judgment.
- **Threshold alerting at 3**: Balances signal vs. noise. One mistake is a one-off. Two is a coincidence. Three is a pattern.
- **System classification**: Core error categories, failure modes, and analysis logic are framework-agnostic. Any IES instance benefits from self-improvement tracking.

### Notes

- Error log starts empty — entries accumulate as sessions run
- The `quinn-weekly-review` integration is classified as personal (skill is personal) even though the error tracking system itself is system-classified
- Future consideration: training module generation from recurring patterns (Rigby → training system handoff exists but no auto-generation yet)

---

## WHOOP MCP Connector — Applied 2026-03-27

**Evolution ID:** ccf13216-ba05-465c-88bd-b39787b24fcf
**Type:** Personal evolution
**Applied:** 2026-03-27T00:00:00Z
**Applied by:** Manual (David + Jarvis session)

### Summary

Installed community WHOOP MCP server (nissand/whoop-mcp-server-claude) to connect IES to WHOOP fitness data — recovery scores (HRV, resting heart rate), sleep analysis (duration, stages, efficiency), workout strain, and physiological cycles. Uses WHOOP v2 API via OAuth 2.0. 18 tools available. Awaiting OAuth credential registration at developer.whoop.com.

### Files Changed

- `.mcp.json` — added (MCP server config with command, args, env placeholders)
- `reference/whoop-mcp-setup.md` — added (full setup guide with OAuth flow, tool inventory, pagination docs)

### External Dependencies

- `/home/user/mcp-servers/whoop-mcp/` — cloned from github.com/nissand/whoop-mcp-server-claude, built with npm
- WHOOP Developer Portal app registration (pending — Client ID + Secret needed)
- Active WHOOP membership required for API access

### Conflicts

None.

### Personal Blocks Preserved

N/A — all new files.

### Setup Status

| Step | Status |
|------|--------|
| Clone and build MCP server | Done |
| Configure `.mcp.json` | Done (env var placeholders) |
| Register WHOOP developer app | Pending |
| Set OAuth credentials | Pending |
| Complete OAuth flow | Pending |
| Verify data retrieval | Pending |

### Notes

- Server is built and ready at `/home/user/mcp-servers/whoop-mcp/dist/index.js`
- OAuth tokens expire ~1 hour; server supports refresh
- Rate limits: 100 req/min, 10K/day
- Raw/continuous heart rate NOT available via API
- Personal evolution — WHOOP integration is instance-specific, not promotable to system

---

## Cowork Scheduled Tasks — Published 2026-03-28

**Evolution ID:** 294593e2-5ca6-419a-8abe-3e8797d818b9
**DB ID:** cmnapu67100001tptdispl34i
**Type:** System evolution
**Published:** 2026-03-28T00:00:00Z
**Status:** submitted (awaiting admin approval)
**Published by:** Rigby (David + Jarvis session)

### Summary

Replaces session-scoped CronCreate approach with Cowork's native Scheduled Tasks panel. config/scheduled-tasks.json restructured with configured status flags and copy-paste prompts per task. New rigby-scheduled-setup skill presents unconfigured tasks as copy-paste setup cards. chief-morning boot check surfaces a one-line notice when tasks need setup.

### Files Included

- `config/scheduled-tasks.json` — add (Cowork-native config with configured flag, cowork_prompt, schedule_display, keep_awake per task)
- `.claude/skills/rigby-scheduled-setup/SKILL.md` — add (new Rigby skill: surface unconfigured tasks as copy-paste setup cards)

### Notes

- chief-morning boot check is a personal block — configure locally, not included in this evolution
- Status: submitted. Admin approval required before available at poll endpoint.

---

## Jarvis Channel Daemon — Published 2026-03-29

**Evolution ID:** ies-35eb59a2-646a-4aa0-a26f-4f2ef96fbbe1
**Version:** 35eb59a2-646a-4aa0-a26f-4f2ef96fbbe1
**Published:** 2026-03-29T21:45:40Z
**Status:** Submitted (awaiting admin approval)
**Published by:** Rigby (via Evolution Package workflow)

### Summary

New system component: Slack channel polling daemon that monitors #jarvis for messages from David, routes them to a headless Claude Code session (Jarvis master agent with full context via CLAUDE.md bootstrap), and posts responses back via Jarvis bot. Enables asynchronous interaction with Jarvis from Slack when not in an active Code session.

### Files Included

**Added (3 files):**
- `systems/jarvis-channel/jarvis-channel.py` — main daemon script
- `systems/jarvis-channel/install.sh` — setup script with verification
- `systems/jarvis-channel/.gitignore` — excludes runtime state and logs

**Merged (2 files):**
- `config/scheduled-tasks.json` — added jarvis-channel task definition
- `config/.env.example` — documented JARVIS_CHANNEL_ID and JARVIS_USER_ID env vars

### Features

- **Adaptive polling**: 5min idle → 30s-300s active with backoff → 5min after silence
- **Session persistence**: Claude Code session_id stored in data/state.json for conversation continuity across daemon restarts
- **Automatic context compaction**: Sends /compact every 10 turns to prevent context overflow
- **Process cleanup**: Kills stale jarvis-channel.py processes on startup
- **Configurable ownership**: JARVIS_CHANNEL_ID and JARVIS_USER_ID env vars enable repackaging for other IES users
- **Cowork integration**: Scheduled task configuration for Cowork's native Scheduled Tasks panel

### Conflicts

None.

### Architecture Notes

- Daemon runs independently of any active Code session — David's #jarvis messages are routed to headless Claude invocations running in JARVIS_ROOT
- Session bootstrap occurs automatically via CLAUDE.md — no separate context files needed
- Token-based authentication with Anthropic API (ANTHROPIC_API_KEY in config/.env)
- Slack bot posts via systems/slack-bot/post.py using SLACK_BOT_TOKEN
- Extensible polling controller enables future rate-limiting or backpressure strategies

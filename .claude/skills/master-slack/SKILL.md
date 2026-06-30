---
name: master-slack
description: Send a Slack notification to David as the Jarvis bot. Used by any agent or scheduled task that needs to deliver a report, alert, or summary. Posts via Desktop Commander using the Jarvis bot token — separate identity from David, triggers real push notifications.
evolution: system
model: sonnet
---

<!-- system:start -->
## Trigger Phrases

- "send report", "notify David", "post to Slack", "send to #jarvis"
- Automatically invoked at the end of any scheduled task that produces output David needs to see
- Any agent can invoke this skill when it has a deliverable ready

## Prerequisites

- **Desktop Commander MCP** must be available (`mcp__Desktop_Commander__start_process`)
- **Bot script** lives at `systems/slack-bot/post.py` (relative to IES root)

## Locating the Script

The IES folder may live at different paths across David's machines. Use this priority order to locate the script:

**Option 1: Use mdfind (macOS interactive shells)**

```bash
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" <channel_id> "<message>"
```

**Option 2: Find via SYSTEM.md (reliable fallback for scripted/non-interactive environments)**

```bash
IES_ROOT="$(find ~ -name 'SYSTEM.md' -path '*/jarvis/SYSTEM.md' 2>/dev/null | head -1 | sed 's|/SYSTEM.md||')"
python3 "$IES_ROOT/systems/slack-bot/post.py" <channel_id> "<message>"
```

**Option 3: Direct path (if IES_ROOT is known)**

```bash
python3 "$IES_ROOT/systems/slack-bot/post.py" <channel_id> "<message>"
```

Use Option 2 or 3 when executing from scheduled tasks, agents, or non-interactive environments where `mdfind` is unavailable.

## Channels

| Target | Channel ID | When to Use |
|--------|-----------|-------------|
| #jarvis | C0AN2PQNXBR | Default — briefings, reports, scheduled task output, alerts |
| #golf | C0B15SW9FB5 | Golf tee time previews, booking confirmations |
| DM to David | U0ANHV5UXEW | Urgent or private — overdue items, time-sensitive decisions |

## How to Send

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "$IES_ROOT/systems/slack-bot/post.py" <channel_id> "<message>"
Timeout: 15000
```

Where `$IES_ROOT` is found via:
```bash
IES_ROOT="$(find ~ -name 'SYSTEM.md' -path '*/jarvis/SYSTEM.md' 2>/dev/null | head -1 | sed 's|/SYSTEM.md||')"
```

### Example Calls

**Pattern — always use the find-based path lookup:**

```bash
# Set IES_ROOT once, then reuse it
IES_ROOT="$(find ~ -name 'SYSTEM.md' -path '*/jarvis/SYSTEM.md' 2>/dev/null | head -1 | sed 's|/SYSTEM.md||')"

# Post morning briefing summary to #jarvis (multi-line — newlines are real)
python3 "$IES_ROOT/systems/slack-bot/post.py" C0AN2PQNXBR "*Morning Briefing — March 24, 2026*

📅 4 meetings today
⚡ Convergence AI prep (6 days out)
🔴 2 overdue delegations
📥 7 inbox items"

# DM David about an urgent item
python3 "$IES_ROOT/systems/slack-bot/post.py" U0ANHV5UXEW "Integrated Financial Settlements has been unassigned for 35 days post-call. Need an AM decision today."
```

## Message Formatting Rules

1. **Keep it tight.** Headline + 3-5 key bullets max. David should get the picture in 10 seconds.
2. **Use Slack markdown.** `*bold*`, `_italic_`, `~strikethrough~`, `` `code` ``, links.
3. **Structured format for reports:**
   ```
   *[Report Name] — [Date]*

   📅 *Calendar:* [summary]
   ⚡ *Priority:* [top item]
   🔴 *Overdue:* [count and what]
   📥 *Inbox:* [count]

   [Link to full report if applicable]
   ```
4. **Max 5000 chars per message.** Split longer reports into multiple sends.
5. **No fluff.** Don't open with "Hi David" or "Here's your report." Lead with the content.

### ⚠️ Newline Handling (Critical)

**Never use literal `\n` in the message string.** Desktop Commander passes the command to the shell as-is — `\n` stays as a literal two-character sequence and Slack renders it as visible `\n` instead of line breaks.

**Do this — use actual multi-line strings:**
```bash
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0AN2PQNXBR "*Morning Briefing — March 24, 2026*

📅 4 meetings today
⚡ Convergence AI prep (6 days out)
🔴 2 overdue delegations
📥 7 inbox items"
```

**Don't do this — literal `\n` won't render:**
```bash
python3 ... C0AN2PQNXBR "*Morning Briefing*\n\n📅 4 meetings\n⚡ Priority item"
```

The double-quoted multi-line string preserves real newlines through Desktop Commander → shell → Python → Slack API.

## Reading Slack (read.py)

For reading channel history or thread replies, use the companion `systems/slack-bot/read.py` script via Desktop Commander. No Slack MCP connector is used or needed.

```bash
# Find IES_ROOT once
IES_ROOT="$(find ~ -name 'SYSTEM.md' -path '*/jarvis/SYSTEM.md' 2>/dev/null | head -1 | sed 's|/SYSTEM.md||')"

# Read last 24 hours of a channel (returns top-level messages only)
python3 "$IES_ROOT/systems/slack-bot/read.py" channel <channel_id> <hours_ago>

# Read replies in a thread
python3 "$IES_ROOT/systems/slack-bot/read.py" thread <channel_id> <thread_ts>
```

Both return JSON: `{"ok": true, "messages": [...]}` or `{"ok": true, "replies": [...]}`.
Each message includes: `ts`, `user`, `text`, `thread_ts`.

## Critical Rules

- **ALWAYS use post.py for outbound Slack messages.** It posts as Jarvis bot and triggers push notifications.
- **ALWAYS use read.py for reading.** No Slack MCP connector is used or available.
- **#jarvis is the default.** Only DM for urgent/private items.
- **Every scheduled task that produces output should invoke this skill** to notify David the task is complete and deliver the summary.

## Error Handling

If Desktop Commander is unavailable or the script fails:
1. Log the failure — do not silently skip notification
2. Include the report content in the session output so David can still see it
3. Note: "Slack notification failed — Desktop Commander unavailable" so the issue can be diagnosed

### Missing Bot Token — Self-Healing Setup

If the script returns `SLACK_BOT_TOKEN not found` (or `config/.env` doesn't exist), run through setup inline:

1. **Check if `config/.env` exists.** If not, copy from the template:
   ```bash
   cp config/.env.example config/.env
   ```
2. **Ask David for the token:**
   > I need the Slack bot token to send reports as Jarvis.
   > Grab it from: **https://api.slack.com/apps** → Jarvis → OAuth & Permissions → **Bot User OAuth Token** (starts with `xoxb-`).
3. **Write the token** into `config/.env` — replace the placeholder value for `SLACK_BOT_TOKEN`.
4. **Verify** by re-running the send. If it succeeds, continue with the original report. If it fails again, surface the error and stop.

Do NOT skip the notification just because the token is missing — always attempt setup first.

## Agent Usage

Any agent can invoke this skill. Common patterns:

| Agent | When | What to Send |
|-------|------|-------------|
| **Chief** | Morning briefing, daily review | Day summary, overdue flags |
| **Chase** | Pipeline review, lead alerts | Revenue updates, unassigned leads |
| **Quinn** | Weekly review | Week summary, rock progress |
| **Shep** | 1:1 prep complete | Prep brief ready notification |
| **Harper** | Content drafted | Draft ready for review |
| **Rigby** | Evolution deployed, error threshold | System status, fix proposals |

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/master-slack-latest.json
```

Content:
```json
{
  "skill": "master-slack",
  "agent": "master",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
name: master-slack
description: Interact with Slack as the Jarvis bot. Send messages, read David's replies, reply in threads, add reactions, and check for threaded conversations. Posts via Desktop Commander using the Jarvis bot token — separate identity from David, triggers real push notifications. Also reads channel history to pick up David's replies and instructions left in Slack.
evolution: system
---

<!-- system:start -->
## Trigger Phrases

**Sending:** "send report", "notify David", "post to Slack", "send to #jarvis", "message David"
**Reading:** "check Slack", "read #jarvis", "any replies", "what did David say", "check for instructions"
**Threads:** "reply to thread", "follow up in Slack", "react to message"
- Automatically invoked at the end of any scheduled task that produces output David needs to see
- On boot, check #jarvis for any replies from David since last session
- Any agent can invoke this skill when it has a deliverable ready

## Prerequisites

- **Desktop Commander MCP** must be available (`mcp__Desktop_Commander__start_process`)
- **Bot script** lives at `systems/slack-bot/jarvis.py` (relative to IES root)
- Old `post.py` still works for send-only (backward compatible) but `jarvis.py` is preferred

## Locating the Script

The IES folder may live at different paths across David's machines. **Never hardcode the path.** Use Spotlight to find it at runtime:

```bash
JARVIS="$(mdfind -name 'jarvis.py' | grep 'systems/slack-bot/jarvis.py' | head -1)"
```

**Alternative** — find via SYSTEM.md (guaranteed unique marker):

```bash
IES_ROOT="$(mdfind -name 'SYSTEM.md' | grep '/IES/SYSTEM.md' | head -1 | sed 's|/SYSTEM.md||')"
JARVIS="$IES_ROOT/systems/slack-bot/jarvis.py"
```

## Channels

| Target | Channel ID | When to Use |
|--------|-----------|-------------|
| #jarvis | C0AN2PQNXBR | Default — briefings, reports, scheduled task output, alerts, two-way conversation |
| DM to David | U0ANHV5UXEW | Urgent or private — overdue items, time-sensitive decisions |

## Commands

All commands run via Desktop Commander:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "$JARVIS" <command> [args...]
Timeout: 15000
```

### Send a Message

```bash
python3 "$JARVIS" send <channel_id> "<message>"
```

**Examples:**
```bash
# Post morning briefing to #jarvis
python3 "$JARVIS" send C0AN2PQNXBR "*Morning Briefing — March 26, 2026*\n\n📅 4 meetings today\n⚡ Convergence AI prep (4 days out)\n🔴 2 overdue delegations"

# DM David about something urgent
python3 "$JARVIS" send U0ANHV5UXEW "Integrated Financial Settlements unassigned 35 days post-call. Need AM decision today."
```

### Read Messages

```bash
python3 "$JARVIS" read <channel_id> [--limit N] [--since TIMESTAMP] [--from-user USER_ID] [--thread THREAD_TS]
```

**Flags:**
- `--limit N` — Number of messages to fetch (default: 20)
- `--since TIMESTAMP` — Only messages after this Slack timestamp
- `--from-user USER_ID` — Filter to messages from a specific user (or name substring like "David")
- `--thread THREAD_TS` — Read replies in a specific thread

**Examples:**
```bash
# Read last 10 messages from #jarvis
python3 "$JARVIS" read C0AN2PQNXBR --limit 10

# Read only David's messages
python3 "$JARVIS" read C0AN2PQNXBR --from-user David

# Read replies in a specific thread
python3 "$JARVIS" read C0AN2PQNXBR --thread 1711489200.123456
```

**Output format:**
```json
{
  "ok": true,
  "count": 5,
  "messages": [
    {
      "ts": "1711489200.123456",
      "time": "2026-03-26 20:00:00 UTC",
      "sender": "David O'Hara",
      "is_david": true,
      "is_bot": false,
      "text": "Follow up with Stephen tomorrow morning",
      "thread_ts": "",
      "reply_count": 0
    }
  ]
}
```

### Reply in a Thread

```bash
python3 "$JARVIS" reply <channel_id> <thread_ts> "<message>"
```

Use this to respond to David's replies in-thread rather than posting a new top-level message. Keeps conversations organized.

### Add a Reaction

```bash
python3 "$JARVIS" react <channel_id> <timestamp> <emoji_name>
```

**Examples:**
```bash
# Acknowledge David's instruction
python3 "$JARVIS" react C0AN2PQNXBR 1711489200.123456 white_check_mark

# Flag something as in-progress
python3 "$JARVIS" react C0AN2PQNXBR 1711489200.123456 hourglass_flowing_sand
```

### List Threads with Replies

```bash
python3 "$JARVIS" threads <channel_id> [--limit N]
```

Returns recent messages that have thread replies — useful for finding conversations David responded to.

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
6. **Reactions as acknowledgment.** When picking up a David reply, react with ✅ to signal it's been read and acted on.

## Boot Sequence Integration

On every session boot, after reading identity files:

1. **Check #jarvis for David's replies** since the last known timestamp:
   ```bash
   python3 "$JARVIS" read C0AN2PQNXBR --from-user David --limit 10
   ```
2. **Check for threaded conversations** that may have David's instructions:
   ```bash
   python3 "$JARVIS" threads C0AN2PQNXBR --limit 5
   ```
3. **React to any messages picked up** with ✅ to signal receipt.
4. **Surface any instructions** found in David's replies before proceeding with the morning briefing.

## Critical Rules

- **ALWAYS use this skill for outbound Slack messages.** The Slack MCP connector (`mcp__85b26e93-*`) posts as David and does NOT trigger notifications.
- **Use the Slack MCP connector for searching across workspaces** if needed, but prefer `jarvis.py read` for #jarvis channel interactions.
- **#jarvis is the default.** Only DM for urgent/private items.
- **Every scheduled task that produces output should invoke this skill** to notify David the task is complete and deliver the summary.
- **React with ✅ when picking up David's instructions** so he knows the message was received.

## Error Handling

If Desktop Commander is unavailable or the script fails:
1. Log the failure — do not silently skip notification
2. Include the report content in the session output so David can still see it
3. Note: "Slack notification failed — Desktop Commander unavailable" so the issue can be diagnosed

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
| **Any** | Boot sequence | Check for David's Slack replies |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

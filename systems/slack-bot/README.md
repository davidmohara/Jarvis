# Jarvis Slack Bot — Send Report

## Purpose

Send Slack messages as the Jarvis bot (separate identity from David). This triggers real push notifications on David's phone.

## Bot Identity

- **App Name:** Jarvis
- **Bot Token:** stored in `post.py`
- **Workspace:** improvingai.slack.com

## Channels

| Target | ID | Use |
|--------|----|-----|
| #jarvis | C0AN2PQNXBR | Default — briefings, reports, alerts |
| DM to David | U0ANHV5UXEW | Urgent / private notifications |

## How to Send

Use Desktop Commander to run the bot script. **Never hardcode the IES path** — use `mdfind` to locate the script at runtime so it works across all of David's machines:

```
DC: start_process → python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" <channel_id> "<message>"
```

### Examples

```bash
# Post to #jarvis channel
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0AN2PQNXBR "Morning briefing ready."

# DM David directly
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" U0ANHV5UXEW "3 overdue delegations need attention."
```

## Rules

1. **Always use this bot for outbound messages.** The Slack MCP connector posts as David and won't trigger notifications.
2. **Use the Slack MCP connector for reading only** — searching channels, reading messages, pulling context.
3. **#jarvis is the default channel.** Use DMs only for urgent or private items.
4. **Keep messages concise.** Slack markdown supported: *bold*, _italic_, `code`, ~strikethrough~, lists, links.
5. **Max 5000 chars per message.** Split longer reports into multiple messages.

## Formatting Guide

For reports and briefings, use this structure:

```
*Morning Briefing — March 24, 2026*

📅 *Calendar:* 4 meetings today
⚡ *Priority:* Convergence AI prep (6 days out)
🔴 *Overdue:* 2 delegations past due
📥 *Inbox:* 7 items pending triage

Full briefing: [link to file if applicable]
```

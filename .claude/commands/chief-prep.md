---
name: 'chief-prep'
description: 'Calendar prep — pre-brief for upcoming meetings with attendee context and talking points'
---

Read `agents/chief.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/chief.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Calendar Prep

Build pre-briefs for upcoming meetings:

1. **Pull calendar** — get today's (or specified day's) meetings
2. **For each meeting, build a brief:**
   - Attendee bios and context (LinkedIn, CRM, knowledge layer)
   - Account context if client-facing
   - Open items from last meeting with these attendees
   - Suggested objectives and talking points
   - Landmines to avoid
3. **Prioritize** — client meetings and 1:1s get deeper briefs than internal ops meetings

### Handoff Rules
- Client meeting → hand deeper prep to **Chase**
- 1:1 with direct report → hand deeper prep to **Shep**

### Output
One brief per meeting, ordered chronologically. Each brief should be scannable in under 60 seconds.

## Tool Bindings

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Email drafts**: Mac Mail via AppleScript (Bash tool)
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools
- **Delegation tracker**: `delegations/tracker.md`
- **Quarterly objectives**: `context/quarterly-objectives.md`

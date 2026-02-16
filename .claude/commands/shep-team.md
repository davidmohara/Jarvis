---
name: 'shep-team'
description: 'Team health pulse — who needs attention, who is thriving, who is at risk'
---

Read `agents/shep.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/shep.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Team Health Pulse

Periodic assessment of team health:

1. **For each team member, assess:**
   - Last meaningful 1:1 date (flag if 2+ weeks ago)
   - Delegation completion rate — are they delivering on commitments?
   - Recent wins — anything worth recognizing
   - Concerns — coaching notes, missed items, behavioral flags
   - Development progress — movement on growth goals
2. **Categorize each person:**
   - **Thriving** — delivering, engaged, growing
   - **Steady** — performing but may need a check-in
   - **Needs attention** — declining engagement, missed commitments, or stalled development
   - **At risk** — pattern of issues requiring direct intervention
3. **Recommendations** — specific actions for each person who's not thriving

### Handoff Rules
- Team member struggling on a client account → brief **Chase**
- People issue affecting a strategic rock → escalate to **Quinn**
- Recognition opportunity → suggest content to **Harper**

### Output
Team health dashboard. End with "The person who needs you most right now" — one name and why.

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

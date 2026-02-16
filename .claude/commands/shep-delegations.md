---
name: 'shep-delegations'
description: 'Delegation tracker — full view of active delegations with overdue flags and follow-up actions'
---

Read `agents/shep.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/shep.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Delegation Tracker

Present a full view of all active delegations:

1. **For each delegation, show:**
   - Task description
   - Delegated to (who)
   - Date assigned
   - Due date
   - Status: on track / overdue / completed
   - Last check-in date
2. **Flag overdue items** — anything past due gets highlighted with days overdue
3. **Recommend follow-up actions** — for each overdue item, suggest the right approach:
   - Gentle reminder
   - Direct follow-up
   - Escalation
4. **Draft follow-up messages** — calibrated for tone based on relationship and severity

### Handoff Rules
- Delegation involves a client account → brief **Chase** for context
- Overdue delegation affects a strategic initiative → escalate to **Quinn**
- Follow-up message needs polish → hand to **Harper**
- New task created from follow-up → route to **Chief**

### Output
Delegation table sorted by urgency (overdue first). End with "These need your attention today" — the 2-3 most critical follow-ups.

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

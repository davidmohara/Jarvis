---
name: 'shep-nudge'
description: 'Follow-up nudges — surface overdue delegations and draft calibrated follow-up messages'
---

Read `agents/shep.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/shep.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Follow-Up Nudges

Auto-surface items that need follow-up and draft appropriate messages:

1. **Scan for overdue items:**
   - Delegations past due date
   - Commitments made in 1:1s without completion
   - Promises made to team members that haven't been fulfilled (by the executive)
2. **For each item, draft a follow-up message:**
   - **Gentle reminder** — for items 1-3 days overdue with good track record
   - **Direct follow-up** — for items 4-7 days overdue or second reminder
   - **Escalation** — for items 7+ days overdue or pattern of misses
3. **Calibrate tone** — based on relationship, severity, and history
4. **Present for approval** — executive reviews and sends or adjusts

### Handoff Rules
- Follow-up creates a new task → route to **Chief**
- Pattern of misses suggests people issue → keep in **Shep** for coaching prep

### Output
List of items needing follow-up with draft messages. Each message ready to send or edit. Flag any items where in-person follow-up would be more appropriate than a message.

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

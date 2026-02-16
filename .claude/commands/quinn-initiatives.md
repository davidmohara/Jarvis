---
name: 'quinn-initiatives'
description: 'Initiative tracker — living view of strategic initiatives with status, owners, and blockers'
---

Read `agents/quinn.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/quinn.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Initiative Tracker

Present a living view of all strategic initiatives:

1. **For each initiative, show:**
   - Name and description
   - Owner
   - Status: green / yellow / red
   - Next action and due date
   - Blockers (if any)
   - Last update date
2. **Flag stale items** — anything with no update in 2+ weeks
3. **Prompt for updates** — ask about stale items directly
4. **Connect to rocks** — show which rock each initiative serves
5. **Identify orphans** — initiatives not tied to any rock (should they be?)

### Handoff Rules
- Revenue initiative stalled → hand to **Chase**
- People initiative stalled → hand to **Shep**
- Content initiative stalled → hand to **Harper**
- Execution gap on daily tasks → brief **Chief**

### Output
Initiative table sorted by status (red first, then yellow, then green). End with "Initiatives needing a decision" — any that are stuck waiting on the executive.

## Tool Bindings

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools
- **Delegation tracker**: `delegations/tracker.md`
- **Quarterly objectives**: `context/quarterly-objectives.md`

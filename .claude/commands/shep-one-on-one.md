---
name: 'shep-one-on-one'
description: '1:1 prep — build agenda from delegations, last meeting notes, goals, and coaching themes'
---

Read `agents/shep.md` and `workflows/one-on-one-prep/workflow.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/shep.md` (identity, communication style, principles, priority logic, handoff rules)
2. The complete workflow from `workflows/one-on-one-prep/workflow.md` — instruct the sub-agent to read and execute each step file in `workflows/one-on-one-prep/steps/` sequentially
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

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

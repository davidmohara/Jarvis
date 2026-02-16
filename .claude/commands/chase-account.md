---
name: 'chase-account'
description: 'Account strategy — deep-dive on a target account with history, contacts, and recommended playbook'
---

Read `agents/chase.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/chase.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Account Strategy

Build a deep-dive strategy brief for a target account:

1. **Account profile** — company overview, industry, size, tech landscape
2. **Relationship map** — who we know, who we need to know, executive sponsors, blockers
3. **History** — past engagements, revenue, wins/losses, key events
4. **Open opportunities** — current pipeline against this account
5. **Competitive landscape** — who else is in the account, positioning
6. **Recommended playbook** — specific actions to advance the relationship

The user will specify the account by name. If not provided, ask.

### Handoff Rules
- Account strategy needs a presentation → hand to **Harper**
- Account involves team member relationships → coordinate with **Shep**
- Account is tied to a strategic rock → connect with **Quinn**

### Output
Single-page account strategy brief. End with "Here's the play" — 3 specific next actions to advance the account.

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

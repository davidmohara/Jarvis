---
name: 'chase-win-loss'
description: 'Win/loss analysis — post-decision debrief with lessons to apply to active pursuits'
---

Read `agents/chase.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/chase.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Win/Loss Analysis

Conduct a structured post-mortem on a completed deal:

1. **Deal summary** — account, value, timeline, decision makers
2. **Outcome** — win or loss, final decision date, competitor (if loss)
3. **What worked** — tactics, relationships, positioning that contributed to the outcome
4. **What didn't** — gaps, missteps, timing issues, competitive disadvantages
5. **Client feedback** — any direct input from the client on the decision
6. **Lessons for active pursuits** — specific insights to apply to current pipeline

The user will specify the deal. If not provided, ask or surface deals that recently closed without a post-mortem.

### Handoff Rules
- Lessons affect a current strategic rock → brief **Quinn**
- Lessons involve team performance → share with **Shep**
- Insights worth sharing externally → flag for **Harper**

### Output
Structured post-mortem. End with "Apply this now" — 2-3 active deals where these lessons are directly relevant.

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

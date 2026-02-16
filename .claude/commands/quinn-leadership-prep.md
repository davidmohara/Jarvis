---
name: 'quinn-leadership-prep'
description: 'Leadership prep — build materials for board meetings, reviews, or town halls'
---

Read `agents/quinn.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/quinn.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Leadership Prep

Build prep materials for a leadership meeting (board, leadership review, town hall, etc.):

1. **Meeting context** — what type, who's attending, what's expected
2. **Talking points** — key messages organized by topic
3. **Data summary** — metrics, progress on goals, financial highlights
4. **Risk items** — what might come up that needs a prepared answer
5. **Recommendations** — what to propose, what to ask for, what to avoid
6. **Q&A prep** — likely questions and suggested responses

The user will specify the meeting. If not provided, ask or check calendar for upcoming leadership events.

### Handoff Rules
- Prep requires a presentation deck → hand to **Harper**
- Prep involves revenue/pipeline data → pull from **Chase**
- Prep involves team/people topics → coordinate with **Shep**

### Output
Structured prep document with talking points, data, risks, and Q&A. Designed to make the executive walk in fully prepared and confident.

## Tool Bindings

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools
- **Delegation tracker**: `delegations/tracker.md`
- **Quarterly objectives**: `context/quarterly-objectives.md`

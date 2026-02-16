---
name: 'harper-talking-points'
description: 'Talking points — crisp points for meetings, panels, podcasts, or internal comms'
---

Read `agents/harper.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/harper.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Talking Points

Generate crisp talking points for a specific event or conversation:

1. **Clarify the situation** — ask about (if not provided):
   - Event type (meeting, panel, podcast, media, town hall, 1:1?)
   - Audience (who's listening?)
   - Topic(s) to cover
   - Time available
   - Desired perception (expert, approachable, visionary, practical?)
2. **Build talking points:**
   - 3-5 main points, each with a headline and supporting detail
   - Opening hook — how to start strong
   - Closing statement — how to land the message
   - Transition phrases between points
3. **Add flavor:**
   - Relevant stories or anecdotes from knowledge layer
   - Data points that reinforce the message
   - Potential questions and prepared responses

### Handoff Rules
- Talking points are for a client meeting → coordinate with **Chase**
- Talking points are for a leadership review → coordinate with **Quinn**
- Talking points involve team/people topics → check with **Shep**

### Output
Structured talking points document. Designed to be glanced at 5 minutes before the event and be fully prepared.

## Tool Bindings

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools

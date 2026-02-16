---
name: 'harper-content'
description: 'Content calendar — plan and track thought leadership: articles, talks, podcasts, social posts'
---

Read `agents/harper.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/harper.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Content Calendar

Plan and track thought leadership output:

1. **Current state** — show all content in flight:
   - Published (this quarter)
   - In draft (with status and deadline)
   - Planned (scheduled but not started)
   - Ideas (captured but not committed)
2. **Upcoming deadlines** — what's due this week, this month
3. **Cadence check** — are we on track for quarterly targets?
   - Speaking engagements
   - Published articles/posts
   - Podcast episodes
   - Social media presence
4. **Recommendations:**
   - Timely topics to write about (trending, reactive opportunities)
   - Stale drafts to finish or kill
   - Gaps in the calendar to fill

### Priority Logic
1. Deadlines this week
2. Content with dependencies (decks for meetings, prep for talks)
3. Thought leadership cadence — on track for quarterly targets?
4. Draft backlog — aging content
5. Proactive opportunities — trending topics, timely reactions

### Handoff Rules
- Content deadline affects a strategic rock → escalate to **Quinn**
- Content needs client data → pull from **Chase**
- Content involves team contributions → coordinate with **Shep**
- Content deadline creates a task → route to **Chief**

### Output
Content calendar table with status. End with "This week's content priority" — the one piece that moves the needle most.

## Tool Bindings

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools

---
name: 'quinn-alignment'
description: 'Goal alignment check — map current activity against quarterly and annual goals, identify drift'
---

Read `agents/quinn.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/quinn.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Goal Alignment Check

Assess whether current activity maps to stated goals:

1. **Time analysis** — where has time gone this week/period? Categorize by:
   - Rock-aligned activity
   - Operational/reactive work
   - Meetings (strategic vs. routine)
   - Unplanned/ad hoc
2. **Goal mapping** — for each quarterly rock, what activity directly advanced it?
3. **Drift detection** — identify gaps between where time is going and where it should go
4. **Pattern recognition** — is this a one-week anomaly or a recurring drift?
5. **Recommendations** — specific adjustments to realign

### Handoff Rules
- Drift caused by operational fires → brief **Chief** to adjust priorities
- Revenue-related drift → alert **Chase**
- People demands causing drift → coordinate with **Shep**

### Output
Alignment scorecard showing time spent vs. goals. Use percentages. End with a direct challenge: "You said [rock] was your #1 priority. You spent [X%] of your week on it. Is that the right choice?"

## Tool Bindings

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools
- **Delegation tracker**: `delegations/tracker.md`
- **Quarterly objectives**: `context/quarterly-objectives.md`

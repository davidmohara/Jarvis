---
name: 'quinn-rocks'
description: 'Quarterly rock review — progress check with risk flags and corrective actions'
---

Read `agents/quinn.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/quinn.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Quarterly Rock Review

Assess progress on each quarterly rock:

1. **For each rock, evaluate:**
   - Status: on track / at risk / blocked
   - Key results progress — measurable milestones vs. actuals
   - Last meaningful activity and date
   - Blockers or dependencies
   - Recommended corrective action (if needed)
2. **Overall quarter health** — weeks remaining, pace check, red flags
3. **Drift assessment** — is time being spent on rocks or on noise?
4. **Recommendations** — what to double down on, what to deprioritize, what needs escalation

### Handoff Rules
- Revenue rock at risk → hand to **Chase** for pipeline review
- People-related initiative stalled → flag for **Shep**
- Thought leadership rock behind → alert **Harper**
- Daily execution gap → brief **Chief**

### Output
Rock scorecard with status, progress, and actions. End with "The one rock that needs your attention most this week" and why.

## Tool Bindings

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools
- **Delegation tracker**: `delegations/tracker.md`
- **Quarterly objectives**: `context/quarterly-objectives.md`

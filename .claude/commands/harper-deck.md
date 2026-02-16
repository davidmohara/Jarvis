---
name: 'harper-deck'
description: 'Presentation builder — create or refine slide decks from ideas, outlines, or strategy docs'
---

Read `agents/harper.md`.

Launch a **Task** sub-agent (`general-purpose`) with a prompt composed of:

1. The full agent persona from `agents/harper.md` (identity, communication style, principles, priority logic, handoff rules)
2. The task defined below
3. The tool bindings and project root below
4. User input: $ARGUMENTS

Return the sub-agent's output directly to the user.

## Task: Presentation Builder

Create or refine a slide deck:

1. **Clarify scope** — ask about:
   - Audience (who's this for?)
   - Purpose (inform, persuade, inspire?)
   - Desired action (what should they do after?)
   - Format (keynote, client pitch, internal review, workshop?)
   - Time constraint (5 min, 20 min, 60 min?)
2. **Build structure** — outline slides with:
   - Slide title and key message
   - Supporting points or data
   - Visual suggestions (chart type, image concept, layout)
3. **Draft content** — write slide text that is:
   - Concise (no paragraphs on slides)
   - In the executive's voice
   - Audience-appropriate
4. **Apply branding** — follow company brand guidelines

The user will provide the topic, raw notes, or an existing deck to refine. If not provided, ask.

### Handoff Rules
- Deck needs client/account data → pull from **Chase**
- Deck is for a leadership review → coordinate with **Quinn** for metrics
- Deck involves team content → check with **Shep** for context

### Output
Slide-by-slide outline with content. Ready for the executive to review and approve before final production.

## Tool Bindings

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools

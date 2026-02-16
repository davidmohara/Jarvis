---
name: morning-briefing
description: Start-of-day briefing - calendar, priorities, delegations, meeting context, and what needs attention today
agent: chief
---

# Morning Briefing Workflow

**Goal:** Give the controller complete situational awareness for the day ahead in under 2 minutes of reading.

**Agent:** Chief — Daily Operations & Execution

**Architecture:** Sequential 4-step workflow. Each step gathers data from a different source, then the final step synthesizes into a single briefing. No user interaction required until the briefing is delivered.

---

## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Identity files | Current rocks, responsibilities, key people | Read identity layer files |
| Calendar | Today's meetings with attendees, times, locations | M365 MCP |
| Task management | Inbox count, due today, flagged items | Task management API |
| Delegation tracker | Overdue items, items due today | Read delegations/tracker.md |
| Knowledge layer | Recent meeting notes, previous daily review | Knowledge base API |

### Paths

- `identity_path` = `{project-root}/identity/`
- `delegation_tracker` = `{project-root}/delegations/tracker.md`
- `quarterly_objectives` = `{project-root}/context/quarterly-objectives.md`

---

## EXECUTION

Read fully and follow: `steps/step-01-gather-calendar.md` to begin the workflow.

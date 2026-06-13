---
name: calendar-prep
description: Build meeting pre-briefs with attendee context, account history, and talking points
agent: chief
model: sonnet
---

<!-- system:start -->
# Calendar Prep Workflow

**Goal:** Build a scannable pre-brief for each upcoming meeting. Every brief covers attendee context from the knowledge layer, account or team history, suggested objectives and talking points, and any open items with the attendees.

**Agent:** Chief — Daily Operations & Execution

**Architecture:** Sequential enrichment workflow. Pull meetings, enrich each with knowledge layer context, deliver ordered briefs. Trigger Chase handoff for any client or prospect meetings.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Calendar | Upcoming meetings — attendees, subject, time, location | M365 / Google Calendar MCP |
| Knowledge layer | Attendee relationship history, past meeting notes, open items | Read knowledge layer |
| Task management | Open delegations and commitments with attendees | Task management API |

### Meeting Categories

| Type | Characteristics | Special Handling |
|------|----------------|-----------------|
| **Client** | External — paying account | Chase domain for account history; trigger Chase handoff |
| **Prospect** | External — sales opportunity | Chase domain for pipeline context; trigger Chase handoff |
| **Partner** | External — vendor/partner org | Chase domain for relationship history |
| **1:1 (direct report)** | Internal — manager-to-report | Shep domain for delegation and performance context |
| **Internal ops** | Internal — team meeting, all-hands | Shep domain for team context |
| **Leadership** | Internal — exec team, board | Standard brief; no domain handoff required |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-pull-meetings.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
name: one-on-one-prep
description: Build a comprehensive prep brief for an internal 1:1 meeting from email, calendar, Teams, tasks, and previous briefs
agent: shep
---

<!-- system:start -->
# One-on-One Prep Workflow

**Goal:** Produce a prep brief the controller can scan 5 minutes before a 1:1 and walk in fully prepared. Every talking point backed by real data from the last 2 weeks.

**Agent:** Shep — People & Delegation

**Architecture:** Sequential 5-step workflow. Data-intensive. Steps 1-3 gather from different sources, step 4 assembles the brief, step 5 quality-checks and saves. Minimal user interaction until the brief is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Required Input

- **Who**: Name of the person for the 1:1
- **When**: Date and time of the meeting (if known, otherwise find it on calendar)

### Data Sources Required

| Source | What to Pull | Lookback | Access Method |
|--------|-------------|----------|---------------|
| Email | Direct exchanges, forwarded items, action requests | 2 weeks | M365 MCP |
| Calendar | Shared meetings, upcoming events involving both | 2 weeks back + 2 weeks forward | M365 MCP |
| Teams | Chat threads, channel mentions | 2 weeks | M365 MCP |
| Task management | Tasks tagged with person, delegated items | Current | Task management API |
| Knowledge layer | Person files, project notes, previous prep briefs | Most recent | Knowledge base API |
| Delegation tracker | Items delegated to/from this person | Current | Read delegations/tracker.md |

### Excluded Meetings (noise for 1:1 prep)

These types of recurring meetings should always be filtered out of the calendar data (specific names defined in the controller's preferences):
- All-hands / townhalls
- Sales standups
- Recurring standups
- Daily standup equivalents

### Output

- Prep brief saved to knowledge layer: `working directory/{Person Name} - {YYYY-MM-DD}.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-identify-meeting.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

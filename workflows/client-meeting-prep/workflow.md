---
name: client-meeting-prep
description: Client/prospect meeting prep - attendee research, account context, opportunity status, talking points, landmines
agent: chase
---

<!-- system:start -->
# Client Meeting Prep Workflow

**Goal:** Walk into every client meeting knowing more about their business than they expect. No surprises. No "remind me what we talked about last time."

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Sequential 4-step workflow. Identify the meeting and attendees, pull account context from CRM, research externally, assemble the brief. No user interaction required until the brief is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Calendar | Meeting details, attendees, time, location, purpose | M365 MCP |
| CRM (CRM) | Account history, open opportunities, contact records, engagement history | CRM via Chrome/M365 auth |
| Web | LinkedIn profiles, company news, financials, tech stack | Web search / ZoomInfo |
| Knowledge layer | Past meeting notes, relationship history, prep docs | Knowledge base API |
| M365 (Email/Teams) | Recent email and Teams threads with attendees | M365 MCP |

### Paths

- `quarterly_objectives` = `{project-root}/context/quarterly-objectives.md`
- `delegation_tracker` = `{project-root}/delegations/tracker.md`

### Input

This workflow requires a meeting identifier to begin. One of:
- A specific calendar event (date + subject or attendee name)
- An account name with a known upcoming meeting
- A direct request: "Prep me for [meeting/client]"

If triggered from the pipeline-review workflow, the meeting will be pre-identified.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-meeting-details.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

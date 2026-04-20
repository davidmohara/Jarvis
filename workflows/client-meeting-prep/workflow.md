---
name: client-meeting-prep
description: Client/prospect meeting prep - attendee research, account context, opportunity status, talking points, landmines
agent: chase
model: sonnet
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

- `quarterly_objectives` = `{project-root}/memory/personal/quarterly-objectives.md`
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
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-meeting-details.md` to begin the workflow.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

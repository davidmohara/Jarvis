---
name: morning-briefing
description: Start-of-day briefing - calendar, priorities, delegations, meeting context, and what needs attention today
agent: chief
model: sonnet
---

<!-- system:start -->
# Morning Briefing Workflow

**Goal:** Give the controller complete situational awareness for the day ahead in under 2 minutes of reading.

**Agent:** Chief — Daily Operations & Execution

**Architecture:** Sequential 4-step workflow. Each step gathers data from a different source, then the final step synthesizes into a single briefing. No user interaction required until the briefing is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
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
- `quarterly_objectives` = `{project-root}/memory/personal/quarterly-objectives.md`
<!-- system:end -->

<!-- personal:start -->
### Additional Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Clay | Upcoming reminders (next 7 days), upcoming birthdays, attendee relationship context | Clay MCP (mcp__clay__*) |
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

Read fully and follow: `steps/step-01-gather-calendar.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

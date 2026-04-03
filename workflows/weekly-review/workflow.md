---
name: weekly-review
description: Weekly review - rocks, delegations, inbox health, calendar audit, people check, next week priorities
agent: master
orchestrates: [chief, chase, quinn, shep]
---

<!-- system:start -->
# Weekly Review Workflow

**Goal:** The most important cadence. Review everything that matters, surface what's drifting, and set next week up for execution. This is where the execution gap gets closed.

**Agent:** Master agent (orchestrates sub-agents as needed)

**Architecture:** Sequential 6-step workflow. Each step reviews a different domain. The master agent drives, pulling in sub-agents when their domain expertise is needed. Interactive throughout - the controller walks through each section.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Quarterly objectives | Rock status and progress | Read context/quarterly-objectives.md |
| Delegation tracker | All active delegations, overdue items | Read delegations/tracker.md |
| Task management | Inbox count, flagged items, items > 7 days old | Task management API |
| Calendar | This week's meetings (what happened), next week's meetings (what's coming) | M365 MCP |
| Daily reviews | This week's daily review files | Read reviews/daily/ |
| Knowledge layer | Recent meeting notes, decisions made this week | Knowledge base API |

### Output

- Weekly review file: `reviews/weekly/YYYY-Wxx.md`

### Agent Routing

| Step | Domain | Sub-Agent |
|------|--------|-----------|
| Wins and misses | Operations | Master (interactive) |
| Rocks review | Strategy | Quinn |
| Delegation review | People | Shep |
| Inbox and calendar | Operations | Chief |
| People check | People | Shep |
| Set priorities | Strategy | Quinn |
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

Read fully and follow: `steps/step-01-wins-and-misses.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

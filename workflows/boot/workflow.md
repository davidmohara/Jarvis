---
name: boot
description: Full session boot sequence — context load, data gather, verification, briefing, and workflow scan
agent: master
model: sonnet
---

<!-- system:start -->
# Boot Workflow

**Goal:** Establish complete situational awareness at the start of every session. Load identity context, gather live data from all sources in parallel, verify completion, synthesize the briefing, and surface any in-flight workflows.

**Agent:** Master — Orchestrator & Executive Operating System

**Architecture:** Sequential 6-step workflow. Steps 1 and 2 are data-gathering phases. Step 3 verifies Step 2 via Ralph. Steps 4 and 5 complete the briefing. Step 6 scans in-flight workflows and concludes boot.

---

## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| SYSTEM.md | Full operating manual, file map, conventions | Read file |
| identity/MEMORY.md | Controller profile, context, history | Read file |
| identity/VOICE.md | Personality and communication config | Read file |
| identity/GOALS_AND_DREAMS.md | Vision, long-term objectives | Read file |
| identity/RESPONSIBILITIES.md | Role, accountabilities, key people | Read file |
| identity/AUTOMATION.md | Standing permissions, trust tiers | Read file |
| identity/MISSION_CONTROL.md | Mission context, strategic framing | Read file |
| workflows/morning-briefing/workflow.md | Steps 01-02 (calendar + tasks) | Run sub-steps |
| workflows/plaud-ingest/workflow.md | Plaud transcript ingestion | Spawn Knox (fire-and-forget) |
| workflows/lead-review/workflow.md | Unassigned lead scan | Run workflow |
| M365 Calendar | Next 3 days of events | M365 MCP (outlook_calendar_search) |
| M365 Email | Flagged and time-sensitive messages only | M365 MCP (outlook_email_search) |
| skills/jarvis-inbox/SKILL.md | /Jarvis email folder triage | Run skill |
| Clay | Reminders and birthdays (next 7 days) | Clay MCP |
| workflows/*/state.yaml | All workflow state files | Read all |

### Paths

- `identity_path` = `{project-root}/identity/`
- `workflows_path` = `{project-root}/workflows/`
- `morning_briefing` = `{project-root}/workflows/morning-briefing/`
- `boot_verification` = `{project-root}/workflows/boot-verification/workflow.md`

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Master]: Resuming boot from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Master]: Boot was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-load-context.md` to begin the workflow.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

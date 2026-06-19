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

**Architecture:** Sequential 7-step workflow. Steps 1 and 2 are data-gathering phases. Step 3 verifies Step 2 via Ralph. Steps 4 and 5 complete the briefing. Step 6 scans in-flight workflows. Step 7 is a hard gate — verifies all prior steps completed before marking boot complete.

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

Steps execute in order. Each step's NEXT STEP section chains to the following step.

1. `steps/step-01-load-context.md`
2. `steps/step-02-gather-data.md`
3. `steps/step-03-verify-phase2.md`
4. `steps/step-04-gather-meeting-context.md`
5. `steps/step-05-synthesize-briefing.md`
6. `steps/step-06-scan-workflows.md`
7. `steps/step-07-verify-completion.md` ← hard gate; boot is NOT complete until this passes

Read fully and follow: `steps/step-01-load-context.md` to begin the workflow.

<!-- system:end -->

<!-- personal:start -->
## Session Index Boot

After reading identity files but before any other operations in step-01:
- If `memory/sessions/index.json` does not exist, create it as an empty JSON array: `[]`
- Generate session ID: `session-{YYYY-MM-DD}-{HHMMSS}` using the current local timestamp
- Append a new session record with: `started` = ISO 8601 timestamp, `closed` = null, `current_topic` = null, `topics` = []
- This record is the active session for the entire conversation. The PostToolUse hook will write file captures to it.
<!-- personal:end -->

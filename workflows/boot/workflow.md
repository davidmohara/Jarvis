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

### Execution Groups (Stage 4 Architecture)

Steps execute in groups with per-step token extraction and guardrail validation at boundaries.

| Group | Steps | Parallel | Guardrail | Notes |
|-------|-------|----------|-----------|-------|
| 1 | step-01 | No | step-01-checkpoint | Context loading |
| 2 | step-01.5 | No | step-01.5-checkpoint | Calendar consolidation |
| 3 | step-02 | No | step-02-checkpoint | Data gathering |
| 4 | step-03 | No | step-03-checkpoint | Phase 2 verification |
| 5 | step-04 | No | step-04-checkpoint | Meeting context |
| 6 | step-05 | No | step-05-checkpoint | Briefing synthesis |
| 7 | step-06 | No | step-06-checkpoint | Workflow scan |
| 8 | step-06.5 | No | step-06.5-checkpoint | Content review (pre-completion) |
| 9 | step-07 | No | step-07-checkpoint | Completion verification |

**Per-step token extraction:** step-complete.py hook fires after each step, extracting real tokens for that step's time window from transcript.

**Guardrail evaluation:** Each group has an optional guardrail checkpoint. If result='escalate', workflow halts and punches out to controller. Only critical issues escalate (missing timestamps, failed assertions). Warnings are flagged but continue.

**Punch-out signal:** If guardrail escalates, eval record gets punch_out_signal with step name, reason, and awaiting_controller_decision flag. Workflow does not continue until controller reviews and approves in eval record.

### Paths

- `identity_path` = `{project-root}/identity/`
- `workflows_path` = `{project-root}/workflows/`
- `morning_briefing` = `{project-root}/workflows/morning-briefing/`
- `boot_verification` = `{project-root}/workflows/boot-verification/workflow.md`

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - **Staleness check first.** Compare `session-started` to the current time. If it is more than 4 hours old, this is not a resumable interruption — it's a prior run that never reached step-07's completion gate (crashed, was aborted without updating status, or the session simply ended). Treat it the same as case 4 (aborted): do NOT auto-resume. Notify the controller: "[Master]: Boot has been stuck at `in-progress` since [session-started] ([current-step]) — treating as stale, not resuming. Starting fresh." Then proceed to case 3 (fresh run) instead of resuming. This also matters for the eval harness: a boot that never reaches `status: complete` never gets an eval record, and blocks the Session Index Boot step (below) from running on every subsequent boot in the meantime — see `err-` entries referencing this if it recurs.
   - Otherwise (genuinely recent — within the 4-hour window): You are resuming a previous run. Do NOT start over.
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

**Phase 0: Context Load**
1. `steps/step-01-load-context.md`

**Phase 1: Unified Data Pull** ← **NEW CONSOLIDATION PHASE**
1.2. `steps/step-01.2-unified-data-pull.md` ← Pulls ALL external data (email, tasks, reminders, inbox) in parallel, writes to disk
1.5. `steps/step-01.5-unified-calendar-pull.md` ← Calendar consolidation (single M365 call)

**Phase 2: Data Verification & Measurement**
2. `steps/step-02-gather-data.md`
2.5. `steps/step-02.5-measure-phase2.md` ← Measures context (should show minimal bloat now)

**Phase 3-7: Processing**
3. `steps/step-03-verify-phase2.md`
4. `steps/step-04-gather-meeting-context.md`
5. `steps/step-05-synthesize-briefing.md`
6. `steps/step-06-scan-workflows.md`
6.5. `steps/step-06.5-guardrail-checkpoint.md` ← automated content-quality review before the completion gate
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

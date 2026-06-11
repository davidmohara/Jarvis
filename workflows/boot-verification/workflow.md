---
name: boot-verification
description: Post-Phase-2 boot verification pass. Spawns Ralph with the Phase 2 task manifest and waits for his verdict before Phase 3 proceeds.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Boot Verification Workflow

**Goal:** Confirm that every Phase 2 boot task was genuinely executed — not just claimed. Ralph receives the manifest, checks evidence, returns a verdict table. Master acts on the results.

**Agent:** Ralph — Verification Agent

**Architecture:** Sequential 2-step workflow. Step 01 builds the manifest from the Phase 2 completion report. Step 02 spawns Ralph, receives his verdict, and surfaces any re-run requirements to Master.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Phase 2 completion report | Claimed status of each Phase 2 task | Passed from Master as accumulated-context |
| Workflow state files | `state.yaml` for each Phase 2 workflow | File system read |
| Eval harness skill runs | `systems/eval-harness/skill-runs/` per-skill records | File system read |
| Working memory | `memory/working/` entries from today | File system read |

### Paths

- `morning_briefing_state` = `workflows/morning-briefing/state.yaml`
- `plaud_ingest_state` = `workflows/plaud-ingest/state.yaml`
- `lead_review_state` = `workflows/lead-review/state.yaml`
- `jarvis_inbox_run` = `systems/eval-harness/skill-runs/jarvis-inbox-latest.json`
- `working_memory_dir` = `memory/working/`
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
   - Load `accumulated-context` — this is data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify: "[Boot Verification]: Resuming from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to Master:
     "[Boot Verification]: Workflow was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-build-manifest.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

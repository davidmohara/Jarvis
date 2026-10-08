---
name: daily-review
description: End-of-day shutdown - capture completions, carry-forwards, and tomorrow's priorities
agent: chief
model: sonnet
cost_tracking: required
cost_tracking_note: "Eval harness must capture total_cost_usd via eval-agent-stop.py hook (subagent transcript path required). See systems/eval-harness/schema.md for audit-trail requirements. Backfill script at systems/eval-harness/backfill-daily-review-costs.py for historical records."
---

<!-- system:start -->
# Daily Review Workflow

**Goal:** Close the day with accountability. Capture what happened, surface what didn't, and set tomorrow's priorities so the morning briefing has something to work with.

**Agent:** Chief — Daily Operations & Execution

**Architecture:** Two modes. Interactive (default): Chief guides the controller through a structured shutdown, then updates system files. Auto (pass `auto` as argument): fully autonomous, no user interaction — synthesizes from data sources and writes narrative to the knowledge system only.

**Dispatch model:** This workflow runs as a **Chief** subagent spawned by the coordinator, never inline in the coordinator's session. Chief executes the steps below; the root audit hands off to Rigby and the git commit routes to Rigby via `skills/git/SKILL.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Task management | Tasks completed today, tasks created today, inbox state | Task management API |
| Calendar | What meetings happened today | M365 MCP |
| Delegation tracker | Any delegations completed or created today | Read delegations/tracker.md |
| Quarterly objectives | Current rocks for alignment check | Read memory/personal/quarterly-objectives.md |

### Paths

- `delegation_tracker` = `{project-root}/delegations/tracker.md`
- `quarterly_objectives` = `{project-root}/memory/personal/quarterly-objectives.md`
- `daily_review_output` = `{project-root}/reviews/daily/YYYY-MM-DD.md`
- `daily_review_template` = `{project-root}/reviews/daily/_template.md`
- `morning_briefing` = `{project-root}/reviews/daily/YYYY-MM-DD.md` (if exists, for cross-check)

### Output

- Interactive mode: daily review file (`reviews/daily/YYYY-MM-DD.md`) + knowledge system narrative + updated delegation tracker
- Auto mode: knowledge system narrative only (no local filesystem write, no delegation updates)
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

Check `$ARGUMENTS` for the word `auto` (case-insensitive).

- If `auto` is present: read fully and follow `steps/step-auto.md`. Do not load any other step files.
- Otherwise: read fully and follow `steps/step-01-capture.md` to begin the interactive workflow.
- After step-03, run `steps/step-03b-guardrail-checkpoint.md` — an automated review gate before anything is committed. `escalate` halts the workflow for a controller decision; `pass`/`flag` continue.
- Then run `steps/step-03c-adversarial-verify.md`, which spawns **Ralph** with `workflows/daily-review-verification/workflow.md` (the output-vs-source-data and completion-vs-state lens). Ralph re-derives every completion claim from recorded state and returns a verdict table; the result is recorded as an `adversarial-verification` guardrail checkpoint. This runs before the commit, so a finding can still be acted on.
- After step-04, proceed to `steps/step-05-session-close.md` to finalize the session and commit all changes.

**Deterministic step guardrails:** Every step transition is machine-checked. The verifiers in `workflows/daily-review/verify/` run at each step's completion (dispatched by `.claude/hooks/step-complete.py`) and record a pass/retry/fail verdict with derived fields on the run's eval record. Manual review is not the gate.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

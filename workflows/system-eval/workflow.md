---
name: system-eval
description: Full eval maintenance cycle — grade ungraded records, run assertions, compute composite scores, analyze patterns, regenerate the dashboard. Closes the eval feedback loop automatically so every workflow and skill run has complete 4-tier coverage.
agent: rigby
model: sonnet
---

<!-- system:start -->
# System Eval Workflow

**Goal:** Ensure every eval record has complete 4-tier assessment coverage and the dashboard reflects current reality. Rigby runs this end-to-end: grade what's ungraded, check structural assertions on partial records, compute composite scores, analyze patterns across the full corpus, and regenerate the dashboard.

**Agent:** Rigby — System Operator

**Architecture:** Four sequential steps. No controller approval gate — this workflow is fully autonomous. Designed to run on a schedule or on demand.

**When to run:**
- On a schedule (daily or after a batch of workflow runs)
- On demand: "run system eval", "update eval dashboard", "grade the evals"
- After any significant workflow run that produced new eval records

**When NOT to run:**
- If `status: in-progress` in state.yaml — resume, don't restart
- During active sessions where workflows are still producing eval records (wait for session close)

---

## INITIALIZATION

### Data Sources Required

| Source | Tool/Path | Purpose |
|--------|-----------|---------|
| Eval records | `systems/eval-harness/runs/*.json` | Source of truth for all workflow/skill runs |
| Assertion definitions | `systems/eval-harness/assertions/*.json` | Per-workflow structural assertion specs |
| Score script | `systems/eval-harness/scoring/score_eval.py` | Authoritative composite score computation |
| Dashboard generator | `systems/eval-harness/generate-dashboard.py` | HTML dashboard generation |
| Grading outputs | `systems/eval-harness/grading/` | Analysis report output directory |
| Skill-run signals | `systems/eval-harness/skill-runs/` | Signal files for sub-skill executions |

### Paths

```
workflows/system-eval/
├── workflow.md          ← this file
├── state.yaml           ← execution state
├── steps/
│   ├── step-01-intake.md        ← open eval record, assess what needs work
│   ├── step-02-assert.md        ← run structural assertions on unasserted records
│   ├── step-03-grade.md         ← invoke rigby-eval-grade on all ungraded records
│   ├── step-03b-guardrail-checkpoint.md  ← adversarial review of grades before scoring
│   ├── step-04-score.md         ← compute composite scores via score_eval.py
│   ├── step-05-analyze.md       ← invoke rigby-eval-analyze across full corpus
│   └── step-06-dashboard.md     ← regenerate dashboard, close eval record, deliver summary
```

### Key Metrics

- **Records assessed**: total eval records in runs/ at workflow start
- **Unasserted records**: records with assertions_checked == 0
- **Ungraded records**: records with grade == null
- **Unscored records**: records missing composite score data
- **Records updated**: count of records modified during this run
- **Assertions run**: total assertions evaluated in Step 2
- **Grades assigned**: count of new grades assigned in Step 3
- **Scores computed**: count of records scored in Step 4

---

## STATE CHECK

Before starting any step, read `state.yaml` and apply the correct case:

| State | Action |
|-------|--------|
| `status: in-progress` | Resume from `current-step`. Read that step file. Do not restart. Surface: "[Rigby]: Resuming system-eval from step [N]." |
| `status: not-started` or `status: complete` | Initialize fresh. Write initial state to state.yaml. Proceed to Step 1. |
| `status: aborted` | Surface to controller: "Previous system-eval run was aborted at step [current-step]. Resume or start fresh?" Wait for decision. |

---

## EXECUTION

Run steps in order. Read each step file fully before executing it.

| Step | File | Model | Description |
|------|------|-------|-------------|
| 1 | [step-01-intake.md](steps/step-01-intake.md) | **haiku** | Open eval record, inventory all runs, classify what needs work |
| 2 | [step-02-assert.md](steps/step-02-assert.md) | **haiku** | Run structural assertions on records with assertions_checked == 0 |
| 3 | [step-03-grade.md](steps/step-03-grade.md) | **sonnet** | Invoke rigby-eval-grade skill on all ungraded records |
| 3b | [step-03b-guardrail-checkpoint.md](steps/step-03b-guardrail-checkpoint.md) | **haiku** | Automated guardrail checkpoint — adversarial review of step-03's grades before they drive the composite score gate |
| 4 | [step-04-score.md](steps/step-04-score.md) | **haiku** | Compute composite scores via score_eval.py for all records |
| 5 | [step-05-analyze.md](steps/step-05-analyze.md) | **sonnet** | Invoke rigby-eval-analyze across full corpus, write analysis report |
| 6 | [step-06-dashboard.md](steps/step-06-dashboard.md) | **haiku** | Regenerate dashboard, close eval record, deliver summary |

**Instrumentation:** Step 1 opens an eval record (`new-eval.py`). Each step appends its result to the record's `steps` array in state.yaml. Step 6 closes the record (`close-eval-record.py`) with the full step list and outcome.

**Fully autonomous:** No controller approval gate. All steps run to completion unless a failure occurs.

---

## TERMINATION CONDITIONS

The workflow terminates after Step 6 when:
- Dashboard regenerated and path surfaced
- state.yaml set to `complete`
- Eval record closed

If any step encounters a blocking failure (e.g., score_eval.py not found, generate-dashboard.py fails), Rigby surfaces the specific error and sets state.yaml to `aborted`. She does not silently swallow failures.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

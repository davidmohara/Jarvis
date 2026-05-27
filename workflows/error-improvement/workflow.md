---
name: error-improvement
description: Rigby's full error improvement cycle — analyze the error log for patterns, propose and apply systemic fixes, verify fixes are reflected in system files, compact resolved entries into monthly digests, and record the improvement as a pending evolution. Closes the feedback loop between corrections and durable system change.
agent: rigby
model: sonnet
---

<!-- system:start -->
# Error Improvement Workflow

**Goal:** Turn accumulated corrections into durable system improvements. Not just pattern detection — actual fixes applied, verified, and preserved across the system's evolution history.

**Agent:** Rigby — System Operator

**Architecture:** Six-step sequential workflow. Steps 1-3 are analytical; Steps 4-6 are operational. The controller approves the fix list between Step 3 and Step 4 — no fixes are applied without explicit sign-off. Compact only runs after fixes are verified (Step 5), never mid-cycle.

**When to run:**
- After a triage pass produces an Apply Now bucket
- When entry count in `entries/` exceeds 100
- During weekly review (Quinn invokes Rigby for this step)
- On demand: "run error improvement", "close the error loop", "apply the error fixes"

**When NOT to run:**
- Mid-session while errors are still being logged (wait for session close)
- If `status: in-progress` in state.yaml (resume, don't restart)

---

## INITIALIZATION

### Data Sources Required

| Source | Tool/Path | Purpose |
|--------|-----------|---------|
| Error entries | `systems/error-tracking/entries/*.json` | Source data for analysis |
| Error schema | `systems/error-tracking/schema.md` | Category and failure mode definitions |
| Error meta | `systems/error-tracking/_meta.json` | Last analysis timestamp, compaction history |
| Error digests | `systems/error-tracking/digests/compact-*.json` | Historical periods for trend comparison |
| System files | `SYSTEM.md`, `agents/*.md`, `skills/*/SKILL.md`, `workflows/*/` | Targets for fix application |
| Eval records | `systems/eval-harness/runs/*.json` | Cross-reference: are error patterns reflected in eval failures? |
| Pending changes | `evolutions/.pending-changes.json` | Track files modified by this workflow |
| Compact script | `systems/error-tracking/compact.py` | Used in Step 6 |

### Paths

```
workflows/error-improvement/
├── workflow.md          ← this file
├── state.yaml           ← execution state
├── steps/
│   ├── step-01-intake.md       ← gate check, load data, assess volume
│   ├── step-02-analyze.md      ← invoke rigby-error-analysis skill
│   ├── step-03-triage.md       ← bucket fixes, present Apply Now list for approval
│   ├── step-04-apply.md        ← execute approved fixes across system files
│   ├── step-05-verify.md       ← confirm fixes are actually present in target files
│   ├── step-06-compact.md      ← invoke rigby-error-compact, log to pending-changes, write episodic memory
│   └── step-07-summary.md      ← close state, write skill-run signal, deliver final report
```

### Key Metrics

- **Entry count**: total active entries at workflow start
- **Open entries**: entries with `fix_status: proposed` or `in-progress`
- **Apply Now count**: fixes approved for immediate application
- **Needs Your Call count**: fixes requiring controller judgment
- **Files modified**: count of system files changed in Step 4
- **Assertions passed**: Step 5 verification pass rate
- **Entries compacted**: entries archived in Step 6

---

## STATE CHECK

Before starting any step, read `state.yaml` and apply the correct case:

| State | Action |
|-------|--------|
| `status: in-progress` | Resume from `current-step`. Read that step file. Do not restart. Surface: "[Rigby]: Resuming error-improvement from step [N]." |
| `status: not-started` or `status: complete` | Initialize fresh. Write initial state to state.yaml. Proceed to Step 1. |
| `status: aborted` | Surface to controller: "Previous error-improvement run was aborted at step [current-step]. Resume or start fresh?" Wait for decision. |
| `status: awaiting-approval` | The Apply Now list is waiting for controller sign-off. Re-surface it. Wait. Do not advance to Step 4 without explicit approval. |

---

## EXECUTION

Run steps in order. Read each step file fully before executing it. The `model` column is the Claude model to use for that step — spawn accordingly.

| Step | File | Model | Description |
|------|------|-------|-------------|
| 1 | [step-01-intake.md](steps/step-01-intake.md) | **haiku** | Gate check, load error data, assess volume and eligibility |
| 2 | [step-02-analyze.md](steps/step-02-analyze.md) | **sonnet** | Invoke `rigby-error-analysis` skill — statistics, patterns, tiered fix proposals |
| 3 | [step-03-triage.md](steps/step-03-triage.md) | **haiku** | Bucket fixes; present Apply Now list; **workflow pauses here for controller sign-off** |
| 4 | [step-04-apply.md](steps/step-04-apply.md) | **sonnet** | Execute approved fixes across system files; update fix_status on entries |
| 5 | [step-05-verify.md](steps/step-05-verify.md) | **haiku** | Assert each fix is present in target file; confirm fix_status updated; compact eligibility check |
| 6 | [step-06-compact.md](steps/step-06-compact.md) | **haiku** | Compact eligible months; log files to pending-changes; write episodic memory |
| 7 | [step-07-summary.md](steps/step-07-summary.md) | **sonnet** | Deliver final cycle report; close state.yaml; write eval record via `close-eval-record.py` |

**Instrumentation:** Step 1 opens an eval record (`new-eval.py`). Each step appends its result to the record's `steps` array in state.yaml. Step 7 closes the record (`close-eval-record.py`) with the full step list and outcome.

---

## EXECUTION PHASES

**Phase A — Analysis (Steps 1-3):** Rigby runs these during the weekly review session (or fully on-demand). Ends with the approval prompt. The weekly review does not wait past this point — it closes after the controller responds to the triage list.

**Phase B — Operations (Steps 4-7):** Rigby runs these as a follow-on task after the weekly review closes, or immediately on approval in an on-demand session. Steps 4-7 are autonomous — no further controller interaction required unless Step 5 surfaces a verification failure.

This split means the weekly review never blocks on file edits, compaction, or report generation. The controller sees the analysis and approves the list; Rigby handles the rest.

---

## TERMINATION CONDITIONS

The workflow terminates after Step 07 when:
- Summary report delivered to controller
- state.yaml set to `complete`
- Skill-run signal written

If Step 05 surfaces a verification failure: workflow pauses, surfaces the specific failing assertions, and waits for controller guidance before proceeding to Step 06.

---

## CADENCE

| Trigger | Frequency | Caller | Phase |
|---------|-----------|--------|-------|
| Weekly review | Weekly | Quinn invokes Rigby | Phase A during review; Phase B after review closes |
| Entry threshold (>100) | As needed | Master (threshold alert) | Full cycle on-demand |
| Post-triage (manual) | As needed | Rigby on demand | Full cycle on-demand |
| Monthly close | First week of new month | Rigby | Phase B only (compaction-focused) |

**Weekly review integration:** Quinn calls Rigby to run Phase A (Steps 1-3). The triage list surfaces as the final item of the review session. The controller approves (or defers) during the review. The review then closes. Rigby picks up Phase B (Steps 4-7) as a follow-on task — the summary report is delivered separately after Phase B completes, not during the review session itself.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

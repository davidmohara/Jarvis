---
name: system-eval-verification
description: Adversarial verification of a system-eval maintenance run. Ralph cross-checks the run's grades, assertion counts, and analysis findings against the eval records themselves before the run is declared complete.
agent: ralph
model: sonnet
---

<!-- system:start -->
# System Eval Verification Workflow

**Goal:** Confirm that the maintenance run's analysis claims match the records: every grade it reports is on a record, every assertion count it reports is reflected in `assessment.structural`, every pattern/finding in the analysis report traces to actual records, and the run did not grade itself.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the maintenance manifest (step outputs, state, eval records, analysis report) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (system-eval):** Eval-record analysis claims vs the records themselves. The producing agent (Rigby) summarizes what it graded, asserted, scored, and concluded; Ralph re-derives each claim from the recorded evidence: the step outputs, `workflows/system-eval/state.yaml`, `systems/eval-harness/runs/*.json`, and the analysis report in `systems/eval-harness/grading/`. This is the system-eval lens in `agents/adversarial-isolation.md`.

## Lens checklist (what Ralph checks that the producer structurally cannot)

1. **Grades are real:** every grade the run reports (and every `grade_distribution` count) corresponds to a record whose `assessment.grading.grade` matches - no grade claimed that no record carries.
2. **Assertion counts reconcile:** the reported `assertions_run` tally matches what the records' `assessment.structural` blocks actually show.
3. **Findings trace to files:** each pattern/recommendation in the analysis report names a workflow/record and a concrete detail that exists in the corpus (e.g., a failing assertion ID present in the records), not an invented finding.
4. **No self-grading:** no record for `system-eval` itself was graded by this run.
5. **Counts are true:** the reported `records_total`, `total_graded`, and `records_scored` match the actual record counts on disk (within the documented skips).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|--------------|
| Maintenance manifest | Step output paths + run-date + report path | Passed from Rigby as accumulated-context |
| Step outputs | `workflows/system-eval/steps/step-0{1..6}-*.md` frontmatter `outputs` | File system read |
| Workflow state | `workflows/system-eval/state.yaml` | File system read |
| Eval records | `systems/eval-harness/runs/eval-*.json` | File system read |
| Analysis report | `<report_path>` from state.yaml accumulated-context.analysis | File system read |

### Verdict table format

| Item | Run claim | Recorded evidence | Verdict |
|------|-----------|-------------------|---------|
| (one row per claim) | (what the summary asserts) | (what the records show) | ✅ Verified / ⚠️ Unverified |

### Output

- Verdict table + one-line summary
- Mark ⚠️ on any claim the record does not support
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Single step: `steps/step-01-verify.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

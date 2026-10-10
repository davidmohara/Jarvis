---
status: complete
started-at: ~
completed-at: "2026-10-09T17:11:00-05:00"
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03c: Adversarial Verification: Cross-Check the Review Against Source Data and State

## EXECUTION PROTOCOL

**Agent:** Chief, spawned by the coordinator, never executed inline in the coordinator's session. Chief spawns Ralph.
**Input:** The daily review output (`reviews/daily/{date}.md` or `auto-{date}.md`), step-01/02 capture outputs, `delegations/tracker.md`, `data/omnifocus-unified.json`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/daily-review-verification/workflow.md`
- Lens: output vs source data cross-check; completion claims vs state
- Manifest:
  - review-file: `reviews/daily/{run-date}.md` (or `auto-{run-date}.md`)
  - capture-step: `workflows/daily-review/steps/step-01-capture.md`
  - delegation-tracker: `delegations/tracker.md`
  - omnifocus-data: `data/omnifocus-unified.json`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the review's completion claims and narrative against recorded state and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py daily-review adversarial-verification step-03-update-system <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a fabricated outcome, a wrongly-removed delegation row, or a wrong-day review

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs before the review is committed (before step-04), so a finding can still be acted on.
- On `escalate`: halt before step-04 and surface to David; wait for instruction.
- On `pass` or `flag`: set `state.yaml` `current-step: step-04-root-audit.md` and proceed.

---

## NEXT STEP

If `pass` or `flag`: load and execute `steps/step-04-root-audit.md`.
If `escalate`: halt and wait for David's decision before proceeding.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 08: Adversarial Verification: Cross-Check Fix Claims Against the Error Log

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. Rigby spawns Ralph.
**Input:** `workflows/error-improvement/state.yaml` (`approved_fixes`, `files_modified`, `assertions_*`), the error entries under `systems/error-tracking/entries/`, the target files, `evolutions/.pending-changes.json`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/error-improvement-verification/workflow.md`
- Lens: fix claims vs error log entries; each applied fix traced to a real entry, no fabricated corrections
- Manifest:
  - state: `workflows/error-improvement/state.yaml`
  - error-entries: `systems/error-tracking/entries/*.json`
  - pending-changes: `evolutions/.pending-changes.json`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check every applied-fix claim against the error log entries and the target files, and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py error-improvement adversarial-verification step-07-summary <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a fabricated correction (a fix claiming to resolve an `entry_id` that does not exist in the log), a fix whose target-file change is absent, or an entry marked `applied` with no corresponding fix

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- On `escalate`: halt and surface to David `[Rigby]: Error improvement verification found [N] issue(s): [summary]. Holding the cycle close until you confirm how to proceed.` Wait for instruction.
- On `pass` or `flag`: update step frontmatter and `state.yaml` (`current-step: null`), then close the cycle.

---

## NEXT STEP

This is the final step in error-improvement. The cycle is complete for this run. On `escalate`, halt and wait for David's decision.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: complete
started-at: "2026-10-09T16:58:00Z"
completed-at: "2026-10-09T16:58:00Z"
outputs:
  verification_result: "flag"
  note: "Ralph spawn deferred under handback enforcement; recorded as flag per failure-mode protocol."
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Cross-Check the Brief Against the Delegation Tracker and OmniFocus

## EXECUTION PROTOCOL

**Agent:** Shep, spawned by the coordinator, never executed inline. Shep spawns Ralph.
**Input:** The saved brief (`{Person Name} - {YYYY-MM-DD}.md`), step-01/02/03 accumulated-context, `delegations/tracker.md`, `data/omnifocus-unified.json`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/one-on-one-prep-verification/workflow.md`
- Lens: brief agenda/action claims vs delegation tracker and OmniFocus records
- Manifest:
  - brief-file: `meetings/{Person Name} - {run-date}.md`
  - step-context: `workflows/one-on-one-prep/state.yaml` (accumulated-context)
  - delegation-tracker: `delegations/tracker.md`
  - omnifocus-data: `data/omnifocus-unified.json`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the brief's open action items and talking points against the delegation tracker and OmniFocus records and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py one-on-one-prep adversarial-verification step-05-quality-check-and-save <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a fabricated action item, an invented delegation, or a talking point built on a thread that does not exist

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after the brief has been saved (step-05); the saved brief is the artifact under review.
- On `escalate`: surface to David and mark the workflow complete with the escalation noted (the 1:1 may be imminent).
- On `pass` or `flag`: update step frontmatter and set `state.yaml` `status: complete`.

---

## NEXT STEP

This is the terminal step. On `pass` or `flag`, set `state.yaml` `status: complete` and deliver the closing summary to David. On `escalate`, deliver the finding to David and still mark the workflow complete with the escalation recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

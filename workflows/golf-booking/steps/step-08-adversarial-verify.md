---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 08: Adversarial Verification: Cross-Check Booking Claims Against Confirmation Evidence

## EXECUTION PROTOCOL

**Agent:** Sterling, spawned by the coordinator, never executed inline. Sterling spawns Ralph.
**Input:** The step 00-07 frontmatter `outputs`, `workflows/golf-booking/state.yaml`, `workflows/golf-booking/preview-output.json`, the Gate 3/4/6 evidence
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/golf-booking-verification/workflow.md`
- Lens: booking claims vs confirmation evidence; window calculated correctly, no double-booking, confirmation recorded before any success claim
- Manifest:
  - step-outputs: `workflows/golf-booking/steps/step-0{0..7}-*.md` frontmatter outputs
  - state: `workflows/golf-booking/state.yaml`
  - preview-output: `workflows/golf-booking/preview-output.json`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the booking's success claims against the confirmation evidence and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py golf-booking adversarial-verification step-07-slack-confirmation <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a booking claimed with no Gate 3 `BOOKING-SUCCESS` evidence, a Gate 4 skipped while success was claimed, a booked date that does not match the Gate 1 target (a silent date substitution), a double-booking (a prior booking still live while a new one is claimed), or a success claimed while `state.yaml` records `verification-failed`/`aborted`

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- On `escalate`: halt and surface to David `[Sterling]: Golf booking verification found [N] issue(s): [summary]. Do not assume the booking succeeded; holding for your review.` Wait for instruction.
- On `pass` or `flag`: update step frontmatter and `state.yaml` (`current-step: null`), then close the run.

---

## NEXT STEP

This is the final step in golf-booking. The run is complete. On `escalate`, halt and wait for David's decision.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Cross-Check Preview Claims Against Weather and Course Source Data

## EXECUTION PROTOCOL

**Agent:** Sterling, spawned by the coordinator, never executed inline. Sterling spawns Ralph.
**Input:** The step 01-05 frontmatter `outputs`, `workflows/golf-preview/state.yaml`, `workflows/golf-booking/preview-output.json`, the weather source data for the target weekend
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/golf-preview-verification/workflow.md`
- Lens: preview claims vs weather/course source data; target dates correct, no day marked available against a hard block, weather claims match the source
- Manifest:
  - step-outputs: `workflows/golf-preview/steps/step-0{1..5}-*.md` frontmatter outputs
  - state: `workflows/golf-preview/state.yaml`
  - preview-output: `workflows/golf-booking/preview-output.json`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the preview's dates, calendar status, drought flag, and weather claims against the source data, and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py golf-preview adversarial-verification step-05-notify-slack <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a target date that is not the correct Friday/8-days-out, a day marked available against a hard calendar block, a `weather_data_missing` claim that contradicts the source, or a scored option that contradicts the recorded weather/calendar data

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- On `escalate`: halt and surface to David `[Sterling]: Golf preview verification found [N] issue(s): [summary]. Holding before the booking workflow acts on this preview.` Wait for instruction.
- On `pass` or `flag`: update step frontmatter and `state.yaml` (`current-step: null`), then close the run.

---

## NEXT STEP

This is the final step in golf-preview. The run is complete. On `escalate`, halt and wait for David's decision.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

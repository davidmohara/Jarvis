---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Adversarial Verification: Cross-Check the Briefing Against Source Data

## EXECUTION PROTOCOL

**Agent:** Chief, spawned by the coordinator, never executed inline in the coordinator's session. Chief spawns Ralph.
**Input:** The delivered briefing (`memory/working/morning-briefing-*.md`) and the source-data files from boot steps 01.2/01.5 (`data/calendar-unified.json`, `data/email-unified.json`, `data/omnifocus-unified.json`), plus `delegations/tracker.md`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/morning-briefing-verification/workflow.md`
- Lens: calendar/email/omnifocus cross-check
- Manifest:
  - briefing-file: `<most recent memory/working/morning-briefing-*.md>`
  - calendar-data: `data/calendar-unified.json`
  - email-data: `data/email-unified.json`
  - omnifocus-data: `data/omnifocus-unified.json`
  - delegation-tracker: `delegations/tracker.md`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check every claim in the briefing against the source data and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py morning-briefing adversarial-verification step-04-synthesize-briefing <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a fabricated claim, wrong-day data, or a degraded-source claim presented as clean

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step is blocking for the checkpoint, not for delivery (the briefing was already delivered in step-04).
- On `flag` or `escalate`: surface the finding to David in one line `[Chief]: Briefing verification found [N] issue(s): [summary]. Recorded on the eval record; the briefing was already delivered.`
- On `pass` or `flag`: set this step complete and set `state.yaml` `status: complete`, `current-step: step-05`.

---

## NEXT STEP

This is the final step. When complete, set `state.yaml` `status: complete`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

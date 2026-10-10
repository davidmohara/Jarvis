---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Cross-Check the Prep Sheet Against Source Data

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline. Chase spawns Ralph.
**Input:** The prep sheet markdown (`{Person Name} - {Company} - {YYYY-MM-DD}.md`), step-01/02/03 accumulated-context, and the source records it cites (calendar invite, email thread, CRM account record)
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/client-meeting-prep-verification/workflow.md`
- Lens: prep-sheet claims vs source data; every attendee/company fact traced to calendar, email, or CRM
- Manifest:
  - prep-sheet: `meetings/{Person Name} - {Company} - {run-date}.md`
  - step-context: `workflows/client-meeting-prep/state.yaml` (accumulated-context)
  - source-records: calendar invite, introduction/most-recent email thread, CRM account record
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Trace every attendee and company fact in the prep sheet back to a calendar, email, or CRM record and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py client-meeting-prep adversarial-verification step-05-remarkable-delivery <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: an invented attendee, a fabricated company fact, or a reason-for-call that contradicts the email evidence

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after the PDF has been delivered (step-05). The prep sheet markdown is still the artifact under review; a finding can still be corrected and the PDF regenerated if the controller chooses.
- On `escalate`: surface to David and mark the workflow complete with the escalation noted (the meeting may be imminent); do not halt the run.

---

## NEXT STEP

This is the terminal step. On `pass` or `flag`, set `state.yaml` `status: complete` and deliver the closing summary to David. On `escalate`, deliver the finding to David and still mark the workflow complete with the escalation recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

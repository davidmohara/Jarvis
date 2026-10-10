---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Adversarial Verification: Cross-Check the Document Against the Account and Event Records

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline. Chase spawns Ralph.
**Input:** The saved document (`{Partner} - {YYYY-MM-DD}.md`), step-01/02/03 accumulated-context, the CRM account records, and the calendar/email records the overlap and event claims cite
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/partner-meeting-prep-verification/workflow.md`
- Lens: account-overlap and event claims vs actual CRM/calendar records
- Manifest:
  - document: `{partner-slug} - {run-date}.md`
  - step-context: `workflows/partner-meeting-prep/state.yaml` (accumulated-context)
  - crm-records: account/pipeline records for the accounts named in the overlap table
  - calendar-email: the partner meeting invite and correspondence
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the account-overlap and event claims in the document against the actual records and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py partner-meeting-prep adversarial-verification step-04-build-document <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: an invented account, a fabricated overlap, a made-up event, or a partner-side column filled in with a guess

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after the document has been saved (step-04); the saved document is the artifact under review and is intended to be shared with the partner team, so accuracy matters more than for an internal-only sheet.
- On `escalate`: surface to David and mark the workflow complete with the escalation noted.
- On `pass` or `flag`: update step frontmatter and set `state.yaml` `status: complete`.

---

## NEXT STEP

This is the terminal step. On `pass` or `flag`, set `state.yaml` `status: complete` and deliver the closing summary to David. On `escalate`, deliver the finding to David and still mark the workflow complete with the escalation recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

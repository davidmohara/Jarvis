---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Adversarial Verification - Standing-Intelligence Accounting

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline. Knox spawns Ralph.
**Input:** Step 01-06 frontmatter outputs, `workflows/watchtower/state.yaml`, `workflows/watchtower/seen.jsonl`, the draft/angle sources, `reference/blog-ideas.md`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/watchtower-verification/workflow.md`
- Lens: standing-intelligence accounting: drafts approved/posted vs source digests, no unpublished claims of publishing
- Manifest:
  - step-outputs: `workflows/watchtower/steps/weekly-step-0{1,2,2b,3,4,5,6}-*.md` frontmatter outputs
  - state: `workflows/watchtower/state.yaml`
  - seen-ledger: `workflows/watchtower/seen.jsonl`
  - blog-ideas: `reference/blog-ideas.md`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the weekly run's claims (drafts created vs sent, sources proposed, no claims of publishing) against the sources and the record, and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py watchtower adversarial-verification weekly-step-06-publish-drafts <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a draft claimed sent that was never delivered, a claim of publishing when Watchtower only sends to Slack `#content`, or a theme asserted with no source item

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after weekly-step-06 (publish drafts). If step-06 was skipped, this step still runs (verifying the run's claims with `drafts_sent` empty).
- On `escalate`: halt and surface to David `[Knox]: Watchtower verification found [N] issue(s): [summary]. Holding the run's close until you confirm how to proceed.` Do not mark the run complete.
- On `pass` or `flag`: confirm `state.yaml` `status: complete` (step-05 already set it), update this step's frontmatter, and include the one-line verification result in the terminal report.

---

## NEXT STEP

End of the weekly run. Daily run resumes Tuesday.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

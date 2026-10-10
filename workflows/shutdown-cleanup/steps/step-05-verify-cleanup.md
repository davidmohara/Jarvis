---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Adversarial Verification: Cross-Check the Cleanup Against the Commit and Audit Trail

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. Rigby spawns Ralph.
**Input:** Step 01-04 frontmatter outputs, `workflows/shutdown-cleanup/state.yaml`, `systems/eval-harness/git-ops.jsonl`, the commit sha from step-04
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/shutdown-cleanup-verification/workflow.md`
- Lens: cleanup claims vs commit and audit trail
- Manifest:
  - step-outputs: `workflows/shutdown-cleanup/steps/step-0{1,2,3,4}-*.md` frontmatter outputs
  - state: `workflows/shutdown-cleanup/state.yaml`
  - git-audit: `systems/eval-harness/git-ops.jsonl`
  - commit-sha: `<from step-04 outputs>`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the cleanup claims against the commit and audit trail and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py shutdown-cleanup adversarial-verification step-04-commit <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: temp artifacts committed, a deliverable/media file deleted rather than preserved (see the standing no-screenshot-deletion feedback), a commit that bypassed the wrapper (no `git-ops.jsonl` entry), or a false "workspace clean" claim

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after the commit (terminal verification; the pre-commit review duty is covered by step-04's own wrapper enforcement and verifier).
- Record the result in `state.yaml` under `accumulated-context.adversarial-verification` as a single string: `"<result> - <one-line summary> (<date>)"` (this workflow uses the string form, not the block form).
- On `flag` or `escalate`: surface the finding to the controller in the final cleanup summary, verbatim from Ralph's table.
- If Ralph cannot spawn, record `flag` with reason `ralph-unavailable` and note it in the summary; do not block the session exit. If no commit was needed (workspace clean), verify the nothing-to-commit claim against the lock-free diff lists and record Ralph's verdict on that claim. If `guardrail-checkpoint` refuses, fix the arguments and retry; an unrecordable escalate is a loud failure, surface it to the controller directly.
<!-- system:end -->

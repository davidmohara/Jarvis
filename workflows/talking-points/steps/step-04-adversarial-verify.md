---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Adversarial Verification: Cross-Check the Points Against Their Sources

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph.
**Input:** The delivered document (`meetings/{...}-talking-points.md`), step-01/02 accumulated-context, and the source strategy/notes the points cite (identity/VOICE.md, knowledge-layer entries, agent-domain data)
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/talking-points-verification/workflow.md`
- Lens: talking points traced to source strategy/notes; no unsourced claims
- Manifest:
  - deliverable: `meetings/{...}-talking-points.md`
  - step-context: `workflows/talking-points/state.yaml` (accumulated-context)
  - voice-profile: `identity/VOICE.md`
  - source-material: knowledge-layer entries and agent-domain data the points cite
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Trace each talking point back to a real source and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py talking-points adversarial-verification step-03-format-and-deliver <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a fabricated statistic, an invented quote, a position attributed to the executive that no source supports, or a point with no source at all

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after the points have been delivered (step-03); the delivered document is the artifact under review.
- On `escalate`: surface to David and mark the workflow complete with the escalation noted (the event may be imminent).
- On `pass` or `flag`: update step frontmatter and set `state.yaml` `status: complete`.

---

## NEXT STEP

This is the terminal step. On `pass` or `flag`, set `state.yaml` `status: complete` and deliver the closing summary to David. On `escalate`, deliver the finding to David and still mark the workflow complete with the escalation recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

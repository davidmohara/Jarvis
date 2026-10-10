---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Cross-Check the Deliverables Against the Episode Inputs

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph.
**Input:** The detailed prep sheet (`meetings/podcast-prep/YYYY-MM-DD-guest-name.md`), the PDF-format markdown (`Episode {N}.md`), the rendered PDF (`Episode {N}.pdf`), step-01/02 accumulated-context (episode inputs and `sources_used`)
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/podcast-prep-verification/workflow.md`
- Lens: prep-sheet completeness vs episode inputs; reference sheet + PDF both exist and are substantive
- Manifest:
  - detailed-sheet: `meetings/podcast-prep/YYYY-MM-DD-guest-name.md`
  - pdf-markdown: `meetings/podcast-prep/Episode {N}.md`
  - pdf-rendered: `meetings/podcast-prep/Episode {N}.pdf`
  - step-context: `workflows/podcast-prep/state.yaml` (accumulated-context, sources_used)
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the episode deliverables against the episode inputs and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py podcast-prep adversarial-verification step-05-generate-pdf <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a missing deliverable, an empty/thin PDF, a guest name that does not match the episode inputs, or questions invented where a real source existed

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after the PDF has been generated (step-05); both deliverables are the artifacts under review.
- On `escalate`: surface to David and mark the workflow complete with the escalation noted (filming may be imminent).
- On `pass` or `flag`: update step frontmatter and set `state.yaml` `status: complete`.

---

## NEXT STEP

This is the terminal step. On `pass` or `flag`, set `state.yaml` `status: complete` and deliver the closing summary to David. On `escalate`, deliver the finding to David and still mark the workflow complete with the escalation recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

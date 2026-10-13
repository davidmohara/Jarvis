---
status: complete
started-at: 2026-10-09T12:15:00Z
completed-at: 2026-10-09T12:20:00Z
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification - Memory-Conservation Accounting

## EXECUTION PROTOCOL

**Agent:** Jarvis, spawned by the coordinator, never executed inline. Jarvis spawns Ralph.
**Input:** Step 01-05 outputs from `workflows/dream-cycle/state.yaml` `accumulated-context`, `workflows/dream-cycle/state.yaml`, `memory/dream.log`, the real `memory/working/` and `memory/episodic/` trees, the semantic targets written in step-03
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml; state.yaml set to complete

## PARAMETERS

- Verification workflow: `workflows/dream-cycle-verification/workflow.md`
- Lens: memory-conservation accounting: archived/promoted/compressed claims vs actual memory files and dream.log
- Manifest:
  - step-outputs: `workflows/dream-cycle/state.yaml` `accumulated-context`
  - state: `workflows/dream-cycle/state.yaml`
  - dream-log: `memory/dream.log`
  - working-dir: `memory/working/`
  - episodic-dir: `memory/episodic/`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check the cycle's memory-conservation claims against the actual memory files and dream.log and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py dream-cycle adversarial-verification step-05-logging <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a silent drop of a working-memory entry, a promoted/high-salience entry that was deleted, or a dream.log entry that does not match the run

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after step-05's log write and commit (terminal verification; the pre-deletion duty is already covered by step-03b's own checkpoint).
- On `escalate`: write to `memory/dream.log` `escalated: adversarial verification halted the cycle - [reason]`, leave `state.yaml` at `status: aborted` with a note, and surface it at the next session boot. dream-cycle runs unattended, so do not block the nightly run indefinitely.
- On `pass` or `flag`: set `state.yaml` `status: complete`, `current-step: null`, and update this step's frontmatter.
- If the `state.yaml` write fails, report it in the closing summary; do not silently accept an unclosed state.

---

## NEXT STEP

End of cycle. The dream cycle is complete once the adversarial verdict is recorded and state.yaml is closed.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

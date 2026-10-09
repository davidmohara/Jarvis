---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification - Memory-Conservation Accounting

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/dream-cycle-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own consolidation. This is a separate spawn with a distinct lens.
2. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification` before finalizing.
3. You MUST NOT edit memory files, the dream log, or step outputs to make a finding disappear. Findings are surfaced and recorded as-is.
4. Ralph verifies claims against the recorded memory state. He does not fix, re-run, or re-write anything.
5. This step runs after step-05's log write and commit (terminal verification, matching the shutdown-cleanup terminal-verify pattern). The pre-deletion duty is already covered by step-03b's own checkpoint.

---

## EXECUTION PROTOCOL

**Agent:** Jarvis, spawned by the coordinator, never executed inline. Jarvis spawns Ralph.
**Input:** Step 01-05 frontmatter outputs, `workflows/dream-cycle/state.yaml`, `memory/dream.log`, the real `memory/working/` and `memory/episodic/` trees, the semantic targets written in step-03
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml; state.yaml set to complete

---

## CONTEXT BOUNDARIES

- Scope is this run's consolidation: working-memory archival, episodic scoring, semantic promotion, episodic compression, and the dream.log entry.
- This step does not re-run the cycle. It checks whether the cycle's conservation claims hold up against the files on disk.
- Findings are a report, not a retry.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/dream-cycle-verification/workflow.md
   Manifest:
     step-outputs: workflows/dream-cycle/steps/step-0{1,2,3,4,5}-*.md frontmatter outputs
     state: workflows/dream-cycle/state.yaml
     dream-log: memory/dream.log
     working-dir: memory/working/
     episodic-dir: memory/episodic/
     run-date: <YYYY-MM-DD>
   Task: Cross-check the cycle's memory-conservation claims against the actual memory files and dream.log and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Cycle claim | Recorded state | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified → `pass`.
   - A minor accounting mismatch (e.g., a summary count off by one) → `flag`.
   - A silent drop of a working-memory entry, a promoted/high-salience entry that was deleted, or a dream.log entry that does not match the run → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py dream-cycle adversarial-verification step-05-logging <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "memory-conservation accounting: archived/promoted/compressed claims vs actual memory files and dream.log"
   ```

6. **On `escalate`:** write to `memory/dream.log`: `escalated: adversarial verification halted the cycle - [reason]`, leave `state.yaml` at `status: aborted` with a note, and surface it to David at the next session boot. dream-cycle runs unattended, so do not block the nightly run indefinitely - the next boot surfaces the aborted state.

7. **On `pass` or `flag`:** set `state.yaml` `status: complete`, `current-step: null`, update this step's frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`), and deliver the one-line verification result in the closing summary.

---

## SUCCESS METRICS

- Ralph was spawned (separate agent, distinct lens) and his verdict table received intact
- An `adversarial-verification` checkpoint result is recorded
- The verdict summary is written to state.yaml
- Any finding is surfaced, not silently absorbed

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph fails to spawn | Record `result: flag` with reason "adversarial verification unavailable, Ralph not spawnable"; note it in the closing summary. Do not self-verify in place of Ralph. |
| Ralph returns a partial table | Record the partial result and note which items were missing. Do not suppress it. |
| `guardrail-checkpoint.py` fails to write | Still write the verdict summary to state.yaml; note the recording gap in the closing summary. |
| state.yaml write fails | Report it in the closing summary; do not silently accept an unclosed state. |

---

## NEXT STEP

End of cycle. The dream cycle is complete once the adversarial verdict is recorded and state.yaml is closed.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

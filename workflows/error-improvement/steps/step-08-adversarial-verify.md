---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 08: Adversarial Verification: Cross-Check Fix Claims Against the Error Log

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/error-improvement-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own fixes. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before closing the cycle.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit a target file or an error entry to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state (the error log entries, the target files, `state.yaml`, `evolutions/.pending-changes.json`). He does not fix, re-apply, or re-write anything.

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. Rigby spawns Ralph.
**Input:** `workflows/error-improvement/state.yaml` (`approved_fixes`, `files_modified`, `assertions_*`), the error entries under `systems/error-tracking/entries/`, the target files, `evolutions/.pending-changes.json`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this cycle's applied fixes and the entries they claim to resolve.
- This step does not re-apply fixes or edit entries. It checks whether each applied-fix claim holds up against the error log and the target files.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be corrected in the next cycle.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/error-improvement-verification/workflow.md
   Manifest:
     state: workflows/error-improvement/state.yaml
     error-entries: systems/error-tracking/entries/*.json
     pending-changes: evolutions/.pending-changes.json
     run-date: <YYYY-MM-DD>
   Task: Cross-check every applied-fix claim against the error log entries and the target files, and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Fix claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified or not-applicable → `pass`.
   - Any minor mismatch (e.g., an entry resolved by a broader fix but not individually listed) → `flag`.
   - Any fabricated correction (a fix claiming to resolve an `entry_id` that does not exist in the log), a fix whose target-file change is absent, or an entry marked `applied` with no corresponding fix → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py error-improvement adversarial-verification step-07-summary <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported fixes or fabricated corrections, or empty]
       lens: "fix claims vs error log entries; each applied fix traced to a real entry, no fabricated corrections"
   ```

6. **On `escalate`:** halt and surface to David: `[Rigby]: Error improvement verification found [N] issue(s): [summary]. Holding the cycle close until you confirm how to proceed.` Wait for instruction.

7. **On `pass` or `flag`:** update step frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`) and state.yaml (`current-step: null`), then close the cycle.

---

## SUCCESS METRICS

- Ralph was spawned (separate agent, distinct lens) and his verdict table received intact
- An `adversarial-verification` checkpoint result is recorded
- The verdict summary is written to state.yaml
- Any finding is surfaced to David, not silently absorbed

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph fails to spawn | Record `result: flag` with reason "adversarial verification unavailable, Ralph not spawnable"; note it in the closing summary. Do not self-verify in place of Ralph. |
| Ralph returns a partial table | Record the partial result and note which items were missing. Do not suppress it. |
| `guardrail-checkpoint.py` fails to write | Still write the verdict summary to state.yaml; note the recording gap in the closing summary. |

---

## NEXT STEP

This is the final step in error-improvement. The cycle is complete for this run. On `escalate`, halt and wait for David's decision.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

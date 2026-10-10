---
status: complete
started-at: ~
completed-at: "2026-10-09T17:11:00-05:00"
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03c: Adversarial Verification: Cross-Check the Review Against Source Data and State

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/daily-review-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own review. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before proceeding to step-04. This step runs before the review is committed, so a finding can still be acted on.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit the review to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state. He does not fix, re-run, or re-write anything.

---

## EXECUTION PROTOCOL

**Agent:** Chief, spawned by the coordinator, never executed inline in the coordinator's session. Chief spawns Ralph.
**Input:** The daily review output (`reviews/daily/{date}.md` or `auto-{date}.md`), step-01/02 capture outputs, `delegations/tracker.md`, `data/omnifocus-unified.json`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's daily review, its capture outputs, and the recorded state it references.
- This step does not re-write the review. It checks whether the review's claims hold up against the record.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be corrected before commit or flagged for the next run.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/daily-review-verification/workflow.md
   Manifest:
     review-file: reviews/daily/{run-date}.md (or auto-{run-date}.md)
     capture-step: workflows/daily-review/steps/step-01-capture.md
     delegation-tracker: delegations/tracker.md
     omnifocus-data: data/omnifocus-unified.json
     run-date: <YYYY-MM-DD>
   Task: Cross-check the review's completion claims and narrative against recorded state and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Review claim | Recorded state | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ or ➖ → `pass`.
   - Any ⚠️ that is a minor mismatch → `flag`.
   - Any ⚠️ that is a fabricated outcome, a wrongly-removed delegation row, or a wrong-day review → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py daily-review adversarial-verification step-03-update-system <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "output vs source data cross-check; completion claims vs state"
   ```

6. **On `escalate`:** halt before step-04 and surface to David: `[Chief]: Daily review verification found [N] issue(s): [summary]. Holding the commit until you confirm how to proceed.` Wait for instruction.

7. **On `pass` or `flag`:** update step frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`) and state.yaml (`current-step: step-04-root-audit.md`), then proceed.

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

If `pass` or `flag`: load and execute `steps/step-04-root-audit.md`.
If `escalate`: halt and wait for David's decision before proceeding.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

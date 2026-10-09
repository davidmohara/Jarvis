---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Cross-Check the Brief Against the Delegation Tracker and OmniFocus

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/one-on-one-prep-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent (Shep) grade its own brief. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before declaring the workflow complete. Findings are surfaced so they can be corrected before the controller walks into the 1:1.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit the brief to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state. He does not fix, re-run, or re-write anything.
6. This step runs after the brief has been saved (step-05). The saved brief is the artifact under review.

---

## EXECUTION PROTOCOL

**Agent:** Shep, spawned by the coordinator, never executed inline. Shep spawns Ralph.
**Input:** The saved brief (`{Person Name} - {YYYY-MM-DD}.md`), step-01/02/03 accumulated-context, `delegations/tracker.md`, `data/omnifocus-unified.json`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's brief and the delegation/task records it cites.
- This step does not re-write the brief. It checks whether the brief's open threads and action items are real.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be corrected before the 1:1.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/one-on-one-prep-verification/workflow.md
   Manifest:
     brief-file: meetings/{Person Name} - {run-date}.md
     step-context: workflows/one-on-one-prep/state.yaml (accumulated-context)
     delegation-tracker: delegations/tracker.md
     omnifocus-data: data/omnifocus-unified.json
     run-date: <YYYY-MM-DD>
   Task: Cross-check the brief's open action items and talking points against the delegation tracker and OmniFocus records and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Brief claim | Recorded state | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ or ➖ → `pass`.
   - Any ⚠️ that is a minor mismatch (e.g., a slightly stale status) → `flag`.
   - Any ⚠️ that is a fabricated action item, an invented delegation, or a talking point built on a thread that does not exist → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py one-on-one-prep adversarial-verification step-05-quality-check-and-save <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "brief agenda/action claims vs delegation tracker and OmniFocus records"
   ```

6. **On `escalate`:** surface to David before the workflow is marked complete: `[Shep]: 1:1 brief verification found [N] issue(s): [summary]. Do not rely on [item] until corrected.` Record the finding and mark the workflow complete with the escalation noted, the 1:1 may be imminent.
7. **On `pass` or `flag`:** update step frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`) and set `state.yaml` `status: complete`.

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

This is the terminal step. On `pass` or `flag`, set `state.yaml` `status: complete` and deliver the closing summary to David. On `escalate`, deliver the finding to David and still mark the workflow complete with the escalation recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

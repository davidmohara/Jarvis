---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Adversarial Verification - Eval-Record Analysis Claims vs the Records

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/system-eval-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own analysis. This is a separate spawn with a distinct lens.
2. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification` before finalizing.
3. You MUST NOT edit eval records, the analysis report, or step outputs to make a finding disappear. Findings are surfaced and recorded as-is.
4. Ralph verifies the analysis's claims against the eval records themselves. He does not fix, re-run, or re-write anything.
5. This step runs after step-06's dashboard regeneration and record closure (terminal verification, matching the shutdown-cleanup terminal-verify pattern).

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. Rigby spawns Ralph.
**Input:** Step 01-06 outputs, `workflows/system-eval/state.yaml`, `systems/eval-harness/runs/*.json`, the analysis report in `systems/eval-harness/grading/`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's eval maintenance: the grades assigned, the assertions run, the scores computed, and the analysis report's findings.
- This step does not re-grade or re-score. It checks whether the run's analysis claims hold up against the records.
- Findings are a report, not a retry.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/system-eval-verification/workflow.md
   Manifest:
     step-outputs: workflows/system-eval/steps/step-0{1,2,3,4,5,6}-*.md frontmatter outputs
     state: workflows/system-eval/state.yaml
     eval-records-dir: systems/eval-harness/runs/
     analysis-report: <report_path from state.yaml accumulated-context.analysis>
     run-date: <YYYY-MM-DD>
   Task: Cross-check this run's grades, assertion counts, and analysis findings against the eval records themselves and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Run claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified → `pass`.
   - A minor accounting mismatch (e.g., a count off by one) → `flag`.
   - A finding the records do not support, a grade with no evidentiary basis, or a self-grading violation → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py system-eval adversarial-verification step-06-dashboard <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "eval-record analysis claims vs the records themselves (counts, grades, findings traced to files)"
   ```

6. **On `escalate`:** system-eval is fully autonomous with no controller approval gate, but an escalation overrides that. Set `state.yaml` to `aborted` with a note naming the specific claim(s) at issue, and surface it in the closing summary the next time a controller session reviews the dashboard.

7. **On `pass` or `flag`:** update this step's frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`) and deliver the one-line verification result in the closing summary. (`state.yaml` was already set complete by step-06; this step does not re-open it.)

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

---

## NEXT STEP

End of run. system-eval is complete once the adversarial verdict is recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Adversarial Verification: Cross-Check the Points Against Their Sources

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/talking-points-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent (Harper) grade its own points. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before declaring the workflow complete.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit the delivered points to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state and source material. He does not fix, re-run, or re-write anything.
6. This step runs after the points have been delivered (step-03). The delivered document is the artifact under review.

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph.
**Input:** The delivered document (`meetings/{...}-talking-points.md`), step-01/02 accumulated-context, and the source strategy/notes the points cite (identity/VOICE.md, knowledge-layer entries, agent-domain data)
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's delivered points and the source material they claim to draw from.
- This step does not re-write the points. It checks whether each point's evidence and sourcing hold up.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be corrected before the event.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/talking-points-verification/workflow.md
   Manifest:
     deliverable: meetings/{...}-talking-points.md
     step-context: workflows/talking-points/state.yaml (accumulated-context)
     voice-profile: identity/VOICE.md
     source-material: knowledge-layer entries and agent-domain data the points cite
     run-date: <YYYY-MM-DD>
   Task: Trace each talking point back to a real source and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Point claim | Source evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ or ➖ → `pass`.
   - Any ⚠️ that is a minor mismatch (e.g., a point whose evidence is thin but sourced) → `flag`.
   - Any ⚠️ that is a fabricated statistic, an invented quote, a position attributed to the executive that no source supports, or a point with no source at all → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py talking-points adversarial-verification step-03-format-and-deliver <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsourced claims, or empty]
       lens: "talking points traced to source strategy/notes; no unsourced claims"
   ```

6. **On `escalate`:** surface to David before the workflow is marked complete: `[Harper]: Talking-points verification found [N] issue(s): [summary]. Do not deliver [point] as-is.` Record the finding and mark the workflow complete with the escalation noted, the event may be imminent.
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

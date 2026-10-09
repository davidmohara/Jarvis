---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Cross-Check the Deliverables Against the Episode Inputs

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/podcast-prep-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent (Harper) grade its own deliverables. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before declaring the workflow complete.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit the deliverables to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state and the actual files. He does not fix, re-run, or re-write anything.
6. This step runs after the PDF has been generated (step-05). Both deliverables are the artifacts under review.

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph.
**Input:** The detailed prep sheet (`meetings/podcast-prep/YYYY-MM-DD-guest-name.md`), the PDF-format markdown (`Episode {N}.md`), the rendered PDF (`Episode {N}.pdf`), step-01/02 accumulated-context (episode inputs and `sources_used`)
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's episode deliverables and the inputs they were built from.
- This step does not re-write the deliverables. It checks that both deliverables exist, are substantive, and actually reflect the episode inputs.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be corrected before filming.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/podcast-prep-verification/workflow.md
   Manifest:
     detailed-sheet: meetings/podcast-prep/YYYY-MM-DD-guest-name.md
     pdf-markdown: meetings/podcast-prep/Episode {N}.md
     pdf-rendered: meetings/podcast-prep/Episode {N}.pdf
     step-context: workflows/podcast-prep/state.yaml (accumulated-context, sources_used)
     run-date: <YYYY-MM-DD>
   Task: Cross-check the episode deliverables against the episode inputs and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Deliverable claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ or ➖ → `pass`.
   - Any ⚠️ that is a minor mismatch (e.g., a missing follow-up prompt) → `flag`.
   - Any ⚠️ that is a missing deliverable, an empty/thin PDF, a guest name that does not match the episode inputs, or questions invented where a real source existed → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py podcast-prep adversarial-verification step-05-generate-pdf <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "prep-sheet completeness vs episode inputs; reference sheet + PDF both exist and are substantive"
   ```

6. **On `escalate`:** surface to David before the workflow is marked complete: `[Harper]: Podcast prep verification found [N] issue(s): [summary]. Do not film from these until corrected.` Record the finding and mark the workflow complete with the escalation noted, filming may be imminent.
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

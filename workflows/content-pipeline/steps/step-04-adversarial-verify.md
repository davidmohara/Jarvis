---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 04: Adversarial Verification: End-to-End Accounting Across the Pipeline

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/content-pipeline-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own accounting. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before closing the run.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit `pending-drafts.json` or any step output to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state (the Slack pull, the shared `pending-drafts.json`, the Ghost post records). He does not fix, re-run, or re-write anything.

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph.
**Input:** The run's `outputs` (step-01/step-02 frontmatter), `workflows/content-approval/pending-drafts.json` (shared state file), the #content Slack pull, the live Ghost post records
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's end-to-end accounting: every discovered item, every approved item, and every published item, with no silent drops.
- This step does not re-draft, re-approve, or re-publish. It checks whether each item is accounted for across the pipeline.
- Findings are a report, not a retry. A finding is surfaced and recorded.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/content-pipeline-verification/workflow.md
   Manifest:
     discover-step: workflows/content-pipeline/steps/step-01-discover.md (frontmatter outputs)
     approve-step: workflows/content-pipeline/steps/step-02-approve.md (frontmatter outputs)
     pending-drafts: workflows/content-approval/pending-drafts.json
     state: workflows/content-pipeline/state.yaml
     run-date: <YYYY-MM-DD>
   Task: Account for every item from discovered through approved to published, flag any silent drop, and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Pipeline claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified or not-applicable → `pass`.
   - Any minor mismatch (e.g., a count off by one, a stalled item not surfaced) → `flag`.
   - Any silent drop (an item discovered but absent from `pending-drafts.json`, an approved item never published and never explained, a `pending-drafts.json` entry with no Ghost post) → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py content-pipeline adversarial-verification step-03-git-finalize <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-accounted" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of silent drops or unsupported claims, or empty]
       lens: "end-to-end accounting; discovered to approved to published, zero silent drops"
   ```

6. **On `escalate`:** halt and surface to David: `[Harper]: Content pipeline verification found [N] unaccounted item(s): [summary]. Holding for your review.` Wait for instruction.

7. **On `pass` or `flag`:** update step frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`) and state.yaml (`current-step: null`), then close the run.

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

This is the final step in content-pipeline. The workflow is complete for this run. On `escalate`, halt and wait for David's decision.
<!-- personal:end -->

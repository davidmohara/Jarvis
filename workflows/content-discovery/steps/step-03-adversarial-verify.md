---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 03: Adversarial Verification: Cross-Check the Drafts Against the Slack/Digest Source

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/content-discovery-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own drafts. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before closing the run.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit a draft or the pending-drafts.json entry to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state (the Slack pull, the digest text, `pending-drafts.json`, the Ghost post records). He does not fix, re-run, or re-write anything.

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph.
**Input:** This run's `outputs` (step-01 frontmatter), `workflows/content-approval/pending-drafts.json`, the #content Slack pull, the digest text for any digest-path draft
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's discovery output: every draft claimed, every skip claimed, and the entries appended to `pending-drafts.json`.
- This step does not re-draft or re-scan. It checks whether each claim holds up against the source data.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be acted on before the next run.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/content-discovery-verification/workflow.md
   Manifest:
     discovery-step: workflows/content-discovery/steps/step-01-discover.md (frontmatter outputs)
     pending-drafts: workflows/content-approval/pending-drafts.json
     state: workflows/content-discovery/state.yaml
     run-date: <YYYY-MM-DD>
   Task: Cross-check the discovery run's draft/skip claims against the Slack pull and the digest source, and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Discovery claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified or not-applicable → `pass`.
   - Any minor mismatch (e.g., a count off by one, a skip noted without the source URL) → `flag`.
   - Any fabricated draft (a post claimed against a digest item that does not exist in the pull), a claimed skip with no matching source message, or a `pending-drafts.json` entry with no corresponding Slack notification → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py content-discovery adversarial-verification step-02-git-finalize <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "draft claims vs Slack/digest source; every draft traced to a real digest item, no invented angles"
   ```

6. **On `escalate`:** halt and surface to David: `[Harper]: Content discovery verification found [N] issue(s): [summary]. Nothing was published; holding for your review.` Wait for instruction.

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

This is the final step in content-discovery. The workflow is complete for this run. On `escalate`, halt and wait for David's decision.
<!-- personal:end -->

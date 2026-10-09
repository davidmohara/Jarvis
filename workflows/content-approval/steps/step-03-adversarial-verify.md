---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 03: Adversarial Verification: Cross-Check Approval State Against Ghost Reality

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/content-approval-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own publishing work. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before closing the run.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit `pending-drafts.json` or a Slack message to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state (the Slack approval replies, the Ghost post records, `pending-drafts.json`). He does not publish, delete, or re-write anything.

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph.
**Input:** This run's `outputs` (step-01 frontmatter), `workflows/content-approval/pending-drafts.json`, the #content Slack thread replies, the live Ghost post records
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's approval cycle: every publish claimed, every reject claimed, every edit/regeneration claimed, and the resulting `pending-drafts.json` status transitions.
- This step does not publish, delete, or re-edit. It checks whether each status claim matches Ghost's actual state.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be acted on before the next run.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/content-approval-verification/workflow.md
   Manifest:
     approve-step: workflows/content-approval/steps/step-01-approve.md (frontmatter outputs)
     pending-drafts: workflows/content-approval/pending-drafts.json
     state: workflows/content-approval/state.yaml
     run-date: <YYYY-MM-DD>
   Task: Cross-check every publish/reject/edit status claim against the live Ghost post state and the Slack approval replies, and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Approval claim | Ghost/recorded state | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified or not-applicable → `pass`.
   - Any minor mismatch (e.g., a stale `pending-drafts.json` status that Ghost contradicts but that carries no publish consequence) → `flag`.
   - Any claim that a draft is `published` while Ghost still shows `draft`, a publish with no `[PUBLISHED]` Slack confirmation, a publish without a matching David approval reply, or a `published` entry not removed from `pending-drafts.json` → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py content-approval adversarial-verification step-02-git-finalize <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "approval state vs Ghost reality; every 'published' status claim matched to the live Ghost post record"
   ```

6. **On `escalate`:** halt and surface to David: `[Harper]: Content approval verification found [N] issue(s): [summary]. Holding for your review.` Wait for instruction.

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
| Ghost API unreachable during verification | Ralph marks Ghost-dependent rows Unverified with note "Ghost unreadable"; record the partial result. Do not suppress it. |
| `guardrail-checkpoint.py` fails to write | Still write the verdict summary to state.yaml; note the recording gap in the closing summary. |

---

## NEXT STEP

This is the final step in content-approval. The workflow is complete for this run. On `escalate`, halt and wait for David's decision.
<!-- personal:end -->

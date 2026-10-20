---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

<!-- personal:start -->
# Step 03: Adversarial Verification: Cross-Check Tracker State Against Ghost Reality

> Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters below.

## Parameters

| Parameter | Value |
|-----------|-------|
| Workflow | content-approval |
| Agent | Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph. |
| Verification workflow | `workflows/content-approval-verification/workflow.md` |
| Previous step | step-02-git-finalize |
| Checkpoint name | adversarial-verification |
| Lens | tracker state vs Ghost reality; every `pending-drafts.json` status matched to the live Ghost post record, every claimed editorial edit traced to the post |
| Scope | this run's resync/edit cycle: every resync status transition claimed, every cleanup removal claimed, every editorial edit claimed, and the resulting `pending-drafts.json` state |
| Ralph task | Cross-check every resync/cleanup/edit claim against the live Ghost post state and the Slack thread replies, and return your verdict table |
| Verdict columns | Item, Run claim, Ghost/recorded state, Verdict |
| Escalate conditions | any entry tracked as `pending` that Ghost shows as `published` or `scheduled`-past, any `published` entry not removed from `pending-drafts.json`, or any claimed editorial edit not present in the live post |
| Escalate message | `[Harper]: Content approval verification found [N] issue(s): [summary]. Holding for your review.` |
| Workflow-specific failure mode | Ghost API unreachable during verification: Ralph marks Ghost-dependent rows Unverified with note "Ghost unreadable"; record the partial result. Do not suppress it. |

**Manifest fields:**

```
approve-step: workflows/content-approval/state.yaml (accumulated-context outputs)
pending-drafts: workflows/content-approval/pending-drafts.json
state: workflows/content-approval/state.yaml
run-date: <YYYY-MM-DD>
```

**Checkpoint command:**

```bash
python3 systems/eval-harness/guardrail-checkpoint.py content-approval adversarial-verification step-02-git-finalize <pass|flag|escalate> "<one-line reason>"
```

---

## NEXT STEP

This is the final step in content-approval. The workflow is complete for this run. On `escalate`, halt and wait for David's decision.
<!-- personal:end -->

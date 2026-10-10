---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 03: Adversarial Verification: Cross-Check Approval State Against Ghost Reality

> Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters below.

## Parameters

| Parameter | Value |
|-----------|-------|
| Workflow | content-approval |
| Agent | Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph. |
| Verification workflow | `workflows/content-approval-verification/workflow.md` |
| Previous step | step-02-git-finalize |
| Checkpoint name | adversarial-verification |
| Lens | approval state vs Ghost reality; every 'published' status claim matched to the live Ghost post record |
| Scope | this run's approval cycle: every publish claimed, every reject claimed, every edit/regeneration claimed, and the resulting `pending-drafts.json` status transitions |
| Ralph task | Cross-check every publish/reject/edit status claim against the live Ghost post state and the Slack approval replies, and return your verdict table |
| Verdict columns | Item, Approval claim, Ghost/recorded state, Verdict |
| Escalate conditions | any claim that a draft is `published` while Ghost still shows `draft`, a publish with no `[PUBLISHED]` Slack confirmation, a publish without a matching David approval reply, or a `published` entry not removed from `pending-drafts.json` |
| Escalate message | `[Harper]: Content approval verification found [N] issue(s): [summary]. Holding for your review.` |
| Workflow-specific failure mode | Ghost API unreachable during verification: Ralph marks Ghost-dependent rows Unverified with note "Ghost unreadable"; record the partial result. Do not suppress it. |

**Manifest fields:**

```
approve-step: workflows/content-approval/steps/step-01-approve.md (frontmatter outputs)
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

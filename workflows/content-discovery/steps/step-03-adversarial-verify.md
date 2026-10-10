---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 03: Adversarial Verification: Cross-Check the Drafts Against the Slack/Digest Source

> Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters below.

## Parameters

| Parameter | Value |
|-----------|-------|
| Workflow | content-discovery |
| Agent | Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph. |
| Verification workflow | `workflows/content-discovery-verification/workflow.md` |
| Previous step | step-02-git-finalize |
| Checkpoint name | adversarial-verification |
| Lens | draft claims vs the Slack/digest source; every draft traced to a real digest item or source URL, no invented angles |
| Scope | this run's discovery output: every draft claimed, every skip claimed, and the entries appended to `pending-drafts.json` |
| Ralph task | Cross-check the discovery run's draft/skip claims against the Slack pull and the digest source, and return your verdict table |
| Verdict columns | Item, Discovery claim, Recorded evidence, Verdict |
| Escalate conditions | any fabricated draft (a post claimed against a digest item that does not exist in the pull), a claimed skip with no matching source message, or a `pending-drafts.json` entry with no corresponding Slack notification |
| Escalate message | `[Harper]: Content discovery verification found [N] issue(s): [summary]. Nothing was published; holding for your review.` |

**Manifest fields:**

```
discovery-step: workflows/content-discovery/steps/step-01-discover.md (frontmatter outputs)
pending-drafts: workflows/content-approval/pending-drafts.json
state: workflows/content-discovery/state.yaml
run-date: <YYYY-MM-DD>
```

**Checkpoint command:**

```bash
python3 systems/eval-harness/guardrail-checkpoint.py content-discovery adversarial-verification step-02-git-finalize <pass|flag|escalate> "<one-line reason>"
```

---

## NEXT STEP

This is the final step in content-discovery. The workflow is complete for this run. On `escalate`, halt and wait for David's decision.
<!-- personal:end -->

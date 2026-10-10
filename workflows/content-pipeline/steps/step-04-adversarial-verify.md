---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 04: Adversarial Verification: End-to-End Accounting Across the Pipeline

> Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters below.

## Parameters

| Parameter | Value |
|-----------|-------|
| Workflow | content-pipeline |
| Agent | Harper, spawned by the coordinator, never executed inline. Harper spawns Ralph. |
| Verification workflow | `workflows/content-pipeline-verification/workflow.md` |
| Previous step | step-03-git-finalize |
| Checkpoint name | adversarial-verification |
| Lens | end-to-end accounting; discovered to approved to published, zero silent drops |
| Scope | this run's end-to-end accounting: every discovered item, every approved item, and every published item, with no silent drops |
| Ralph task | Account for every item from discovered through approved to published, flag any silent drop, and return your verdict table |
| Verdict columns | Item, Pipeline claim, Recorded evidence, Verdict |
| Escalate conditions | any silent drop (an item discovered but absent from `pending-drafts.json`, an approved item never published and never explained, a `pending-drafts.json` entry with no Ghost post) |
| Escalate message | `[Harper]: Content pipeline verification found [N] unaccounted item(s): [summary]. Holding for your review.` |

**Manifest fields:**

```
discover-step: workflows/content-pipeline/steps/step-01-discover.md (frontmatter outputs)
approve-step: workflows/content-pipeline/steps/step-02-approve.md (frontmatter outputs)
pending-drafts: workflows/content-approval/pending-drafts.json
state: workflows/content-pipeline/state.yaml
run-date: <YYYY-MM-DD>
```

**Checkpoint command:**

```bash
python3 systems/eval-harness/guardrail-checkpoint.py content-pipeline adversarial-verification step-03-git-finalize <pass|flag|escalate> "<one-line reason>"
```

---

## NEXT STEP

This is the final step in content-pipeline. The workflow is complete for this run. On `escalate`, halt and wait for David's decision.
<!-- personal:end -->

# Impact Analysis: workflows/content-approval

Date: 2026-10-20
Note: reconstructed and persisted 2026-10-20 evening, after the boot-window run (16:59-17:16 UTC) gated the content-approval rework without persisting this file (the skill then had no persistence mandate; it does now). The searches below were re-run live at persist time; the reference set matches what gated the edits.

## Direct references found in 29 files

### Workflow orchestrators (12)
- workflows/content-approval-verification/workflow.md
- workflows/content-discovery/workflow.md
- workflows/content-discovery-verification/workflow.md
- workflows/content-pipeline/workflow.md
- workflows/content-pipeline-verification/workflow.md

### Workflow steps (15)
- workflows/content-approval-verification/steps/step-01-verify.md
- workflows/content-discovery/steps/step-01-discover.md, step-02-git-finalize.md, step-03-adversarial-verify.md
- workflows/content-discovery-verification/steps/step-01-verify.md
- workflows/content-pipeline/steps/step-01-discover.md, step-02-approve.md, step-03-git-finalize.md, step-04-adversarial-verify.md
- workflows/content-pipeline-verification/steps/step-01-verify.md
- workflows/system-eval/steps/step-03-grade.md
- plus verify scripts: workflows/content-discovery/verify/step-01-discover.py, step-02-git-finalize.py; workflows/content-pipeline/verify/step-01-discover.py, step-02-approve.py

### Agent files (2)
- agents/adversarial-isolation.md
- agents/references/master-workflow-registry.md

### Skills (2)
- skills/delivery-router/SKILL.md
- skills/schema-validator/SKILL.md

### State/config (4)
- workflows/conventions-migration/state.yaml, state-baseline-findings.json, state-close-findings.json
- workflows/content-approval-verification/state.yaml

### References (2)
- workflows/content-discovery/references/ghost-conventions.md, pending-drafts-schema.md

Total direct matches across the search scope: 45 lines in 29 files (excluding the target directory itself).

## Assessment

Proceed with caution: 29 files reference `content-approval`. The rework that shipped (content-approval hardening, eval-20261020T165826-CFTG2B) edited the target with the fence/JSON/parse checks clean and no cascading breaks observed across the referencing set.

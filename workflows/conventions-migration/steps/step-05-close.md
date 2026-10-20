---
status: complete
started-at: 2026-10-20
completed-at: 2026-10-20
---

<!-- system:start -->
# Step 05: Close

1. Re-run the linter report mode; save findings to `state-close-findings.json` and diff against the baseline. Any rule whose count went UP is a regression — investigate before closing.
2. Re-run the census; compare distributions against the baseline in state.yaml.
3. FAIL count must be zero. If it is not, the sweep is incomplete — say so plainly rather than closing.
4. Report: findings fixed by shape, exceptions recorded (with approval status), rejected drafts, WARN count remaining and why, census delta.
5. Update `workflows/conventions-migration/state.yaml` and surface the report to the controller.
<!-- system:end -->

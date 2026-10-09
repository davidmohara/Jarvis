---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Render + Validate

## MANDATORY EXECUTION RULES

1. The render script runs a hard schema validation before rendering. If it exits with code 1, read the error output, fix the run JSON, and re-run.
2. Do not proceed to step 08 until render exits cleanly with `✓ Schema validation passed`.

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** `systems/political-monitor/runs/YYYY-MM-DD.json`
**Output:** A validated `dashboard.html`

---

## YOUR TASK

Run `python3 systems/political-monitor/render.py systems/political-monitor/runs/YYYY-MM-DD.json`. The script runs a **hard schema validation before rendering** — if it exits with code 1, read the error output, fix the run JSON, and re-run. Do not proceed to step 8 until render exits cleanly with `✓ Schema validation passed`. Confirm the written `dashboard.html` has shared cards with gauges and relevance badges, both gap panels ordered by relevance, the muted-source note, and working links.

## NEXT STEP

Read fully and follow: `step-08-send-dashboard.md`
<!-- system:end -->

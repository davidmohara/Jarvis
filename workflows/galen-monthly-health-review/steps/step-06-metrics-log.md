---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Write Monthly Summary to Health Metrics Log

## MANDATORY EXECUTION RULES

1. Populate `summary` with the actual status assessments derived from this review, not defaults.
2. Follow the schema in `data/health/schema.md`.

---

## EXECUTION PROTOCOL

**Agent:** Galen, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** The completed monthly review and its status assessments
**Output:** A `monthly_review` entry appended to `data/health/metrics-log.json`

---

## YOUR TASK

After the Obsidian note is written (Step 05), append a `monthly_review` entry to `data/health/metrics-log.json`.

- Use `entry_id` format: `monthly-review-{YYYY-MM}`
- Set `period` to the month name and year (e.g., "June 2026")
- Populate `summary` with the actual status assessments derived from this review — not defaults
- Set `obsidian_note` to the exact path of the note written in Step 05
- Follow the schema in `data/health/schema.md`

This is the final step before the workflow is marked complete in `state.yaml`.
<!-- system:end -->

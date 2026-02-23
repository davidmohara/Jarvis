---
name: pipeline-review
description: Pipeline health check - stage analysis, risk flags, deal velocity, weighted forecast, recommended actions
agent: chase
---

<!-- system:start -->
# Pipeline Review Workflow

**Goal:** Give the controller a clear picture of pipeline health and exactly which deals need attention this week. No hand-waving, no "pipeline looks good." Numbers, flags, actions.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Sequential 4-step workflow. Pull CRM data, analyze health metrics, flag risks, produce actionable report. No user interaction required until the report is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| CRM (CRM) | Active opportunities — stage, amount, weighted, age, owner, next step, last activity | CRM via Chrome/M365 auth |
| Quarterly objectives | Revenue targets, pipeline rocks | Read context/quarterly-objectives.md |
| Knowledge layer | Recent client meeting notes, deal context | Knowledge base API |
| Calendar | Upcoming client meetings this week | M365 MCP |

### Paths

- `quarterly_objectives` = `{project-root}/context/quarterly-objectives.md`
- `delegation_tracker` = `{project-root}/delegations/tracker.md`

### Key Metrics

| Metric | Definition |
|--------|-----------|
| Weighted pipeline | Sum of (deal amount x stage probability) for all active deals |
| Coverage ratio | Weighted pipeline / remaining quarterly target |
| Deal velocity | Average days spent per stage across all active deals |
| Stale deal | No activity (email, meeting, note) in 14+ days |
| Stage concentration | Any single stage holding > 40% of total pipeline value |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-pull-pipeline.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

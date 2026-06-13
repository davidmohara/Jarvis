---
name: delegation-tracker
description: Full view of all active delegations with overdue flags, sortable by person, due date, or status
agent: shep
model: sonnet
---

<!-- system:start -->
# Delegation Tracker Workflow

**Goal:** Give the executive a complete, current picture of every active delegation — who owns what, when it's due, and what's overdue. No dropped balls.

**Agent:** Shep — People, Delegation & Development

**Architecture:** Sequential 3-step workflow. Pull all delegation data from the task management layer, detect overdue and stale items, present the tracker in the requested sort order with summary statistics.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Task management | All active delegations — owner, description, assignment date, due date, status | Task management API |

### View Options (Sort Orders)

| View | Default | Description |
|------|---------|-------------|
| By person | ✓ | Grouped by owner, sorted by due date within group |
| By due date | — | All delegations sorted ascending by due date |
| By status | — | Grouped by status: overdue → due this week → on track → no due date |
| By assignment date | — | Sorted by when the delegation was created |

### Status Definitions

| Status | Meaning |
|--------|---------|
| `active` | In progress, not yet due |
| `overdue` | Past due date, not completed |
| `stale` | No update in 7+ days regardless of due date |
| `completed` | Done — shown only if requested |
| `cancelled` | Dropped — shown only if requested |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-pull-delegations.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

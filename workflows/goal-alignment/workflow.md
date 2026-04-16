---
name: goal-alignment
description: Goal alignment check — maps last 14 days of activity against annual and quarterly goals, detects drift, recommends adjustments
agent: quinn
model: opus
---

<!-- system:start -->
# Goal Alignment Workflow

**Goal:** Tell the executive whether their last two weeks of activity actually moved them toward their stated goals — or not. This is the difference between being busy and being productive. Quantify drift. Identify the gaps. Recommend specific changes.

**Agent:** Quinn — Strategist

**Architecture:** Sequential 3-step workflow. Pull activity for the last 14 calendar days, map against goals, detect drift and produce alignment report. No user interaction required until the report is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Goals and Dreams | Annual and quarterly goals / rocks | Read `identity/GOALS_AND_DREAMS.md` |
| Task management | Completed tasks in last 14 days | Task management API — `tasks/todos/`, `tasks/delegations/` |
| Knowledge layer | Meeting notes, decisions, interactions in last 14 days | Knowledge base API — `context/` |

### Paths

- `goals_and_dreams` = `{project-root}/identity/GOALS_AND_DREAMS.md`
- `todos_dir` = `{project-root}/tasks/todos/`
- `delegations_dir` = `{project-root}/tasks/delegations/`
- `knowledge_layer` = `{project-root}/context/`

### Analysis Window

- **14 calendar days** ending today
- Include completed tasks and knowledge layer entries within this window

### Drift Definition

- Drift exists when **> 30%** of completed tasks in the last 14 days do not map to any defined annual or quarterly goal
- A task maps to multiple goals: it is credited to ALL applicable goals
- Output shows each goal with: aligned task count, effort percentage, drift items listed separately
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-load-goals-and-activity.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

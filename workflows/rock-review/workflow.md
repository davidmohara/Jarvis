---
name: rock-review
description: Quarterly rock review — evidence-based status assessment with risk flags, corrective actions, and knowledge layer update
agent: quinn
model: opus
---

<!-- system:start -->
# Rock Review Workflow

**Goal:** Give the executive an honest, evidence-based picture of quarterly rock progress. No self-reported status accepted. Assess each rock against the elapsed quarter timeline, flag dependencies, recommend corrective actions, and write updated status to the knowledge layer.

**Agent:** Quinn — Strategist

**Architecture:** Sequential 4-step workflow. Load rocks, gather evidence, classify status, deliver report and update knowledge layer. No user interaction required until the report is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Goals and Dreams | Quarterly rocks — title, description, target, dependencies | Read `identity/GOALS_AND_DREAMS.md` |
| Task management | Task completions mapped to rocks | Task management API |
| Knowledge layer | Progress entries, review history, initiative updates | Knowledge base API |
| Initiative tracker | Initiative status linked to rocks | Read `tasks/initiatives/` |

### Paths

- `goals_and_dreams` = `{project-root}/identity/GOALS_AND_DREAMS.md`
- `knowledge_layer` = `{project-root}/context/`
- `initiatives_dir` = `{project-root}/tasks/initiatives/`

### Rock Status Thresholds

| Status | Criterion |
|--------|-----------|
| `on-track` | Progress >= 70% of expected for elapsed quarter time |
| `at-risk` | Progress 40%–69% of expected |
| `blocked` | Active blocker present preventing forward progress |
| `completed` | Rock fully achieved |

### Evidence Sources (in priority order)

1. Task completions mapped to rocks in task management
2. Knowledge layer entries referencing rock or initiative
3. Initiative tracker status and last-update date
4. Calendar activity relevant to rock (meetings, reviews)
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-load-rocks.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

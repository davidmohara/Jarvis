---
name: initiative-tracker
description: Initiative tracker — living view of all strategic initiatives with status, owners, blockers, dependencies, and cross-agent escalation
agent: quinn
model: opus
---

<!-- system:start -->
# Initiative Tracker Workflow

**Goal:** Give the executive a clear, honest picture of every strategic initiative — what's moving, what's stuck, who owns it, and what needs a decision. Surface blockers with unblocking paths. Flag revenue-impacting initiatives for Chase escalation.

**Agent:** Quinn — Strategist

**Architecture:** Sequential 4-step workflow. Load initiatives, analyze blockers and dependencies, escalate revenue-impacting items to Chase, deliver prioritized report. No user interaction required until the report is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Task management | All initiative entries — status, owners, next actions, blockers, dependencies | Read `tasks/initiatives/` |
| Knowledge layer | Context entries for each initiative | Knowledge base API — `memory/episodic/projects/` |
| Cross-agent | Revenue context from Chase for revenue-impacting initiatives | Cross-agent handoff pattern |

### Paths

- `initiatives_dir` = `{project-root}/tasks/initiatives/`
- `knowledge_layer_projects` = `{project-root}/memory/episodic/projects/`

### Initiative Status Values (from shared-definitions.md)

| Status | Meaning |
|--------|---------|
| `planned` | Defined but not started |
| `active` | In progress |
| `at-risk` | Behind schedule or approaching blocker |
| `blocked` | Cannot proceed |
| `completed` | Delivered |
| `cancelled` | Abandoned |

### Dependency Classification

| Type | Meaning |
|------|---------|
| `blocking` | This dependency must complete before the initiative can advance |
| `informational` | This dependency provides context but does not block |
| `shared-resource` | Both initiatives rely on the same person or resource |

### Stale Threshold

An initiative is stale when no status update or activity has been recorded for 14+ calendar days, regardless of due date (see shared-definitions.md#Stale Commitment).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-load-initiatives.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

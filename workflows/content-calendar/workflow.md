---
name: content-calendar
description: Content calendar manager — load, track, and deliver the executive's thought leadership pipeline with deadline management and topic recommendations
agent: harper
model: sonnet
---

<!-- system:start -->
# Content Calendar Workflow

**Goal:** Give the executive a clear, current view of their thought leadership pipeline — every commitment, every deadline, every gap. Surface overdue and approaching items. Recommend new topics from expertise and strategy. Keep everything synced to the task management layer.

**Agent:** Harper — Storyteller, Communication, Content & Thought Leadership

**Architecture:** Sequential 4-step workflow. Load content data from task management and calendar → flag deadlines (overdue and approaching, 3-business-day threshold) → generate topic recommendations from expertise and strategic themes → deliver chronological calendar view with task sync.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Content Item Schema

Every content item tracked by Harper has these fields:

| Field | Values |
|-------|--------|
| `type` | `article`, `talk`, `podcast`, `social-post` |
| `topic` | Description of the content |
| `deadline` | YYYY-MM-DD |
| `status` | `draft`, `scheduled`, `published`, `cancelled` |
| `next_action` | What needs to happen next |
| `calendar_event_id` | Linked calendar event (if event-linked content like a talk) |

### Deadline Thresholds

| Status | Criterion |
|--------|-----------|
| `overdue` | Deadline has passed and status is not `published` or `cancelled` |
| `approaching` | Deadline is within 3 business days and status is `draft` or `scheduled` |
| `on-track` | Deadline is more than 3 business days away |
| `no-deadline` | No deadline set — prompt to assign one |

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Task management | All content commitments stored as tasks | Task management API |
| Calendar MCP | Event-linked content (talks, podcasts, appearances) | M365 / Google Calendar |
| Knowledge layer | Executive expertise tags, past content themes | Knowledge base API |
| Quinn domain | Current strategic themes and quarterly rocks | Quinn context |

### Paths

- `tasks_dir` = `{project-root}/tasks/todos/`
- `knowledge_layer` = `{project-root}/memory/`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow these steps in order:
1. `steps/step-01-load-content-data.md`
2. `steps/step-02-deadline-management.md`
3. `steps/step-03-content-recommendations.md`
4. `steps/step-04-deliver-calendar.md`
5. `steps/step-05-git-finalize.md` (final: commits all state to git)
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

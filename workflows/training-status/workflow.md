---
name: training-status
description: Training dashboard — load progress, render by domain, suggest next capability
agent: shep
---

<!-- system:start -->
# Training Status Workflow

**Goal:** Render a comprehensive progress dashboard showing what the user has learned, what's in progress, and what's next.

**Agent:** Shep — Coach & Development

**Architecture:** Sequential 2-step workflow. Load all state data, then render the dashboard. No user interaction required — this is a read-only report.

**Critical Rule:** Group modules by capability domain (Daily operations, People & coaching, etc.), never by agent name. Use display_names only.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Progress state | Tier, completion %, session count, streak | Read training/state/progress.json |
| Mastery state | Per-module attempts, skill levels | Read training/state/mastery.json |
| Curriculum | All modules, display_names, tiers | Read training/curriculum.json |
| User config | Role, preferences | Read training/state/config.json |

### Paths

- `curriculum` = `{project-root}/training/curriculum.json`
- `state_path` = `{project-root}/training/state/`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-load-progress.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

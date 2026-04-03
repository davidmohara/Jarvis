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
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-load-progress.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

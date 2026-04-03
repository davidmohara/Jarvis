---
name: training-module-runner
description: Generic module runner — load curriculum entry, coach through guided walkthrough with real data, record mastery
agent: shep
---

<!-- system:start -->
# Training Module Runner Workflow

**Goal:** Coach the user through a single training module using their real data. Record the result to mastery tracking.

**Agent:** Shep — Coach & Development

**Architecture:** Sequential 5-step workflow. Loads the module definition from curriculum, runs the guided walkthrough with actual data, captures reflection, and records mastery state. This workflow is invoked by the shep-training skill in Run Module mode.

**Critical Rule:** Frame everything as capabilities. Never expose agent names, module IDs, or internal terminology to the user.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Curriculum | Module definition, display_name, guided_file path | Read training/curriculum.json |
| Guided walkthrough | Step-by-step coaching content | Read from module's guided_file path |
| Mastery state | Previous attempts for this module | Read training/state/mastery.json |
| Progress state | Current tier, session count, streak | Read training/state/progress.json |
| User config | Role, preferences, connectors | Read training/state/config.json |

### Input

- `module_identifier` — Either the module ID (e.g., "chief-morning") or display_name (e.g., "Morning Briefings"). Match flexibly.

### Paths

- `curriculum` = `{project-root}/training/curriculum.json`
- `state_path` = `{project-root}/training/state/`
- `modules_path` = `{project-root}/training/modules/`
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

Read fully and follow: `steps/step-01-load-module.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

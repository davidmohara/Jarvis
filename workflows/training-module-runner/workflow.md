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
| Curriculum | Module definition, display_name, guided_file path | Read systems/training/curriculum.json |
| Guided walkthrough | Step-by-step coaching content | Read from module's guided_file path |
| Mastery state | Previous attempts for this module | Read systems/training/state/mastery.json |
| Progress state | Current tier, session count, streak | Read systems/training/state/progress.json |
| User config | Role, preferences, connectors | Read systems/training/state/config.json |

### Input

- `module_identifier` — Either the module ID (e.g., "chief-morning") or display_name (e.g., "Morning Briefings"). Match flexibly.

### Paths

- `curriculum` = `{project-root}/systems/training/curriculum.json`
- `state_path` = `{project-root}/systems/training/state/`
- `modules_path` = `{project-root}/systems/training/modules/`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-load-module.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

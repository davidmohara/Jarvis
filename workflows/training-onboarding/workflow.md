---
name: training-onboarding
description: First-launch onboarding — intake interview, system orientation, first real task, progression intro
agent: shep
---

<!-- system:start -->
# Training Onboarding Workflow

**Goal:** Take a new user from zero to running their first real task in a single session. Set up their training state, orient them to the system's capabilities, and give them a clear path forward.

**Agent:** Shep — Coach & Development

**Architecture:** Sequential 4-step workflow. Each step builds on the previous. User interaction required throughout — this is a coached conversation, not an automated pipeline.

**Important:** Frame everything as capabilities, not agent names. The user should leave knowing what the system can DO, not which internal component does it.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Training state | config.json, progress.json, mastery.json | Read systems/training/state/ |
| Curriculum | Module index, tiers, pacing rules | Read systems/training/curriculum.json |
| Orientation module | System orientation walkthrough | Read systems/training/modules/system/orientation.md |
| Identity files | Current user context if available | Read identity/ |

### Paths

- `training_root` = `{project-root}/systems/training/`
- `state_path` = `{project-root}/systems/training/state/`
- `curriculum` = `{project-root}/systems/training/curriculum.json`
- `orientation_module` = `{project-root}/systems/training/modules/system/orientation.md`

### Pre-check

Before starting, verify:
1. `state/config.json` exists (should be template)
2. `state/config.json.onboarded` is null (not already onboarded)
3. If already onboarded, inform user and offer `/training-status` instead
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-user-intake.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
step: 1
name: Load Progress
next: step-02-render-dashboard.md
---

<!-- system:start -->
# Step 1: Load Progress

**Goal:** Load all training state data needed for the dashboard.

## Process

### 1.1 Read State Files

Load:
- `training/state/progress.json` — tier, completion %, category counts, streak
- `training/state/mastery.json` — per-module mastery data
- `training/curriculum.json` — full module list with display_names

### 1.2 Build Module Status Map

For every module in curriculum.json, determine its status:

1. **Mastered** — Module exists in mastery.json with `skill_level: "mastered"`
2. **Tried** — Module exists in mastery.json with `skill_level: "tried"` or `"practicing"`
3. **Not started** — Module does not exist in mastery.json

### 1.3 Group by Domain

Map modules to capability domains using their `agent` field:

| Agent | Domain Name |
|-------|-------------|
| chief | Daily operations |
| shep | People & coaching |
| quinn | Strategy & goals |
| chase | Revenue & clients |
| harper | Communications |
| null (system/connector) | System operations |

### 1.4 Check for Stale Modules

For each mastered module, calculate days since `last_attempt`:
- If 14+ days → flag for reinforcement

## Next Step

Proceed to `step-02-render-dashboard.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

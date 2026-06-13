---
name: evolution-training-sync
description: Detects new and deprecated components from applied evolutions and integrates them into the training curriculum
agent: shep-training
version: 2.0
model: sonnet
---

<!-- system:start -->
# Evolution Training Sync Workflow

This workflow runs on boot when new evolutions have been applied since the last training sync. It detects new agents and tasks from the evolution manifest, integrates them into the training curriculum, preserves all existing progress, and surfaces discovery prompts for newly available capabilities.

## Entry Point

Begin at `steps/step-01-detect-new-components.md`.

## Data Sources

| Source | Path | Purpose |
|--------|------|---------|
| Evolution manifest | `evolution.manifest.json` | Registry of all applied evolutions and current components |
| Curriculum | `training/curriculum.json` | Module registry, tier assignments, pacing rules |
| Progress | `training/state/progress.json` | Executive's completion %, tier, session count |
| Mastery | `training/state/mastery.json` | Per-module attempts and skill levels |

## Invocation Triggers

| Trigger | When | Called By |
|---------|------|-----------|
| `boot` | New evolutions detected on boot | Boot sequence step 8 (training check) |
| `manual` | Implementer-requested resync | Direct invocation |

## Workflow Steps

1. `steps/step-01-detect-new-components.md` — Scan evolution manifest; identify new agents/tasks and deprecated tasks not yet reflected in curriculum.json
2. `steps/step-02-integrate-into-curriculum.md` — Add new modules to curriculum.json; handle deprecated modules; recalculate progress denominator
3. `steps/step-03-surface-discoveries.md` — Generate "New capability available" discovery prompts; surface at boot using display_name framing

## Failure Handling

If this workflow fails at any step:
- Log: "Evolution training sync failed — training curriculum may not reflect latest evolution"
- Do NOT block boot sequence
- Continue with existing training state
- Retry on next boot

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

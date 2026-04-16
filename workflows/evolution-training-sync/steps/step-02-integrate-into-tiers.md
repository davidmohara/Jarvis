---
step: 2
name: integrate-into-curriculum
workflow: evolution-training-sync
model: sonnet
---

<!-- system:start -->
# Step 2 — Integrate into Curriculum

## Purpose

Add new modules to `training/curriculum.json`, handle deprecated modules, recalculate the completeness denominator, and preserve all existing progress in `training/state/progress.json`.

---

## Actions

### 2A. Skip if no sync needed

If `sync_needed = false` from Step 1, skip this step entirely and proceed to Step 3.

---

### 2B. Assign new agents to tiers

For each new agent in `new_agents`:

**Tier assignment rule:**

1. Read `training/state/progress.json` → get current `tier`
2. Map tier name to tier index: Getting Started=0, Building Rhythm=1, Strategic Mode=2, Full System=3
3. Assign new agent to: tier at `min(current_tier_index + 1, 3)` (one tier above current, capped at Full System)

Store: `{agent_name, assigned_tier_name}` for each new agent.

---

### 2C. Create new module entries

For each new task in `new_tasks`:

1. Determine parent agent from task ID prefix
2. Look up assigned tier (from 2B if agent is new, or from existing module with same agent prefix)
3. Create a new module entry in `curriculum.json.modules`:

```json
{
  "id": "{task_id}",
  "category": "agent",
  "agent": "{agent_name}",
  "task": "{Human-readable task name}",
  "tier": "{assigned_tier_name}",
  "guided_file": "training/modules/agent/{task_id}.md",
  "skill_trigger": "{task_id}",
  "duration_minutes": 15,
  "mastery_threshold": 2,
  "success_criteria": "Use this capability successfully twice",
  "role_notes": {},
  "prerequisites": [],
  "evolution_source": "{evolution_id}",
  "display_name": "{Human-readable display name}",
  "nudge_phrase": "{capability-framed nudge}"
}
```

4. Create a stub guided walkthrough file at `training/modules/agent/{task_id}.md` if it doesn't exist

---

### 2D. Handle deprecated modules

For each deprecated task:

1. Find the module entry in `curriculum.json.modules`
2. Add `"deprecated": true` to the module object
3. Deprecated modules are excluded from:
   - Recommendation engine
   - Progress denominator
   - Boot nudges
4. Deprecated modules are NOT deleted — they remain in curriculum.json for history

---

### 2E. Recalculate progress

Read `training/state/progress.json`:

- `completion_percent` = existing value
- Count mastered modules from `training/state/mastery.json` (where `skill_level` == "mastered")

Calculate new completeness:

```text
active_modules = count of modules in curriculum.json where deprecated is not true and _template is not true
mastered_count = count of mastered modules in mastery.json
new_completion_percent = round((mastered_count / active_modules) * 100)
```

**Tier preservation rule:** The executive's tier never regresses. If the new percentage would correspond to a lower tier, keep the current tier.

Update `training/state/progress.json`:
- `completion_percent: {new_completion_percent}`
- DO NOT change `tier` (tier is preserved or advances, never regresses)

---

## Failure Mode

If `training/curriculum.json` cannot be written:
- Log: "Could not update curriculum.json — new components not integrated"
- Continue to Step 3 with in-memory data

---

## NEXT STEP

`steps/step-03-surface-discoveries.md`

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

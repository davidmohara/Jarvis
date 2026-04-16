---
step: 1
name: detect-new-components
workflow: evolution-training-sync
model: sonnet
---

<!-- system:start -->
# Step 1 — Detect New Components

## Purpose

Scan `evolution.manifest.json` for new agents and tasks introduced by applied evolutions. Compare against the current contents of `training/curriculum.json` to identify what has not yet been integrated.

---

## Actions

### 1A. Load current training state

1. Read `training/curriculum.json`
2. Extract all currently registered module IDs from the `modules` array
3. Extract all currently registered agent names from the modules (unique `agent` values, excluding null)

Store as:

- `known_module_ids` = set of all module IDs in curriculum.json
- `known_agents` = set of all agent names in curriculum modules
- `current_total_modules` = count of modules where `_template` is not true

---

### 1B. Load evolution manifest

1. Read `evolution.manifest.json`
2. Extract `appliedEvolutions` array — the list of evolutions that have been applied
3. Extract `components.agents.files` — current agent file list
4. Extract `components.skills.files` — current skill file list (skills correspond to tasks)

Store as:

- `applied_evolutions_count` = length of `appliedEvolutions`
- `manifest_agents` = list of agent names derived from agent files (e.g., `agents/chief.md` → `chief`)
  - Exclude: `master`, `rigby` (not training tasks)
- `manifest_tasks` = list of task IDs derived from skill files (e.g., `skills/chief-morning.md` → `chief-morning`)
  - Exclude: `master-*` skills (meta-skills)
  - Exclude: `rigby-*` skills (system operator, not training tasks)

---

### 1C. Detect new agents

Compare `manifest_agents` against `known_agents`.

```text
new_agents = manifest_agents - known_agents
```

For each new agent:
- Store: `{agent_name, agent_file}`

---

### 1D. Detect new tasks

Compare `manifest_tasks` against `known_module_ids`.

```text
new_tasks = manifest_tasks - known_module_ids
```

For each new task:
- Determine parent agent from task ID prefix (e.g., `nova-weekly` → agent = `nova`)
- Store: `{task_id, agent_name}`

---

### 1E. Detect deprecated tasks

Deprecated tasks are module IDs that exist in `known_module_ids` but are no longer present in `manifest_tasks`.

```text
deprecated_tasks = known_module_ids - manifest_tasks
```

Filter: exclude system and connector category modules (they don't map to skill files). Only agent-category modules can be deprecated this way.

---

### 1F. Determine if sync is needed

If ALL of the following are true, there is nothing to sync — skip to Step 3 (display only):

- `new_agents` is empty
- `new_tasks` is empty
- `deprecated_tasks` is empty

Otherwise, store the detected changes and proceed to Step 2.

---

## Failure Mode

If `evolution.manifest.json` cannot be read:
- Log: "Evolution manifest unreadable — skipping evolution training sync"
- Set `sync_needed = false`
- Continue without blocking

If `training/curriculum.json` cannot be read:
- Log: "curriculum.json unreadable — skipping evolution training sync"
- Set `sync_needed = false`
- Continue without blocking

---

## NEXT STEP

`steps/step-02-integrate-into-curriculum.md`

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

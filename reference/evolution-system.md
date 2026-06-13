# Evolution System

## Overview

Evolutions are versioned upgrade packages for IES. Each evolution is a curated set of definition files — agents, workflows, permissions, and configuration — that extend or improve the system without breaking what already exists.

The core design constraint: **personal evolutions are never overwritten by system evolutions.** A user's preferences, directives, and customizations survive every upgrade.

---

## Evolution Types

### System Evolutions

Changes to system function. These are authored and distributed by IES administrators (David / Improving).

**Includes:**

- New agents
- New workflows and workflow steps
- Updates to existing agent personas, task portfolios, or logic
- New or revised permissions
- New tools, integrations, or data sources
- Structural changes to the IES framework itself

**Characteristics:**

- Owned by the IES platform
- Safe to overwrite on upgrade — no user customization lives here by default
- Applied automatically for internal (Improving) deployments; opt-in for client deployments

### Personal Evolutions

User-specific customizations. These are generated during onboarding (Initialization Sequence) and refined over time through direct user instruction.

**Includes:**

- Communication style and tone directives
- Scheduling rules and protected time
- Relationship context (direct reports, clients, key people)
- Tool preferences and integration settings
- Agent personality overrides
- Workflow behavioral preferences (e.g., "always lead with delegations in the morning briefing")
- Any explicit user directive ("never suggest LinkedIn posts on Fridays")

**Characteristics:**

- Owned by the user
- Never overwritten by a system evolution
- Survive all upgrades intact
- Can only be changed by the user directly

---

## Classification Guide

When making a change, use this rubric to determine whether it belongs in a system block or a personal block.

### The Litmus Test

> "Would this change make sense if someone else forked IES with zero knowledge of the current user?"
>
> **Yes → system block.** Author it in the framework repo, propagate via evolution.
> **No → personal block.** Lives only in the user's live instance.

### Decision Matrix

| Signal | → System | → Personal |
|--------|----------|------------|
| New workflow step logic | Generic process improvement | User-specific data sources or thresholds |
| New agent behavior | How the agent *thinks* (priority logic, handoff rules, persona) | What it *connects to* (specific tools, APIs, integrations) |
| New skill | Reusable task any user would want (pipeline review, 1:1 prep) | User-specific task (credit card optimizer, podcast prep) |
| Tool binding | Abstract placeholder (`Calendar API`, `CRM API`) | Concrete binding (`M365 MCP outlook_calendar_search`, `Dynamics 365`) |
| Threshold or heuristic | Framework default (`flag stale items`, `prioritize client meetings`) | User's calibration (`14d for directs, 30d for extended team`) |
| Data source | Generic category (`relationship intelligence`, `task management`) | Specific integration (`Clay MCP`, `OmniFocus via osascript`) |
| Agent personality | Base persona and communication style | Controller directives and overrides |

### File-Level Classification

| File Pattern | Typical Classification | Rationale |
|-------------|----------------------|-----------|
| Agent files (`agents/*.md`) | **Mixed** — system skeleton + personal directives | Agent persona and logic are system; user's tool bindings, thresholds, and additional skills are personal |
| Shared skill files (`.claude/skills/*/SKILL.md`) | **Mixed** — system task + personal tool bindings | What the skill does is system; how it connects to the user's tools is personal |
| Personal-only skill files | **Personal** — entire body wrapped in personal tags | Skills that exist only for one user (e.g., credit card optimizer, podcast prep) |
| Shared workflow files (`workflows/*/workflow.md`) | **Mixed** — system structure + personal data sources | Workflow architecture is system; user-specific data sources or preferences are personal |
| Step files (`workflows/*/steps/*.md`) | **System** — rarely personalized | Step logic is generic; if a user needs a custom step, add a personal block rather than modifying the system step |
| Personal-only workflow files | **Personal** — entire body wrapped in personal tags | Workflows that exist only for one user |

### Grey Area Protocol

When unsure whether a change is system or personal:

1. **Start personal.** Add it to a personal block in the live instance.
2. **Observe.** Use it across a few sessions. Does it prove useful and generalizable?
3. **Promote if warranted.** Extract the generic pattern into the framework repo as a system block. Leave the user-specific bits (tool names, thresholds, calibrations) in the personal block.

This is how integration patterns should evolve: the *concept* of relationship intelligence belongs in system blocks (the framework says "relationship API"), but the specific tool calls, warmth thresholds, and lookup patterns belong in personal blocks.

### Examples

**System evolution:** "Chase should now include competitive landscape analysis in account briefs."
→ This improves the agent's *thinking* for all users. Add to the system Task block.

**Personal evolution:** "Use Clay MCP to look up all contacts at the account by work_history filter."
→ This is a specific tool binding. Add to the personal Tool Bindings block.

**System evolution:** "Add a new step to the weekly review that checks delegation completion rates."
→ Generic process improvement. Add as a new step file in the framework.

**Personal evolution:** "Flag any direct report with no 1:1 in 14+ days as yellow."
→ User-specific threshold. Add to a personal block in the relevant agent or skill.

**Promotion example:** A user adds a personal podcast prep skill. After refinement, the *structure* (guest research → talking points → one-pager) is extracted into the framework as a system skill template. The user's specific podcast name, format preferences, and PDF styling remain in personal blocks.

---

## Delineation in Definition Files

Definition files (agents, workflows, permissions) use **HTML comments** to mark sections as system-owned or personally-owned. This allows a single file to carry both types of content inline — the comment tags are the contract.

### Comment Syntax

```html
<!-- system:start -->
... system-owned content ...
<!-- system:end -->

<!-- personal:start -->
... user-owned content ...
<!-- personal:end -->
```

### Rules

- Content inside `<!-- system:start -->` / `<!-- system:end -->` blocks is **replaceable** by a system evolution.
- Content inside `<!-- personal:start -->` / `<!-- personal:end -->` blocks is **immutable** during system evolution application — it is preserved verbatim.
- Content outside any block is treated as **system-owned** by default.
- Personal blocks may appear anywhere in a file — inline within a section, appended at the end, or interspersed throughout.
- A file may have multiple personal blocks and multiple system blocks.

### Example: Agent File with Both Types

```markdown
# Agent: Chief

<!-- system:start -->
## Metadata

| Field | Value |
|-------|-------|
| **Name** | Chief |
| **Title** | Chief of Staff — Daily Operations & Execution |
| **Module** | IES Core |
| **Capabilities** | Morning briefings, daily reviews, inbox processing, calendar prep |

## Persona

### Role
Executive Chief of Staff specializing in daily operational rhythm...

### Communication Style
Direct, efficient, occasionally sharp. Chief doesn't waste words...
<!-- system:end -->

## Controller Directives

- Always lead the morning briefing with delegations, not calendar
- When flagging overdue items, use plain language — no bullet drama
<!-- personal:start -->
- Never suggest tasks before 8am
- Scott is my most reliable direct report; don't nudge him unless 3+ days overdue
<!-- personal:end -->

<!-- system:start -->
## Task Portfolio

| Trigger | Task | Description |
|---------|------|-------------|
| `morning` | **Morning Briefing** | Calendar review, priority tasks, delegations due... |
<!-- system:end -->

<!-- personal:start -->
## Workflow Overrides

- Morning Briefing: skip the inbox count summary — I process it separately
<!-- personal:end -->
```

### Example: Workflow File with Personal Override

```markdown
---
name: morning-briefing
agent: chief
---

<!-- system:start -->
# Morning Briefing Workflow

**Goal:** Give the controller complete situational awareness for the day ahead.

**Architecture:** Sequential 4-step workflow...
<!-- system:end -->

## Controller Preferences

- Surface the single most important thing first, not a list
<!-- personal:start -->
- Deliver briefing in under 90 seconds of reading — I'm usually on my phone
- If no meetings before 10am, skip the calendar section entirely
<!-- personal:end -->
```

---

## Evolution Manifest

Every evolution is a package described by a **manifest file**. The manifest is the authoritative record of what the evolution contains, what type each file is, and how it should be applied.

### Manifest Format

**Filename:** `evolution.manifest.json`  
**Location:** Root of the evolution package directory

```json
{
  "id": "ies-evolution-2026-03",
  "version": "2026.03",
  "name": "Q1 2026 — Harper Expansion + Pipeline Intelligence",
  "description": "Adds 3 new Harper workflows, upgrades Chase pipeline review with risk scoring, and introduces the Analyst agent (beta).",
  "released": "2026-03-01",
  "type": "system",
  "compatibility": {
    "minimum_base_version": "2026.01"
  },
  "files": [
    {
      "path": "agents/analyst.md",
      "type": "system",
      "action": "add",
      "description": "New Analyst agent — financial and operational intelligence"
    },
    {
      "path": "agents/chase.md",
      "type": "mixed",
      "action": "merge",
      "description": "Updated pipeline review logic and risk scoring. Personal blocks preserved."
    },
    {
      "path": "agents/harper.md",
      "type": "mixed",
      "action": "merge",
      "description": "Expanded task portfolio. Personal blocks preserved."
    },
    {
      "path": "workflows/pipeline-review/workflow.md",
      "type": "system",
      "action": "replace",
      "description": "Full replacement — no personal content expected in this file"
    },
    {
      "path": "workflows/pipeline-review/steps/step-03-risk-scoring.md",
      "type": "system",
      "action": "add",
      "description": "New step — risk scoring engine for pipeline deals"
    },
    {
      "path": "workflows/linkedin-post/workflow.md",
      "type": "system",
      "action": "add",
      "description": "New workflow — LinkedIn post drafting"
    },
    {
      "path": "workflows/speaking-abstract/workflow.md",
      "type": "system",
      "action": "add",
      "description": "New workflow — speaking abstract and bio generation"
    },
    {
      "path": "docs/Permissions.md",
      "type": "mixed",
      "action": "merge",
      "description": "New permissions for Analyst agent. Personal blocks preserved."
    }
  ],
  "changelog": [
    "Added Analyst agent (beta) — financial and operational intelligence",
    "Chase: pipeline risk scoring — deals flagged by age, stage velocity, and executive sponsor gap",
    "Harper: 3 new workflows — LinkedIn post drafting, speaking abstract, podcast prep",
    "Permissions updated for Analyst agent data access"
  ],
  "training_prompts": [
    {
      "agent": "analyst",
      "prompt": "Try the new Analyst — ask it to run a balanced scorecard review"
    },
    {
      "agent": "chase",
      "prompt": "Chase now scores pipeline risk — ask it to flag your at-risk deals"
    },
    {
      "agent": "harper",
      "prompt": "Harper can now draft LinkedIn posts — try 'draft a post about [recent win]'"
    }
  ]
}
```

### File Action Types

| Action | Meaning |
| --- | --- |
| `add` | New file — does not exist in current installation. Write directly. |
| `replace` | Full file replacement. File is system-only (no personal blocks). Safe to overwrite. |
| `merge` | File contains or may contain personal blocks. Apply system sections only; preserve all personal blocks. |
| `delete` | Remove the file. Only valid for system-only files. Never applied to files with personal blocks. |

### File Type Values

| Type | Meaning |
| --- | --- |
| `system` | File contains only system content. No personal blocks present or expected. |
| `personal` | File is entirely user-owned. Never touched by a system evolution. |
| `mixed` | File contains both system and personal blocks. Merge logic applies. |

---

## Application Protocol

How an evolution is applied — the rules that guarantee personal evolutions survive.

### Pre-Application

1. **Validate the manifest** — confirm all listed files exist in the evolution package
2. **Snapshot current state** — create a versioned backup of all files listed in the manifest before any changes
3. **Scan for personal blocks** — for every `merge` file, parse and extract all `<!-- personal:start --> ... <!-- personal:end -->` blocks with their positions
4. **Conflict check** — if a `replace` or `delete` action targets a file that contains personal blocks, **halt and surface for user review** — do not proceed automatically

### Application

For each file in the manifest, apply by action type:

**`add`**

- Write the new file to the target path
- If a file already exists at that path, treat as `merge` and re-evaluate

**`replace`**

- Confirm no personal blocks exist in the current file (pre-application scan)
- Overwrite the file with the evolution version
- If personal blocks are found: halt, surface conflict, do not overwrite

**`merge`**

1. Parse the current file — extract all personal blocks with their surrounding context (section heading, position in file)
2. Write the new system version of the file (from the evolution package)
3. Re-inject each personal block at its original logical position:
   - Match by section heading if the section still exists
   - Append to end of file if the original section no longer exists, with a comment noting the original location
4. Verify all personal blocks are present in the output before finalizing

**`delete`**

- Confirm the file is system-only (no personal blocks)
- Remove the file
- If personal blocks are found: halt, do not delete, surface for user review

### Post-Application

1. **Verify integrity** — confirm all personal blocks from the pre-application scan are present in the post-application files
2. **Record the evolution** — append to `evolutions/history.md` with version, date, files changed, and any conflicts surfaced
3. **Surface changelog** — present the evolution's `changelog` entries to the user as a "What's New" summary
4. **Queue training prompts** — inject the evolution's `training_prompts` into the training system for progressive unlock

### Conflict Resolution

When the protocol halts due to a conflict, the user is presented with:

- The file in question
- The personal block(s) that would be affected
- The proposed system change
- Three options: **Apply system change and preserve personal block**, **Skip this file**, **Review manually**

---

## Evolution Package Structure

```text
evolutions/
  ies-evolution-2026-03/
    evolution.manifest.json
    agents/
      analyst.md
      chase.md
      harper.md
    workflows/
      pipeline-review/
        workflow.md
        steps/
          step-03-risk-scoring.md
      linkedin-post/
        workflow.md
      speaking-abstract/
        workflow.md
    docs/
      Permissions.md
  history.md
```

`history.md` is the running log of all applied evolutions — version, date, files changed, conflicts encountered.

---

## Evolution History Log Format

**Location:** `evolutions/history.md`

```markdown
## IES Evolution 2026.03 — Applied 2026-03-04

**Package:** ies-evolution-2026-03
**Applied by:** auto-deploy (internal)

### Files Changed
- `agents/analyst.md` — added
- `agents/chase.md` — merged (2 personal blocks preserved)
- `agents/harper.md` — merged (1 personal block preserved)
- `workflows/pipeline-review/workflow.md` — replaced
- `workflows/pipeline-review/steps/step-03-risk-scoring.md` — added
- `workflows/linkedin-post/workflow.md` — added
- `workflows/speaking-abstract/workflow.md` — added
- `docs/Permissions.md` — merged (1 personal block preserved)

### Conflicts
None.

### Personal Blocks Preserved
- `agents/chase.md`: Controller Directives (4 items), Workflow Overrides (1 item)
- `agents/harper.md`: Controller Directives (2 items)
- `docs/Permissions.md`: Custom Conventions (3 items)
```

---

## Relationship to the Training System

When an evolution is applied, its `training_prompts` are handed to the Training & Progression System:

- New agents are introduced with a "Try this" prompt at the user's next session
- New workflows are surfaced contextually — if the user's next action is relevant, the new workflow is suggested
- The progression tier system incorporates new capabilities into the user's journey without resetting existing progress

---

## Summary: The Contract

| Rule | Guarantee |
| --- | --- |
| Personal blocks are never overwritten | System evolutions cannot touch `<!-- personal:start/end -->` content |
| Conflicts halt the process | No silent data loss — user reviews before anything destructive proceeds |
| Every evolution is snapshotted before apply | Full rollback available if something goes wrong |
| History is always written | Every applied evolution is logged with what changed and what was preserved |
| Personal-only files are never in a manifest | Files typed `personal` are invisible to the evolution system |

---

---

### Tags

Topic: [[IES]] [[Evolution System]]
Note Type: [[Design]]
Date Created: [[2026-02-23]]
Last Updated: [[2026-02-23]]

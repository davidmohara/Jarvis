---
name: rock1-revenue-monthly
description: Monthly Rock 1 revenue pull. Runs revenue-tracker skill for Dallas and South Texas, then appends a dated snapshot to the Rock 1 tracking file in Obsidian. Triggered automatically on the 11th of each month. Includes a recency gate — will not double-write if a snapshot for the current month already exists.
agent: chase
model: sonnet
schedule: monthly (11th at 7:00 AM)
rock: Rock 1 — Revenue Visibility
---

# Rock 1 — Revenue Monthly Workflow

**Goal:** Pull live revenue data for One Texas and store a dated snapshot to the Obsidian
tracking file. No user interaction required. This feeds the One Texas Scorecard assembly step.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Two steps — pull revenue data, then append to Obsidian with recency gate.

---

## INITIALIZATION

### Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Enterprise Scorecard v4 | Revenue vs. Target, Revenue vs. Prior Year, Sequential Quarterly, Monthly Revenue | Playwright/Control Chrome → `skills/revenue-tracker/SKILL.md` |
| Obsidian | Last entry in Rock 1 tracking file | Obsidian MCP |

### Paths

- `tracking_file` = `Mind/One Texas/Rock 1 - Revenue Snapshots.md`
- `revenue_skill` = `skills/revenue-tracker/SKILL.md`

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.
2. If `status: in-progress`: resume from `current-step`. Load `accumulated-context`.
3. If `status: not-started` or `status: complete`: fresh run. Initialize `state.yaml`.
4. If `status: aborted`: surface to controller and wait for instruction.

---

## EXECUTION

**Dispatch model:** This workflow runs as a **Chase** subagent spawned by the coordinator, never inline in the coordinator's session. Chase executes the steps below in order.

### Steps

| # | File | Executed by |
|---|------|-------------|
| 1 | `steps/step-01-pull-revenue.md` | spawned subagent (Chase) |
| 2 | `steps/step-02-save.md` | spawned subagent (Chase) |

Begin: `steps/step-01-pull-revenue.md`

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| PowerBI unavailable | Log failure. Set state: aborted. Surface: "[Chase]: Rock 1 monthly pull failed — PowerBI unavailable on [date]. Reschedule or trigger manually." |
| Obsidian MCP unavailable | Store revenue data in state.yaml only. Surface: "[Chase]: Revenue data collected but could not write to Obsidian — MCP unavailable. Run /rock1-save to retry write." |
| SSO fails | Surface to controller: "[Chase]: SSO failed for PowerBI. Manual login required." Pause. |

---

## OUTPUT

Appended entry in `Mind/One Texas/Rock 1 - Revenue Snapshots.md` — one dated block per month.
This file is the data source for the One Texas Scorecard assembly step (one-texas-scorecard workflow step 1).

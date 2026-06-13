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

### Step 1 — Pull Revenue Data

Read and follow `skills/revenue-tracker/SKILL.md` in full.

Collect for Dallas and South Texas separately:
- Revenue vs. Target (CQ %, LQ %, YTD %)
- Revenue vs. Prior Year (CQ %, LQ %, YTD %)
- Sequential Quarterly Revenue (CQ %, PQ %, 90-Day Forecast %)
- Monthly Revenue (most recent closed month, dollar figure)

Compile the formatted output per the skill's output format.

Store in `state.yaml` under `accumulated-context.revenue`.

Update `state.yaml`: `current-step: step-02-save`

### Step 2 — Recency Gate + Append to Obsidian

1. **Read the tracking file** via Obsidian MCP:
   ```
   mcp__obsidian-local__get_vault_file
   filepath: Mind/One Texas/Rock 1 - Revenue Snapshots.md
   ```

2. **Recency check**: scan the file for a heading matching the current month and year
   (e.g., `## April 2026`). If found, do NOT append — output:
   ```
   [Chase]: Rock 1 revenue snapshot for [Month YYYY] already recorded. Skipping write.
   ```
   Set `state.yaml` status: complete and stop.

3. **If no entry for this month**, append the following block to the file:

   ```markdown
   ## [Month YYYY] — Revenue Snapshot
   *Pulled: [YYYY-MM-DD] | Source: Enterprise Scorecard v4*

   [full formatted output from revenue-tracker skill]

   ---
   ```

   Use `mcp__obsidian-local__append_to_vault_file` with the above content.

4. **Confirm write** and output:
   ```
   [Chase]: Rock 1 revenue snapshot for [Month YYYY] written to Mind/One Texas/Rock 1 - Revenue Snapshots.md.
   ```

5. Update `state.yaml`: `status: complete`, `current-step: step-02-save`.

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

---
name: rock4-pipeline-weekly
description: Weekly Rock 4 pipeline pull. Runs co-sell-pipeline and pipeline-snapshot skills for One Texas, then appends a dated snapshot to the Rock 4 tracking file in Obsidian. Triggered automatically every Monday at 7:00 AM. Co-sell tracks progress toward the $15M Rock 4 target. Pipeline snapshot tracks the 90-day weighted pipeline (Rock 1 secondary metric).
agent: chase
model: sonnet
schedule: weekly (Monday at 7:00 AM)
rocks: Rock 4 — Partner Co-Sell Pipeline | Rock 1 (secondary — 90-day weighted pipeline)
---

# Rock 4 — Pipeline Weekly Workflow

**Goal:** Pull live co-sell and pipeline data for One Texas and store a dated weekly snapshot
to the Obsidian tracking file. No user interaction required. This feeds the One Texas Scorecard
assembly step and provides the week-over-week pipeline trend for Rock 4 grading.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Three steps — pull co-sell data, pull pipeline snapshot, append both to Obsidian.

---

## INITIALIZATION

### Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Sales Analytics | Co-sell pipeline + won revenue by partner, Rock 4 gap to $15M | Playwright/Control Chrome → `skills/co-sell-pipeline/SKILL.md` |
| Sales Analytics | 90-day weighted pipeline, total pipeline, stage breakdown | Playwright/Control Chrome → `skills/pipeline-snapshot/SKILL.md` |
| Obsidian | Last entry date in Rock 4 tracking file | Obsidian MCP |

### Paths

- `tracking_file` = `Mind/One Texas/Rock 4 - Pipeline Snapshots.md`
- `cosell_skill` = `skills/co-sell-pipeline/SKILL.md`
- `pipeline_skill` = `skills/pipeline-snapshot/SKILL.md`

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.
2. If `status: in-progress`: resume from `current-step`. Load `accumulated-context`.
3. If `status: not-started` or `status: complete`: fresh run. Initialize `state.yaml`.
4. If `status: aborted`: surface to controller and wait for instruction.

---

## EXECUTION

### Step 1 — Pull Co-Sell Pipeline Data

Read and follow `skills/co-sell-pipeline/SKILL.md` in full.

Collect:
- Pipeline Revenue w/ Co-Selling Partner (total + by partner)
- Won Revenue w/ Co-Selling Partner (total + by partner)
- Rock 4 gap calculation: `$15M - Pipeline Revenue - Won Revenue`

Store formatted output in `state.yaml` under `accumulated-context.cosell`.

Update `state.yaml`: `current-step: step-02-pipeline`

### Step 2 — Pull Pipeline Snapshot

Read and follow `skills/pipeline-snapshot/SKILL.md` in full.

Collect for Dallas and South Texas separately:
- 90-Day Weighted Pipeline (primary Rock 1 metric)
- Total Pipeline Revenue + Opp Count
- Pipeline by Probability Stage
- Pipeline by Opportunity Type

Store formatted output in `state.yaml` under `accumulated-context.pipeline`.

Update `state.yaml`: `current-step: step-03-save`

### Step 3 — Append to Obsidian

1. **Read the tracking file** via Obsidian MCP:
   ```
   mcp__obsidian-local__get_vault_file
   filepath: Mind/One Texas/Rock 4 - Pipeline Snapshots.md
   ```

2. **Recency check**: look for an entry from the current week (within last 5 days).
   If found, do NOT append — output:
   ```
   [Chase]: Rock 4 pipeline snapshot already recorded this week ([date]). Skipping write.
   ```
   Set `state.yaml` status: complete and stop.

3. **If no entry this week**, append the following block:

   ```markdown
   ## Week of [YYYY-MM-DD] — Pipeline Snapshot
   *Pulled: [YYYY-MM-DD] | Source: Sales Analytics*

   ### Co-Sell Pipeline (Rock 4)
   [full formatted output from co-sell-pipeline skill]

   ### Pipeline Health (Rock 1 — 90-Day Weighted)
   [full formatted output from pipeline-snapshot skill]

   ---
   ```

   Use `mcp__obsidian-local__append_to_vault_file`.

4. **Confirm write** and output:
   ```
   [Chase]: Rock 4 pipeline snapshot for week of [date] written to Mind/One Texas/Rock 4 - Pipeline Snapshots.md.
   Rock 4 gap: $[X]M remaining to $15M target.
   90-Day weighted pipeline: $[X]M One Texas.
   ```

5. Update `state.yaml`: `status: complete`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| PowerBI unavailable | Log failure. Set state: aborted. Surface: "[Chase]: Rock 4 weekly pull failed — PowerBI unavailable on [date]. Will retry next Monday or trigger manually." |
| Obsidian MCP unavailable | Store data in state.yaml only. Surface: "[Chase]: Pipeline data collected but Obsidian write failed — MCP unavailable. Run /rock4-save to retry." |
| SSO fails | Surface to controller: "[Chase]: SSO failed for PowerBI. Manual login required." Pause. |

---

## OUTPUT

Appended entry in `Mind/One Texas/Rock 4 - Pipeline Snapshots.md` — one dated block per week.
This file is the data source for the One Texas Scorecard assembly step.

Week-over-week trend: each entry shows Rock 4 gap progression and 90-day pipeline movement,
enabling Chase to surface whether pipeline is building or eroding between scorecard runs.

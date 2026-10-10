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

## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `rock4-pipeline-weekly`; agent: `chase`.

---

## EXECUTION

**Dispatch model:** This workflow runs as a **Chase** subagent spawned by the coordinator, never inline in the coordinator's session. Chase executes the steps below in order.

### Steps

| # | File | Executed by |
|---|------|-------------|
| 1 | `steps/step-01-cosell.md` | spawned subagent (Chase) |
| 2 | `steps/step-02-pipeline.md` | spawned subagent (Chase) |
| 3 | `steps/step-03-save.md` | spawned subagent (Chase) |

Begin: `steps/step-01-cosell.md`

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


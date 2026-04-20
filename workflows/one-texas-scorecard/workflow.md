---
name: one-texas-scorecard
description: Pull revenue, co-sell, pipeline, and new client data for One Texas via Chase skills and append a consolidated dated snapshot to the Obsidian tracking file.
agent: chase
model: sonnet
---

<!-- system:start -->
# One Texas Scorecard Workflow

**Goal:** Assemble a complete One Texas scorecard snapshot by running four Chase skills in
sequence, then append the consolidated output to the Obsidian tracking file with today's date.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Sequential 5-step workflow. Steps 1-4 each execute a Chase skill and collect
output. Step 5 checks the Obsidian file for recency, prompts if the last entry is within 28
days, and appends the full snapshot. No user interaction required until the recency gate in
step 5.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Enterprise Scorecard v4 | Revenue vs. Target, Revenue vs. Prior Year, Sequential Quarterly, Monthly Revenue | Chrome MCP → `skills/revenue-tracker/SKILL.md` |
| Sales Analytics | Co-sell pipeline and won revenue by partner, Rock 4 gap | Chrome MCP → `skills/co-sell-pipeline/SKILL.md` |
| Sales Analytics | 90-day weighted pipeline, total pipeline, stage breakdown | Chrome MCP → `skills/pipeline-snapshot/SKILL.md` |
| Enterprise Scorecard v4 | New Logos & Anchors YTD by enterprise, gap to Q1 target | Chrome MCP → `skills/new-clients/SKILL.md` |
| Obsidian | 2026 annual goals and targets | Obsidian MCP → `Mind/One Texas/2026 Goals.md` |
| Obsidian | Last entry date in scorecard tracking file | Obsidian MCP → `mcp__obsidian-local__get_vault_file` |

### Paths

- `scorecard_file` = `Mind/One Texas/One Texas Scorecard Tracking.md`
- `goals_file` = `Mind/One Texas/2026 Goals.md`
- `revenue_skill` = `skills/revenue-tracker/SKILL.md`
- `cosell_skill` = `skills/co-sell-pipeline/SKILL.md`
- `pipeline_skill` = `skills/pipeline-snapshot/SKILL.md`
- `new_clients_skill` = `skills/new-clients/SKILL.md`

### Goal Alignment Pre-Load

**At the start of every run**, read `Mind/One Texas/2026 Goals.md` via Obsidian MCP.
Extract the `Annual Target Reference` YAML block and the `Scorecard Alignment Map` table.
Load these into `accumulated-context.goals` — they inform the goal alignment section
appended by step-05 and the PPTX scorecard commentary.

Key targets to carry forward:
- Co-sell target: $15M by Q2 end (Rock 4)
- New anchors target: 3 per enterprise (6 One Texas annual)
- New logos: context for account pursuit, not a hard annual number
- Revenue: beat target, both enterprises — watch large/medium account thresholds
- Speaking engagements: 10 for year (manual track, not in PowerBI)

### Key Metrics Collected

| Metric | Source Skill | One Texas Scope |
|--------|-------------|-----------------|
| Revenue vs. Target (QTD/LQ/YTD) | revenue-tracker | Dallas + South Texas |
| Revenue vs. Prior Year (QTD/LQ/YTD) | revenue-tracker | Dallas + South Texas |
| Sequential Quarterly Revenue | revenue-tracker | Dallas + South Texas |
| Monthly Revenue (most recent month) | revenue-tracker | Dallas + South Texas |
| Co-sell pipeline + won by partner | co-sell-pipeline | Company-wide |
| Rock 4 gap to $15M target | co-sell-pipeline | Company-wide |
| 90-day weighted pipeline (Rock 1) | pipeline-snapshot | Dallas + South Texas |
| Total pipeline + stage breakdown | pipeline-snapshot | Dallas + South Texas |
| New Logos & Anchors YTD | new-clients | Dallas + South Texas |
| Gap to Q1 targets | new-clients | Dallas + South Texas |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — data already gathered. Do not re-pull it.
   - Check that step's frontmatter: if `status: in-progress`, re-execute it; if `status:
     not-started`, begin it fresh.
   - Notify the controller: "[Chase]: Resuming one-texas-scorecard from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01-revenue`.
   - Begin at step-01.

4. If `status: aborted`:
   - Surface to controller: "[Chase]: one-texas-scorecard was previously aborted at
     [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow each step in order. Do not proceed to the next step until the current
step's frontmatter is updated to `status: complete`.

1. `steps/step-01-revenue.md`
2. `steps/step-02-co-sell.md`
3. `steps/step-03-pipeline.md`
4. `steps/step-04-new-clients.md`
5. `steps/step-05-save-to-obsidian.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

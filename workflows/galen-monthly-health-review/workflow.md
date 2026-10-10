---
name: galen-monthly-health-review
description: Monthly health review. Pull 30-day WHOOP, latest bloodwork, DEXA data. Run trend analysis vs. Lifebook goals. Output Obsidian note with monthly summary, progress, and gaps.
agent: galen
model: sonnet
---

<!-- system:start -->
# Monthly Health Review Workflow

**Goal:** Comprehensive monthly health snapshot across all data sources. Track progress vs. longevity goals (bio age -8 years, healthspan +20 years). Identify trends, protocol adjustments needed, and success metrics.

**Agent:** Galen — Longevity Advisor

**Trigger:**
- On demand: "monthly health review", "health review", "monthly check-in"
- Scheduled: Last day of each month (auto-triggered)
- Manual: Whenever David wants a full health assessment

**Architecture:** Sequential workflow pulling from 4 data sources, synthesizing into monthly health note for Obsidian.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| WHOOP | 30 days of recovery, sleep, workout, HRV data | WHOOP MCP (`whoop-get-recovery-collection`, `whoop-get-sleep-collection`, `whoop-get-workout-collection`) |
| Bloodwork | Latest Function Health results (if available this month) | Obsidian vault (`Mind/Health/Visit - [Date].md`) |
| DEXA | Body composition (latest scan) | Dropbox Excel (`~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`) |
| Lifebook | Health goals (bio age target, healthspan target, body comp goals) | Obsidian Lifebook (`Projects/Lifebook - Health.md`) |
| Active Protocols | Current supplement stack, peptide cycles | Obsidian + `projects/Peptides.md` |
| Calendar | Training load (any major deloads, travel, stress events) | Calendar context + WHOOP workout data |

### Paths

- `lifebook_health` = `Projects/Lifebook - Health.md`
- `dropbox_health_tracking` = `~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`
- `obsidian_health_folder` = `Mind/Health/`
- `monthly_output` = `Mind/Health/Monthly Review - [Month Year].md`
- `metrics_log` = `data/health/metrics-log.json` (schema: `data/health/schema.md`)

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `galen-monthly-health-review`; agent: `galen`.

## EXECUTION

**Dispatch model:** This workflow runs as a **Galen** subagent spawned by the coordinator, never inline in the coordinator's session. Galen executes the steps below in order.

### Steps

| # | File | Executed by |
|---|------|-------------|
| 1 | `steps/step-01-whoop.md` | spawned subagent (Galen) |
| 2 | `steps/step-02-bloodwork.md` | spawned subagent (Galen) |
| 3 | `steps/step-03-dexa.md` | spawned subagent (Galen) |
| 4 | `steps/step-04-lifebook.md` | spawned subagent (Galen) |
| 5 | `steps/step-05-synthesize.md` | spawned subagent (Galen) |
| 6 | `steps/step-06-metrics-log.md` | spawned subagent (Galen) |

Begin: `steps/step-01-whoop.md`

---

## PRE-FLIGHT: Load Metrics History

Before pulling any live data, read `data/health/metrics-log.json`. This gives Galen the full longitudinal picture:
- Identify the most recent entry for each category (`bloodwork`, `whoop_monthly`, `dexa`) — these establish the baseline for trend comparison
- Note any gaps (e.g., if no `whoop_monthly` entry exists for last month, this month's analysis is the first data point, not a trend)
- Use prior log entries as authoritative values for trend deltas — do not re-derive them from memory

---

## SUCCESS METRICS

- All 4 data sources (WHOOP, bloodwork, DEXA, Lifebook) included
- 30-day WHOOP trends analyzed (recovery, sleep, HRV, load)
- Latest bloodwork (if available) interpreted with out-of-range flagging
- Body composition tracked vs. Lifebook goals
- 4 Horsemen risk assessment completed
- Monthly note is comprehensive, scannable, and exportable to Obsidian
- Action items are specific and prioritized
- Next review date is scheduled

---

## FAILURE MODES & ERROR HANDLING

| Scenario | Recovery |
|----------|----------|
| WHOOP data incomplete | Proceed with available data; note "X days captured" |
| No new bloodwork this month | Use most recent results; note date in summary |
| DEXA scan not available | Use weight + prior body fat estimate; note "DEXA pending" |
| Lifebook goals not accessible | Proceed with standard goals; note "Lifebook context pending" |
| Protocol changes undocumented | Flag "Current protocol status to be confirmed with David" |

---

## INTEGRATION NOTES

- Monthly health review output is saved to Obsidian (`Mind/Health/Monthly Review - [Month].md`)
- If bloodwork shows urgent flags, Galen escalates to Bloodwork Review skill for detailed interpretation
- At end of quarter (March, June, September, December), monthly review feeds into quarterly health rock review with Quinn
- Any significant health concerns (e.g., recovery crashing, new out-of-range markers) escalate to Chief for schedule/stress adjustments
- Scheduled to run on demand or automatically last day of month

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

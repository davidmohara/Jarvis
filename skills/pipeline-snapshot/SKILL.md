---
name: pipeline-snapshot
description: >
  Pull a weekly pipeline health snapshot for Dallas, TX and South Texas (One Texas) from the
  Improving Sales Analytics PowerBI report. Primary data source for grading Rock 1 (Revenue
  Visibility). Reports total pipeline and 90-day weighted pipeline side-by-side for both regions.
  Trigger on /pipeline-snapshot, "pipeline snapshot", "pipeline health", "rock 1 data", or
  "90 day pipeline".
owning_agent: chase
model: sonnet
trigger_keywords: [pipeline, deal status, revenue snapshot, crm]
trigger_agents: [chase]
---

# Pipeline Snapshot

## Purpose

Pull pipeline data for Dallas, TX and South Texas from the Improving Sales Analytics
PowerBI report. This is the primary grading source for Rock 1 (Revenue Visibility):
"Jarvis pulls account trajectory data weekly; Rock 1 graded on actuals, not feel."

**Scope: One Texas only** — Dallas, TX and South Texas. Do not report all-Improving totals.

Two pages pulled on every run:
1. **Pipeline Analytics** — total pipeline, stage breakdown, opportunity type mix
2. **90 Day Weighted Pipeline** — weighted pipeline within 90-day close window (primary Rock 1 metric)

Note: South Texas = Austin + Houston combined in PowerBI slicer terminology.

This skill delegates its mechanics to three shared skills — it owns only the report URLs,
which KPI labels matter, the cache location, and the output voice/format.

---

## Phase 0 — Cache Check (Run First)

Call `skills/vault-freshness-check/SKILL.md` with:
```
vault_file: "Mind/One Texas/Rock 4 - Pipeline Snapshots.md"
entry_heading_pattern: "^## Week of (\d{4}-\d{2}-\d{2}) — Pipeline Snapshot"
date_field_pattern: "\*Pulled: (\d{4}-\d{2}-\d{2})"
freshness_threshold_days: 7
extract_section_heading: "### Pipeline Health (Rock 1)"
caller_label: "Chase/Pipeline"
```

If `cache_status: "hit"` — output `extracted_text` in the standard format below, noting
the snapshot date, report the message the skill returns, and **stop here**.

If `"stale"` or `"not_found"` — proceed to Phase 1.

---

## Phase 1 — Navigate to Pipeline Analytics, Filter to Dallas, TX

Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: "https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/84f84d9e-1283-4aad-8feb-b301bb819881/ReportSection7e20c80e361d6cc45eed?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi"
connector: "chrome"
slicer_pattern: "text-click"
select: [{label: "Dallas, TX"}]
```

Then call `skills/powerbi-extract-kpis/SKILL.md` with `connector: "chrome"`, `mode: "raw"`, `char_limit: 5000`.

Read from the returned text:
- **Total Pipeline Revenue** (KPI tile)
- **Pipeline Opp Count** (KPI tile)
- **Weighted Pipeline Value** (KPI tile)
- **Pipeline by Probability Stage** table: 10%-Identified through 99%-Procurement, $ each
- **Pipeline by Opportunity Type**: New / Extension / Backfill, revenue + %

---

## Phase 2 — Filter to South Texas (same page)

South Texas = Austin, TX + Houston, TX. No "South Texas" slicer label exists — select both
cities. Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: (same as Phase 1 — already on the page, but safe to re-pass)
connector: "chrome"
slicer_pattern: "checkbox-flat"
deselect: ["Dallas, TX"]
select: ["Houston, TX", "Austin, TX"]
wait_ms: {between_deselect_select: 600, between_selects: 400, verify: 500}
verify_after: true
```

Confirm the returned `selected` list shows Austin, TX + Houston, TX. Then call
`skills/powerbi-extract-kpis/SKILL.md` the same way as Phase 1 and read the same KPI values.

Note: if the slicer instead behaves as single-select on a given report, read Austin and
Houston separately (two `text-click` calls) and combine for the South Texas total.

---

## Phase 3 — Navigate to 90 Day Weighted Pipeline, Filter to Dallas, TX

Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: "https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/84f84d9e-1283-4aad-8feb-b301bb819881/9f4623c483c060b75480?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi"
connector: "chrome"
slicer_pattern: "text-click"
select: [{label: "Dallas, TX"}]
```

Then call `skills/powerbi-extract-kpis/SKILL.md` with `connector: "chrome"`, `mode: "raw"`, `char_limit: 5000`.

Read:
- **Weighted Pipeline Value** (90-day KPI tile)
- **Weighted Pipeline Opp Count** (KPI tile)
- **90-day pipeline by Probability Stage**: each stage $ value
- **90-day pipeline by Opportunity Type**: New / Extension / Backfill weighted values

---

## Phase 4 — Filter to South Texas (90-day page)

Same `powerbi-navigate-slicer` call as Phase 2 (`checkbox-flat`, deselect Dallas, select
Houston then Austin). Read the same 90-day values via `powerbi-extract-kpis`.

For Austin and Houston separately: if the slicer is single-select, read each city
individually and combine for South Texas total.

---

## Phase 5 — Save to Obsidian and Output

Append the pipeline snapshot to `Mind/One Texas/Rock 4 - Pipeline Snapshots.md` under
a new `## Week of [today] — Pipeline Snapshot` heading (or add `### Pipeline Health (Rock 1)`
subsection to an existing week entry if co-sell was already written today).

Use `mcp__obsidian-local__append_to_vault_file`.

Output using the standard format below.

---

## Output Format

```
## Pipeline Snapshot — Rock 1 — [Today's Date]

### 90-Day Weighted Pipeline (Primary Rock 1 Metric)

| Metric                        | Dallas, TX    | South Texas   | One Texas     |
|-------------------------------|---------------|---------------|---------------|
| 90-Day Weighted Value         | $X.XXM        | $X.XXM        | $X.XXM        |
| 90-Day Weighted Opp Count     | XXX           | XXX           | XXX           |

### Total Pipeline

| Metric                   | Dallas, TX    | South Texas   | One Texas     |
|--------------------------|---------------|---------------|---------------|
| Total Pipeline Revenue   | $X.XXM        | $X.XXM        | $X.XXM        |
| Pipeline Opp Count       | XXX           | XXX           | XXX           |
| Weighted Pipeline Value  | $X.XXM        | $X.XXM        | $X.XXM        |

### Pipeline by Probability Stage

| Stage                    | Dallas, TX    | South Texas   |
|--------------------------|---------------|---------------|
| 10%-Identified           | $X.XXM        | $X.XXM        |
| 25%-Qualified            | $X.XXM        | $X.XXM        |
| 50%-Proposing            | $X.XXM        | $X.XXM        |
| 75%-Positive Feedback    | $X.XXM        | $X.XXM        |
| 90%-Verbal               | $X.XXM        | $X.XXM        |
| 99%-Procurement          | $X.XXM        | $X.XXM        |
```

Follow with 2-3 sentences of Chase-voice commentary. Lead with the 90-day weighted number —
that is the Rock 1 grading metric, not total pipeline. Flag stage concentration risk if > 40%
of pipeline is at 10%-Identified. Note region imbalance if one side is significantly weaker.
Do not soften numbers.

---

## Notes

- **One Texas only** — never report all-Improving numbers.
- **South Texas = Austin, TX + Houston, TX** — no "South Texas" slicer label. Select both cities.
  Deselect Dallas first (600ms), then Houston (400ms), then Austin (400ms). Verify selection.
- Use `.slicerCheckbox` clicks — clicking the container directly hits the expand toggle
  (this is `powerbi-navigate-slicer`'s `checkbox-flat` pattern; it handles this already).
- If KPI text not visible in body text after 2s, `powerbi-extract-kpis`'s retry handles a
  3-second re-read automatically.
- The 90-Day Weighted Pipeline is the Rock 1 metric. Lead with it. Total pipeline is context.

---

## Source

PowerBI report: Improving Sales Analytics — Pipeline Analytics
Pages: Pipeline Analytics, 90 Day Weighted Pipeline
Mechanics: `skills/powerbi-navigate-slicer/SKILL.md`, `skills/powerbi-extract-kpis/SKILL.md`,
`skills/vault-freshness-check/SKILL.md`, `skills/eval-signal-write/SKILL.md`
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/Rock 4 - Pipeline Snapshots.md`
Freshness threshold: 7 days
Auth: SSO (auto via Chrome session)
Rock 1 context: Revenue Visibility — "graded on actuals, not feel." One Texas only.

---

## SKILL COMPLETE

After the output is delivered (Phase 5), call `skills/eval-signal-write/SKILL.md` with:
```
skill_name: "pipeline-snapshot"
agent: "chase"
trigger: "manual"   (or "boot"/"scheduled" per the calling context)
started: <actual start time of this run>
completed: <actual completion time>
status: "success"   (or "partial" if only one region's data was captured or cache was
                      used due to staleness detection; a clean cache hit is still "success".
                      "failure" if PowerBI could not be reached and no cache existed.)
tool_failures: 0
error_ids: []
```
This call is always the final action.


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/pipeline-snapshot-latest.json
```

Content:
```json
{
  "skill": "pipeline-snapshot",
  "agent": "pipeline",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill pipeline-snapshot
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/pipeline-snapshot.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

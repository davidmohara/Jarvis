---
name: co-sell-pipeline
description: >
  Pull live co-sell pipeline and won data from the Improving Sales Analytics PowerBI report.
  Reports pipeline revenue and opps by partner, won revenue and opps by partner, and gap to
  Rock 4's $15M co-sell pipeline target. Trigger on /co-sell-pipeline, "co-sell", "cosell",
  "partner pipeline", or "rock 4 pipeline".
owning_agent: chase
model: sonnet
trigger_keywords: [co-sell, partner pipeline, microsoft, cosell]
trigger_agents: [chase]
---

# Co-Sell Pipeline

## Purpose

Pull co-sell pipeline and won revenue data from the Improving Sales Analytics PowerBI
report. Surface partner-level breakdown, progress toward Rock 4's $15M target, and gap
remaining. David tracks this against two key partners: Microsoft (SME&C, John Yurewicz) and
Confluent (Nick Larson and Dante).

Rock 4 target: **$15M co-sell pipeline** by end of Q2 2026.

Gap formula: `$15M - Pipeline Revenue - Won Revenue = Remaining Gap`

This skill delegates its mechanics to three shared skills — it owns only the report URLs,
which KPI labels matter, the disaggregation logic (this report requires per-enterprise
reads that the caller sums itself), the cache location, and the output voice/format.

---

## Phase 0 — Cache Check (Run First)

Call `skills/vault-freshness-check/SKILL.md` with:
```
vault_file: "Mind/One Texas/Rock 4 - Pipeline Snapshots.md"
entry_heading_pattern: "^## Week of (\d{4}-\d{2}-\d{2}) — Pipeline Snapshot"
date_field_pattern: "\*Pulled: (\d{4}-\d{2}-\d{2})"
freshness_threshold_days: 7
extract_section_heading: "### Co-Sell Pipeline (Rock 4)"
caller_label: "Chase/CoSell"
```

If `cache_status: "hit"` — output `extracted_text` in the standard format below, noting
the snapshot date, report the message the skill returns, and **stop here**.

If `"stale"` or `"not_found"` — proceed to Phase 1.

---

## Phase 1 — Navigate to Coselling Partner Pipeline Page

Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: "https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/8a62865681ae18b5ec9b?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi"
connector: "chrome"
slicer_pattern: "checkbox-flat"    (used here purely to read current filter state — see Phase 2a)
select: []
```
Navigate directly to this URL — do NOT use the mcas.ms variant. Wait 5 seconds for SSO
and page load. Confirm title contains "Power BI".

---

## Phase 2 — Disaggregate Pipeline Data by One Texas Enterprise

**CRITICAL: Do NOT read the aggregate "Improving, Enterprise" KPI. Disaggregate by clicking each location filter.**

One Texas consists of three enterprises: **Dallas, Houston, and Austin**. The report's
default view shows an aggregate that masks critical execution differences across
enterprises. You MUST gather individual numbers for each enterprise and sum them.

### Phase 2a — Check Filter State

Call `skills/powerbi-extract-kpis/SKILL.md` with `mode: "tile-scan"` first, or run this
targeted check via the connector directly to see which location is currently selected:
```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const locations = ['Dallas, TX', 'Houston, TX', 'Austin, TX'];
  const result = [];
  for (const location of locations) {
    for (const el of document.querySelectorAll('[class*="slicerText"]')) {
      if (el.textContent?.trim() === location) {
        const container = el.closest('[class*="slicerItemContainer"]');
        const checkbox = container?.querySelector('[class*="slicerCheckbox"]');
        result.push({location, isSelected: checkbox?.className.includes('selected')});
        break;
      }
    }
  }
  return result;
})()
```

### Phase 2b — Click Each Location and Record Pipeline KPIs

For each of Dallas, Houston, Austin: call `skills/powerbi-navigate-slicer/SKILL.md` with
`slicer_pattern: "checkbox-flat"`, `select: [{label: "<City>, TX"}]` (this location's
checkbox is exclusive per Improving's report config — selecting one deselects the
others, so no explicit `deselect` is needed here), then call
`skills/powerbi-extract-kpis/SKILL.md` with:
```
mode: "regex"
kpi_labels: [
  {name: "pipelineRevenue", pattern: "Pipeline Revenue w/.*?Partner\\s*\\$([\\d,]+)"},
  {name: "pipelineOpps",    pattern: "Pipeline Opps w/.*?Partner\\s*(\\d+)"}
]
retry_if_empty: true
```
Record all three readings (Dallas, Houston, Austin). You will sum these at the end.

---

## Phase 3 — Navigate to Won Coselling Partner Opps Page

Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: "https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/57bac82f202223c91446?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi"
connector: "chrome"
select: []
```
Wait 5 seconds for page load.

---

## Phase 4 — Disaggregate Won Data by One Texas Enterprise

Same as Phase 2: the Won page shows an aggregate KPI by default. You MUST disaggregate by
clicking each location filter and recording individual won revenue numbers.

For each of Dallas, Houston, Austin: call `skills/powerbi-navigate-slicer/SKILL.md` with
`slicer_pattern: "checkbox-flat"`, `select: [{label: "<City>, TX"}]`, then
`skills/powerbi-extract-kpis/SKILL.md` with:
```
mode: "regex"
kpi_labels: [
  {name: "wonRevenue", pattern: "Won Revenue w/.*?Partner\\s*\\$([\\d,]+)"},
  {name: "wonOpps",    pattern: "Won Opps w/.*?Partner\\s*(\\d+)"}
]
retry_if_empty: true
```
If a value comes back `null` after retry, treat it as `$0` / `0` for that enterprise
rather than blocking the run. Record all three readings — you will sum these with the
pipeline data to calculate the true Rock 4 gap.

---

## Phase 5 — Calculate and Output

### Sum Enterprise Data

Add the three enterprise readings:
- **Total Pipeline Revenue** = Dallas + Houston + Austin pipeline
- **Total Pipeline Opps** = Dallas + Houston + Austin opps
- **Total Won Revenue** = Dallas + Houston + Austin won
- **Total Won Opps** = Dallas + Houston + Austin opps

### Calculate Rock 4 Gap

```
Remaining Gap = $15,000,000 - (Pipeline Revenue + Won Revenue)
Gap % = (Remaining Gap / $15,000,000) * 100
```

### Output Format

```
## Co-Sell Pipeline — Rock 4 Progress — [Today's Date]
**Report period: 2026 YTD (One Texas: Dallas + Houston + Austin disaggregated)**

### Pipeline vs Won by Enterprise

| Enterprise   | Pipeline Revenue | Pipeline Opps | Won Revenue | Won Opps |
|--------------|-----------------|---------------|------------|----------|
| Dallas       | $XXX,XXX        | X             | $XXX,XXX   | X        |
| Houston      | $XXX,XXX        | X             | $XXX,XXX   | X        |
| Austin       | $XXX,XXX        | X             | $XXX,XXX   | X        |
| **Total**    | **$X,XXX,XXX**  | **XX**        | **$XXX,XXX** | **XX**  |

### Rock 4 Gap (One Texas)

| Metric                        | Amount          |
|-------------------------------|-----------------|
| Target                        | $15,000,000     |
| Pipeline Revenue              | $X,XXX,XXX      |
| Won Revenue (2026 YTD)        | $X,XXX,XXX      |
| **Combined Progress**         | **$X,XXX,XXX**  |
| **Remaining Gap**             | **$XX,XXX,XXX** |
| Gap % remaining               | **XX%**         |
```

Follow with 2-3 sentences of Chase-voice commentary analyzing enterprise split (which is
carrying pipeline, which is converting wins, which is dormant), and direct assessment of
gap closure likelihood. David owns the co-sell pipeline — address gaps to him directly.
Do not soften numbers. Do not suggest partner contacts are responsible — David is.

---

## Notes — Filter Selection (CRITICAL)

The location slicer on both PowerBI pages uses `checkbox-flat` semantics as documented in
`skills/powerbi-navigate-slicer/SKILL.md` — checkboxes styled with class `slicerCheckbox`,
selected items carrying an appended `selected` class. Each location on this report is
exclusive (clicking one deselects the others), so no explicit `deselect` list is required
when moving between Dallas/Houston/Austin — passing only `select` for the next city is
sufficient.

- Both pages use direct URL navigation — no in-report nav clicks needed.
- Quarter/Year table confirms the report period (should always show 2026).
- Gap = pipeline + won combined against $15M. Both count toward Rock 4.
- One Texas = Dallas, TX + Houston, TX + Austin, TX. These are the ONLY locations David
  manages for Rock 4 — do not include other cities.

---

## Source

PowerBI report: Improving Sales Analytics — Co-Sell Pipeline
Mechanics: `skills/powerbi-navigate-slicer/SKILL.md`, `skills/powerbi-extract-kpis/SKILL.md`,
`skills/vault-freshness-check/SKILL.md`, `skills/eval-signal-write/SKILL.md`
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/Rock 4 - Pipeline Snapshots.md`
Freshness threshold: 7 days
Auth: SSO (auto via Chrome session)
Rock 4 Target: $15M co-sell pipeline by end of Q2 2026

## SKILL COMPLETE

After the skill's final output is delivered, call `skills/eval-signal-write/SKILL.md` with:
```
skill_name: "co-sell-pipeline"
agent: "chase"
trigger: "manual"   (or "boot"/"scheduled" per the calling context)
started: <actual start time of this run>
completed: <actual completion time>
status: "success"   (or "partial" if the skill completed with degraded output, "failure"
                      if it could not run at all)
tool_failures: 0
error_ids: []
```
This call is always the final action.

After that, also write a working memory file to `memory/working/` using this filename pattern:

```
co-sell-pipeline-YYYY-MM-DD-HHmmss.md
```

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "chase-{YYYY-MM-DD}-{HHmmss}"
agent-source: chase
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "Co-sell pipeline snapshot — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/co-sell-pipeline-latest.json
```

Content:
```json
{
  "skill": "co-sell-pipeline",
  "agent": "co",
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
python3 systems/eval-harness/grade_skill_run.py --skill co-sell-pipeline
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/co-sell-pipeline.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

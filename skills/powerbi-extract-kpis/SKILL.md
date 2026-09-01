---
id: powerbi-extract-kpis
name: PowerBI KPI & Table Extraction
owning_agent: rigby
model: sonnet
context: inline
fairness: {applicable: false, reason: "Browser-automation utility — reads numeric report values from a page. No differential treatment of people, no eligibility or scoring decisions."}
trigger_keywords:
  - powerbi kpi
  - read kpi tile
  - extract report values
---

<!-- system:start -->
# PowerBI KPI & Table Extraction

Reads named KPI tile values and table rows off the *currently loaded* PowerBI page — call this after `powerbi-navigate-slicer` has already navigated and filtered the view. Works from `document.body.innerText`, either handed back raw for the caller to eyeball, or pre-extracted against caller-supplied label patterns.

**Scope note:** this skill covers the common case — values legible directly in page text. It does **not** cover chart-hover tooltip reads or SVG bar-color inspection (used by a couple of Improving's scorecard charts to distinguish actual vs. forecast bars). Those are genuinely different mechanics — dispatching synthetic mouse events at pixel coordinates and inspecting SVG `fill` attributes — and stay inline in the one or two skills that need them rather than being forced into this generic shape.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Inputs

| Input | Type | Required | Description |
|-------|------|----------|--------------|
| `connector` | `"chrome"` \| `"playwright"` | no (default `"chrome"`) | Which MCP tool family reads the DOM. `chrome` uses `mcp__Control_Chrome__execute_javascript`. `playwright` uses `mcp__playwright__browser_evaluate`. |
| `mode` | `"raw"` \| `"regex"` \| `"tile-scan"` | yes | See Modes below. |
| `char_limit` | integer | no (default 5000) | For `raw` mode, how many characters of `document.body.innerText` to capture. |
| `kpi_labels` | array of `{name: string, pattern: string}` | required for `regex` mode | Each `pattern` is a JS regex (as a string) with one capture group for the value, matched against `document.body.innerText`. E.g. `{name: "pipelineRevenue", pattern: "Pipeline Revenue w/.*?Partner\\s*\\$([\\d,]+)"}`. |
| `retry_if_empty` | boolean | no (default `true`) | If the initial read comes back without the expected text, wait 3 more seconds and read once more before giving up — PowerBI tiles sometimes lag the slicer update. |

## Modes

### `raw` — hand back page text for the caller to read
```js
(() => document.body.innerText.substring(0, {char_limit}))()
```
Use this when the caller (a human-voiced skill) is going to read the labeled values itself out of the returned text — e.g. "Total Pipeline Revenue", "Pipeline Opp Count" — rather than needing them pre-parsed. This is the lowest-risk mode: it never silently mis-extracts, it just returns text.

### `regex` — extract named values via caller-supplied patterns
```js
(() => {
  const text = document.body.innerText;
  const results = {};
  const labels = {kpi_labels_json};
  for (const {name, pattern} of labels) {
    const m = text.match(new RegExp(pattern));
    results[name] = m ? m[1] : null;
  }
  return results;
})()
```
Returns `{name: value_or_null, ...}`. If any value comes back `null` and `retry_if_empty` is true, wait 3s and re-run once before reporting the miss to the caller.

### `tile-scan` — enumerate anything that looks like a KPI tile or card
Useful when the caller doesn't know exact label text yet (first-time setup against a new report) and wants to see what's actually on the page:
```js
(() => {
  const tiles = [];
  document.querySelectorAll('[class*="kpiVisual"], [class*="kpi-"], [class*="card"]').forEach(el => {
    const text = el.innerText?.trim();
    if (text) tiles.push(text);
  });
  return { tiles, allText: document.body.innerText.substring(0, 3000) };
})()
```

## Process

1. Run the JS for the requested `mode` via the connector's execute/evaluate tool.
2. If the result looks empty or clearly wrong (e.g. all regex matches `null`, or `raw` text is empty/still shows a loading state) and `retry_if_empty` is true, wait 3 seconds and re-run once.
3. Return the result to the caller as-is: raw text string (`raw`), a name→value object (`regex`), or the tile/allText object (`tile-scan`). This skill does not interpret or reformat values — the caller owns output formatting (currency symbols, rounding, table layout).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## SKILL COMPLETE

This skill reads page state only and writes no files — it does not write its own eval-harness signal file. The caller skill signals completion of its overall run via `eval-signal-write`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/powerbi-extract-kpis-latest.json
```

Content:
```json
{
  "skill": "powerbi-extract-kpis",
  "agent": "powerbi",
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
python3 systems/eval-harness/grade_skill_run.py --skill powerbi-extract-kpis
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/powerbi-extract-kpis.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

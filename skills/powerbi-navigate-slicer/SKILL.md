---
id: powerbi-navigate-slicer
name: PowerBI Navigate & Slicer Filter
owning_agent: rigby
model: sonnet
context: inline
fairness: {applicable: false, reason: "Browser-automation utility — navigates and filters a report view. No differential treatment of people, no eligibility or scoring decisions."}
trigger_keywords:
  - powerbi navigate
  - powerbi slicer
  - filter report
  - select slicer
---

<!-- system:start -->
# PowerBI Navigate & Slicer Filter

Opens a PowerBI report URL and drives its region/category slicer into a caller-specified selection state, using the wait-timing sequence proven across Improving's Sales Analytics and Enterprise Scorecard reports. Generalized beyond any specific report or region names — a caller working against a different PowerBI report with its own slicer labels calls this the same way.

This skill knows about **three distinct slicer DOM shapes** that Improving's reports actually use. Pick the one that matches the target report; if unsure, inspect the page (see Pattern Detection below) before calling.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Inputs

| Input | Type | Required | Description |
|-------|------|----------|--------------|
| `report_url` | string | yes | Full PowerBI report/page URL to open. Navigate directly to it — do not use an `mcas.ms` variant or click through in-report nav; both cause redirects or wrong-page landings. |
| `connector` | `"chrome"` \| `"playwright"` | no (default `"chrome"`) | Which MCP tool family drives the browser. `chrome` uses `mcp__Control_Chrome__open_url` / `mcp__Control_Chrome__execute_javascript`. `playwright` uses `mcp__playwright__browser_navigate` / `mcp__playwright__browser_evaluate`. |
| `slicer_pattern` | `"text-click"` \| `"checkbox-flat"` \| `"dropdown-nested"` | yes | Which DOM shape the target slicer uses — see Pattern Reference below. |
| `select` | array of `{label: string, parent?: string}` | yes | Slicer values to end up selected, in the order to select them. `parent` is required only for `dropdown-nested` (the hierarchy level above the leaf, e.g. `"United States"` above `"Dallas"`). |
| `deselect` | array of strings | no | Values to explicitly deselect before selecting (used by `checkbox-flat`, where the report defaults to some other selection already checked). Not needed for `text-click` (single-select — selecting one auto-deselects the rest) or `dropdown-nested` (the script below detects and toggles off whatever is currently selected). |
| `wait_ms` | object | no | Override default wait timings: `{initial_load: 5000, between_deselect_select: 600, between_selects: 400, verify: 500}`. Defaults match what has been proven reliable — increase only if a specific report is slower to render. |
| `verify_after` | boolean | no (default `true`) | After the selection sequence, read back which items are `aria-selected` and return them so the caller can confirm the filter actually applied before reading KPIs. |

## Pattern Reference

### `text-click` — single-select, plain span
Used when the slicer renders as simple clickable spans and is single-select (choosing one deselects whatever else was selected). No explicit `deselect` needed.

```js
(() => {
  const spans = document.querySelectorAll('span.slicerText');
  for (const span of spans) {
    if (span.textContent.trim() === '{label}') { span.click(); return 'clicked ' + '{label}'; }
  }
  return 'not found';
})()
```
If this returns `'not found'`, fall back to a broader text-content scan:
```js
(() => {
  const els = document.querySelectorAll('*');
  for (const el of els) {
    if (el.textContent.trim() === '{label}') { el.click(); return 'clicked'; }
  }
  return 'not found';
})()
```

### `checkbox-flat` — multi-select checkbox items, one level
Used when the slicer is a flat list of `.slicerItemContainer` elements, each with a `.slicerCheckbox`, and more than one value can be selected simultaneously (e.g. combining two cities into one region reading). Always click the checkbox, never the container — clicking the container can hit an expand toggle instead.

Deselect step (repeat per label in `deselect`, waiting `between_deselect_select` after the last one):
```js
(() => {
  const items = document.querySelectorAll('.slicerItemContainer');
  for (const item of items) {
    if (item.getAttribute('title') === '{label}' && item.getAttribute('aria-selected') === 'true') {
      item.querySelector('.slicerCheckbox')?.click();
    }
  }
  return 'deselected {label}';
})()
```

Select step (repeat per label in `select`, waiting `between_selects` between each):
```js
(() => {
  const items = document.querySelectorAll('.slicerItemContainer');
  for (const item of items) {
    if (item.getAttribute('title') === '{label}') item.querySelector('.slicerCheckbox')?.click();
  }
  return 'selected {label}';
})()
```

Or run the whole deselect → select sequence in one chained promise (proven pattern, preferred when selecting 2+ values so timing is deterministic):
```js
(function() {
  return new Promise((resolve) => {
    const deselectLabels = {deselect_json};   // e.g. ["Dallas, TX"]
    const selectLabels = {select_json};       // e.g. ["Houston, TX", "Austin, TX"]
    const clickByTitle = (title, mustBeSelected) => {
      document.querySelectorAll('.slicerItemContainer').forEach(item => {
        if (item.getAttribute('title') === title &&
            (mustBeSelected === undefined || item.getAttribute('aria-selected') === (mustBeSelected ? 'true' : 'false'))) {
          item.querySelector('.slicerCheckbox')?.click();
        }
      });
    };
    deselectLabels.forEach(l => clickByTitle(l, true));
    let delay = {between_deselect_select};
    selectLabels.forEach((label, i) => {
      setTimeout(() => clickByTitle(label, false), delay + i * {between_selects});
    });
    setTimeout(() => {
      const sel = Array.from(document.querySelectorAll('.slicerItemContainer'))
        .filter(i => i.getAttribute('aria-selected') === 'true')
        .map(i => i.getAttribute('title'));
      resolve('Selected: ' + sel.join(', '));
    }, delay + selectLabels.length * {between_selects} + {verify});
  });
})()
```

Alternate variant seen on some pages: checkboxes carry a `selected` CSS class suffix (`class="slicerCheckbox selected"`) instead of `aria-selected` on the container. If `aria-selected` reads are unreliable, check `checkbox.className.includes('selected')` instead, and locate items via `[class*="slicerText"]` → `.closest('[class*="slicerItemContainer"]')` → `.querySelector('[class*="slicerCheckbox"]')`.

### `dropdown-nested` — hierarchical dropdown (e.g. Country → City)
Used when the slicer is a closed dropdown that must be opened, and the target value sits under a parent node that may need expanding first (e.g. a city under a country). Handles open + expand + select + retry in one call — do not split into separate steps, the popup can take a couple of render passes to appear.

```js
new Promise((resolve) => {
  const wrappers = document.querySelectorAll('.slicer-content-wrapper');
  const dropdown = wrappers[1]?.querySelector('.slicer-dropdown-menu'); // index may vary by report — verify with a snapshot if this misses
  if (!dropdown) return resolve('no dropdown');
  dropdown.click();
  const attempt = (tries) => {
    setTimeout(() => {
      const popups = document.querySelectorAll('[id^="slicer-dropdown-popup"]');
      let popup = null;
      for (const p of popups) {
        if (p.querySelectorAll('.slicerItemContainer').length > 0) { popup = p; break; }
      }
      if (!popup && tries > 0) return attempt(tries - 1);
      if (!popup) return resolve('popup never ready');
      const parentItem = Array.from(popup.querySelectorAll('.slicerItemContainer'))
        .find(i => i.getAttribute('title') === '{parent}');
      if ('{parent}' && !parentItem) return resolve('{parent} not found');
      if (parentItem && parentItem.getAttribute('aria-expanded') !== 'true') {
        parentItem.querySelector('.expandButton')?.click();
        setTimeout(() => { dropdown.click(); attempt(3); }, 400);
        return;
      }
      if (parentItem && parentItem.getAttribute('aria-selected') === 'true') {
        parentItem.querySelector('.slicerCheckbox')?.click();
      }
      setTimeout(() => {
        const leaf = Array.from(popup.querySelectorAll('.slicerItemContainer'))
          .find(i => i.getAttribute('title') === '{label}');
        leaf?.querySelector('.slicerCheckbox')?.click();
        resolve('{label} selected');
      }, 200);
    }, 400);
  };
  attempt(5);
})
```
For selecting multiple leaves under the same open popup in one pass (e.g. two cities forming a combined region), extend the final block to toggle off whatever leaf(s) don't belong and toggle on each label in `select`:
```js
new Promise((resolve) => {
  const wrappers = document.querySelectorAll('.slicer-content-wrapper');
  const dropdown = wrappers[1]?.querySelector('.slicer-dropdown-menu');
  if (!dropdown) return resolve('no dropdown');
  dropdown.click();
  const attempt = (tries) => {
    setTimeout(() => {
      const popups = document.querySelectorAll('[id^="slicer-dropdown-popup"]');
      let popup = null;
      for (const p of popups) {
        if (p.querySelectorAll('.slicerItemContainer').length > 0) { popup = p; break; }
      }
      if (!popup && tries > 0) return attempt(tries - 1);
      if (!popup) return resolve('popup never ready');
      const items = popup.querySelectorAll('.slicerItemContainer');
      const deselectLabels = {deselect_json};
      const selectLabels = {select_json};
      for (const item of items) {
        const title = item.getAttribute('title');
        const selected = item.getAttribute('aria-selected') === 'true';
        if (deselectLabels.includes(title) && selected) item.querySelector('.slicerCheckbox')?.click();
        if (selectLabels.includes(title) && !selected) item.querySelector('.slicerCheckbox')?.click();
      }
      resolve('applied');
    }, 400);
  };
  attempt(5);
})
```
Close the dropdown after selection:
```js
document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))
```

## Pattern Detection (when the caller doesn't already know the pattern)

Take a quick read of the slicer DOM before committing to a pattern:
```js
(() => {
  return {
    hasSlicerText: document.querySelectorAll('span.slicerText').length,
    hasFlatCheckbox: document.querySelectorAll('.slicerItemContainer').length,
    hasDropdown: document.querySelectorAll('.slicer-dropdown-menu').length,
  };
})()
```
`hasDropdown > 0` → `dropdown-nested`. `hasFlatCheckbox > 0` and no dropdown → `checkbox-flat`. `hasSlicerText > 0` and neither of the above → `text-click`.

## Process

1. **Navigate.** `open_url` (chrome) or `browser_navigate` (playwright) to `report_url`. Wait `wait_ms.initial_load` (default 5000ms). Confirm the page loaded — check that `document.title` contains "Power BI" or "Scorecard"; if it looks like a login screen, wait 3 more seconds and re-check once before treating it as a load failure.

2. **Apply the deselect/select sequence** using the JS template matching `slicer_pattern`, substituting `{label}`, `{parent}`, `{deselect_json}`, `{select_json}`, and the wait values from `wait_ms`.

3. **If `verify_after` is true**, read back the currently selected items (the same query used inside each pattern's script) and return them to the caller. If the returned selection doesn't match `select`, report this clearly — the caller should not proceed to read KPIs against a wrongly filtered view. This matters: a past incident (`err-20260727T143315-NTKXRY`) traced bad revenue numbers directly to an unverified filter that silently didn't apply.

4. **Return** `{applied: bool, selected: [...], pattern_used, notes}` to the caller.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## SKILL COMPLETE

This skill has no side effects beyond in-page browser state and writes no files — it does not write its own eval-harness signal file. The caller skill signals completion of its overall run via `eval-signal-write`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/powerbi-navigate-slicer-latest.json
```

Content:
```json
{
  "skill": "powerbi-navigate-slicer",
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
python3 systems/eval-harness/grade_skill_run.py --skill powerbi-navigate-slicer
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/powerbi-navigate-slicer.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

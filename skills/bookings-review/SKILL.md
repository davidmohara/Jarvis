---
name: bookings-review
description: >
  Pull YTD bookings data for Dallas, TX and South Texas from the Improving Sales Analytics
  PowerBI report. Reports both regions side-by-side. Trigger when David says "bookings",
  "bookings review", "/bookings-review", or asks about YTD bookings for Dallas or South Texas.
owning_agent: chase
model: sonnet
trigger_keywords: [bookings, weekly bookings, bookings review]
trigger_agents: [chase, chief]
---

# Bookings Review

## Purpose

Pull live YTD bookings data for Dallas, TX and South Texas from the Improving Sales Analytics
PowerBI report. Report both regions side-by-side using Playwright browser automation.

Note: South Texas = Austin + Houston combined in PowerBI slicer terminology. Output is
intentionally side-by-side only — bookings are not aggregated into a One Texas combined total.

This skill delegates navigation to the shared `powerbi-navigate-slicer` skill using the
`playwright` connector (not `chrome` — this is the one report in the collection driven by
Playwright rather than Chrome MCP; the slicer DOM shape is identical `text-click`, only the
underlying browser tool differs). There is no cache-check phase — bookings are reviewed
live every time this skill runs, no Obsidian snapshot file backs it.

---

## Execution

### Step 1 — Navigate Directly to Wins By Enterprise

Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: "https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/61775932-91be-43e4-bb21-fd3354978687/ReportSection7e20c80e361d6cc45eed?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi"
connector: "playwright"
slicer_pattern: "text-click"
select: []
```
SSO auto-authenticates. No manual login needed. Navigate directly to this URL — do NOT use
the mcas.ms variant or click through the nav, both cause unnecessary redirects or wrong-page
landings. The report loads in 3-5 seconds. Take a screenshot (`mcp__playwright__browser_take_screenshot`)
to confirm the enterprise slicer is visible before proceeding.

### Step 2 — Read Dallas, TX

Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: (same page — already loaded)
connector: "playwright"
slicer_pattern: "text-click"
select: [{label: "Dallas, TX"}]
```

Then take a screenshot (`mcp__playwright__browser_take_screenshot`) to capture the KPI tiles.

Read the following values from the screenshot:
- Bookings YTD
- Bookings (New) YTD
- Bookings (Extension) YTD
- Annual Bookings Target
- Sales amount needed to reach Target
- Opportunities Won
- On Target %

### Step 3 — Read South Texas

Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: (same page)
connector: "playwright"
slicer_pattern: "text-click"
select: [{label: "South Texas"}]
```

Take a screenshot and read the same KPI values.

---

## Output Format

Report results as a side-by-side comparison table:

```
## YTD Bookings — [Today's Date]

| Metric                          | Dallas, TX   | South Texas  |
|---------------------------------|-------------|-------------|
| Bookings YTD                    | $X.XM        | $X.XM        |
| Bookings (New) YTD              | $X.XM        | $X.XM        |
| Bookings (Extension) YTD        | $X.XM        | $X.XM        |
| Annual Bookings Target          | $X.XM        | $X.XM        |
| Sales Needed to Hit Target      | $X.XM        | $X.XM        |
| Opportunities Won                | XX           | XX           |
| On Target %                     | XX%          | XX%          |
```

Follow with one sentence of Chase-voice commentary on combined trajectory or any region
significantly off-pace. If one region is at risk, say so directly.

---

## Notes

- The slicer is single-select — clicking one deselects the other. This is
  `powerbi-navigate-slicer`'s `text-click` pattern: real DOM elements (`span.slicerText`)
  clicked by exact text match, with a fallback broader text-content scan built in if the
  primary selector returns not-found. Do NOT use coordinate injection, which breaks when
  the slicer tree renders differently.
- Output is side-by-side only. Bookings are dollar amounts that could be summed, but the
  report format intentionally keeps them separate for regional clarity.

---

## Source

PowerBI report: Improving Sales Analytics — Sales Wins / Wins By Enterprise
Mechanics: `skills/powerbi-navigate-slicer/SKILL.md` (`connector: "playwright"`)
Connector: Playwright MCP (`mcp__playwright__*`)
Auth: SSO (auto)



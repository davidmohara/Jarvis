# Galen: Hume Bodypod + Apple Health Integration Plan

**Status:** Research complete — not yet implemented
**Created:** 2026-06-07
**Triggered by:** Request to integrate Hume Bodypod body composition data into Galen's metrics tracking, with appropriate accuracy guardrails and trend-only interpretation

---

## Context

David uses a **Hume Bodypod** (BIA-based smart scale) that takes body composition readings more frequently than the quarterly DEXA scan. The BIA readings are less accurate than DEXA in absolute terms but useful for detecting directional trends between DEXA appointments. The goal is to give Galen visibility into that interim movement — particularly weight direction, body fat trajectory, and lean mass — without treating BIA readings as ground truth.

**Design requirement:** Hume data must be clearly isolated from DEXA data. Galen should only act on BIA trends (3+ consistent readings in a direction), never on individual readings. BIA values are labeled `accuracy: estimated` throughout the system.

---

## Research Findings

### Hume Health App — No API

Hume Health (humehealth.com) has no public developer API or SDK. There is no MCP server available for direct Hume integration. The only external data path is through Apple Health.

**Note:** "Hume AI" (dev.hume.ai) is a completely different company making speech/expression models — unrelated.

### Hume → Apple Health Data Flow

The Hume Health app supports Apple Health sync via Profile > Connected Apps > Connect. Once linked, body composition data writes to Apple Health. The data types that flow through are determined by what HealthKit supports:

| Hume Metric | HealthKit Type | Flows to Apple Health? |
|-------------|----------------|------------------------|
| Weight | `HKQuantityTypeIdentifier.bodyMass` | Yes |
| Body Fat % | `HKQuantityTypeIdentifier.bodyFatPercentage` | Yes |
| BMI | `HKQuantityTypeIdentifier.bodyMassIndex` | Yes |
| Lean Body Mass | `HKQuantityTypeIdentifier.leanBodyMass` | Likely |
| Waist Circumference | `HKQuantityTypeIdentifier.waistCircumference` | Possibly |
| Visceral Fat | No HealthKit equivalent | No — stays in Hume app only |
| Segmental muscle mass | No HealthKit equivalent | No — stays in Hume app only |
| Water % | No HealthKit equivalent | No — stays in Hume app only |

**Key constraint:** The more granular Hume metrics that overlap with DEXA (VAT, segmental lean mass, A/G ratio) do not have HealthKit equivalents and will not flow through. What flows is limited to weight, body fat %, BMI, and lean mass — still valuable for trending.

**Reliability concern:** The Hume app has no WiFi; the phone must be nearby with the app open for readings to save. There are known Apple Health sync reliability issues (reported user complaints in the Hume community as of early 2026). The integration plan must account for gaps — Galen should not assume a reading will appear for every scan.

---

## Apple Health MCP Options Evaluated

Three viable MCP server options were identified:

### Option A: Vitalink (RyanLisse/Vitalink)
**GitHub:** github.com/RyanLisse/Vitalink

- macOS CLI + MCP server that reads directly from HealthKit — no XML export required
- Same developer as the WHOOP MCP server already in Jarvis's stack
- Supported read types: weight, body fat %, heart rate, steps, workouts, activity rings, blood glucose
- Supports write operations as well (not needed here)
- Requires the MCP server process to run on David's Mac (local process, not remote)
- **Assessment:** Best fit for Jarvis. Reads HealthKit live, aligns with existing stack (same developer pattern as whoop-mcp-server), surgical addition without touching existing WHOOP integration.

### Option B: neiltron/apple-health-mcp
**GitHub:** github.com/neiltron/apple-health-mcp

- SQL/DuckDB-based querying over Apple Health data
- **Requires manual XML export** from the Apple Health app — not automatic
- Runs via `npx`, no persistent process needed
- Supports natural language and SQL queries over the exported data
- **Assessment:** Not suitable for Galen's autonomous operation. Manual export step breaks the automated data pull workflow.

### Option C: Open Wearables (the-momentum/apple-health-mcp-server, now openwearables.io)
**GitHub:** github.com/the-momentum/apple-health-mcp-server

- Self-hosted REST API + MCP server
- Supports: Apple Health, WHOOP, Garmin, Polar, Suunto, Strava, Samsung Health, Google Health Connect
- MIT licensed, zero per-user fees
- MCP server included for direct AI assistant integration
- Introduced in January 2026, v0.3 in February 2026
- Could theoretically replace the existing WHOOP MCP and add Apple Health in one platform
- **Assessment:** More powerful but adds operational complexity. Replacing the WHOOP MCP would require testing and migration. Best considered if/when Jarvis adds additional wearable integrations (Oura, Garmin, etc.) and a unified wearables layer becomes worth the investment.

### Recommendation

**Start with Vitalink (Option A).** It's the most surgical fit — reads HealthKit directly without manual exports, is by the same developer as the existing WHOOP MCP server (same patterns, same trust level), and doesn't touch anything already working.

**Future consideration:** If David adds other wearables (Oura Ring, Garmin, continuous glucose monitor), evaluate migrating to Open Wearables as a unified wearables MCP layer at that point.

---

## Full Data Pipeline

```
Hume Bodypod (BIA scan)
        ↓  Bluetooth
Hume Health iOS App
        ↓  Apple Health sync (must be connected, app open)
Apple Health (HealthKit)
        ↓  Vitalink MCP server (running on David's Mac)
Galen (via mcp__vitalink__* tools)
        ↓
data/health/metrics-log.json  (body_comp_bia entry)
        ↓
Trend analysis (3+ readings, directional only)
```

---

## Schema Changes Required

### New entry type: `body_comp_bia`

Add to `data/health/schema.md` and `data/health/metrics-log.json`:

```json
{
  "entry_id": "body-comp-bia-2026-06-07",
  "date": "2026-06-07",
  "category": "body_comp_bia",
  "source": "Hume Bodypod via Apple Health / Vitalink",
  "accuracy": "estimated",
  "accuracy_note": "BIA-based. Less accurate than DEXA in absolute terms. Use for trend direction only — do not compare directly to DEXA values.",
  "metrics": {
    "weight_lbs": null,
    "body_fat_pct": null,
    "lean_mass_lbs": null,
    "bmi": null,
    "waist_circumference_in": null
  },
  "notes": ""
}
```

**Separation rule:** `body_comp_bia` entries are never mixed with `dexa` entries in absolute comparisons. Trend logic operates only within the same category type.

---

## Galen Skill Changes Required

### galen-morning-snapshot

Add an optional Step 6b (between peptide reminders and routing to Chief):

- Read the last 10 `body_comp_bia` entries from `metrics-log.json`
- Only surface if: 3+ consecutive readings show the same directional movement (all up or all down) in weight or body fat %
- Threshold for flagging: >1 lb consistent direction over 3+ readings, or >0.5% body fat in one direction
- Output format: `"Scale trend: weight down 2.4 lbs over last 4 readings (Hume, estimated)"` — always labeled as estimated
- If no trend signal, omit entirely (don't surface noise)

### galen-visit-prep

Add to Step 5 (Body Composition Update):

- After reading DEXA data, also read the last 30 days of `body_comp_bia` entries
- Show BIA trend alongside DEXA: "DEXA (ground truth): 237.8 lbs / 19.6% BF as of April 1. Scale trend since then: down ~3 lbs over 12 readings (Hume BIA, estimated)."
- Clearly label the two sources and their accuracy difference
- Do not compute a "combined" body fat % — DEXA and BIA values stay separate

### galen-monthly-health-review (Step 03)

In the body composition step, add:

- After reading DEXA/Excel data, read all `body_comp_bia` entries for the current month
- If 4+ readings exist, compute: month-start weight, month-end weight, direction, and reading count
- Include in the monthly note as a supplementary data row labeled "(Hume BIA, estimated)"
- If fewer than 4 readings, note "insufficient BIA readings this month for trend (N readings)"

### galen-protocols (Step 1 — context loading)

No change needed. Protocol skill does not use body composition data.

### New skill consideration: `galen-body-comp-trend`

A lightweight skill that could be triggered on demand ("how's my weight trending?") that:
1. Reads all `body_comp_bia` entries from metrics-log
2. Reads all `dexa` entries
3. Produces a timeline chart (markdown table) showing DEXA ground-truth anchors + BIA trend readings
4. Computes rate of change (lbs/week) from BIA readings since last DEXA
5. Projects time to goal weight at current BIA trend rate — clearly labeled as a projection from estimated data
6. Not a morning skill — on-demand only

---

## Data Backfill Question

Apple Health may have historical Hume readings already stored (if the sync was connected previously). On first Vitalink integration, Galen should query the full available history for `bodyMass` and `bodyFatPercentage` samples from the Hume source and backfill `body_comp_bia` entries into the metrics log. This gives immediate trend context rather than starting from zero.

---

## Implementation Steps (Ordered)

### Phase 1: Infrastructure

1. **Verify Hume → Apple Health sync is active.** Open Hume Health app, go to Profile > Connected Apps, confirm Apple Health is connected. Take a scan and confirm the reading appears in the Apple Health app under Body Measurements.

2. **Install and configure Vitalink MCP server.** Clone `github.com/RyanLisse/Vitalink`, follow setup instructions, add to `.mcp.json` alongside the existing WHOOP MCP server. Verify it can read `bodyMass` and `bodyFatPercentage` samples from HealthKit.

3. **Test the data path.** Have Galen query Vitalink for the last 30 days of weight and body fat readings. Confirm Hume readings are present and labeled with the correct source bundle ID from Hume Health app.

### Phase 2: Schema

4. **Add `body_comp_bia` entry type to `data/health/schema.md`** (per spec above).

5. **Add Vitalink to `.mcp.json`** and add `mcp__vitalink__*` to the allowed tools list for galen-morning-snapshot and galen-visit-prep skill stubs in `.claude/skills/`.

### Phase 3: Skill Updates

6. **Update `skills/galen-morning-snapshot/SKILL.md`** with Step 6b (BIA trend check, threshold logic, "estimated" label).

7. **Update `skills/galen-visit-prep/SKILL.md`** Step 5 to include BIA trend alongside DEXA.

8. **Update `workflows/galen-monthly-health-review/workflow.md`** Step 03 to include monthly BIA summary.

9. **Add `data/health/schema.md` entry for `body_comp_bia`.**

10. **Backfill historical Hume readings** from Apple Health into metrics-log on first run.

### Phase 4: Optional

11. **Create `galen-body-comp-trend` skill** for on-demand trending analysis.

---

## Open Questions

| Question | Notes |
|----------|-------|
| Is Hume sync currently active to Apple Health? | Needs manual verification in the iOS app before any code work |
| What source bundle ID does Hume use in HealthKit? | Needed to filter Hume readings from other weight sources (manual entries, etc.) |
| How many historical Hume readings are in Apple Health? | Determines value of backfill step |
| Does Vitalink expose the data source per reading? | Critical — need to distinguish Hume readings from manual entries or other apps |
| Is Open Wearables worth evaluating now vs. Vitalink? | Only matters if additional wearables are being added soon |

---

## What This Does Not Solve

- The more detailed Hume metrics (visceral fat, segmental muscle, water %) will not flow through Apple Health. For VAT trending specifically, only DEXA captures it. There is no workaround without a Hume API (which doesn't exist).
- If the Hume app is not open when a scan is taken, the reading will not save. Galen has no way to detect or compensate for missed readings — gaps in the BIA timeline are expected and the trend logic must tolerate them.
- BIA accuracy degrades with hydration, recent meals, and time of day. Even for trending purposes, readings should ideally be taken at the same time of day under consistent conditions. Galen cannot enforce this but can note it when significant variance appears.

---

## Sources

- [Vitalink — GitHub (RyanLisse)](https://github.com/RyanLisse/Vitalink)
- [neiltron/apple-health-mcp — GitHub](https://github.com/neiltron/apple-health-mcp)
- [Open Wearables — openwearables.io](https://openwearables.io/)
- [Open Wearables MCP Server Guide](https://www.themomentum.ai/blog/talk-to-your-wearable-data-how-open-wearables-mcp-server-connects-health-metrics-to-ai-assistants)
- [Hume Health App — App Store](https://apps.apple.com/us/app/hume-health/id1477782599)
- [Hume Health FAQ](https://humehealth.com/pages/faq)
- [Apple HealthKit Data Types — Apple Developer Docs](https://developer.apple.com/documentation/healthkit/healthkit-data-types)
- [Claude AI adds Apple Health connectivity — MacRumors](https://www.macrumors.com/2026/01/22/claude-ai-adds-apple-health-connectivity/)

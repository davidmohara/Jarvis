# Galen: Hume Bodypod + Apple Health Integration Plan

**Status:** Implementation ready — binary written, skill updates pending
**Created:** 2026-06-07
**Updated:** 2026-06-21 (CloudKit fallback added)
**Triggered by:** Request to integrate Hume Bodypod body composition data into Galen's metrics tracking — expanded to unified Apple Health read layer covering all devices and data sources

---

## Context

Originally scoped as a Hume Bodypod integration, this expanded into a **unified Apple Health read layer** for Galen. Apple Health aggregates data from multiple sources David already uses — Hume (body composition), WHOOP (resting HR, sleep stages, respiratory rate), iPhone sensors (steps, gait, flights climbed), and Apple itself (VO2 max, environmental audio) — making it the right single data bus for health metrics that don't require the WHOOP proprietary API.

**What this does not replace:** The WHOOP MCP server remains the authoritative source for WHOOP-specific data that WHOOP deliberately withholds from HealthKit: HRV (RMSSD), per-day recovery scores, and the Red/Yellow/Green classification. HealthKit provides complementary data, not a WHOOP replacement.

**Hume design requirements (preserved):** Hume BIA data must be clearly isolated from DEXA data. Galen acts only on BIA trends (3+ consistent readings), never on individual readings. BIA values are labeled `accuracy: estimated` throughout.

---

## Architecture Decision (Updated 2026-06-21)

### Options Evaluated and Eliminated

**Vitalink (RyanLisse/Vitalink):** Eliminated. Requires Apple Watch paired to MacBook Pro. David does not have an Apple Watch.

**Open Wearables (the-momentum/open-wearables):** Eliminated. Requires Docker, self-hosted REST API, iOS companion app running on the network, and the WHOOP MCP layer is in beta with critical gaps (per-day recovery score, HRV rmssd, sleep stages are REST-only, not exposed as MCP tools). Operational complexity not justified.

**neiltron/apple-health-mcp:** Eliminated. Requires manual XML export from Apple Health — breaks autonomous operation.

**SQLite direct query:** Eliminated. `~/Library/Health/` does not exist on macOS — the Health database does not sync from iPhone to Mac.

### Selected Architecture: Swift HealthKit CLI Binary (with CloudKit Fallback)

A purpose-built Swift Package executable that queries health data on macOS via two pathways:

1. **Primary (HealthKit, preferred):** If the Mac has the Health app installed and HealthKit available, query directly via HealthKit on macOS across all connected data sources.

2. **Fallback (CloudKit):** If HealthKit is unavailable locally but Health data exists in iCloud (visible in System Settings > iCloud > Health), fetch records directly from the private iCloud Health container via CloudKit REST API.

Both require the Mac to be signed into the same iCloud account as the iPhone syncing the health data. Compiled and signed once with David's existing Apple Developer account, called by Galen as a shell command via Desktop Commander.

```
Hume Bodypod ──► Apple Health ──────────────────────┐
WHOOP ──────────► Apple Health (partial — see below) ┤
iPhone sensors ─► Apple Health ─────────────────────┤
                                                     ▼
                              Apple Health (HealthKit on Mac via iCloud sync)
                                                     │
                                      tools/health-query/.build/release/HealthQuery
                                                     │
                               JSON output (56 types, source-tagged per record)
                                                     │
                                              Galen skills
                                             /             \
                               body_comp_bia entries     WHOOP MCP server
                               in metrics-log.json       (HRV, recovery score,
                                                          sleep detail)
```

**WHOOP split:** WHOOP writes resting HR, sleep stages, and respiratory rate to HealthKit — the binary captures these. WHOOP deliberately withholds HRV (RMSSD) and per-day recovery scores from HealthKit. The WHOOP MCP server remains the only source for those.

**Why this works:**
- macOS 13+ exposes HealthKit to properly signed Mac apps and executables
- David already has a paid Apple Developer account (iOS dev) — the only hard prerequisite
- No persistent process, no Docker, no companion app, no Apple Watch required
- Binary is compiled once, lives at `tools/health-query/` in the IES repo, called on demand
- Authorization prompt fires on first run only, persists indefinitely thereafter
- Every record is source-tagged (`source` + `source_bundle`) — Galen filters by source as needed
- **Fallback:** If HealthKit is unavailable locally but Health data exists in iCloud, the tool attempts to fetch records via CloudKit REST API (requires iCloud account sign-in on the Mac)

---

## Data Pipeline

### What Flows Through Apple Health from Hume

| Hume Metric | HealthKit Type | Flows to Apple Health? |
|-------------|----------------|------------------------|
| Weight | `bodyMass` | Yes |
| Body Fat % | `bodyFatPercentage` | Yes |
| BMI | `bodyMassIndex` | Yes |
| Lean Body Mass | `leanBodyMass` | Likely |
| Waist Circumference | `waistCircumference` | Possibly |
| Visceral Fat | No HealthKit equivalent | No |
| Segmental muscle mass | No HealthKit equivalent | No |
| Water % | No HealthKit equivalent | No |

**Key constraint:** VAT, segmental lean mass, A/G ratio do not have HealthKit equivalents and will never flow through. The integration tracks weight, body fat %, and lean mass — sufficient for trending.

### Reliability Notes

- Hume app has no WiFi. Phone must be nearby with the app open during a scan for data to save.
- Apple Health sync has known reliability issues (user-reported in Hume community). Gaps in the BIA timeline are expected. Trend logic must tolerate them.
- BIA accuracy degrades with hydration, recent meals, and time of day. Galen can note high variance but cannot enforce consistent conditions.

---

## Phase 1: Swift CLI Tool Build

### Tool Location

All files are written and committed:

```
IES/
  tools/
    health-query/
      Package.swift
      Sources/HealthQuery/main.swift
      Resources/HealthQuery.entitlements
      build.sh
```

### What the Binary Does

Queries **56 HealthKit types** across Tier 1 (always pull) and Tier 2 (pull when available). Every record is tagged with `source` (human-readable app name) and `source_bundle` (bundle ID) so Galen can filter by device. Output is structured JSON with three arrays: `quantity_records`, `category_records`, and `workout_records`.

**Query windows by type group** (built into the binary):

| Type Group | Window | Rationale |
|---|---|---|
| Body composition (Hume) | 365 days | Monthly scans; need full year for trend |
| VO2 max | 365 days | Infrequent measurement |
| Raw heart rate samples | 7 days | Dense data; longer windows are unmanageable |
| Resting HR, HRV, recovery | 90 days | Quarterly trend context |
| Activity (steps, calories, exercise) | 90 days | Quarterly baseline |
| Sleep analysis | 30 days | Monthly review cadence |

**Types queried — Tier 1 (always):**
body mass, body fat %, lean body mass, BMI, height, heart rate, resting heart rate, HRV SDNN (Apple Watch only — see note), walking avg HR, HR recovery, steps, active calories, basal calories, exercise minutes, stand time, flights climbed, walk/run distance, VO2 max, respiratory rate, SpO2, sleep analysis

**Types queried — Tier 2 (when device/app is connected):**
waist circumference, body temperature, blood pressure (systolic + diastolic), blood glucose, insulin delivery, walking speed, step length, walking asymmetry %, double support %, stair ascent/descent speeds, 6-min walk distance, running stride/oscillation/ground contact/power/speed, environmental audio exposure, headphone audio exposure, time in daylight, alcoholic beverages, BAC, dietary macros + key micronutrients (magnesium, vitamin D, zinc, caffeine, water, sodium, protein, fat, carbs, fiber, sugar, energy), mindful sessions, cardiac alert events (high/low HR, irregular rhythm, low cardio fitness)

**Workouts:** All HKWorkout records from the last 90 days with activity type, duration, active calories, and distance.

### Key Behavioral Notes

**HRV methodology mismatch.** `hrv_sdnn_ms` in the output is Apple Watch SDNN — a different algorithm than WHOOP's RMSSD. SDNN typically runs 1.5–2x higher than RMSSD at rest. The binary embeds a warning in `meta.note_hrv`. Galen must never compare these values directly. WHOOP RMSSD is only available via the WHOOP MCP server.

**Sleep source conflict.** Both WHOOP and Apple Watch write `sleepAnalysis` records for the same nights. The binary captures both, tagged by `source_bundle`. Galen prefers WHOOP sleep stages (`com.whoop.Whoop`) when available; falls back to Apple Watch. Never merge both sources for the same night.

**Respiratory rate conflict.** Same situation — WHOOP and Apple Watch both write it during sleep. Filter by `source_bundle`.

**Body fat % format.** Returned as a decimal fraction (0.194 = 19.4%). Galen multiplies by 100 when displaying.

**Aggregate vs. raw.** Daily aggregate types (steps, calories, exercise time, dietary entries) are summed per calendar day — one record per day. Spot measurement types (body weight, HR, resting HR) are individual samples.

**Hume source bundle.** The bundle ID `com.hume.health` is an educated guess. Confirm on first run by checking the `source_bundle` field on body mass records. If it differs, update `SourceID.hume` in `main.swift` and rebuild.

### Build Steps for David

```bash
cd IES/tools/health-query/

# 1. Edit build.sh — replace YOUR_TEAM_ID with your actual Team ID
#    Find it at: https://developer.apple.com/account → Membership Details
nano build.sh

# 2. Build and sign
bash build.sh

# 3. First run — approve the HealthKit permission prompt (one time only)
.build/release/HealthQuery

# 4. Verify output and confirm Hume's source bundle
.build/release/HealthQuery | jq '[
  .quantity_records[]
  | select(.type == "body_mass_kg")
  | {date, value, source, source_bundle}
] | .[0:5]'
```

After step 4, note the exact `source_bundle` value for Hume. If it differs from `com.hume.health`, update `SourceID.hume` in `main.swift` and rerun `bash build.sh`.

### Sample Output Shape

```json
{
  "generated_at": "2026-06-21T09:14:22Z",
  "meta": {
    "note_hrv": "hrv_sdnn_ms is Apple Watch SDNN. WHOOP reports RMSSD. Do not compare directly.",
    "note_sleep": "sleep records include WHOOP and Apple Watch. Filter by source_bundle.",
    "quantity_types_queried": 49,
    "category_types_queried": 7,
    "total_records": 2847,
    "windows_used": { "body_composition_days": 365, "sleep_days": 30, ... }
  },
  "quantity_records": [
    {
      "type": "body_mass_kg",
      "value": 103.6,
      "unit": "kg",
      "date": "2026-06-20T07:23:11-05:00",
      "end_date": "2026-06-20T07:23:11-05:00",
      "source": "Hume Health",
      "source_bundle": "com.hume.health"
    },
    {
      "type": "resting_heart_rate_bpm",
      "value": 52,
      "unit": "count/min",
      "date": "2026-06-20T00:00:00-05:00",
      "end_date": "2026-06-20T00:00:00-05:00",
      "source": "WHOOP",
      "source_bundle": "com.whoop.Whoop"
    }
  ],
  "category_records": [
    {
      "type": "sleep",
      "value": 5,
      "value_label": "asleepREM",
      "start_date": "2026-06-20T01:14:00-05:00",
      "end_date": "2026-06-20T02:47:00-05:00",
      "duration_minutes": 93.0,
      "source": "WHOOP",
      "source_bundle": "com.whoop.Whoop"
    }
  ],
  "workout_records": [
    {
      "type": "workout",
      "activity": "Running",
      "start_date": "2026-06-19T06:30:00-05:00",
      "end_date": "2026-06-19T07:15:00-05:00",
      "duration_minutes": 45.0,
      "active_calories": 412.0,
      "distance_meters": 7800.0,
      "source": "WHOOP",
      "source_bundle": "com.whoop.Whoop"
    }
  ]
}
```

## Phase 2: Schema Changes

### Add `body_comp_bia` to `data/health/schema.md`

New entry type, added after the existing `body_comp` entry:

```markdown
### `body_comp_bia`

Written by Galen skills when BIA readings are pulled from Apple Health via the `HealthQuery` tool. Only readings sourced from Hume Health are written — manual entries and other apps are filtered out by source name.

**Accuracy note:** BIA-based. Less accurate than DEXA in absolute terms. Use for directional trend only — never compare directly to DEXA values. Galen does not act on individual readings; trend logic requires 3+ consistent readings.

\```json
{
  "entry_id": "body-comp-bia-2026-06-20",
  "date": "2026-06-20",
  "category": "body_comp_bia",
  "source": "Hume Bodypod via Apple Health / HealthQuery",
  "accuracy": "estimated",
  "accuracy_note": "BIA-based. Use for trend direction only. Do not compare to DEXA values.",
  "metrics": {
    "weight_lbs": 228.4,
    "body_fat_pct": 19.4,
    "lean_mass_lbs": 184.1,
    "bmi": null,
    "waist_circumference_in": null
  },
  "notes": ""
}
\```

**Separation rule:** `body_comp_bia` entries are never mixed with `dexa` entries in absolute comparisons. Trend logic operates only within the same category type.
```

---

## Phase 3: Skill Updates

### 3a. galen-morning-snapshot — Add Step 6b

Insert between Step 6 and Step 7 (after peptide reminders, before routing to Chief):

```markdown
### Step 6b: BIA Body Composition Trend (Optional)

Run the HealthQuery tool to check for recent Hume scale readings:

\```bash
tools/health-query/.build/release/HealthQuery 30 2>/dev/null | \
  jq '[.records[] | select(.source | test("Hume"; "i"))]'
\```

**If the tool is unavailable or returns no Hume readings:** skip this step entirely. Do not surface to Chief.

**If Hume readings are present:**

1. Extract `bodyMass` readings only, sorted by date descending
2. Apply trend logic:
   - Need 3+ consecutive readings to establish a trend
   - Threshold for flagging: >1 lb consistent direction over 3+ readings, OR >0.5% body fat in one direction
   - "Consistent direction" means all readings move the same way — a reversal resets the count
3. **If trend threshold is met:** add one line to Chief's output:
   - `"Scale trend: weight down 2.4 lbs over last 4 readings (Hume, estimated)"`
   - `"Scale trend: weight up 1.8 lbs over last 3 readings (Hume, estimated)"`
   - Always labeled as `estimated`
4. **If no trend threshold is met:** omit entirely. Do not surface noise.
5. **Backfill check:** If new Hume readings exist that are not yet in `data/health/metrics-log.json` (check by date), append `body_comp_bia` entries for each new reading before continuing. Schema in `data/health/schema.md`.
```

### 3b. galen-visit-prep — Update Step 5

Replace the current Step 5 body composition section with:

```markdown
### Step 5: Body Composition Update

#### 5a: DEXA Data (Ground Truth)

Pull DEXA data from Dropbox Excel (`~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`):
- Weight, body fat %, BMI, lean mass, VAT (if captured)
- Compare to prior DEXA scan

#### 5b: BIA Trend Since Last DEXA (Supplementary)

Run HealthQuery for the period since the last DEXA scan date:

\```bash
tools/health-query/.build/release/HealthQuery 90 2>/dev/null | \
  jq '[.records[] | select(.source | test("Hume"; "i")) | select(.type == "bodyMass")]'
\```

If 3+ Hume readings exist since last DEXA:
- Compute direction (up/down/stable) and magnitude
- Report alongside DEXA, clearly separated:

\```
DEXA (ground truth, [date]): 237.8 lbs / 19.6% BF
Scale trend since DEXA: weight down ~3.1 lbs over 12 readings (Hume BIA, estimated)
\```

**Rules:**
- Never compute a "combined" body fat % — DEXA and BIA values stay separate
- Always label Hume readings as `(Hume BIA, estimated)`
- If fewer than 3 readings since last DEXA, note "insufficient Hume readings for trend since DEXA (N readings)"
- If HealthQuery fails or returns no data, proceed with DEXA only — do not block the skill

#### 5c: Store in Working Memory

\```
body_comp_update:
  dexa_date: YYYY-MM-DD
  weight: N lbs (goal: 210 lbs)
  body_fat: N% (goal: 17%)
  bmi: N (goal: <20)
  lean_mass: N lbs
  trend: "improving" | "stable" | "drifting"
  progress_vs_goal: "on track" | "at risk" | "off track"
  bia_trend_since_dexa: "down ~3 lbs over 12 readings (estimated)" | null
\```
```

### 3c. galen-monthly-health-review — Update Step 03

Replace the current Step 03 body comp section with:

```markdown
## STEP 03: Pull DEXA & Body Composition

#### DEXA (Ground Truth)

Read `~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`:
- Latest DEXA scan date, weight, body fat %, BMI, lean mass, trend vs. prior month
- Compare to Lifebook goals: 210 lbs, 17% BF, BMI <20

#### BIA Monthly Summary (Supplementary)

Run HealthQuery for the current calendar month:

\```bash
# Set START to first day of current month, END to today
tools/health-query/.build/release/HealthQuery 31 2>/dev/null | \
  jq '[.records[] | select(.source | test("Hume"; "i")) | select(.type == "bodyMass")]'
\```

**If 4+ readings this month:**
- month_start_weight: weight of earliest reading in month
- month_end_weight: weight of latest reading in month
- direction: up | down | stable (delta > 0.5 lbs)
- reading_count: N
- Include in monthly note as supplementary row:
  `"Scale (Hume BIA, estimated): [start] lbs → [end] lbs ([direction] [delta] lbs, [N] readings)"`

**If fewer than 4 readings:**
- Note: `"Insufficient Hume BIA readings this month for trend (N readings)"`

**Backfill new readings:** Before writing the monthly note, check `data/health/metrics-log.json` for any Hume readings from this month that aren't yet logged. Append `body_comp_bia` entries for any missing dates.

#### Store in Working Memory

\```
body_comp_monthly:
  dexa_date: YYYY-MM-DD
  weight: N lbs (goal: 210)
  body_fat: N% (goal: 17%)
  bmi: N (goal: <20)
  weight_trend: "up" | "stable" | "down"
  body_fat_trend: "up" | "stable" | "down"
  progress_assessment: "on track" | "at risk" | "off track"
  lbs_from_goal: N
  bf_from_goal: N%
  bia_monthly_summary: "228.4 → 225.1 lbs (down 3.3 lbs, 8 readings)" | "insufficient readings (2)"
\```
```

---

## Phase 4: Historical Backfill (First Run Only)

On the first execution of any Galen skill that calls HealthQuery, run a 365-day query to capture all historical Hume readings:

```bash
tools/health-query/.build/release/HealthQuery 365 2>/dev/null | \
  jq '[.records[] | select(.source | test("Hume"; "i"))]'
```

For each date that has at least a `bodyMass` reading, check `data/health/metrics-log.json` for an existing `body_comp_bia` entry with that date. If none exists, append one. Group readings by date — one entry per scan session (readings within 5 minutes of each other are from the same scan).

This is a one-time operation. After the initial backfill, Galen only appends new readings in Step 6b of galen-morning-snapshot.

---

## Phase 5: Optional — `galen-body-comp-trend` On-Demand Skill

A lightweight skill for "how's my weight trending?" queries:

1. Run HealthQuery for 365 days, filter to Hume readings
2. Read all `dexa` entries from `metrics-log.json`
3. Produce a markdown table: DEXA ground-truth anchors + BIA readings between them
4. Compute rate of change (lbs/week) from BIA readings since last DEXA
5. Project time to goal weight (210 lbs) at current BIA trend rate — clearly labeled as a projection from estimated data
6. Not a morning skill — on-demand only via "how's my weight trending" or "body comp trend"

Build this after Phases 1-4 are verified working.

---

## Implementation Checklist

### Phase 1: Infrastructure
- [ ] Verify Hume → Apple Health sync is active (Profile > Connected Apps in Hume app)
- [ ] Create `tools/health-query/` directory structure
- [ ] Write `Package.swift`, `main.swift`, `HealthQuery.entitlements`, `build.sh`
- [ ] Update `TEAM_ID` in `build.sh`
- [ ] Run `bash build.sh`
- [ ] Run first time to approve HealthKit permission
- [ ] Confirm JSON output contains Hume readings
- [ ] Note exact Hume source string from output

### Phase 2: Schema
- [ ] Add `body_comp_bia` entry type to `data/health/schema.md`

### Phase 3: Skill Updates
- [ ] Add Step 6b to `skills/galen-morning-snapshot/SKILL.md`
- [ ] Update Step 5 in `skills/galen-visit-prep/SKILL.md`
- [ ] Update Step 03 in `workflows/galen-monthly-health-review/workflow.md`

### Phase 4: Backfill
- [ ] Run 365-day HealthQuery and backfill all historical Hume entries to `metrics-log.json`

### Phase 5: Optional
- [ ] Create `skills/galen-body-comp-trend/SKILL.md`

---

## Environment Constraint (2026-06-21)

**Current Status:** The macOS Health app is not available on this Mac (not in App Store, region-restricted). The HealthQuery tool requires either:
- The macOS Health app to be installed (provides local HealthKit access), OR  
- HealthKit to be available through the framework

**CloudKit fallback (attempted):** Access to Health data via CloudKit requires the app to have Apple-provided entitlements that are only available to the official Health app. Third-party apps cannot directly access iCloud Health containers due to privacy restrictions.

**Workaround:** Health data is synced to iCloud (55.7 MB). To make it accessible locally:
1. Install the Health app on a different Mac that has it available, or
2. Export health data from iPhone as XML/CSV and process locally, or  
3. Wait for the Health app to become available in this region/account

## Open Questions

| Question | Status |
|----------|--------|
| Is Hume sync currently active to Apple Health? | Verified — syncing to iCloud (55.7 MB detected) |
| Does the Health app work on this Mac? | No — not available in App Store for this region |
| Can CloudKit provide fallback access to Health data? | No — requires Health app entitlements (Apple-only) |
| What is the exact source name Hume uses in HealthKit? | Pending (requires functional HealthKit access) |
| How many historical Hume readings are in Apple Health? | Pending (requires functional HealthKit access) |
| Does the HealthQuery binary need to be rebuilt after OS upgrades? | Likely not — but re-codesign may be needed after major Xcode updates |

---

## What This Does Not Solve

- Visceral fat, segmental muscle mass, water %, A/G ratio — these do not have HealthKit equivalents. DEXA remains the only source for these metrics. No workaround.
- If the Hume app is not open during a scan, the reading will not save. Gaps are expected.
- BIA accuracy degrades with hydration, meals, and time of day. Galen notes high variance but cannot enforce consistent conditions.

---

## Sources

- [Vitalink — GitHub (RyanLisse)](https://github.com/RyanLisse/Vitalink) — evaluated, eliminated (requires Apple Watch)
- [Open Wearables — openwearables.io](https://openwearables.io/) — evaluated, eliminated (Docker + iOS companion + beta MCP)
- [Hume Health App — App Store](https://apps.apple.com/us/app/hume-health/id1477782599)
- [Apple HealthKit Data Types — Apple Developer Docs](https://developer.apple.com/documentation/healthkit/healthkit-data-types)
- [Configuring HealthKit Access — Apple Developer Docs](https://developer.apple.com/documentation/xcode/configuring-healthkit-access)
- [HealthKit Entitlement — Apple Developer Docs](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.healthkit)

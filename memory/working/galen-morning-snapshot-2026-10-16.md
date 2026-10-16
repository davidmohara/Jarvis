---
type: working
task_id: "galen-morning-snapshot"
agent-source: galen
created: 2026-10-16T13:12:24Z
status: active
context: "Galen morning health snapshot — 2026-10-16. Consumed by Chief's morning briefing (skill step-07)."
---

# Galen — Morning Health Snapshot — 2026-10-16

## Brief for Chief (1-2 line summary)

**Recovery: 35 (RED) — HRV 22.5 ms (low), resting HR 84 bpm (elevated), sleep efficiency 83.5% (below the 85% threshold).** 7-day recovery trend **UNAVAILABLE** — WHOOP MCP in this build exposes only today's recovery (no collection endpoint). Recommend deferring hard training today and protecting sleep tonight. Note: Dr Ryan Jones appointment 08:45 (personal calendar).

---

## WHOOP Data Structure

```
whoop_data:
  today_recovery: 35
  last_7_days: UNAVAILABLE (recovery-collection tool not exposed in this MCP build; direct API blocked by credential policy)
  trend: unknown (cannot compute — no 7-day recovery series)
  hrv_7day_avg: UNAVAILABLE (today rmssd: 22.54 ms)
  rhr_7day_avg: UNAVAILABLE (today: 84 bpm)
  last_night_sleep:
    duration_minutes: 458 (7h38m asleep; 550 min / 9h10m in bed)
    efficiency: 83.5%
    stages_captured: true
  red_count_7days: UNAVAILABLE
  yellow_count_7days: UNAVAILABLE
```

## Today's Recovery (live pull, 2026-10-16T11:13Z)

| Metric | Value | Read |
|--------|-------|------|
| Recovery score | **35** | **RED (<40)** — compromised |
| HRV (rmssd) | 22.54 ms | Low |
| Resting HR | 84 bpm | Elevated (matches today's cycle avg HR of 84) |
| SpO2 | 96.65% | Normal |
| Skin temp | 34.20 °C | — |

## Last Night's Sleep (2026-10-15 21:01 → 2026-10-16 06:11 CDT)

| Metric | Value | Flag |
|--------|-------|------|
| Time in bed | 9h10m (550 min) | Generous window |
| Asleep | 7h38m (458 min) | Light 4.9h / SWS 1.32h (79 min) / REM 1.42h (85 min) |
| Awake | 1h32m (92 min) | High — fragmenting the night |
| Efficiency | **83.5%** | **BELOW 85% threshold — FLAG** |
| Consistency | 75 | Moderate |

## 7-Day Context (cycles only — recovery series unavailable)

| Date | Strain | Avg HR | Max HR | Note |
|------|--------|--------|--------|------|
| Oct 16 | 4.16 | 84 | 129 | Today (partial cycle); avg HR = elevated RHR |
| Oct 15 | 4.52 | 75 | 133 | — |
| Oct 14 | 3.27 | 70 | 117 | — |
| Oct 13 | 0.55 | 75 | 114 | Near-zero load |
| Oct 12 | 13.15 | 78 | 159 | Hard workout (sport_id 259) |
| Oct 11 | 1.02 | 77 | 113 | — |
| Oct 10 | 13.43 | 89 | 169 | Hard workout (sport_id 259) |

Two hard sessions early in the window (Oct 10, Oct 12 — both ~13 strain, max HR 169/159), followed by a low-strain taper, yet recovery is red today with an elevated resting HR. Pattern is consistent with accumulated strain and/or an acute non-training stressor (travel, disrupted sleep) rather than a simple training-load spike.

## Flags (skill Step 4)

1. **RED recovery (35, <40)** — present. Recommend deferring hard training today.
2. **Sleep efficiency 83.5% (below 85%)** — present. 1h32m awake time; investigate cause (travel, schedule, alcohol, stress).
3. **HRV trend** — CANNOT ASSESS. 7-day HRV series not retrievable from this MCP build. Today's 22.5 ms is low in isolation.
4. **Resting HR trend (up 3+ bpm)** — CANNOT ASSESS. 7-day RHR series not retrievable. Today's 84 bpm is elevated in isolation and equals today's cycle average HR.
5. **3+ consecutive red days** — UNKNOWN. Requires the recovery collection, which is unavailable. Not fabricating a count.
6. **Red after known stressor** — plausible: bootcamp week + travel/hotel stay (HOU, through Oct 16) and a HOU→DAL travel flag carried from Oct 15.

## Peptide / Protocol Cycle Reminders (skill Step 5)

**Data integrity flag — protocol sources disagree and are stale:**

- The skill-referenced `memory/personal/health-protocols.md` (last updated **2026-05-24**) lists: **BPC-157 30 IU daily** and **Retatrutide (Reta) 40 IU weekly**, both Active. This file does **not** reflect the June 2026 GH-stack start.
- The authoritative data files (`data/health/tracking.json` `current_phase` + `peptide_cycles`, and `data/health/metrics-log.json` protocol_change entries, last updated **2026-06-25/28**) show a different stack:
  - **Retatrutide (Reta) 3 mg weekly** — active (dose reduced 5 mg→3 mg on 2026-06-15).
  - **MOTS-C 5 mg every 5 days** — cycle 2026-06-28 → 2026-08-23 (scheduled end **passed**).
  - **Tesamorelin 1 mg, 5 nights/week** — cycle 2026-06-28 → 2026-08-30 (scheduled end **passed**).
  - **Ipamorelin 300 mcg, 5 nights/week** — same window (scheduled end **passed**).
  - **Semax 400 mcg AM** — planned 2026-07-12 → 2026-08-16 (scheduled end **passed**).

**Flag:** The GH-stack cycles were scheduled to end Aug 23–30, 2026 (≈7 weeks ago) and are now presumably in a rest window, but **no protocol update has been logged since 2026-06-28**. Current active status as of 2026-10-16 is **unconfirmed**. `health-protocols.md` contradicts the data files. Recommend a `galen-protocols` reconciliation before treating any cycle as active. Given the red recovery + low HRV, if Reta is active, note the skill's guidance to watch for energy/appetite suppression concurrent with declining recovery.

## Physician Visit Note

**Dr Ryan Jones — today 08:45 (personal calendar).** The skill's output format has no dedicated visit section (that is `galen-visit-prep`, scoped to Dr. Randol), so surfacing the objective status here:

- Recovery red (35), HRV 22.5 ms, resting HR 84 bpm, sleep efficiency 83.5% with 1h32m awake — worth mentioning if the visit touches sleep, cardiovascular, or fatigue.
- Carry-forward bloodwork flags from the June 2026 draw remain open items if relevant: homocysteine 19.5 µmol/L (high), hs-CRP 2.2 mg/L (trending up), platelets 114 (low), AST 42 (high), MCV/MCH macrocytosis worsening (107.6/35.4), LDL Pattern B. (Source: `memory/working/2026-10-10-relocated-galen-protocols-state.md`.)
- Protocol reconciliation flag above is a question worth raising.

## Data Sources Used

- `mcp__whoop__get_recovery` — live, today (2026-10-16). ✓
- `mcp__whoop__get_sleep` — live, last night. ✓
- `mcp__whoop__get_cycles` — live, 7 cycles. ✓
- `mcp__whoop__get_workouts` — live, 7 workouts. ✓
- `mcp__whoop__get_body_measurement` — live (height 1.905 m, weight 97.55 kg, max HR 188). ✓
- `memory/personal/health-protocols.md` — read (STALE, 2026-05-24).
- `data/health/tracking.json`, `data/health/metrics-log.json` — read (authoritative, last 2026-06-25/28).
- `memory/working/2026-10-10-relocated-galen-protocols-state.md` — read.

## Degradations / Unavailable Sources

- **7-day recovery/HRV/RHR series — UNAVAILABLE.** WHOOP MCP in this build exposes only the single most-recent recovery record (`get_recovery` takes no parameters). The skill's `get-recovery-collection` endpoint is not exposed. A direct WHOOP API call was attempted and blocked by credential policy (correctly — the token was not to be materialized). Per Galen's data-integrity principle, no 7-day recovery/HRV/RHR values were estimated or interpolated.
- **Obsidian MCP — UNAVAILABLE** (ECONNREFUSED). `health-protocols.md` was read from the local IES filesystem copy instead.

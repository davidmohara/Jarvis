---
name: galen-morning-snapshot
description: Pull today's WHOOP recovery score, interpret in context of last 7 days, surface health status for Chief's morning briefing. Flags red recovery, notable HRV trends, sleep quality, and active peptide cycle reminders.
evolution: system
model: sonnet
---

<!-- system:start -->
## Trigger Phrases

- "morning snapshot", "how am I recovering", "WHOOP status", "my recovery score"
- Automatically invoked by Chief during morning briefing (boot sequence)
- Proactively triggered if recovery drops below 30 (red) 3+ consecutive days

## Workflow

### Step 1: Pull WHOOP Data (Last 7 Days)

Use MCP WHOOP connector (`mcp__whoop__get-recovery-collection`) to fetch:
- Recovery scores for last 7 days
- HRV (rmssd) daily trend
- Resting heart rate daily trend
- Sleep duration and efficiency for last night
- Today's target status (if available)

Store as working memory structure:
```
whoop_data:
  today_recovery: N (0-100)
  last_7_days: [N, N, N, N, N, N, N] (most recent first)
  trend: "improving" | "declining" | "flat"
  hrv_7day_avg: N (rmssd)
  rhr_7day_avg: N
  last_night_sleep:
    duration_minutes: N
    efficiency: N%
    stages_captured: true/false
  red_count_7days: N (how many days < 30)
  yellow_count_7days: N (how many days 30-69)
```

### Step 2: Interpret Recovery Status

Classify today's score:
- **Green (70+):** Fully recovered, ready for hard effort. Note if HRV is elevated (strong vagal tone).
- **Yellow (40-69):** Moderate recovery. Watch for trends. If 2+ consecutive yellows, flag loading pattern.
- **Red (<40):** Compromised recovery. Accumulated strain, sleep debt, or acute stressor. Recommend action.

### Step 3: Assess Trend

Compare today's score to 7-day average:
- If improving: brief acknowledgment ("Recovery climbing back — good trajectory")
- If declining: flag ("Down 3 days straight — loading pattern or sleep debt?")
- If flat: note if baseline is yellow/red ("Stuck in yellow zone — watch for overtraining")

### Step 4: Flag Notable Patterns

Check for:
- **3+ consecutive red days** → Immediate attention, load reduction recommended
- **HRV trending down** → Could indicate subclinical infection, overtraining, or accumulated stress
- **Resting HR trending up 3+ bpm** → Another indicator of accumulated strain
- **Sleep efficiency below 85%** → Could be driving low recovery, investigate cause (schedule, alcohol, stress)
- **Red after a known stressor** → Validate expected stress response (e.g., after hard workout or late night)

### Step 5: Surface Peptide Cycle Reminders

If a peptide protocol is active:
- **CJC-1295 w/DAC (1mg/wk):** note if this is an injection day (helps frame recovery expectation)
- **Ipamorelin (1400ug/wk):** note if this is a pulse day
- **BPC-157 (as needed):** remind if recent injury/recovery protocol active
- **Epithalon, DSIP, MOTS-C cycles:** note if in active cycle (these affect recovery markers)

Reminder format: "Active: CJC-1295 cycle (week 4 of 8)" or "BPC-157 protocol ongoing"

### Step 6: Generate Brief Output for Chief

**Format for Chief consumption (single line to 2-line summary):**

**GREEN (70+):**
```
"Recovery: 75 (green) — HRV strong, slept 7h30. Ready for intensity."
```

**YELLOW (40-69) — stable or improving:**
```
"Recovery: 52 (yellow) — climbing from 48 yesterday, sleep improving. Trend positive."
```

**YELLOW (40-69) — declining or stuck:**
```
"Recovery: 42 (yellow, 3rd day in yellow zone) — HRV dipping, resting HR up 3bpm. Watch loading."
```

**RED (<40):**
```
"Recovery: 28 (red) — accumulated strain. HRV down 12%, sleep only 6h20. Recommend deferring hard workout today, protect afternoon energy."
```

**With Cycle Reminder:**
```
"Recovery: 48 (yellow) — improving trend. Active: Ipamorelin week 2. Expect minor sleep disruption this week."
```

### Step 7: Route to Chief

Pass structured brief to Chief's morning briefing input. Chief decides whether to:
- Weave into paragraph 1 if status is normal or improving
- Flag in paragraph 3 (sharp edge) if red or declining trend
- Surface only if recovery is green (quick win to build momentum)

---

## Success Metrics

- All 7 days of WHOOP data captured and analyzed
- Today's recovery score correctly classified (red/yellow/green)
- Trend direction identified (improving/declining/flat)
- Any 3+ day red pattern flagged with explicit recommendation
- Chief receives usable 1-2 line summary
- Peptide cycle status included if active

## Error Handling

| Scenario | Response |
|----------|----------|
| WHOOP data unavailable or OAuth expired | Report "WHOOP data unavailable" to Chief; proceed without recovery data |
| Recovery data exists but < 7 days | Analyze available data; note "partial week" in trend assessment |
| No peptide cycle currently active | Omit cycle reminder entirely; keep output clean |
| Last night sleep data missing | Use resting HR and HRV as proxy; note "sleep data incomplete" |

---

## Integration Notes

- This skill is called **automatically during Chief's morning briefing boot sequence**
- Output is NOT a standalone deliverable — it's consumed by Chief's step-04 synthesis
- If red recovery detected, Chief may choose to escalate load/schedule adjustments through Master
- Repeated red flags (3+ in a week) should trigger Galen's Recovery Coaching task on demand

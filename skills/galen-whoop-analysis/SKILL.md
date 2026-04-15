---
name: galen-whoop-analysis
description: Deep WHOOP analysis over 30 days. Pulls recovery, sleep, and workout data. Identifies patterns (trend, sleep quality drivers, load correlation, HRV drift). Outputs narrative + data table + actionable recommendations.
evolution: system
model: sonnet
---

<!-- system:start -->
## Trigger Phrases

- "WHOOP analysis", "pull my WHOOP", "analyze my recovery", "what's my WHOOP trend"
- "30-day review", "WHOOP deep dive", "how's my recovery trending"
- Triggered by Galen on demand via Master routing

## Workflow

### Step 1: Pull 30 Days of WHOOP Data

Use MCP WHOOP connector to fetch:
- **Recovery scores** (daily, 30 days) via `whoop-get-recovery-collection` with date range
- **Sleep data** (duration, stages, efficiency, quality) via `whoop-get-sleep-collection` with date range
- **Workout data** (strain, type, duration, intensity) via `whoop-get-workout-collection` with date range
- **User body measurements** via `whoop-get-user-body-measurements` (for baseline HR context)

Store in working memory with full 30-day history.

### Step 2: Compute Recovery Trend

Calculate:
- **Recovery trend direction:** Calculate 7-day moving average for days 1-7 vs. days 23-30. Compare: improving, declining, or flat (< 2% change).
- **Recovery volatility:** Standard deviation across 30 days. High volatility (>10) suggests external stressors or training variation.
- **Red/Yellow/Green distribution:** Count occurrences in each range.
- **Streak analysis:** Longest red streak, longest yellow streak, longest green streak.
- **Baseline:** Average recovery across full 30 days.

Output:
```
recovery_trend:
  baseline_avg: N
  direction: "improving" | "declining" | "flat"
  volatility_stddev: N
  red_days: N
  yellow_days: N
  green_days: N
  longest_red_streak: N
  longest_decline_period: [start_date, end_date, days_count]
```

### Step 3: Analyze Sleep Quality Drivers

For each sleep night, capture:
- **Duration** (minutes)
- **Efficiency** (% of time asleep vs. in bed)
- **REM percentage**
- **Slow-wave sleep percentage**
- **Fragmentation** (number of awakenings, if captured)

Identify patterns:
- **Duration trend:** Increasing, decreasing, or variable? Target is 7-9 hours.
- **Efficiency drivers:** If efficiency is low, look for: late-night intake (alcohol, caffeine, large meals), workout timing, stress spikes.
- **REM insufficiency:** REM < 20-25% could indicate incomplete sleep architecture.
- **Deep sleep trend:** Deep sleep correlates with recovery; if low, may drive low recovery scores.

Hypothesis-test against known sleep disruptors:
- **Did workouts late in day?** (Workouts within 4 hours of bed often reduce sleep efficiency)
- **Alcohol flagged?** (Explicit sleep disruption marker if available)
- **High strain day?** (High workout strain correlates with deeper sleep but may disrupt initial sleep)

Output:
```
sleep_analysis:
  avg_duration: N minutes
  duration_trend: "increasing" | "decreasing" | "stable"
  avg_efficiency: N%
  efficiency_drivers:
    - "late night alcohol on days 3, 7, 12 correlates with efficiency drops"
    - "workouts after 6pm precede lower sleep efficiency next night"
    - "stress spikes (evidenced by high HRV variability) precede short sleep"
  sleep_architecture:
    avg_rem_percent: N%
    avg_deep_percent: N%
    concern: "REM is low" | "Deep sleep is low" | "normal"

  recommendations:
    - "Shift workout window to before 5pm when possible"
    - "No alcohol on work nights — efficiency drops 8-12% next night"
    - "Prioritize 7.5-8.5 hour target; currently averaging X hours"
```

### Step 4: Correlate Workout Load vs. Recovery

For each day, link:
- **Workout strain** (0-21 scale, if workout was logged)
- **Recovery score next day** (how did body respond?)
- **Sleep quality that night** (did hard effort improve sleep or degrade it?)

Identify correlations:
- **High strain → good recovery next day?** → Training stress is being tolerated well
- **High strain → low recovery next day?** → Underrecovered or accumulated fatigue
- **No workouts for 2+ days → recovery climbing?** → Body needs deload days
- **Hard efforts 3+ days in a row → recovery declining?** → Insufficient recovery between sessions

Output:
```
load_vs_recovery:
  hard_workout_days: N
  easy_workout_days: N
  rest_days: N
  correlation_pattern:
    - "High strain (>15) followed by <24h recovery window: 5 instances, avg next-day recovery dropped 10%"
    - "Back-to-back hard days (5 instances): recovery declined on 2nd hard day, avg -8%"
    - "Rest days (3 instances): recovery rebounded avg +12% next day"
  recommendation: "Add 1 intentional rest day per week; recovery suggests undertraining, not overtraining"
```

### Step 5: Assess HRV Trend

HRV (heart rate variability, captured as rmssd in WHOOP) correlates with parasympathetic tone and recovery:

- **HRV baseline:** Average across 30 days
- **HRV trend:** Is it climbing (improving cardiac autonomic fitness) or declining (accumulated fatigue)?
- **HRV volatility:** High day-to-day variation suggests response to stressors (stress, poor sleep, acute illness)
- **HRV correlation to recovery score:** Should be positively correlated (higher HRV = higher recovery)

If HRV is declining while workouts are constant → suggests external stressor (work stress, sleep debt, illness).

Output:
```
hrv_analysis:
  baseline_rmssd: N ms
  trend: "improving" | "declining" | "flat"
  volatility: "high" | "moderate" | "stable"
  concern: "HRV dropping despite stable workouts — suggests non-exercise stressor"
  recommendation: "Monitor for illness symptoms; prioritize sleep this week; consider deload"
```

### Step 6: Synthesize Narrative Summary

Write 2-3 paragraph narrative that connects the dots:

**Paragraph 1: Macro Recovery Trend**
- Recovery direction (improving/declining/flat), baseline average, distribution of red/yellow/green
- Longest streak if relevant
- One-sentence interpretation: "You're in a solid recovery window" vs. "Accumulated fatigue is building"

**Paragraph 2: Sleep Quality Context**
- Average duration and efficiency
- Key driver (late workouts, alcohol, schedule, stress)
- Relationship to recovery: "Sleep efficiency has improved 6% week-over-week, correlating with rising recovery scores" or "Sleep is the limiting factor — averaging 6h45, which is driving low recovery"

**Paragraph 3: Training Load Relationship**
- Workout frequency and distribution
- Correlation between load and recovery
- Deload pattern assessment: "You need structured deload days, or you're leaving recovery on the table"

**Paragraph 4: HRV & Autonomic Health (if notable)**
- HRV trend and what it means
- Any divergence from recovery score (suggests external stressor if declining HRV with stable recovery)

### Step 7: Generate Data Table

Output a markdown table for reference (30-day summary):

| Date | Recovery | Sleep (h:m) | Efficiency | Workout Strain | HRV (rmssd) | Notes |
|------|----------|-------------|------------|----------------|-------------|-------|
| [oldest] | 45 | 7:15 | 82% | 12 (moderate) | 58 | Evening meeting |
| ... | ... | ... | ... | ... | ... | ... |
| [today] | 62 | 7:45 | 88% | 0 (rest) | 68 | Good recovery |

### Step 8: Propose Actionable Recommendations

2-3 specific, testable changes:

**Examples:**
1. "Shift workouts before 5pm — your 6+ pm workouts reduce sleep efficiency by 8-12%. One week test: track sleep efficiency before/after."
2. "Add one intentional rest day per week (currently zero). Recovery scores suggest you're not undertraining; you need active recovery days to consolidate adaptations."
3. "No alcohol on work nights. You're seeing consistent 10-15% efficiency drops night-after. Two-week test: weekends only, track sleep efficiency gain."
4. "Increase sleep duration target from 7h15 to 7h45. You're 90 minutes short of optimal for your training load. Test for 3 weeks, track recovery response."

Each recommendation should include:
- What to change
- Why (data-backed)
- How to measure success (what metric improves?)
- Timeline for test (1-2 weeks)

---

## Output Format

**Markdown file, suitable for Obsidian or standalone review:**

```markdown
# WHOOP 30-Day Analysis — [Date Range]

## Recovery Snapshot
[Paragraph 1 summary]

## Sleep Quality Assessment
[Paragraph 2 summary + drivers]

## Training Load Correlation
[Paragraph 3 summary + pattern]

## Autonomic Health (HRV)
[Paragraph 4 if notable, else omit]

## Data Table
[30-day table]

## Recommendations
1. [Specific change + data backing + success metric + timeline]
2. [...]
3. [...]

---

**Analysis Date:** [timestamp]
**Data Source:** WHOOP API (30-day historical)
**Next Review Trigger:** [Suggested 30-day follow-up date]
```

---

## Success Metrics

- All 30 days of data captured (recovery, sleep, workout, HRV)
- Recovery trend correctly identified (improving/declining/flat)
- Sleep quality drivers identified with specific examples
- Workout load correlation analyzed (high strain → recovery response mapped)
- HRV trend assessed and contextualized
- Narrative synthesis connects recovery, sleep, load, and HRV
- 2-3 actionable recommendations with success metrics included
- Data table formatted for easy scanning
- Output is suitable for sharing with health coach or physician

## Error Handling

| Scenario | Response |
|----------|----------|
| Incomplete 30-day history | Proceed with available data; note "23 days captured" in header |
| Missing sleep data on some nights | Use available nights; note "sleep data incomplete for N nights" |
| No workouts logged | Analyze recovery and sleep without load correlation; focus on rest/recovery pattern |
| WHOOP API unavailable | Report "WHOOP data unavailable — cannot generate analysis" and exit |

---

## Integration Notes

- This skill produces a standalone deliverable suitable for Obsidian vault storage or email sharing
- Galen surfaces recommendation #1 to Chief if it suggests immediate action (e.g., "defer hard workout today")
- If analysis uncovers health concern (e.g., persistent insomnia, HRV crash), Galen escalates to Recovery Coaching task
- Monthly health review (galen-monthly-health-review) will consume this analysis as input

---
name: galen-monthly-health-review
description: Monthly health review. Pull 30-day WHOOP, latest bloodwork, DEXA data. Run trend analysis vs. Lifebook goals. Output Obsidian note with monthly summary, progress, and gaps.
agent: galen
model: sonnet
---

<!-- system:start -->
# Monthly Health Review Workflow

**Goal:** Comprehensive monthly health snapshot across all data sources. Track progress vs. longevity goals (bio age -8 years, healthspan +20 years). Identify trends, protocol adjustments needed, and success metrics.

**Agent:** Galen — Longevity Advisor

**Trigger:**
- On demand: "monthly health review", "health review", "monthly check-in"
- Scheduled: Last day of each month (auto-triggered)
- Manual: Whenever David wants a full health assessment

**Architecture:** Sequential workflow pulling from 4 data sources, synthesizing into monthly health note for Obsidian.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| WHOOP | 30 days of recovery, sleep, workout, HRV data | WHOOP MCP (`whoop-get-recovery-collection`, `whoop-get-sleep-collection`, `whoop-get-workout-collection`) |
| Bloodwork | Latest Function Health results (if available this month) | Obsidian vault (`Mind/Health/Visit - [Date].md`) |
| DEXA | Body composition (latest scan) | Dropbox Excel (`~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`) |
| Lifebook | Health goals (bio age target, healthspan target, body comp goals) | Obsidian Lifebook (`Projects/Lifebook - Health.md`) |
| Active Protocols | Current supplement stack, peptide cycles | Obsidian + `projects/Peptides.md` |
| Calendar | Training load (any major deloads, travel, stress events) | Calendar context + WHOOP workout data |

### Paths

- `lifebook_health` = `Projects/Lifebook - Health.md`
- `dropbox_health_tracking` = `~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`
- `obsidian_health_folder` = `Mind/Health/`
- `monthly_output` = `Mind/Health/Monthly Review - [Month Year].md`

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read and follow in sequence:

1. **Step 01:** Pull WHOOP 30-day data (via galen-whoop-analysis skill — use the same 30-day snapshot)
2. **Step 02:** Pull bloodwork (via galen-bloodwork skill if new results exist, otherwise use prior month's)
3. **Step 03:** Pull DEXA and body composition data from Dropbox Excel
4. **Step 04:** Load Lifebook health goals and compute progress vs. targets
5. **Step 05:** Synthesize monthly health note for Obsidian

---

## STEP 01: Pull WHOOP 30-Day Data

**Reference:** Use `skills/galen-whoop-analysis/SKILL.md` workflow

**Summary Output Needed:**
- Recovery trend (improving/declining/flat)
- Average recovery score for the month
- HRV trend, resting HR trend
- Sleep quality (average duration, efficiency, quality)
- Workout load distribution (easy/moderate/hard)
- Red/yellow/green day count
- Key patterns identified

**Store in working memory:**
```
whoop_monthly:
  month: "March 2026"
  recovery_avg: N
  recovery_trend: "improving" | "declining" | "flat"
  hrv_trend: "improving" | "declining" | "flat"
  rhr_trend: "improving" | "declining" | "flat"
  sleep_avg_duration: Xh Ym
  sleep_efficiency_avg: N%
  red_days: N (count)
  yellow_days: N (count)
  green_days: N (count)
  workouts_easy: N
  workouts_moderate: N
  workouts_hard: N
  key_patterns: [list]
```

---

## STEP 02: Pull Bloodwork (If Available)

**Reference:** Use `skills/galen-bloodwork/SKILL.md` workflow

**If new bloodwork exists this month:**
- Load latest results from `Mind/Health/Visit - [Date].md`
- Flag all out-of-range markers with severity
- Compare to prior month (if available)
- Identify trends (improving/worsening)

**If no new bloodwork this month:**
- Use most recent prior bloodwork (note date in summary)
- Skip detailed interpretation; focus on tracking status

**Store in working memory:**
```
bloodwork_monthly:
  test_date: YYYY-MM-DD or null
  new_results: true | false
  key_markers_out_of_range: [list]
  notable_trends: [list]
  concerns: [list]
```

---

## STEP 03: Pull DEXA & Body Composition

**Read:** `~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`

**Extract:**
- Latest DEXA scan date
- Weight (current vs. prior month)
- Body fat % (current vs. prior month)
- BMI (current vs. prior month)
- Muscle mass (if captured)
- Trend direction for each metric

**Lifebook Health Goals:**
- Weight: 210 lbs
- Body fat: 17%
- BMI: <20

**Calculate:**
- Pounds from goal weight
- Body fat % from goal
- Progress toward goal (on track / at risk / off track)

**Store in working memory:**
```
body_comp_monthly:
  dexa_date: YYYY-MM-DD
  weight: N lbs (goal: 210)
  body_fat: N% (goal: 17%)
  bmi: N (goal: <20)
  weight_trend: "up" | "stable" | "down" (vs. prior month)
  body_fat_trend: "up" | "stable" | "down" (vs. prior month)
  progress_assessment: "on track" | "at risk" | "off track"
  lbs_from_goal: N
  bf_from_goal: N%
```

---

## STEP 04: Load Lifebook Goals & Assess Progress

**Read:** `Projects/Lifebook - Health.md`

**Health Goals:**
- Bio age: 8+ years younger than chronological age (currently 44, target bio age 36 or younger)
- Healthspan: +20 years (target: live healthy until 95+)
- Body composition: 210 lbs, 17% body fat, BMI <20
- 4 Horsemen risk reduction:
  - Cardiovascular: ApoB <70, LDL-P <1100, Lp(a) <50, HDL >40, hsCRP <2
  - Cancer: Fasting insulin <6, HbA1c <5.7, maintain healthy body comp
  - Neuro: Homocysteine <12, B12 adequate, Vitamin D adequate, cognitive testing (if available)
  - Metabolic: Insulin sensitivity, glucose control, metabolic flexibility

**Calculate Progress:**
For each goal area, assess:
- **On Track:** Metrics moving toward goal, timeline feasible
- **At Risk:** Metrics stalled or trending wrong, may miss goal
- **Off Track:** Metrics significantly away from goal, requires intervention

**Store in working memory:**
```
lifebook_progress:
  bio_age_target: 36 (current: 44, target: 8+ years younger)
  bio_age_assessment: "on track" | "at risk" | "off track"

  healthspan_target: "95+ in health"
  healthspan_assessment: "on track" | "at risk" | "off track"

  body_comp_assessment: [see body_comp_monthly]

  cv_risk_assessment: [summary vs. target markers]
  cancer_risk_assessment: [summary vs. metabolic goals]
  neuro_risk_assessment: [summary vs. cognitive/B12/D3 goals]
  metabolic_assessment: [summary vs. glucose/insulin goals]
```

---

## STEP 05: Synthesize Monthly Health Note

**Format:** Markdown file suitable for Obsidian vault

**Path:** `Mind/Health/Monthly Review - March 2026.md`

**Frontmatter:**
```yaml
---
date: 2026-03-29
month: March 2026
tags: [health, monthly-review, WHOOP, bloodwork, body-comp]
---
```

**Content Structure:**

```markdown
# Monthly Health Review — [Month Year]

**Review Date:** [timestamp]
**Metrics Snapshot:** [1-line overview: good/stable/concerning]

---

## Executive Summary

[2-3 paragraph narrative summarizing overall health status, key trends, and assessment]

**Lifebook Progress:**
- Bio Age: [on track / at risk] — [brief status]
- Healthspan: [on track / at risk] — [brief status]
- Body Composition: [on track / at risk] — [progress vs. goal]
- 4 Horsemen Risk: [summary statement]

---

## WHOOP Recovery Analysis (30-Day)

| Metric | Average | Trend | Assessment |
|--------|---------|-------|------------|
| Recovery Score | [N] | [↑/→/↓] | [good/stable/concerning] |
| HRV (rmssd) | [N] | [↑/→/↓] | [interpretation] |
| Resting HR | [N] | [↑/→/↓] | [interpretation] |
| Sleep Duration | [Xh Ym] | [↑/→/↓] | [vs. 7.5-9h target] |
| Sleep Efficiency | [N]% | [↑/→/↓] | [goal: >85%] |

**Day Distribution:**
- Green (70+): [N] days
- Yellow (40-69): [N] days
- Red (<40): [N] days

**Key Pattern:** [Narrative interpretation of WHOOP trend]

**Sleep Quality Drivers:** [What's helping or hurting sleep?]

**Training Load:** [Easy: N%, Moderate: N%, Hard: N%] — [Periodization assessment]

---

## Bloodwork Status

**[IF New Bloodwork This Month]**

**Test Date:** [date]

**Cardiovascular Risk Profile:**
- ApoB: [value, status]
- LDL-P: [value, status]
- Lp(a): [value, status]
- HDL: [value, status]
- Triglycerides: [value, status]
- hsCRP: [value, status]
- **Assessment:** [on track / at risk] for CV goal

**Metabolic Health:**
- Fasting Insulin: [value, status]
- HbA1c: [value, status]
- Fasting Glucose: [value, status]
- **Assessment:** [on track / at risk] for metabolic goal

**Hormonal & Micronutrient:**
- Total T: [value, status]
- E2: [value, status]
- B12: [value, status]
- Vitamin D3: [value, status]
- **Assessment:** [good / needs adjustment]

**Key Changes from Prior Month:**
- [list any significant changes or trends]

**[IF No New Bloodwork This Month]**

**Latest Bloodwork:** [date] — [summary status]
**Next Retest Scheduled:** [date] (or "pending visit scheduling")
**No new results to report this month.** Monitoring via WHOOP and body composition.

---

## Body Composition (Latest DEXA: [Date])

| Metric | Current | Goal | Variance | Trend |
|--------|---------|------|----------|-------|
| Weight | [lbs] | 210 | [+/-] lbs | [↑/→/↓] |
| Body Fat | [%] | 17% | [+/-]% | [↑/→/↓] |
| BMI | [N] | <20 | [+/-] | [↑/→/↓] |

**Assessment:** [On track / At risk / Off track]

**Progress:** [Lbs lost/gained, body fat change since last month, trajectory toward goal]

---

## 4 Horsemen Risk Assessment

### Cardiovascular Disease
**Status:** [Low / Moderate / Elevated]
- Primary drivers: ApoB, LDL-P
- Key metrics: [summary]
- Risk trajectory: [improving / stable / worsening]
- Action items: [if any]

### Cancer (Metabolic Driver)
**Status:** [Low / Moderate / Elevated]
- Primary drivers: Fasting insulin, glucose control
- Key metrics: [summary]
- Risk trajectory: [improving / stable / worsening]
- Action items: [if any]

### Neurodegenerative Disease
**Status:** [Low / Moderate / Elevated]
- Primary drivers: Homocysteine, B12, Vitamin D
- Key metrics: [summary]
- Risk trajectory: [improving / stable / worsening]
- Action items: [if any]

### Metabolic Dysfunction
**Status:** [Low / Moderate / Elevated]
- Primary drivers: Insulin sensitivity, body composition
- Key metrics: [summary]
- Risk trajectory: [improving / stable / worsening]
- Action items: [if any]

---

## Lifespan & Healthspan Tracking

### Bio Age Estimate (Peter Attia Framework)
**Chronological Age:** 44
**Bio Age Target:** 36 (8+ years younger)
**Estimated Bio Age (based on markers):** [N] (on track / at risk)

**Key Bio Age Drivers:**
- Cardiovascular fitness (VO2 max, ApoB, HTN): [status]
- Metabolic health (fasting glucose, insulin): [status]
- Body composition (muscle, fat): [status]
- Cognitive reserve: [status or N/A if not tracked]

### Healthspan Projection
**Current Health Trajectory:** [Good / Stable / Concerning]
**Projected Healthspan:** [estimated years in health, vs. 95+ goal]
**Gap to Goal:** [assessment]

---

## Protocol Status & Adjustments

**Active Supplements:** [list]
**Active Peptide Cycles:** [list with current status]
**Recent Changes:** [any starts, stops, adjustments this month]

**Recommended Adjustments (Based on This Month's Data):**
1. [if any]
2. [if any]

---

## Summary of Wins This Month

- [positive trend 1]
- [positive trend 2]
- [goal progress]

---

## Focus Areas for Next Month

1. **Priority 1:** [specific, measurable focus based on data]
2. **Priority 2:** [second priority]
3. **Priority 3:** [third priority]

---

## Action Items

### This Month
- [ ] [action]
- [ ] [action]

### Next Month
- [ ] [action]
- [ ] [action]

### Timeline: [Next Retest / Quarterly Review / Physician Visit]
- Bloodwork retest: [date]
- DEXA recheck: [date]
- Physician visit: [date]

---

**Next Monthly Review:** [date, typically 1 month from today]
**Tracking System:** WHOOP (daily), Function Health (quarterly), DEXA (semi-annual), Lifebook (annual)

---

## Data Sources

- WHOOP API: 30-day recovery, sleep, workout history
- Function Health: Latest bloodwork (if available this month)
- Dropbox Health Tracking: DEXA, weight, body composition
- Obsidian Lifebook: Health goals and framework
- Calendar: Training load context, travel, stress events

---

**Review Completed By:** Galen (Longevity Advisor)
**Ready for:** Obsidian vault, quarterly review input, physician context
```

---

## SUCCESS METRICS

- All 4 data sources (WHOOP, bloodwork, DEXA, Lifebook) included
- 30-day WHOOP trends analyzed (recovery, sleep, HRV, load)
- Latest bloodwork (if available) interpreted with out-of-range flagging
- Body composition tracked vs. Lifebook goals
- 4 Horsemen risk assessment completed
- Monthly note is comprehensive, scannable, and exportable to Obsidian
- Action items are specific and prioritized
- Next review date is scheduled

---

## FAILURE MODES & ERROR HANDLING

| Scenario | Recovery |
|----------|----------|
| WHOOP data incomplete | Proceed with available data; note "X days captured" |
| No new bloodwork this month | Use most recent results; note date in summary |
| DEXA scan not available | Use weight + prior body fat estimate; note "DEXA pending" |
| Lifebook goals not accessible | Proceed with standard goals; note "Lifebook context pending" |
| Protocol changes undocumented | Flag "Current protocol status to be confirmed with David" |

---

## INTEGRATION NOTES

- Monthly health review output is saved to Obsidian (`Mind/Health/Monthly Review - [Month].md`)
- If bloodwork shows urgent flags, Galen escalates to Bloodwork Review skill for detailed interpretation
- At end of quarter (March, June, September, December), monthly review feeds into quarterly health rock review with Quinn
- Any significant health concerns (e.g., recovery crashing, new out-of-range markers) escalate to Chief for schedule/stress adjustments
- Scheduled to run on demand or automatically last day of month

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

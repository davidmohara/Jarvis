---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Synthesize Monthly Health Note

## EXECUTION PROTOCOL

**Agent:** Galen, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** `whoop_monthly`, `bloodwork_monthly`, `body_comp_monthly`, and `lifebook_progress` from working memory
**Output:** `Mind/Health/Monthly Review - [Month Year].md`

---

## YOUR TASK

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

## NEXT STEP

Read fully and follow: `step-06-metrics-log.md`
<!-- system:end -->

---
name: galen-visit-prep
owning_agent: galen
description: Pre-visit brief for Dr. Julli Randol. Compile WHOOP trends, bloodwork changes, protocol changes, outstanding questions, new questions, body comp update. Exportable to Obsidian note.
evolution: system
model: sonnet
trigger_keywords: [doctor, visit prep, appointment, medical]
trigger_agents: [galen]
---

<!-- system:start -->
## Trigger Phrases

- "visit prep", "Dr. Randol", "appointment prep", "health visit prep"
- "prep for my doctor appointment", "get ready for Function Health visit"
- Triggered by Galen on demand via Master routing

## Workflow

### Step 1: Confirm Visit Date & History

Read from Obsidian vault:
- **Physician:** Dr. Julli Randol
- **Last Visit Date:** [search vault for most recent visit note, typically August/September annually]
- **Upcoming Visit Date:** [check calendar or David's schedule]
- **Time Remaining:** [days until visit]

If visit is less than 1 week away, this should be high priority. If more than 4 weeks away, mark for "future prep" but still gather data.

### Step 2: Gather WHOOP Data Since Last Visit

Pull 90-day WHOOP data (or from last visit date to today):
- **Recovery score average:** [daily avg since last visit]
- **Recovery score trend:** Improving/declining/flat
- **Longest red streak:** How many consecutive red days?
- **HRV trend:** Baseline then vs. now
- **Resting HR trend:** Baseline then vs. now
- **Sleep quality:** Average duration, efficiency, quality trend
- **Workout data:** Frequency, intensity distribution, any patterns (periodization, deloads)

Output summary:
```
whoop_summary_since_last_visit:
  last_visit_date: YYYY-MM-DD
  recovery_avg: N
  recovery_trend: "improving" | "declining" | "flat"
  hrv_baseline_then: N
  hrv_now: N
  rhr_baseline_then: N
  rhr_now: N
  sleep_avg_duration: Xh Ym
  sleep_efficiency_avg: N%
  red_days_count: N
  workouts_count: N
  workouts_intensity_distribution: "X% easy, Y% moderate, Z% hard"
```

### Step 3: Pull Latest Bloodwork & Identify Changes

Read latest bloodwork file from Obsidian vault (`Mind/Health/Visit - [Date].md`):
- **Test date:** [most recent]
- **Prior test date:** [1-2 tests ago]

For each key marker, calculate:
- **Current value**
- **Prior value** (if available)
- **Change:** (current - prior) / prior × 100%
- **Interpretation:** In range / Watch / Act / Urgent

Focus analysis on:
1. **Out-of-range markers:** Flag with severity
2. **Recently out-of-range markers:** New changes
3. **Markers moving toward goal:** Wins to celebrate
4. **Markers moving away from goal:** Concerns to address

Output summary:
```
bloodwork_changes_since_last_visit:
  last_visit_date: YYYY-MM-DD
  bloodwork_date: YYYY-MM-DD
  markers_of_concern:
    - name: "ApoB"
      prior: 72
      current: 80
      change: "+11%"
      status: "Act"
      question_for_dr: "Is this protocol-driven or dietary?"

  markers_improved:
    - name: "Fasting Glucose"
      prior: 110
      current: 105
      change: "-4.5%"
      status: "Watch → positive trend"

  new_out_of_range:
    - name: "E2"
      current: 45
      status: "High"
      question_for_dr: "Is this DHEA dosing or aromatization?"

  critical_questions:
    - [list]
```

### Step 4: Compile Protocol Changes Since Last Visit

Read `projects/Peptides.md` and Obsidian supplement notes:
- **Supplements started:** Any new additions?
- **Supplements paused:** Any changes?
- **Peptide cycles:** What's active now vs. what was active at last visit?
- **Protocol adjustments:** Any dosage changes?

Output summary:
```
protocol_changes_since_last_visit:
  supplements_started: [] or [list]
  supplements_paused: [] or [list]
  supplements_continued: [list with dosages]

  peptide_cycles:
    active_now: [CJC-1295, Ipamorelin (week 4 of 8)]
    active_at_last_visit: [list]
    paused_since_last_visit: [list]
    upcoming: [Epithalon eligible August, DSIP seasonal]

  changes_to_discuss:
    - [list specific changes that warrant Dr. discussion]
```

### Step 5: Body Composition Update

Pull DEXA data from Dropbox Excel (`~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`):
- **Weight:** Current and trend (up/down/stable)
- **Body fat %:** Current and trend
- **BMI:** Current (goal: <20)
- **Muscle mass:** Current and trend (if DEXA captures)

Compare to Lifebook health goals:
- Goal weight: 210 lbs
- Goal body fat: 17%
- Goal BMI: <20

Output summary:
```
body_comp_update:
  last_dexa_date: YYYY-MM-DD
  weight: [current] lbs (goal: 210 lbs)
  body_fat: [current]% (goal: 17%)
  bmi: [current] (goal: <20)
  trend: "improving" | "stable" | "drifting"
  progress_vs_goal: "on track" | "at risk" | "off track"
```

### Step 6: Compile Outstanding Questions from Last Visit

Read visit notes from last appointment (Obsidian `Mind/Health/Visit - [Last Date].md`):
- What did Dr. Randol recommend?
- What follow-ups were promised?
- What questions are still unresolved?

Examples:
- "ApoB protocol — should we add CoQ10 or berberine?"
- "Hormone panel from August — when should we retest?"
- "Peptide cycle questions — how long should GH cycle run?"

Output:
```
outstanding_questions_from_last_visit:
  - "ApoB management — approved CoQ10 + berberine addition?"
  - "E2 monitoring — should we check before next cycle adjustment?"
  - "Peptide efficacy — any IGF-1 testing recommended?"
  - [list]
```

### Step 7: Generate New Questions Based on Data

Synthesize findings and generate new questions for Dr. Randol:

**URGENT (out-of-range bloodwork findings):**
- "ApoB at 80 (up 11%) — is this protocol-driven? Should we adjust CoQ10/berberine dosing?"
- "E2 at 45 (elevated) — is this DHEA dosing or GH protocol aromatization? How do you recommend managing?"
- "MCH/MCV elevated — should we increase B12 supplementation or consider injections?"

**IMPORTANT (trend concerns):**
- "Recovery trending [direction] since last visit — any training load adjustments you'd recommend?"
- "HRV down [%] since last visit — is this overtraining concern or external stressor?"

**DISCUSSION (protocol optimization):**
- "CJC-1295/Ipamorelin in week 4 of cycle — should we recheck IGF-1 or adjust protocol?"
- "Considering Epithalon cycle in August (4-month pause window opening) — any concerns or recommendations?"
- "Should we test Omega-3 index to verify fish oil adequacy?"

**MONITORING:**
- "Any additional testing you'd recommend (Lp(a), advanced lipid, etc.)?"
- "Sleep metrics improving — any correlation to new supplement additions you'd like to track?"

Output:
```
new_questions_for_dr:
  urgent: [list]
  important: [list]
  discussion: [list]
  monitoring: [list]
```

### Step 8: Synthesize Visit Prep Brief

**Format: Markdown note, exportable to Obsidian**

```markdown
# Pre-Visit Brief: Dr. Julli Randol

**Visit Date:** [date]
**Days Until Visit:** [N]
**Location:** Function Health (Quest Diagnostics)

---

## Quick Summary

[1-2 paragraph overview of health status]

- **Recovery:** [trend]
- **Bloodwork:** [status — any urgent findings?]
- **Protocols:** [changes since last visit]
- **Body Composition:** [progress toward goal]
- **Overall:** [good, stable, concerning?]

---

## WHOOP Summary (Since Last Visit: [Date])

| Metric | Baseline | Current | Trend | Notes |
|--------|----------|---------|-------|-------|
| Recovery Avg | [N] | [N] | [↑/→/↓] | [interpretation] |
| HRV (rmssd) | [N] | [N] | [↑/→/↓] | [interpretation] |
| Resting HR | [N] | [N] | [↑/→/↓] | [interpretation] |
| Sleep Avg | [Xh Ym] | [Xh Ym] | [↑/→/↓] | [interpretation] |
| Sleep Efficiency | [N]% | [N]% | [↑/→/↓] | [interpretation] |
| Red Days (count) | [N] | [N] in last 90 | - | [interpretation] |

**Assessment:** [Narrative interpretation of WHOOP trends]

---

## Bloodwork Update (Test Date: [Date])

### Cardiovascular Risk Profile

| Marker | Prior | Current | Change | Status | Goal |
|--------|-------|---------|--------|--------|------|
| ApoB | 72 | 80 | +11% ↑ | **Act** | <70 |
| LDL-P | [N] | [N] | [%] | [status] | <1100 |
| Lp(a) | [N] | [N] | [%] | [status] | <50 |
| HDL | [N] | [N] | [%] | [status] | >40 |
| Triglycerides | [N] | [N] | [%] | [status] | <100 |
| hsCRP | [N] | [N] | [%] | [status] | <2.0 |

**Key Findings:**
- ApoB elevated (80) — up 11% from August
- Other lipids [stable/changing]
- Inflammatory markers [good/concerning]

### Metabolic Health Profile

| Marker | Prior | Current | Change | Status | Goal |
|--------|-------|---------|--------|--------|------|
| Fasting Insulin | [N] | [N] | [%] | [status] | <6 |
| HbA1c | [N] | [N] | [%] | [status] | <5.7 |
| Fasting Glucose | [N] | [N] | [%] | [status] | <100 |

**Key Findings:**
- [interpretation]

### Hormonal & Micronutrient Profile

| Marker | Prior | Current | Change | Status | Goal |
|--------|-------|---------|--------|--------|------|
| Total T | [N] | [N] | [%] | [status] | 400-600 |
| Free T | [N] | [N] | [%] | [status] | 8-12 |
| E2 | [N] | 45 | +29% ↑ | **Act** | 30-40 |
| B12 | [N] | [N] | [%] | [status] | >400 |
| Folate | [N] | [N] | [%] | [status] | >12 |
| Vitamin D3 | [N] | [N] | [%] | [status] | 40-60 |

**Key Findings:**
- E2 elevated at 45 — up 29% from August (possible DHEA dosing or GH protocol aromatization)
- B12 trend [good/watch]
- Vitamin D [adequate/low]

### Summary

**Urgent Items:** [list]
**Important Items:** [list]
**Positive Trends:** [list]

---

## Protocol Status

### Active Supplements
- Ashwaganda, NAC, PQQ, ALA, Omega-3, AG1, Creatine, Vitamin D/K
- **Total:** [count] daily supplements
- **Compliance:** [good/variable]

### Recommended Additions (Not Yet Started)
- **CoQ10** (500mg daily) — for ApoB management
- **Berberine** (500mg BID) — for metabolic support, currently paused
- **Biotin** (5mg) — for B12 support
- **Quercetin** (500mg) — for CV support

### Active Peptide Cycles
- **CJC-1295 w/DAC** (1mg/week) — Week 4 of 8-week cycle
- **Ipamorelin** (1400ug/week) — Concurrent with CJC
- **BPC-157** (as needed) — injury recovery

### Changes Since Last Visit
- [list any starts, stops, adjustments]

---

## Body Composition

| Metric | Prior | Current | Goal | Status |
|--------|-------|---------|------|--------|
| Weight | [lbs] | [lbs] | 210 lbs | [↑/→/↓] |
| Body Fat | [%] | [%] | 17% | [↑/→/↓] |
| BMI | [N] | [N] | <20 | [↑/→/↓] |

**Assessment:** [On track / at risk / off track]

---

## Outstanding Questions from Last Visit

1. ApoB protocol — approved CoQ10 + berberine?
2. [list]

---

## New Questions for Dr. Randol

### URGENT
1. **ApoB at 80 (up 11% from August)** — Is this protocol-driven or dietary? Should we adjust CoQ10/berberine dosing or try other interventions?
2. **E2 at 45 (elevated)** — Is this from DHEA dosing (started 50mg daily in August) or aromatization from GH protocol? How should we manage?
3. **MCH/MCV elevated** — Indicates possible B12 or folate deficiency. Should we increase B12 supplementation or consider injections?

### IMPORTANT
4. **Recovery/HRV trend [direction]** — Any training load adjustments you'd recommend?
5. **Should we order IGF-1 testing** — We're 4 weeks into GH protocol; would like to assess peptide response?

### DISCUSSION
6. **Epithalon cycle eligible August** (4-month pause closing from December cycle) — Any concerns or recommendations?
7. **Berberine restart** — Should we resume given current metabolic markers?
8. **Omega-3 Index testing** — Should we verify fish oil adequacy with bloodwork?

### MONITORING
9. **Any additional testing recommended** (Lp(a), advanced lipid panel, other markers)?
10. **Timeline for ApoB/E2/metabolic retest** — When should we schedule follow-up bloodwork?

---

## Summary for Visit

**Key Items to Discuss:**
1. ApoB + lipid protocol adjustment
2. E2 management (DIM, dosage, other)
3. B12 supplementation strategy
4. GH protocol efficacy check (IGF-1?)
5. Upcoming Epithalon cycle planning

**Bring to Appointment:**
- This brief (printed or digital)
- Any recent lab results (if ordering new tests)
- Questions list

**Follow-Up Actions:**
- [Dr. will likely recommend protocol adjustments]
- [Retest timeline, typically 8-12 weeks for bloodwork changes]
- [Next visit scheduling]

---

**Brief Prepared:** [timestamp]
**Next Review:** [post-visit summary after appointment]
**Data Sources:** WHOOP API (90-day), Function Health Bloodwork (latest), Obsidian vault, Dropbox health tracking
```

### Step 9: Route to Obsidian

Save visit prep brief to Obsidian:
- **Path:** `Mind/Health/Visit Prep - Dr Randol - [Upcoming Visit Date].md`
- **Frontmatter:**
  ```
  ---
  date: YYYY-MM-DD (prep date)
  visit_date: YYYY-MM-DD (appointment date)
  physician: Dr. Julli Randol
  visit_type: Annual physical / Bloodwork review / Protocol check
  tags: [health, physician-visit, Function-Health]
  ---
  ```

---

## Success Metrics

- Visit date confirmed (or marked as "future prep")
- 90-day WHOOP data pulled and summarized
- Latest bloodwork loaded with changes identified
- Out-of-range markers flagged with severity
- Outstanding questions from last visit captured
- New questions generated from latest data
- Protocol changes since last visit documented
- Body composition update included with progress vs. goals
- Visit prep brief is comprehensive, scannable, and shareable
- Brief can be printed or emailed to Dr. Randol pre-visit

## Error Handling

| Scenario | Response |
|----------|----------|
| Visit date not confirmed | Generate prep brief as "future ready" for when date is confirmed |
| Latest bloodwork not found | Note "Waiting for latest bloodwork" and proceed with WHOOP + protocol data |
| Prior visit notes incomplete | Proceed without prior context; note "Prior visit data incomplete" |
| WHOOP data unavailable | Proceed with bloodwork + protocol; note "WHOOP data not available" |

---

## Integration Notes

- Output visit prep brief is saved to Obsidian and ready for physician review
- Visit prep can be shared with Dr. Randol 3-5 days before appointment
- Post-visit, new visit note is created (`Mind/Health/Visit - [Visit Date].md`) with Dr. Randol recommendations
- Any urgent findings (red bloodwork, critical questions) may escalate to Chief if they suggest immediate action
- Quarterly bloodwork retest is scheduled as follow-up action

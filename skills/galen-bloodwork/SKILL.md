---
name: galen-bloodwork
description: Interpret Function Health bloodwork results. Flag out-of-range markers, assess severity, cross-reference with active protocols, compare to prior results, generate Dr. Randol question list. Produces shareable interpretation brief.
evolution: system
---

<!-- system:start -->
## Trigger Phrases

- "bloodwork", "labs", "interpret my results", "Function Health", "bloodwork review"
- "what do my labs mean", "are my biomarkers good", "latest bloodwork"
- Triggered by Galen on demand via Master routing

## Workflow

### Step 1: Locate & Load Bloodwork File

Read latest bloodwork from Obsidian vault:
- **Path:** `Mind/Health/Visit - [Date].md` (sorted by most recent first)
- Extract all biomarkers with values and reference ranges
- Capture test date and lab (Function Health @ Quest Diagnostics)
- Note ordering physician (Dr. Julli Randol)

If multiple recent tests exist, also load 1-2 prior results for trend comparison.

Store in working memory:
```
bloodwork:
  test_date: YYYY-MM-DD
  lab: "Quest Diagnostics via Function Health"
  physician: "Dr. Julli Randol"
  markers:
    [marker_name]:
      value: N
      unit: "mg/dL" | "ng/dL" | "IU/L" | etc
      reference_range: "X - Y" or "< X" or "> X"
      flag: null | "L" (low) | "H" (high)
      prior_value: N (if available)
      prior_date: YYYY-MM-DD (if available)
```

### Step 2: Assess Each Marker for Out-of-Range Status

For every biomarker, determine:
- **In range?** Yes → proceed
- **Out of range?** Yes → classify severity
  - **Watch:** Close to limit, not urgent, monitor trend (severity: watch)
  - **Act:** Out of range, warrants protocol adjustment or physician discussion (severity: act)
  - **Urgent:** Out of range and correlated with disease risk or requiring immediate intervention (severity: urgent)

Use this severity framework:

| Marker Category | Watch Range | Act Range | Urgent Range |
|-----------------|-------------|-----------|--------------|
| **ApoB** | 60-75 | 75-100 | >100 (significant CV risk) |
| **LDL-P** | 900-1100 | 1100-1400 | >1400 (high CV risk) |
| **Lp(a)** | 30-50 | 50-100 | >100 (significant genetic risk) |
| **Total Cholesterol** | 180-200 | 200-240 | >240 |
| **HDL** | 35-40 | <35 | <30 (CV risk) |
| **LDL** | 100-130 | 130-160 | >160 |
| **Triglycerides** | 100-150 | 150-200 | >200 |
| **Fasting Insulin** | 6-10 | 10-15 | >15 (metabolic syndrome) |
| **HbA1c** | 5.7-6.0 | 6.0-6.5 | >6.5 (diabetes) |
| **Fasting Glucose** | 100-110 | 110-125 | >125 (diabetes) |
| **hsCRP** | 1.0-2.0 | 2.0-5.0 | >5.0 (high inflammation) |
| **Homocysteine** | 10-12 | 12-15 | >15 (CV/neuro risk) |
| **Total T** | 400-500 | 300-400 or >700 | <300 or >800 (protocol concern) |
| **Free T** | 8-10 | 6-8 or >12 | <6 or >14 (hormone imbalance) |
| **E2 (Estradiol)** | 30-45 | 20-30 or >45 | <20 or >60 (hormone imbalance) |
| **LH** | 2-8 | <2 (suppressed) | <0.5 (very suppressed) |
| **FSH** | 2-8 | <2 (suppressed) | <0.5 (very suppressed) |
| **B12** | 400-600 | 300-400 | <300 (deficiency) |
| **Vitamin D3** | 40-60 | 30-40 or >100 | <30 (deficiency) |
| **Ferritin** | 30-200 | 200-300 or <20 | >300 or <15 (iron imbalance) |
| **MCH / MCV** | 26-34 / 80-100 | 24-26 or >34 / <80 or >100 | Severe out-of-range (likely B12/folate concern) |
| **ALP** | 40-129 | 20-40 or >150 | <15 or >180 (significant concern) |
| **ALT / AST** | <40 | 40-80 | >80 (liver concern) |

### Step 3: Cross-Reference with Active Supplement Stack

Check if David's current stack addresses out-of-range markers:

**Current stack:**
- Ashwaganda
- NAC
- PQQ
- ALA
- Omega-3
- AG1
- Creatine
- Vitamin D/K
- (Berberine paused)
- (Resveratrol paused)

**Latest Function Health recommendations (from August 2025 visit):**
- Berberine (reactivate for metabolic support)
- Biotin (B-vitamin support)
- Quercetin (antioxidant, CV support)
- CoQ10 (mitochondrial health, CV support)
- DHEA 50mg PURE (hormone support)

For each out-of-range marker:
- Is there an active supplement addressing it? If yes: note "covered"
- Is there a recommended supplement not yet added? If yes: flag "missing from stack"
- Is there a protocol conflict? (e.g., high E2 on TRT protocol) If yes: flag "protocol conflict"

Output:
```
stack_assessment:
  out_of_range_markers: [list]
  covered_by_stack: [list]
  missing_recommendations: [list]
  potential_conflicts: [list]
  action_items: [list]
```

### Step 4: Compare to Prior Results (Trend Analysis)

If prior bloodwork exists:
- Calculate change in each marker: (current - prior) / prior × 100%
- Identify trends:
  - **Improving:** Marker moving toward normal range
  - **Worsening:** Marker moving away from normal range
  - **Stable:** <5% change
  - **Dramatic shift:** >10% change in either direction

Focus analysis on:
1. **Markers that were already out of range:** Are they improving or worsening?
2. **Markers that newly out of range:** What changed?
3. **Markers that normalized:** What intervention worked?

Output trend line for each marker:
```
trend_analysis:
  ApoB:
    prior_value: 72 (2025-08-12)
    current_value: 80 (2026-03-29)
    change: "+11% (worsening)"
    assessment: "ApoB climbing — suggests lipid protocol needs adjustment or dietary shift"

  E2:
    prior_value: 35 pg/ml (2025-08-12)
    current_value: 45 pg/ml (2026-03-29)
    change: "+29% (worsening)"
    assessment: "E2 elevated — may be DHEA dosing or dietary factors; discuss with Dr. Randol"
```

### Step 5: Cross-Reference with Peptide Protocols

If active peptide cycles (CJC-1295, Ipamorelin, etc.):
- These stimulate growth hormone secretion
- GH elevation can affect blood glucose, insulin sensitivity, and estradiol levels
- Check bloodwork for expected markers:
  - Fasting insulin (may rise on GH protocol)
  - Fasting glucose (may rise on GH protocol)
  - E2 (may rise due to aromatization of increased androgens)
  - IGF-1 (if captured, should be elevated during GH cycle)

Flag if bloodwork suggests:
- Protocol is working (IGF-1 elevated, body comp improving)
- Protocol side effects (insulin sensitivity declining, E2 too high)
- Protocol conflict (two hormonal interventions working against each other)

### Step 6: Assess 4 Horsemen Risk

For each biomarker, map to David's longevity framework:

**Cardiovascular Disease Risk:**
- ApoB (primary), LDL-P, Lp(a), Total C, HDL, LDL, Triglycerides, hsCRP, Homocysteine
- Summary: "CV risk profile is [low/moderate/elevated] — ApoB is the primary driver"

**Cancer Risk (Metabolic):**
- Fasting insulin, HbA1c, fasting glucose, triglycerides, body composition
- Summary: "Metabolic cancer risk is [low/moderate/elevated] — insulin control is [good/needs work]"

**Neurodegenerative Disease Risk:**
- Homocysteine (methylation), B12, folate, Vitamin D3, omega-3 index, inflammation (hsCRP)
- Summary: "Neuro risk profile — homocysteine is [low/moderate/elevated], B12 status is [adequate/low]"

**Metabolic Dysfunction:**
- Fasting insulin, HbA1c, fasting glucose, triglycerides, HDL, body composition, leptin (if available)
- Summary: "Metabolic health — insulin sensitivity is [good/declining], glucose control is [tight/loose]"

### Step 7: Generate Dr. Randol Question List

Create a priority-ordered list of questions for the next physician visit:

**Priority 1 (Urgent/Out-of-Range):**
- "ApoB is 80 (up 11% since August) — is this protocol-driven or dietary? Should we adjust CoQ10 or add berberine?"
- "E2 is 45 (high) — is this DHEA dosing, aromatization from GH protocol, or dietary? What's your recommendation?"

**Priority 2 (Trend Concern):**
- "MCH and MCV are elevated (possible B12/folate deficiency) — should I increase B12 supplementation? Any folate status?"

**Priority 3 (Protocol Optimization):**
- "CJC-1295 and Ipamorelin are now 6+ months into cycle — should we reassess response? Any IGF-1 testing recommended?"
- "Berberine is paused — should I restart given current metabolic markers?"

**Priority 4 (Lifestyle/Context):**
- "Any additional testing recommended (Omega-3 index, Lp(a), advanced lipid panel)?"
- "Sleep patterns have been [good/variable] — any impact you'd expect on metabolic markers?"

### Step 8: Synthesize Interpretation Brief

**Format: Markdown file, shareable with physician**

```markdown
# Bloodwork Interpretation Brief — [Test Date]

## Test Summary
- **Lab:** Quest Diagnostics via Function Health
- **Physician:** Dr. Julli Randol
- **Prior Test:** [Date, comparison available: yes/no]

## Overall Health Snapshot
[1-2 paragraphs summarizing CV risk, metabolic health, neuro health, and hormone status]

### Cardiovascular Risk Profile
**ApoB** (primary): 80 mg/dL (Goal: <70)
- **Status:** Out of range (Act)
- **Trend:** Up 11% since August (worsening)
- **Context:** Primary driver of CV risk. ApoB particle count more predictive than LDL-C.
- **Recommendation:** Discuss CoQ10 dosing increase (target 500-600mg/day) and berberine restart. Retest in 12 weeks.

[Repeat for LDL-P, Lp(a), HDL, hsCRP, Homocysteine, etc.]

### Metabolic Health Profile
**Fasting Insulin** (secondary marker): [Value]
- **Status:** [In range / Watch / Act]
- **Trend:** [Stable / Improving / Worsening]
- **Context:** Correlates with cancer risk and metabolic dysfunction.

[Repeat for HbA1c, fasting glucose, triglycerides]

### Hormonal & Micronutrient Profile
**Total T**: [Value]
**Free T**: [Value]
**E2**: 45 pg/ml (Goal: 30-40)
- **Status:** Out of range (Act)
- **Trend:** Up 29% since August
- **Context:** Elevated — may be DHEA dosing (started 50mg daily in August) or GH protocol aromatization.
- **Recommendation:** Discuss E2 management; consider DIM or calcium d-glucarate; retest in 8 weeks.

**B12 / MCH / MCV**: [Values]
- **Status:** Out of range (Watch)
- **Trend:** New out-of-range
- **Context:** Possible B12 or folate deficiency; MCH/MCV elevation suggests macrocytic concern.
- **Recommendation:** Check folate status; increase B12 supplementation (consider sublingual or injections).

### Supplement Stack Assessment
**Current Stack:** Ashwaganda, NAC, PQQ, ALA, Omega-3, AG1, Creatine, Vitamin D/K
**Recommended Additions (Function Health):** Berberine, Biotin, Quercetin, CoQ10, DHEA 50mg

**Assessment:**
- Berberine (paused) — should restart for metabolic support given insulin trend
- CoQ10 (not yet added) — critical for ApoB reduction; recommend 500-600mg/day
- Biotin (not yet added) — consider for B12/folate support
- Quercetin (not yet added) — antioxidant support, CV protective

**Gap:** Currently no targeted lipid protocol beyond Omega-3. Adding CoQ10 + berberine + increased DHA would strengthen CV defense.

### Peptide Protocol Assessment
**Active:** CJC-1295 w/DAC (1mg/wk), Ipamorelin (1400ug/wk), BPC-157 (as needed)
**Status:** 6+ months into current cycle

**Observations:**
- E2 elevation may be aromatization from GH protocol (expected, manageable)
- Fasting insulin stable despite GH stimulus (good metabolic tolerance)
- No IGF-1 testing captured — recommend testing to assess protocol efficacy

### Priority Action Items
1. **[URGENT]** Add CoQ10 500mg daily + restart Berberine 500mg BID for ApoB management
2. **[URGENT]** Address E2 elevation (discuss DIM or calcium d-glucarate with Dr. Randol)
3. **[IMPORTANT]** Increase B12 supplementation; check folate status
4. **[DISCUSSION]** Peptide cycle assessment — 6+ months in, consider IGF-1 testing
5. **[MONITORING]** Retest ApoB, E2, lipid panel in 12 weeks

---

## Questions for Dr. Randol
1. ApoB up 11% — protocol adjustment or dietary shift?
2. E2 elevated — manage with DIM, or dosage adjustment?
3. B12/MCH/MCV concern — folate status, recommend B12 injections?
4. Should we order IGF-1 to assess GH protocol response?
5. Retest timeline recommendation for ApoB/E2?

---

**Analysis Date:** [timestamp]
**Data Source:** Function Health Bloodwork Portal
**Next Retest:** [Recommended date, typically 8-12 weeks for protocol adjustments]
```

---

## Success Metrics

- All markers from Function Health results captured and assessed for range status
- Each out-of-range marker assigned severity (watch/act/urgent)
- Trend analysis completed (current vs. prior, if available)
- Cross-referenced with active supplement stack and peptide protocols
- 4 Horsemen risk assessed for each category
- Dr. Randol question list generated (priority-ordered)
- Interpretation brief is sharable with physician
- Recommendations are specific, testable, and include retest timeline

## Error Handling

| Scenario | Response |
|----------|----------|
| Latest bloodwork not found in vault | Report "No recent bloodwork found" and suggest Galen: "Schedule visit prep" to access Dr. Randol records |
| Prior bloodwork not available | Proceed with snapshot assessment; omit trend analysis |
| Reference ranges differ from expected | Note "Non-standard reference range" and use Galen's standard ranges for severity assessment |
| Incomplete panel (missing key markers) | Proceed with available data; note "Panel incomplete — missing [marker]" for physician follow-up |

---

## Integration Notes

- Output markdown file suitable for Obsidian vault storage under `Mind/Health/Bloodwork - [Date].md`
- Galen feeds bloodwork summary to Visit Prep skill pre-appointment
- Flagged urgent items escalate to Chief if they suggest immediate protocol changes
- Trend analysis informs quarterly health rock review with Quinn

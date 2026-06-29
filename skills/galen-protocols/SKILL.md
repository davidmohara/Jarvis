---
name: galen-protocols
owning_agent: galen
description: Track active supplement stack and peptide cycles. Monitor cycle timing (Epithalon max 2x/year, 4-month pause), surface protocol status, flag conflicts or gaps based on bloodwork. Output protocol status card.
evolution: system
model: sonnet
trigger_keywords: [protocol, supplement, stack, longevity]
trigger_agents: [galen]
---

<!-- system:start -->
## Trigger Phrases

- "protocols", "supplements", "peptides", "supplement stack", "protocol status"
- "what am I taking", "supplement review", "peptide cycle", "protocol check"
- Triggered by Galen on demand via Master routing

## Workflow

### Step 1: Load Current Supplement & Peptide Data

Read supplement stack and peptide protocols from:
- **Supplements:** Obsidian `Mind/Health/` files + `projects/Peptides.md`
- **Peptide Cycles:** `projects/Peptides.md` (detailed cycling history)

**Current Supplement Stack**

Read `data/health/supplement-stack.json` for current stack state, timing, doses, and status. That file is the authoritative source. Do not maintain a duplicate here. Stack changes are logged as `protocol_change` entries in `data/health/metrics-log.json`.

**Current Peptide Protocols — read from data files (authoritative source):**

- Active cycles, dosing, timing, cycle windows: `data/health/tracking.json` → `peptide_cycles` array
- Cycle constraints (max frequency, pause windows, restart eligibility): `data/health/tracking.json` → `peptide_constraints`
- Current phase and Retatrutide status: `data/health/tracking.json` → `current_phase`

Do not hardcode peptide status in this skill. Always read from `tracking.json` before generating output.

**Full Stack Protocol (MOTS-C + Tesamorelin + Ipamorelin + Semax — ACTIVE as of Jun 29, 2026):**

**Morning (fasted, daily):**
- Semax 200mcg/nostril (400mcg total) intranasal — immediately upon waking
- [On MOTS-C days only] MOTS-C 5mg subQ — same morning window

**Evening (Mon–Fri, 2+ hours post-dinner, 30-60 min before sleep):**
1. Ipamorelin 300mcg subQ — inject first
2. Wait 15–20 minutes (brush teeth, wind down — this is not optional; sequencing amplifies GH pulse)
3. Tesamorelin 1mg subQ — inject second

**30 minutes before sleep (nightly):**
- Magnesium L-Threonate 3 caps (2,000mg complex)
- L-Theanine 200mg
- Apigenin 50mg
- Myo-Inositol 500mg

**Optional AM add on training days (3x/week):**
- Ipamorelin 300mcg subQ (fasted, pre-workout) — creates second GH pulse at peak training stimulus. Uses ~0.75 additional vials/9-week cycle.

**High-demand days only (board meetings, speaking, intensive strategy):**
- Semax 100mcg/nostril (200mcg total) PM — must be ≥5 hours before sleep. Monitor WHOOP sleep onset.

**Reconstitution guide (revised):**
- MOTS-C: 40mg + 4ml BW = 10mg/ml. Draw 0.5ml (50 units) for 5mg dose.
- Tesamorelin: 10mg + 2.5ml BW = 4mg/ml. Draw 0.25ml (25 units) for 1mg dose. Each vial = 10 doses.
- Ipamorelin: 10mg + 3ml BW = 3,333mcg/ml. Draw ~0.09ml (9 units) for 300mcg dose. Each vial = ~33 doses.
- Semax: per supplier instructions; common reconstitution: 2ml BW = 5mg/ml = 500mcg/0.1ml. Draw 0.08ml per nostril for 400mcg total (200mcg/nostril).

**Semax Protocol (standalone, runs concurrent with all other peptides):**
- **Form:** Intranasal spray (10mg vial)
- **Dose:** **200mcg per nostril (400mcg total)** per AM session. Optional PM dose: 100mcg/nostril (200mcg total) on high-demand days only.
- **Frequency:** 5 days on / 2 days off (Mon–Fri)
- **Timing:** AM — immediately upon waking (before food, before other agents). PM dose — ≥5 hours before intended sleep. Do NOT use PM dose if bed is before 10 PM and PM dose would be after 5 PM.
- **Cycle:** **~4.5 week test run (single vial).** Intentional test run to assess response before committing to longer cycling. (Previous: 6 weeks on / 2 weeks off.)
- **Mechanism:** ACTH(4-7)PGP analog. Upregulates BDNF and NGF expression (Dolotov et al., 2006, *Journal of Neurochemistry*); modulates melanocortin receptors (MC4R); enhances dopaminergic and serotonergic signaling in prefrontal cortex. Downstream BDNF effects last 20–24 hours despite short peptide half-life. BDNF mRNA tripling in hippocampus documented at single-dose level in animal models.
- **Evidence level:** Emerging evidence — Russian clinical data (stroke, cognitive dysfunction, ADHD). Limited Western RCT data. Protocol based on established peptide community consensus and Russian pharmacological literature.
- **Dose rationale:** 200mcg/nostril (400mcg total) is the established effective cognitive enhancement range. Prior protocol at 100mcg/nostril (200mcg total) was at the low end of documented efficacy. Upper dose boundary for cognitive use is 600–800mcg/day — 400mcg provides meaningful BDNF stimulus without reaching MC4R over-activation threshold.
- **Stacking considerations:**
  - No known pharmacokinetic conflicts with Retatrutide, MOTS-C, Tesamorelin, or Ipamorelin
  - Cognitive/focus enhancement is additive with GH axis peptides (Tesamorelin/Ipamorelin → IGF-1 → neuroplasticity support)
  - MOTS-C mitochondrial/metabolic effects are mechanistically orthogonal — no interaction
  - Space PM dose ≥4 hours from any sedating supplements (DSIP if active, PM ashwagandha)
- **Contraindications / cautions:** MC4R stimulation is activating — avoid in acute anxiety states. If anxiety increases, reduce to 100mcg/nostril 1x/day AM only or drop to 3x/week. Monitor WHOOP sleep onset on PM-dose days.
- **Inventory note:** 1 vial on hand — intentional test run, no reorder needed before start.
- **Reconstitution:** 2ml BW = 5mg/ml = 500mcg per 0.1ml actuation. Draw 0.08ml per nostril for 400mcg total (200mcg/nostril). Verify concentration with supplier before use.

**Inventory as of June 14, 2026 (at revised doses):**
| Peptide | Vials on Hand | Mg/Vial | Total | Cycle Use (revised) | Remaining After | Notes |
|---------|--------------|---------|-------|---------------------|-----------------|-------|
| MOTS-C | 5 | 40mg | 200mg | ~1.75 vials (8 wks @ 5mg/4d) | ~3.25 vials | Every 4 days = ~8.75mg/wk |
| Tesamorelin | 9 | 10mg | 90mg | **4.5 vials** (9 wks @ 1mg/night × 5) | **4.5 vials** | Halved from 2mg — major inventory efficiency; 2 full cycles now possible |
| Ipamorelin | 6 | 10mg | 60mg | ~1.35 vials (nights only) / ~2.1 vials (nights + AM training) | ~4.65 / ~3.9 vials | Add AM training dose costs ~0.75 vials/cycle |
| Semax | 1 | 10mg | 10mg | ~1 full vial (4.5–5 wks at 400mcg/day) | **0 — order 2nd vial** | One vial insufficient for full 6-week cycle at new dose |

**Post-Cycle Rest Windows (once stack starts):**
- MOTS-C: min 4 weeks off after 8-week cycle
- Tesamorelin: min 4 weeks off after 9-week cycle
- Ipamorelin: min 4 weeks off after 9-week cycle

**Retatrutide + Stack Overlap Protocol:**
- Current state and confirmed plan are tracked in `data/health/tracking.json` (peptide section)
- Protein target, weight floor triggers, and recomposition phase decisions: see `data/health/tracking.json`
- If weight gain >2 lbs/week during lean mass recovery phase: restart Berberine 500mg BID

**Tesamorelin Dose — FINALIZED (2026-06-14, Galen bloodwork review):**

IGF-1 was NOT on either the June 2025, December 2025, or June 2026 bloodwork panels. It has never been ordered. The dose decision is therefore made using the clinical framework below:

**Decision: Start Tesamorelin at 1mg as planned.**

Rationale: Without a baseline IGF-1, the default conservative protocol applies. The diabetic family history and glycemic caution noted in the original dose rationale remain valid. At 51 years of age, IGF-1 is statistically likely to be in the 80–150 ng/mL range (age-matched median per Bidlingmaier et al., J Clin Endocrinol Metab 2014). Starting at 1mg is appropriate — it is the FDA-approved Tesamorelin dose for visceral fat reduction (Falutz et al. NEJM 2010; Dhillon S. Drugs 2011), and Baker et al. (Neurology 2021) demonstrated cognitive benefit at 1mg without dose escalation. The Ipamorelin co-administration amplifies GH pulse amplitude, making 2mg unnecessary for target IGF-1 attainment in the 150–225 ng/mL range.

**CRITICAL ACTION: Order IGF-1 baseline lab before starting Tesamorelin.** If IGF-1 comes back >200 ng/mL, hold Tesamorelin and escalate to Dr. Randol. If <150, current 1mg plan holds. Target range at week 6 recheck: 150–225 ng/mL.

**Bloodwork Flags from June 2026 Draw — Protocol Implications:**

| Flag | Value | Implication |
|------|-------|-------------|
| **Estradiol E2 = 69 pg/mL (HIGH, was 45 Jun 2025)** | Significantly elevated, trending up | Cleared by Dr. Randol — June 14, 2026. Proceed as planned. E2 hold lifted. DHEA reduction (50mg → 25mg) remains active recommendation. GH axis peptides (Tesamorelin/Ipamorelin) cleared to start per July 7–14 target. |
| **DHEA-S = 535 mcg/dL (HIGH, was 111 Jun 2025)** | Markedly elevated on DHEA 50mg supplementation | Primary driver of E2 elevation. Consider pausing DHEA 50mg or reducing to 25mg before stack start. Recheck E2/T in 4–6 weeks. |
| **Total T = 1498 ng/dL / Free T = 543.4 pg/mL (HIGH)** | Driven by DHEA; LH/FSH suppressed | HPG axis suppressed — confirms exogenous DHEA driving testosterone; Tesamorelin/Ipamorelin will add additional anabolic load; discuss with Dr. Randol |
| **Homocysteine = 19.5 umol/L (HIGH, was 12.0 Jun 2025)** | Elevated cardiovascular risk marker | Start methylated B-complex immediately: methylcobalamin + methylfolate + P5P (B6). Recheck at next draw. Relevant to Semax CNS protocol — elevated homocysteine impairs BDNF signaling and neuroplasticity. |
| **hs-CRP = 2.2 mg/L (average CV risk, was 1.6 Dec 2025)** | Trending up, in average-risk range | Semax CNS start is fine — no acute CNS inflammation concern. Monitor post-Reta whether CRP improves (GLP-1 has anti-inflammatory effects). |
| **Fasting Glucose = 48 mg/dL** | Almost certainly lab artifact — HbA1c 4.9% and insulin 3.4 inconsistent with hypoglycemia | Do NOT act on this value. Likely prolonged fasting or sample timing error. Metabolic profile is actually excellent: HbA1c 4.9, insulin 3.4, Tesamorelin glycemic risk is LOW at current metabolic state. |
| **MCV 107.6 / MCH 35.4 (worsening macrocytosis)** | MCV was 103.6 in Dec 2025 | MMA improved (230 → 138) so functional B12 is adequate, but macrocytosis worsening — could reflect other causes (medications, alcohol, hypothyroidism excluded by TSH 1.15). Discuss with Dr. Randol. |
| **Platelets 114 (LOW, was 102 Dec 2025)** | Mild thrombocytopenia, slight improvement | Retatrutide may be contributing. Monitor post-Reta. |
| **AST 42 (HIGH, was 29 Dec 2025)** | Mildly elevated | Likely training-related or Retatrutide. Monitor post-Reta. If persists, defer peptide stack until resolved. |
| **LDL Pattern B + Small LDL 274 + HDL Large 5239 (LOW)** | Atherogenic lipid pattern | Restart Berberine 500mg BID immediately. Exercise (which is already happening) is the best intervention for Pattern B. |
| **ApoB = 84 mg/dL** | In range (<90) but borderline | Improved vs prior (was 95 in Jun 2025). Continue monitoring. Berberine restart supports further improvement. |

**Upcoming Actions:**
- **COMPLETE (June 14, 2026): Dr. Randol cleared E2 and IGF-1 concerns** — E2 hold lifted. Tesamorelin and Ipamorelin cleared to proceed per July 7–14 stack start target.
- **RECOMMENDED: Order IGF-1 baseline lab before or shortly after stack start** — not blocking, but advisable for monitoring. If IGF-1 comes back >200 ng/mL at any point, hold Tesamorelin and escalate to Dr. Randol. Target range at week 6 recheck: 150–225 ng/mL.
- **ACTIVE: DHEA reduction — reduce from 50mg to 25mg** — Dr. Randol recommendation for E2 and DHEA-S management. Not yet confirmed as actioned; David to confirm timing.
- **ACTIVE: Methylated B-complex** — methylcobalamin + methylfolate + P5P for homocysteine 19.5 (was 12.0; significant upward trend in 12 months). Continue until recheck.
- **ACTIVE: Restart Berberine 500mg BID** — LDL Pattern B + small LDL 274; metabolic protection during Reta transition.
- GH stack (MOTS-C/Tesa/Ipa) target start: July 7–14, 2026 (1–2 weeks post-Reta end ~July 5). Semax to follow 2 weeks later: Jul 12, 2026
- Recheck IGF-1 at week 6 of stack — target 150–225 ng/mL (upper-normal for age, not supraphysiologic)
- Order second Semax vial before starting (one vial insufficient for 6-week cycle at 400mcg/day)
- Book DEXA mid-August 2026 vs. March 2026 baseline (VAT, A/G ratio, BF%)

### Step 2: Assess Active Status

For each item:
- **Active:** Currently taking/injecting daily/weekly
- **Paused:** Intentionally stopped, reason documented
- **Planned:** On rotation but not currently active
- **Due for Restart:** Time window approaching

For peptides, track:
- **Cycle in progress:** Which week of the cycle?
- **Days until next injection:** For weekly injections
- **Days until cycle end:** When is the break/deload?
- **Protocol limitations:** Epithalon max 2x/year with 4-month pause required

Output:
```
protocol_status:
  supplements:
    active: [list with dosages]
    paused: [list with pause reasons]
    recommended_not_yet_started: [list from Function Health]

  peptides:
    active: [list with cycle week, next injection date]
    paused: [list with restart window]
    cycle_tracking:
      mots_c: "Week [X] of 8, next injection [date] (every 5 days, morning)"
      tesamorelin: "Week [X] of 9, next injection [date] (Mon–Fri nights)"
      ipamorelin: "Week [X] of 9, next injection [date] (Mon–Fri nights, same window as Tesa)"
      cjc_1295_paused: "Paused while Tesamorelin active — restart eligible Sep 14, 2026"
      epithalon_next_eligible: "[date] (4-month pause required)"
      dsip_next_window: "November 2026 (seasonal, winter focus)"
```

### Step 3: Cross-Reference with Latest Bloodwork

Check if active protocols align with recent bloodwork results:

**Supplement + Bloodwork Alignment:**
- Is Berberine paused? Check fasting insulin and glucose trend → if rising, recommend restart
- Is CoQ10 missing? Check ApoB and cholesterol → if elevated, recommend addition
- Is Biotin missing? Check MCH/MCV → if elevated, recommend addition for B12 support

**Peptide + Bloodwork Alignment:**
- CJC-1295/Ipamorelin active → expect elevated IGF-1, possible E2 elevation, possible fasting insulin rise
  - Check if bloodwork shows: IGF-1 (should be elevated), E2 (watch for excess), fasting insulin (watch for decline in sensitivity)
- BPC-157 active → non-systemic, minimal expected bloodwork changes
- Epithalon cycle → expected to elevate telomerase; no major bloodwork markers; focus on recovery/resilience

Output:
```
alignment_check:
  berberine_paused: "Fasting insulin [metric] — RECOMMEND RESTART given metabolic trend"
  coq10_missing: "ApoB at 80 — RECOMMEND ADD 500mg daily for lipid support"
  cjc_ipamorelin_status: "Active (week 4) — expect elevated IGF-1; check for E2 management"
  conflicts: [] or ["E2 high + DHEA dosing — may be aromatization"]
```

### Step 4: Flag Protocol Conflicts & Gaps

**Common Conflicts:**
- **Dual hormone amplification:** CJC-1295 + TRT + high-dose DHEA + elevated E2 → aromatization risk
- **Metabolic timing:** Hard to optimize muscle gain and metabolic health simultaneously; peptides + berberine + glucose control need coordination
- **Micronutrient depletion:** High-dose creatine + intense training depletes certain nutrients; check B vitamins, electrolytes
- **Timing windows:** Some supplements enhance others (creatine + high carb window), while others compete (certain minerals)

**Common Gaps:**
- **Lipid management:** Only Omega-3; missing CoQ10, berberine, niacin (if warranted)
- **Glucose control:** Creatine demands hydration + glucose stability; may need glucose monitoring or inositol
- **Hormone balance:** GH protocol without estrogen management or aromatase inhibition (if needed)
- **Micronutrient insurance:** AG1 covers general, but specific deficiencies (B12, folate, iron) need targeted support

Output:
```
conflicts:
  - "E2 at 45 (elevated) + DHEA 50mg daily — monitor for aromatization; discuss with Dr. Randol"
  - "CJC/Ipamorelin + high training load — confirm fasting insulin not declining"

gaps:
  - "Lipid protocol missing CoQ10 (add 500mg daily) and berberine (add 500mg BID)"
  - "No targeted glucose control supplement despite peptide protocol (consider berberine or inositol)"
  - "B12 concern (MCH/MCV elevated) — add targeted B12 support (sublingual or injection)"
```

### Step 5: Summarize Upcoming Cycle Changes

Check what's coming in the next 4-8 weeks:

- **CJC-1295/Ipamorelin:** Ends [date]? → deload week required, recovery week expected
- **Epithalon:** Eligible [date]? → if ready, 10-day cycle window
- **DSIP:** Eligible [date]? → seasonal, plan winter
- **MOTS-C:** Eligible [date]? → consider if metabolic focus needed

Output:
```
upcoming_changes:
  - "CJC-1295/Ipamorelin cycle ends in ~4 weeks (end of April) → plan 1-week deload → reassess and restart if desired"
  - "Epithalon eligible August 2026 (4-month pause from December cycle) → plan 10-day spring cycle if desired"
  - "DSIP eligible November 2026 → seasonal, winter focus for sleep optimization"
```

### Step 5b: Citation Requirement for Protocol Recommendations

Any recommendation to start, stop, or adjust a supplement or peptide must include:
- **Mechanism:** How this compound affects the target marker or system
- **Evidence:** Citation (author / study / year / publication or clinical body)
- **Confidence:** `strong evidence` / `emerging evidence` / `expert consensus`

Peptide protocols in particular have limited RCT data — flag those as `emerging evidence` and note the primary research source (e.g., "Sikiric et al., BPC-157 GI healing studies" or "Walker et al., Ipamorelin phase II trial").

### Step 6: Generate Protocol Status Card

**Format: Shareable markdown or HTML summary**

```markdown
# Protocol Status Card — [Date]

## Active Supplement Stack

| Supplement | Dosage | Frequency | Status | Days on Protocol |
|-----------|--------|-----------|--------|------------------|
| Ashwaganda | [dose] | Daily | ✅ Active | [days] |
| NAC | [dose] | Daily | ✅ Active | [days] |
| [etc] | | | | |

**Total Daily Supplements:** [count]
**Stack Cost (monthly):** $[estimated]
**Compliance:** [green/yellow/red] — [notes]

---

## Paused Protocols (Ready to Restart)

| Supplement | Dosage | Reason Paused | Restart Trigger | Status |
|-----------|--------|----------------|-----------------|--------|
| Berberine | 500mg BID | Metabolic experimentation | High fasting insulin? | 🔴 RECOMMEND RESTART — see bloodwork |
| Resveratrol | [dose] | [reason] | [trigger] | ⚪ On hold |

---

## Recommended Additions (Not Yet Started)

| Supplement | Dosage | Purpose | Rationale | Priority |
|-----------|--------|---------|-----------|----------|
| CoQ10 | 500mg | Lipid support, mitochondrial | ApoB elevated (80) | 🔴 URGENT |
| Biotin | 5mg | B-vitamin support | MCH/MCV elevated | 🟡 IMPORTANT |
| Quercetin | 500mg | Antioxidant, CV support | Inflammatory support | 🟡 IMPORTANT |
| Berberine | 500mg BID | Metabolic, glucose control | See: Paused Protocols | 🔴 URGENT |

---

## Peptide Cycle Status

### Active Cycles

**CJC-1295 w/DAC + Ipamorelin**
- **Status:** ✅ Active (Week 4 of 8)
- **Next Injection:** [date/time]
- **Cycle End:** [date] (~4 weeks from now)
- **Deload Plan:** 1-week break, reassess
- **Bloodwork Support:** Expect elevated IGF-1, watch E2, monitor fasting insulin

**BPC-157 (as needed)**
- **Status:** ✅ Active (injury recovery protocol)
- **Usage:** PRN, 250-500ug when needed
- **Expected Duration:** Until [recovery milestone]

### Paused/Planned Cycles

**Epithalon**
- **Status:** ⚪ Paused (last cycle: December 2025, 10 days)
- **Max Frequency:** 2x per year, 4-month pause between cycles
- **Next Eligible:** August 2026 (still in 4-month pause window)
- **Purpose:** Telomerase activation, aging marker
- **Plan:** Consider spring cycle if desired

**DSIP**
- **Status:** ⚪ Planned (seasonal focus)
- **Next Window:** November 2026 (winter focus for sleep)
- **Purpose:** Sleep quality, mood, recovery
- **Expected Duration:** 10-day cycle

**MOTS-C**
- **Status:** ⚪ Available for metabolic focus cycles
- **Next Window:** Q3 2026 if metabolic optimization needed
- **Purpose:** Metabolic health, glucose control
- **Notes:** Emerging research, effective for metabolic optimization

---

## Protocol Alignment Assessment

### With Bloodwork
- ✅ CJC/Ipamorelin protocol supported by expected markers
- ⚠️ E2 elevation (45) — may benefit from DIM or aromatase support
- 🔴 Fasting insulin [metric] — recommend berberine restart + glucose monitoring
- ⚠️ B12/MCH/MCV — recommend targeted B12 supplement

### With Goals
- ✅ Peptide protocol supports muscle + GH optimization
- ✅ Omega-3 + AG1 support general health
- 🔴 Lipid management gap — missing CoQ10, berberine for ApoB control
- ⚠️ Metabolic management — may benefit from glucose-control supplement

---

## Action Items

### URGENT (Start Within 1 Week)
1. Add CoQ10 500mg daily (for ApoB management)
2. Restart Berberine 500mg BID (for metabolic support)
3. Add Biotin 5mg daily (for B12 support)

### IMPORTANT (Start Within 2 Weeks)
4. Add Quercetin 500mg daily (CV support)
5. Discuss E2 management with Dr. Randol (DIM or other)

### MONITORING (Track Over Next 4 Weeks)
6. CJC/Ipamorelin cycle → ends [date], plan deload week
7. Fasting insulin trend → retest with bloodwork in 8-12 weeks
8. E2 trend → retest with bloodwork in 8-12 weeks

### PLANNING (4-8 Weeks)
9. Epithalon eligibility check — next cycle eligible August 2026
10. Quarterly bloodwork retest (planned [date])

---

**Status Card Generated:** [timestamp]
**Protocol Tracking Since:** January 2026
**Next Protocol Review:** Monthly (aligned with monthly health review)
**Physician:** Dr. Julli Randol
```

---

### Step 7: Write Protocol Changes to Health Metrics Log

If any protocol change occurred since the last logged entry (a supplement started, stopped, or adjusted; a peptide cycle started or ended), append a `protocol_change` entry to `data/health/metrics-log.json`.

- Use `entry_id` format: `protocol-change-{YYYY-MM-DD}`
- List each change as an object in the `changes` array with: `item`, `type` (supplement/peptide), `action` (started/stopped/adjusted/paused), `dose`, `frequency`, `rationale`
- If no changes occurred since the last log entry, skip this write
- Follow the schema in `data/health/schema.md` exactly

This write happens after the status card is delivered — it is the final action before SKILL COMPLETE.

---

## Success Metrics

- All active supplements listed with dosages and frequency
- All peptide cycles tracked with current phase and next injection date
- Paused protocols listed with restart triggers
- Recommended additions (Function Health) vs. currently active identified
- Protocol conflicts identified and flagged
- Gaps between bloodwork findings and active stack highlighted
- Upcoming cycle changes previewed
- Status card is shareable with physician or health coach
- Action items are specific and prioritized

## Error Handling

| Scenario | Response |
|----------|----------|
| Supplement dosages unclear in vault | Use last known dosage; note "Confirm dosage with David" |
| Peptide cycle history incomplete | Proceed with known history; note "Incomplete cycle history" |
| No recent bloodwork available | Mark all bloodwork alignments as "pending" |
| Active cycle timing unclear | Note "Confirm injection timing with David" |

---

## Integration Notes

- Output protocol status card suitable for Obsidian vault storage or email sharing
- Galen feeds protocol summary to Visit Prep skill pre-appointment
- Protocol conflicts escalate to Bloodwork Review and Dr. Randol question list
- Upcoming cycle changes may trigger Recovery Coaching if load adjustments needed
- Monthly health review incorporates protocol assessment as one data stream

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/galen-protocols-latest.json
```

Content:
```json
{
  "skill": "galen-protocols",
  "agent": "galen",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.


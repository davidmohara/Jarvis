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
- **Mechanism:** ACTH(4-7)PGP analog. Upregulates BDNF and NGF expression (Dolotov et al., 2006, *Journal of Neurochemistry*); modulates melanocortin receptors (MC4R); enhances dopaminergic and serotonergic signaling in prefrontal cortex. Downstream BDNF effects last 20–24 hours despite short peptide half-life. BDNF mRNA tripling in hippocampus documented at single-dose level in animal models.
- **Evidence level:** Emerging evidence — Russian clinical data (stroke, cognitive dysfunction, ADHD). Limited Western RCT data. Protocol based on established peptide community consensus and Russian pharmacological literature.
- **Dose rationale:** 200mcg/nostril (400mcg total) is the established effective cognitive enhancement range. Prior protocol at 100mcg/nostril (200mcg total) was at the low end of documented efficacy. Upper dose boundary for cognitive use is 600–800mcg/day — 400mcg provides meaningful BDNF stimulus without reaching MC4R over-activation threshold.
- **Stacking considerations:**
  - No known pharmacokinetic conflicts with Retatrutide, MOTS-C, Tesamorelin, or Ipamorelin
  - Cognitive/focus enhancement is additive with GH axis peptides (Tesamorelin/Ipamorelin → IGF-1 → neuroplasticity support)
  - MOTS-C mitochondrial/metabolic effects are mechanistically orthogonal — no interaction
  - Space PM dose ≥4 hours from any sedating supplements (DSIP if active, PM ashwagandha)
- **Contraindications / cautions:** MC4R stimulation is activating — avoid in acute anxiety states. If anxiety increases, reduce to 100mcg/nostril 1x/day AM only or drop to 3x/week. Monitor WHOOP sleep onset on PM-dose days.
- **Reconstitution:** 2ml BW = 5mg/ml = 500mcg per 0.1ml actuation. Draw 0.08ml per nostril for 400mcg total (200mcg/nostril). Verify concentration with supplier before use.

**Post-Cycle Rest Windows (once stack starts):**
- MOTS-C: min 4 weeks off after 8-week cycle
- Tesamorelin: min 4 weeks off after 9-week cycle
- Ipamorelin: min 4 weeks off after 9-week cycle

**Retatrutide + Stack Overlap Protocol:**
- Current state and confirmed plan are tracked in `data/health/tracking.json` (peptide section)
- Protein target, weight floor triggers, and recomposition phase decisions: see `data/health/tracking.json`
- If weight gain >2 lbs/week during lean mass recovery phase: restart Berberine 500mg BID

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

<!-- system:end -->



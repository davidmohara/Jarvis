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

**Current Known Stack (as of March 2026):**

| Supplement | Dosage | Frequency | Status | Start Date | Purpose |
|-----------|--------|-----------|--------|------------|---------|
| Ashwaganda | [dose] | Daily | Active | [date] | Stress/cortisol modulation |
| NAC | [dose] | Daily | Active | [date] | Antioxidant, glutathione precursor |
| PQQ | [dose] | Daily | Active | [date] | Mitochondrial protection |
| ALA | [dose] | Daily | Active | [date] | Mitochondrial, antioxidant |
| Omega-3 | [dose] | Daily | Active | [date] | Cardiovascular, anti-inflammatory |
| AG1 | [dose] | Daily | Active | [date] | Micronutrient insurance |
| Creatine | 5g | Daily | Active | [date] | Muscle, cognitive, energy |
| Vitamin D/K | [dose] | Daily | Active | [date] | Bone, cardiovascular |
| Berberine | [dose] | Daily | **PAUSED** | [pause date] | Metabolic, glucose control |
| Resveratrol | [dose] | Daily | **PAUSED** | [pause date] | Sirtuin activation |

**Function Health Recommended (August 2025):**
- Berberine (restart)
- Biotin (new)
- Quercetin (new)
- CoQ10 (new)
- DHEA 50mg PURE (started or confirmed)

**Current Known Peptide Protocols (as of March 2026):**

| Peptide | Dosage | Frequency | Status | Cycle Timing | Purpose | Notes |
|---------|--------|-----------|--------|--------------|---------|-------|
| CJC-1295 w/DAC | 1mg | Weekly (1x/wk) | Active | 8-12 weeks on, 4 weeks off | GH secretagogue | Long-acting, 6+ month half-life in circulation |
| Ipamorelin | 1400ug | Weekly (1x/wk) | Active | Concurrent with CJC | GH pulse amplifier | Works synergistically with CJC |
| BPC-157 | As needed | PRN | Active | Injury/recovery cycles | Healing, recovery, GI support | Minimal side effects, safe for chronic use |
| Epithalon | [dose] | Cycling | **PAUSED/Planned** | 2x/year max, 4-month pause between | Telomerase activation, aging | Max 2 cycles per year, 10-day cycle duration |
| DSIP | [dose] | Cycling | **PAUSED/Planned** | Seasonal (winter focus) | Sleep quality, mood | Excellent for sleep architecture |
| MOTS-C | [dose] | Cycling | **PAUSED/Planned** | Metabolic focus cycles | Metabolic health, glucose control | Emerging research, use when metabolic focus needed |

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
      cjc_ipamorelin_cycle: "Week 4 of 8, injection due [date]"
      epithalon_next_eligible: "August 2026 (4-month pause required, last cycle: December 2025)"
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

Origin file: skills/galen-protocols/SKILL.md
Relocated: 2026-10-10
Reason: State, dated stack inventory, bloodwork flags, dose-finalization narrative, and run log removed from the instructional skill (they violated its own "read from tracking.json, do not hardcode" rule). Much of this state also lives in data/health/tracking.json (current_phase, peptide_cycles) and data/health/supplement-stack.json; relocated verbatim here so nothing is lost.

--- Full Stack Protocol (MOTS-C + Tesamorelin + Ipamorelin + Semax — ACTIVE as of Jun 29, 2026) ---

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

--- Semax cycle state (from the Semax Protocol section) ---

- **Cycle:** **~4.5 week test run (single vial).** Intentional test run to assess response before committing to longer cycling. (Previous: 6 weeks on / 2 weeks off.)
- **Inventory note:** 1 vial on hand — intentional test run, no reorder needed before start.

--- Inventory as of June 14, 2026 (at revised doses) ---

| Peptide | Vials on Hand | Mg/Vial | Total | Cycle Use (revised) | Remaining After | Notes |
|---------|--------------|---------|-------|---------------------|-----------------|-------|
| MOTS-C | 5 | 40mg | 200mg | ~1.75 vials (8 wks @ 5mg/4d) | ~3.25 vials | Every 4 days = ~8.75mg/wk |
| Tesamorelin | 9 | 10mg | 90mg | **4.5 vials** (9 wks @ 1mg/night × 5) | **4.5 vials** | Halved from 2mg — major inventory efficiency; 2 full cycles now possible |
| Ipamorelin | 6 | 10mg | 60mg | ~1.35 vials (nights only) / ~2.1 vials (nights + AM training) | ~4.65 / ~3.9 vials | Add AM training dose costs ~0.75 vials/cycle |
| Semax | 1 | 10mg | 10mg | ~1 full vial (4.5–5 wks at 400mcg/day) | **0 — order 2nd vial** | One vial insufficient for full 6-week cycle at new dose |

--- Tesamorelin Dose — FINALIZED (2026-06-14, Galen bloodwork review) ---

IGF-1 was NOT on either the June 2025, December 2025, or June 2026 bloodwork panels. It has never been ordered. The dose decision is therefore made using the clinical framework below:

**Decision: Start Tesamorelin at 1mg as planned.**

Rationale: Without a baseline IGF-1, the default conservative protocol applies. The diabetic family history and glycemic caution noted in the original dose rationale remain valid. At 51 years of age, IGF-1 is statistically likely to be in the 80–150 ng/mL range (age-matched median per Bidlingmaier et al., J Clin Endocrinol Metab 2014). Starting at 1mg is appropriate — it is the FDA-approved Tesamorelin dose for visceral fat reduction (Falutz et al. NEJM 2010; Dhillon S. Drugs 2011), and Baker et al. (Neurology 2021) demonstrated cognitive benefit at 1mg without dose escalation. The Ipamorelin co-administration amplifies GH pulse amplitude, making 2mg unnecessary for target IGF-1 attainment in the 150–225 ng/mL range.

**CRITICAL ACTION: Order IGF-1 baseline lab before starting Tesamorelin.** If IGF-1 comes back >200 ng/mL, hold Tesamorelin and escalate to Dr. Randol. If <150, current 1mg plan holds. Target range at week 6 recheck: 150–225 ng/mL.

--- Bloodwork Flags from June 2026 Draw — Protocol Implications ---

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

--- Upcoming Actions (run log) ---

- **COMPLETE (June 14, 2026): Dr. Randol cleared E2 and IGF-1 concerns** — E2 hold lifted. Tesamorelin and Ipamorelin cleared to proceed per July 7–14 stack start target.
- **RECOMMENDED: Order IGF-1 baseline lab before or shortly after stack start** — not blocking, but advisable for monitoring. If IGF-1 comes back >200 ng/mL at any point, hold Tesamorelin and escalate to Dr. Randol. Target range at week 6 recheck: 150–225 ng/mL.
- **ACTIVE: DHEA reduction — reduce from 50mg to 25mg** — Dr. Randol recommendation for E2 and DHEA-S management. Not yet confirmed as actioned; David to confirm timing.
- **ACTIVE: Methylated B-complex** — methylcobalamin + methylfolate + P5P for homocysteine 19.5 (was 12.0; significant upward trend in 12 months). Continue until recheck.
- **ACTIVE: Restart Berberine 500mg BID** — LDL Pattern B + small LDL 274; metabolic protection during Reta transition.
- GH stack (MOTS-C/Tesa/Ipa) target start: July 7–14, 2026 (1–2 weeks post-Reta end ~July 5). Semax to follow 2 weeks later: Jul 12, 2026
- Recheck IGF-1 at week 6 of stack — target 150–225 ng/mL (upper-normal for age, not supraphysiologic)
- Order second Semax vial before starting (one vial insufficient for 6-week cycle at 400mcg/day)
- Book DEXA mid-August 2026 vs. March 2026 baseline (VAT, A/G ratio, BF%)

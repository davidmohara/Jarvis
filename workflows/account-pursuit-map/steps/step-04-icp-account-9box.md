---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: ICP & Account 9-Box

## MANDATORY EXECUTION RULES

1. You MUST compute two scores for the target — **Potential** and **Realized** — each built from the same three-factor weighted formula: Geography (10%), Revenue (70%), Gross Margin (20%). Use the exact weights and lookup tables in YOUR TASK below. Do not invent an alternate weighting or scoring scale.
2. You MUST score each of the three factors on a **-5 to +5 band** using the lookup tables provided, then apply the weights to get the weighted Potential and weighted Realized scores. Show the raw factor score, the weight, and the weighted contribution for each factor — do not just present the final number.
3. You MUST plot (Realized, Potential) on the -5 to +5 by -5 to +5 grid and classify into one of the nine named zones (IDEAL, SIGNIFICANT, POISED, SOLID, CORE, STEADY, LIMITED, CONSTRAINED, CAPPED) using the grid arrangement in YOUR TASK Task 4. Flag this grid arrangement to the controller as an inference to sanity-check on first real use — only one confirmed data point (AT&T, POISED) was available when this arrangement was built.
4. You MUST flag the geography scoring logic as an inference. Only one data point was available from the source (AT&T: both flags "N", Geo score = 0). Use the baseline-plus-bonus logic in Task 2 but state plainly that this has not been verified against a case where either flag is "Y."
5. You MUST NOT leave the "best case annual IT services spend" input blank. Follow the two-path sourcing order in Task 1: (1) if the target is public, check its 10-K, annual report, or investor materials first for a disclosed IT/technology spend figure; (2) only if the company is private, or is public but doesn't disclose a usable figure, fall back to estimating from company size (headcount or revenue) cross-referenced against a cited industry IT-spend benchmark. Present the result as an override-able estimate, not a blank prompt, and state which path was used.
6. You MUST NOT leave the gross margin inputs blank. Default to Improving's typical realized gross margin range for the relevant engagement type (proposed default: mid-30s to mid-40s percent, per Task 1), clearly flagged as an assumption David can override.
7. You MUST pull TTM (trailing twelve months) actual revenue and gross margin for the Realized score from CRM if the account has existing engagement history. If no CRM history exists (cold/new pursuit), you MUST default Realized revenue and gross margin to zero/near-zero by definition — do not research-guess a TTM actual. State "no engagement history — Realized defaulted to $0 / 0% margin" rather than estimating.
8. You MUST note the $1M revenue-band and 20%/20% gross-margin-band boundary ambiguity from the source (each appears twice at the 0/-5 or 0/-4 boundary) if a given account's estimate falls near that boundary. Interpolate/round reasonably and say so — do not silently pick one value without flagging it.
9. Do NOT proceed to step 05 until both Potential and Realized weighted scores are computed with full factor-level detail, the 9-box zone is assigned, and every inference in this step (geography scoring logic, 9-box grid arrangement, IT spend estimate, gross margin default) is explicitly flagged for David to verify.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** entity_anchor (step 01), strategic_priorities (step 02), company size/revenue signals (from step 01/02 research), CRM (for TTM actuals if engagement history exists)
**Output:** Potential score, Realized score, 9-box zone classification, and a list of every inference made — stored in accumulated-context for step 06, placed in the final document immediately after the Leadership/Org Chart section

---

## CONTEXT BOUNDARIES

- This section is placed immediately after step 03's Leadership/Org Chart in the final assembled document — it is not an early triage gate before research begins, and it is not bundled with step 03's competitive positioning/strategic-priorities content. It is its own section.
- This step does new estimation work (IT spend sizing, gross margin defaulting) but not new primary-source research beyond what's needed to size the account — reuse company-size signals already gathered in steps 01-02 where possible rather than re-running full research.
- The scoring methodology (weights, bands, formula) is fixed and sourced from Improving's 2026 AT&T Account Plan spreadsheet. Do not adjust the weights, the band values, or the formula shape to fit a particular account — apply the fixed methodology and let the account's numbers determine the outcome.
- Every inference flagged in this step (geography logic, 9-box arrangement, IT spend estimate, GM default) must be carried forward into step 06's Open Items to Confirm — do not let them get lost between steps.

---

## YOUR TASK

### 1. Estimate the Potential-score inputs

**Revenue factor — "Best case, what could annual IT services spend be at this client?"**

Follow this source-priority order — do not skip straight to the benchmark estimate for a public company without checking primary filings first. This is the same "primary filings first" discipline already applied in step-02's stated strategic priorities and in `workflows/client-meeting-prep`.

- **Path 1 — Public company, check filings first:** If the target is publicly traded, check its most recent 10-K, annual report, or investor materials (investor presentations, earnings call transcripts, analyst day decks) for a disclosed technology/IT spend figure. Some companies explicitly break out IT or technology spend (total or as a segment); many don't, so this may come up empty — that's expected, not a failure. If a usable figure is found, use it directly as (or to directly derive) the best-case annual IT services spend estimate, and cite the specific filing/document and date.
- **Path 2 — Fallback (private company, or public with no disclosed figure):** Estimate using company size: pull headcount or annual revenue (whichever is more reliably researched for the target — usually available from step 01/02's entity research, 10-K, or public company-size databases). Cross-reference against a cited industry benchmark for IT-spend-as-percent-of-revenue or per-employee IT spend. Use a named, citable benchmark (e.g., Gartner's IT Key Metrics Data / IT spending as a percentage of revenue by industry — typically ranges ~1-3% for asset-heavy industries like manufacturing/energy, ~4-7% for financial services/telecom, higher for tech-native firms; or a per-employee IT budget benchmark such as Computer Economics' annual IT spending studies). Cite whichever benchmark source is used. Apply the benchmark to the target's revenue or headcount to produce the estimate (note: "IT services spend" is a subset of total IT budget — typically the external-services portion, not internal headcount/licensing — so apply a reasonable discount to a total-IT-budget benchmark if that's the only one available, and say so). The benchmark-citation requirement applies only to this fallback path — Path 1 is sourced directly from the company's own disclosure, not a benchmark.
- Record:
  ```yaml
  potential_revenue_estimate:
    method: "public-filing-disclosed figure" | "company-size cross-referenced against industry IT-spend benchmark (fallback)"
    source_priority_path: "1 - public filings/investor materials" | "2 - headcount/revenue x industry benchmark fallback"
    path_1_check_result: "{If public: what was checked (10-K/annual report/investor materials, with date) and whether a usable figure was found. If private: 'N/A — private company, Path 1 not applicable.'}"
    company_size_input: "{headcount or annual revenue used, with source — only populated if Path 2 used}"
    benchmark_used: "{Named benchmark and citation — only populated if Path 2 used}"
    estimated_annual_it_services_spend: "${X}"
    note: "Estimate — override with a better figure if David has direct knowledge of the account's IT budget."
  ```

**Gross Margin factor — "What's the maximum average gross margin achievable at this client?"**

- Default to Improving's typical realized gross margin range for the relevant engagement type/capability area. Proposed default: **mid-30s to mid-40s percent** (e.g., ~35-42%), adjusted down toward the lower end for staff-augmentation-heavy engagements and up toward the higher end for project-based/IP-driven engagements.
- Record:
  ```yaml
  potential_gm_estimate:
    default_used: "{e.g., '38% — mid-range default for a blended delivery model'}"
    note: "Default assumption — no explicit David input on this account's achievable GM. Override if David has a better estimate for this engagement type."
  ```

**Geography factor — two Y/N flags**

- Flag (a): Does the delivery lead or biz dev executive live in the same location as the client buyer?
- Flag (b): Is the client located where Improving has an office?
- Determine both flags from step 01's entity anchor (HQ location) and known Improving office locations / David's team assignments.
- Record:
  ```yaml
  potential_geo_flags:
    same_location_as_buyer: true/false
    improving_office_in_client_location: true/false
  ```

### 2. Score the Potential factors against the lookup tables

**Revenue band lookup (estimated annual IT services spend → score):**

| Spend | Score |
|-------|-------|
| $200K | -5 |
| $300K | -4 |
| $400K | -3 |
| $500K | -2 |
| $750K | -1 |
| $1M | 0 |
| $1M (upper) | 1 |
| $2M | 2 |
| $5M | 3 |
| $10M | 4 |
| $20M | 5 |

- The source lists $1M twice, at the 0/1 boundary — treat $1M as the 0 point. For a value that falls between two named bands, interpolate/round to the nearer band and flag: "Interpolated between {lower band}→{score} and {upper band}→{score}; source has an unresolved ambiguity at the $1M boundary specifically." Do not silently pick a side without this note if the estimate lands near $1M.
- For values below $200K or above $20M, extrapolate the trend (extend beyond -5 or +5 only if clearly warranted, otherwise cap at -5/+5) and flag as outside the named range.

**Gross margin band lookup (percentage → score):**

| GM % | Score |
|------|-------|
| 20% | -5 |
| 20% | -4 |
| 24% | -3 |
| 27% | -2 |
| 30% | -1 |
| 32% | 0 |
| 34% | 1 |
| 37% | 2 |
| 40% | 3 |
| 45% | 4 |
| 50% | 5 |

- Same treatment: the source shows 20% twice, at the -5/-4 boundary — flag this ambiguity if the estimate lands at or near 20%. Interpolate/round reasonably between named bands otherwise.

**Geography scoring (inference — flag to David):**

- Only one data point exists from the source: AT&T, both flags "N," Geo score = 0. This suggests geography is a bonus-only factor — a 0 baseline when neither flag is "Y," scoring upward if either or both flags are "Y."
- Proposed scoring (inference, unverified beyond the single AT&T data point):
  ```yaml
  geo_scoring_logic_inference:
    both_flags_N: 0
    one_flag_Y: 2   # proposed — same-location-as-buyer OR office-in-location, not both
    both_flags_Y: 4  # proposed — both conditions met
    flag_to_david: "This scoring curve is inferred from a single data point (AT&T, N/N = 0). Verify against the source spreadsheet for any account where a geography flag is 'Y' before trusting this fully."
  ```

- Record the scored factors:
  ```yaml
  potential_scores:
    geo_raw: {score from geo_scoring_logic_inference}
    revenue_raw: {score from revenue band lookup}
    gm_raw: {score from GM band lookup}
  ```

### 3. Compute weighted Potential and weighted Realized

**Formula (fixed, verified against the AT&T source numbers — replicate exactly):**

```
Weighted Score = (Geo_raw × 0.10) + (Revenue_raw × 0.70) + (GM_raw × 0.20)
```

- Verification check performed on this formula against the source: AT&T's Potential = 3.1 came from Geo weighted 0 (0 × 0.10), Revenue weighted 2.1 (raw score 3 × 0.70), GM weighted 1.0 (raw score 5 × 0.20) → 0 + 2.1 + 1.0 = 3.1. Confirmed correct — apply the same arithmetic here.

**Realized-score inputs (before applying the formula):**

- **Revenue factor:** TTM actual revenue at this client.
  - If the account has existing CRM engagement history: pull TTM actual revenue from CRM.
  - If no CRM history exists (cold/new pursuit): default to $0. Do not research-guess a TTM figure. State: "No engagement history — Realized revenue defaulted to $0 by definition."
- **Gross Margin factor:** TTM actual gross margin at this client.
  - Same CRM-pull-if-history-exists / default-to-0%-if-cold rule as above.
- **Geography factor:** same flags and same scoring logic as the Potential calculation (geography doesn't change between Potential and Realized — it's a structural fact about the account, not a performance measure).

- Record:
  ```yaml
  realized_inputs:
    crm_engagement_history: true/false
    ttm_revenue: "${X}" or "$0 — no engagement history"
    ttm_gm: "{X}%" or "0% — no engagement history"
  realized_scores:
    geo_raw: {same as potential_scores.geo_raw}
    revenue_raw: {score from revenue band lookup applied to ttm_revenue}
    gm_raw: {score from GM band lookup applied to ttm_gm}
  weighted_potential:
    geo_weighted: "{geo_raw × 0.10}"
    revenue_weighted: "{revenue_raw × 0.70}"
    gm_weighted: "{gm_raw × 0.20}"
    total: "{sum, e.g., 3.1}"
  weighted_realized:
    geo_weighted: "{geo_raw × 0.10}"
    revenue_weighted: "{revenue_raw × 0.70}"
    gm_weighted: "{gm_raw × 0.20}"
    total: "{sum}"
  ```

### 4. Classify the Account 9-Box

- Plot (Realized, Potential) on a -5 to +5 by -5 to +5 grid. Divide each axis into thirds:
  - **Low:** below -1.7
  - **Mid:** -1.7 to +1.7 (inclusive)
  - **High:** above +1.7

- **Grid arrangement (inference — only one confirmed data point available; flag to David to sanity-check on first real use):**

  | Potential \ Realized | Low Realized | Mid Realized | High Realized |
  |---|---|---|---|
  | **High Potential** | SIGNIFICANT | POISED | IDEAL |
  | **Mid Potential** | LIMITED | CORE | SOLID |
  | **Low Potential** | CAPPED | CONSTRAINED | STEADY |

  - Confirmed data point: AT&T — Realized ≈ 0 (Mid band), Potential = 3.1 (High band) → **POISED**. This matches the Mid-Realized/High-Potential cell above, which is the only verified cell in the grid.
  - The remaining eight zone placements (IDEAL, SIGNIFICANT, SOLID, CORE, STEADY, LIMITED, CONSTRAINED, CAPPED) are a reasoned arrangement built around that one confirmed point — not verified against the source. Flag explicitly: "9-box grid arrangement is inferred beyond the single confirmed AT&T/POISED data point. Verify the remaining eight zone placements against the source spreadsheet before treating this as authoritative for other accounts."

- Record:
  ```yaml
  account_9box:
    realized_band: "Low" | "Mid" | "High"
    potential_band: "Low" | "Mid" | "High"
    zone: "{One of the 9 zone names}"
    inference_flag: "Grid arrangement beyond the single AT&T/POISED data point is inferred, not verified — confirm against the source spreadsheet on first real use."
  ```

### 5. Roll up every inference for controller review

- Assemble a single list of every judgment call made in this step, to be carried into step 06's Open Items to Confirm:
  ```yaml
  icp_9box_inferences:
    - "Geography scoring logic (0 baseline, bonus for Y flags) inferred from a single AT&T data point (N/N = 0) — unverified for any account with a 'Y' flag."
    - "9-box grid arrangement inferred beyond the single confirmed AT&T/POISED cell — verify remaining 8 zone placements against the source spreadsheet."
    - "IT services spend sourced via {'public filings/investor materials — {citation}' if Path 1 found a disclosed figure, else 'company-size benchmark ({benchmark used}), Path 1 checked and no usable figure found/not applicable' if Path 2 fallback used} — override if David has better data."
    - "Gross margin default ({default used}) is Improving's typical range, not account-specific confirmed data — override if a better estimate exists."
    - "{Any $1M revenue-band or 20% GM-band boundary ambiguity encountered for this specific account, if applicable.}"
  ```

---

## SUCCESS METRICS

- Potential and Realized scores both computed with full factor-level detail (raw score, weight, weighted contribution) for Geography, Revenue, and Gross Margin
- Weighted formula arithmetic matches the verified AT&T check (0 + 2.1 + 1.0 = 3.1 pattern) — same formula shape applied here
- Revenue and gross margin band lookups applied correctly, with the $1M / 20% boundary ambiguity flagged if a given account's estimate lands near either boundary
- IT services spend not left blank, and sourced in priority order: public filings/investor materials checked first if the target is public, with the fallback company-size-benchmark method (cited benchmark source) used only if the company is private or public with no disclosed figure — the path used and result stated either way
- Gross margin default applied (not left blank) with the default value stated plainly
- Realized inputs pulled from CRM if engagement history exists; defaulted to $0/0% with an explicit "no engagement history" note if not
- 9-box zone assigned using the Realized/Potential grid
- Every inference (geography logic, 9-box arrangement, IT spend estimate, GM default) explicitly flagged for David to verify — none presented as fully confirmed

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Target is public but 10-K/annual report/investor materials don't disclose a usable IT/technology spend figure | This is expected, not a failure — state "Public filings checked, no disclosed IT/technology spend figure found" and proceed directly to the Path 2 benchmark fallback. Do not skip the filings check for a public company just because it's likely to come up empty. |
| Company size (headcount/revenue) not reliably found | State plainly: "Company size unconfirmed — IT spend estimate based on {whatever partial signal exists, e.g., industry-average company size for a firm of this profile}, flagged as lower-confidence." Do not fabricate a precise headcount. |
| Estimated IT spend or GM lands exactly on the $1M / 20% ambiguous boundary | Flag explicitly rather than silently choosing a side: "Estimate lands at the $1M/20% boundary where the source has an unresolved duplicate entry — used {score} as the more conservative reading; verify against the source spreadsheet." |
| CRM inaccessible this session for Realized inputs | State: "CRM not accessible — Realized inputs could not be confirmed. Do not default to $0 in this case (that's reserved for confirmed no-history accounts) — flag as 'unknown, needs CRM check' instead." |
| Account has partial CRM history (e.g., a single small past engagement) | Use whatever TTM actuals CRM shows, even if small — do not treat "some history" the same as "no history requiring a $0 default." |
| Geography flags ambiguous (e.g., delivery lead not yet assigned) | State the ambiguity and use the more conservative (0) baseline rather than guessing a bonus. |
| 9-box zone falls on a genuine band boundary (e.g., Potential = 1.7 exactly) | State which band it was assigned to and note the borderline nature rather than presenting the classification as unambiguous. |

---

## NEXT STEP

Read fully and follow: `step-05-referral-network.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

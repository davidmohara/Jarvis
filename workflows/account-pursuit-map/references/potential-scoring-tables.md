<!-- system:start -->
# Potential Scoring Tables (account-pursuit-map)

Used by step-04 task 2. Apply the lookups and ambiguity flags exactly as written.


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
<!-- system:end -->

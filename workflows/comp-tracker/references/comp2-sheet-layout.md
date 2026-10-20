<!-- system:start -->
## COMP 2 — REGION SHEET LAYOUT

```
Row 1:  Header — "COMPONENT 2: ONE TEXAS REGIONAL GROWTH"
Row 2:  Threshold description
Row 3:  (blank)
Row 4:  B="2025 One Texas Total Revenue"  C=72200000
Row 5:  B="2025 Focused Accounts Baseline" C=14000000
Row 6:  B="6% Growth Target"  C=formula (=C4*1.06)
Row 7:  (blank)
Row 8:  Column headers:
          B = Metric
          C = Jan
          D = Feb
          E = Mar
          F = Apr
          G = May
          H = Jun
          I = Jul
          J = Aug
          K = Sep
          L = Oct
          M = Nov
          N = Dec
          O = YTD Total (formula: =SUM(C9:N9))

Data rows:
  Row 9:  Regional Revenue      ← WRITE TARGET: C9 through N9 (by month)
  Row 10: Regional Cost         ← WRITE TARGET: C10 through N10 (by month)
  Row 11: Regional Gross Profit (formula: =C9-C10 etc — DO NOT WRITE)
  Row 12: Regional GM %         (formula — DO NOT WRITE)
  Row 13: Cumulative Revenue    (formula — DO NOT WRITE)
  Row 14: Cumulative Growth vs 2025 (formula — DO NOT WRITE)

Row 16: BONUS QUALIFICATION header
Row 17: Regional YoY Growth %  (formula — DO NOT WRITE)
Row 18: Weighted Avg Regional GM % (formula — DO NOT WRITE)
Row 19: Bonus Earned (enter amount) — David fills manually
```

**Month → column map:**

| Month | Column | Revenue Cell | Cost Cell |
|-------|--------|-------------|-----------|
| January | C | C9 | C10 |
| February | D | D9 | D10 |
| March | E | E9 | E10 |
| April | F | F9 | F10 |
| May | G | G9 | G10 |
| June | H | H9 | H10 |
| July | I | I9 | I10 |
| August | J | J9 | J10 |
| September | K | K9 | K10 |
| October | L | L9 | L10 |
| November | M | M9 | M10 |
| December | N | N9 | N10 |

**Do NOT write to rows 11–14 or 17–18 — those are formula rows that calculate automatically.**

---

## ROW 14 FORMULA — PRO-RATED GROWTH vs 2025

Row 14 shows "Cumulative Growth vs 2025". The formula must compare the YTD cumulative revenue against a **pro-rated** 2025 baseline (not the full $72.2M annual figure mid-year).

**Correct formula for Row 14 (apply to C14:N14):**
```
=(C13-($C$4*(COLUMN()-2)/12))/($C$4*(COLUMN()-2)/12)
```

Where:
- `C13` = Cumulative Revenue for that month (formula row — auto-calculated)
- `$C$4` = 2025 full-year baseline ($72,200,000)
- `COLUMN()-2` = month number (column C = 3, so 3-2=1 for January; column D = 4, so 4-2=2 for February, etc.)

**If Row 14 shows an incorrect formula** (e.g., compares YTD to full $72.2M annual baseline instead of pro-rated), fix it by writing the correct formula to C14 and dragging/filling across C14:N14.

If the values shown are wildly off (e.g., a January entry near -90%), the formula is comparing to the full annual baseline — fix it.

---
<!-- system:end -->

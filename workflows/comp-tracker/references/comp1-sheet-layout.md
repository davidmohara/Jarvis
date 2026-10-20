<!-- system:start -->
# Comp 1 — BoB Sheet Layout (comp-tracker)


### Section A: Named Account YTD Table (rows 4–25)

```
Row 4 — Column headers:
  B4 = "Named Account"
  C4 = "2024 Revenue"      ← READ ONLY — never write
  D4 = "2025 Revenue"      ← READ ONLY — never write
  E4 = "2026 Target"       ← READ ONLY — never write
  F4 = "2026 Actual YTD"   ← WRITE TARGET A: one YTD total per account
  G4 = "Gross Margin %"    ← WRITE TARGET (if GM% available from Step 2)
  H4 = "YoY Growth %"      ← FORMULA — never write

Named account rows (B = account name, F = YTD write target, G = GM% write target):
  Row 5:  7-Eleven                  → F5, G5
  Row 6:  Charles Schwab & Co       → F6, G6
  Row 7:  McKesson Corporation      → F7, G7
  Row 8:  Wendy's International, LLC→ F8, G8
  Row 9:  Insperity Services, LP    → F9, G9
  Row 10: PriceSmart                → F10, G10
  Row 11: Autodesk, Inc             → F11, G11
  Row 12: Intuit, Inc               → F12, G12
  Row 13: Siemens Industry, Inc.    → F13, G13
  Row 14: ORIX Corporation USA      → F14, G14
  Row 15: AT&T Services, Inc.       → F15, G15
  Row 16: Constellation Energy      → F16, G16
  Row 17: Marriott                  → F17, G17
  Row 18: Kirby Corp                → F18, G18
  Row 19: Expedia                   → F19, G19
  Row 20: Massimo                   → F20, G20
  Row 21: CBRE                      → F21, G21
  Row 22: Tenet                     → F22, G22
  Row 23: Texas Instruments         → F23, G23
  Row 24: Builders First Source     → F24, G24
  Row 25: TOTALS                    → FORMULA ROW — never write (=SUM(F5:F24) etc)
```

### Section B: Monthly Revenue Tracking (rows 28–40)

```
Row 28: Section header "MONTHLY REVENUE TRACKING — BOOK OF BUSINESS"
Row 29: Month headers:
  B29 = "Metric"
  C29 = (blank — skip this column in monthly section)
  D29 = "Jan"   ← January
  E29 = "Feb"   ← February
  F29 = "Mar"   ← March
  G29 = "Apr"   ← April
  H29 = "May"   ← May
  I29 = "Jun"   ← June
  J29 = "Jul"   ← July
  K29 = "Aug"   ← August
  L29 = "Sep"   ← September
  M29 = "Oct"   ← October
  N29 = "Nov"   ← November
  O29 = "Dec"   ← December
  P29 = "YTD Total" ← FORMULA — never write (=SUM(C30:N30))

Row 30: BoB Revenue  ← WRITE TARGET B: monthly total of ALL named account revenue
Row 31: BoB Cost     ← WRITE TARGET B: monthly total of ALL named account cost
Row 32: BoB Gross Profit  ← FORMULA (=C30-C31 etc) — never write
Row 33: BoB Gross Margin % ← FORMULA — never write
Row 34: Cumulative Revenue ← FORMULA — never write
Row 35: Cumulative Growth % ← leave blank (David fills)
Rows 37–40: Bonus Qualification ← formulas or David fills — never write
```

**Monthly column map for Row 30 (BoB Revenue) and Row 31 (BoB Cost):**

| Month | Column | BoB Revenue Cell | BoB Cost Cell |
|-------|--------|-----------------|---------------|
| January | D | D30 | D31 |
| February | E | E30 | E31 |
| March | F | F30 | F31 |
| April | G | G30 | G31 |
| May | H | H30 | H31 |
| June | I | I30 | I31 |
| July | J | J30 | J31 |
| August | K | K30 | K31 |
| September | L | L30 | L31 |
| October | M | M30 | M31 |
| November | N | N30 | N31 |
| December | O | O30 | O31 |

---
<!-- system:end -->

# Relocated content: comp-tracker real run figures

- Origin: workflows/comp-tracker/steps/step-04-extract-update-comp2.md (example block, lines ~197-210) and step-01-extract-powerbi-revenue.md (data-format example, lines ~192-199)
- Date: 2026-10-10
- Reason: Phase A cleanup. Real 2026 revenue/GP figures were pasted into instruction files as worked examples, contradicting the files' own "never hardcode" rules. Replaced in-file with generic placeholders; actual values preserved here for reference.

## Comp 2 monthly figures (One Texas, from the 2026-04-22 PowerBI read)

```
2026, January:  Austin $1,456,127 + Dallas $2,748,530 + Houston $1,235,959 = $5,440,616 revenue
                Austin GP $507,138 + Dallas GP $1,021,161 + Houston GP $557,515 = $2,085,814 GP
                Cost = $5,440,616 - $2,085,814 = $3,354,802

2026, February: Austin $1,366,394 + Dallas $2,911,328 + Houston $1,167,126 = $5,444,848 revenue
                Austin GP $448,921 + Dallas GP $1,126,638 + Houston GP $490,743 = $2,066,302 GP
                Cost = $5,444,848 - $2,066,302 = $3,378,546

2026, March:    Austin $1,521,899 + Dallas $3,074,539 + Houston $1,268,871 = $5,865,309 revenue
                Austin GP $425,116 + Dallas GP $964,262 + Houston GP $510,519 = $1,899,897 GP
                Cost = $5,865,309 - $1,899,897 = $3,965,412
```

Row 14 (Cumulative Growth vs pro-rated 2025) confirmed values with the pro-rated formula (2026-04-22):
- C14 (Jan): -9.6%
- D14 (Feb): -9.5%
- E14 (Mar): -7.2%

## Customer Distribution data-format example (2026)

```
Customer Name    Dallas
MasterCard       $1,864,184
Wendy's International, LLC  $1,131,915
```

# Success-Rate Recompute

**Date:** 2026-10-26 · **Source:** all eval records in `systems/eval-harness/runs/eval-*.json` · **CSV:** `success-rate-recompute-2026-10-26.csv` (same folder) · **Reproduce:** `python3 systems/eval-harness/success-rate.py`

## Metric definition (unchanged from the 2026-10-08 baseline)

- **strict** = record status `success` or `complete`
- **mech** = strict + `partial` (finished every step with degraded output)
- session-exit aborts (`abort_reason == 'session-exit-normal'`) are excluded from the mech denominator and counted separately
- **instrumented** = at least one step with real token attribution

## Results

| Workflow | Scope | Records | Strict | Degraded | Session-exit | Other | Mech rate | Strict rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| boot | all-records | 64 | 21 | 11 | 5 | 27 | 54.2% | 32.8% |
| boot | instrumented | 18 | 6 | 6 | 1 | 5 | 70.6% | 33.3% |
| morning-briefing | all-records | 23 | 8 | 14 | 0 | 1 | 95.7% | 34.8% |
| morning-briefing | instrumented | 2 | 2 | 0 | 0 | 0 | 100.0% | 100.0% |
| daily-review | all-records | 64 | 48 | 13 | 2 | 1 | 98.4% | 75.0% |
| daily-review | instrumented | 2 | 2 | 0 | 0 | 0 | 100.0% | 100.0% |
| plaud-ingest | all-records | 36 | 16 | 1 | 2 | 17 | 50.0% | 44.4% |
| plaud-ingest | instrumented | 4 | 2 | 0 | 1 | 1 | 66.7% | 50.0% |

## The "other" tier, characterized (no hiding in a bucket)

**boot (27):** 8 `aborted` with reason `session-ended` (the same class as session-exit aborts, recorded under a different reason string; not silently re-tiered), 6 `aborted/unspecified`, 8 `aborted` with no reason recorded, 4 `failure`, 1 in-progress at read time.

**plaud-ingest (17):** 11 `aborted` with no reason recorded — the previously flagged unexplained aborts, still consistent with no-op runs when nothing new is staged but still unverified; 2 `failure`; 4 closed as distinct **`no-op`** terminal status (the close-out path now distinguishes no-ops from failures, so this class stops polluting the abort bucket going forward).

**morning-briefing (1), daily-review (1):** single `incomplete`/failure records, no pattern.

## Honest readings

- The instrumented scope is the defensible headline (real token attribution per step) but its n is thin: 2 (daily-review, morning-briefing), 4 (plaud-ingest), 18 (boot). Treat instrumented percentages as directional until more instrumented runs accumulate; the all-records tiers remain the statistically meaningful rows.
- The plaud-ingest 11 unexplained aborts remain the one outstanding characterization item. A verified no-op explanation would move the all-records mech rate from 50.0% to 62.1% (16/26); the honest current figure is 50.0%.
- boot's degraded tier is substantial (11 of 64): the workflow finishes but with data-source gaps. Strict 32.8% all-records reflects that boot depends on the most data sources.

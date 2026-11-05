# Boot Workflow Token and Timing Review

Window: 2026-10-15 to 2026-11-05 (21 days). Source: `systems/eval-harness/runs/` workflow-level eval records for the boot workflow. Generated 2026-11-05 by Rigby (read-only analysis; no grading).

Boot did not run daily. Workflow-level boot records exist for 13 of 21 days (weekdays only; no records for 10-15, 10-16, or weekends). Several days have multiple records: retries and aborted attempts in separate sessions produce one eval record each. 27 workflow-level records total. Step columns use workflow step ids (01 through 08, including the .2/.5 substeps). Cell values are total tokens (input + output); "?" means the harness holds no attribution for that step, "-" means the step was not recorded in that run, "0" means the attribution window matched zero tokens (an attribution miss, not a free step).

## Run table

| Date | Run | Sess | Status | Dur | Run total (in/out) | 01 | 01.2 | 01.5 | 02 | 02.5 | 03 | 04 | 04.5 | 05 | 06 | 06.5 | 07 | 08 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10-19 | IA1AX8 | 1466 | success | 61m | 17.0M/87k | - | 5.3M | 5.3M | 420k | 420k | 420k | 2.7M | - | 420k | 420k | 420k | 420k | 420k |
| 10-20 | J42OVZ | 1466 | aborted | 122m | ? | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-21 | QNQLC5 | 345c | success | 28m | 2.5M/9k | ? | 83k | 0 | 546k | - | 496k | 533k | - | 0 | 0 | - | 0 | 0 |
| 10-22 | 7OUMW0 | 283f | incomplete | ? | ? | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-22 | IP36P9 | 7608 | partial | 5m | 4.5M/31k | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-22 | TPZO43 | 599c | incomplete | ? | ? | ? | ? | ? | - | - | - | - | - | - | - | - | - | - |
| 10-22 | 5C4OEY | 599c | aborted | 213m | ? | - | ? | - | ? | - | ? | ? | - | ? | ? | - | ? | ? |
| 10-23 | QQIZKW | f430 | partial | 36m | 5.9M/66k | - | 301k | 212k | 156k | - | 80k | 164k | - | 641k | 78k | - | 0 | 830k |
| 10-23 | L9PFZ9 | 348d | aborted | 124m | 226.2M/1.2M | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-26 | O84R10 | 2872 | partial | 19m | 12.2M/142k | ? | 79k | 845k | 469k | - | 83k | 333k | 4.7M | 0 | 0 | - | 0 | 0 |
| 10-26 | B7W765 | 2872 | incomplete | ? | ? | ? | 573k | 845k | 888k | - | 251k | 333k | 91k | 376k | ? | - | ? | ? |
| 10-26 | VXWWK6 | 64d0 | aborted | 151m | 634k/8k | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-26 | NMXCZV | 7de1 | incomplete | ? | ? | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-27 | Q0REQ2 | c7f0 | incomplete | ? | ? | 950k | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-27 | YB6YAM | c7f0 | success | 0m | ? | - | - | - | - | - | - | - | - | - | - | - | ? | ? |
| 10-28 | 26QC3W | 98fa | incomplete | ? | ? | 733k | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-28 | BK458M | 25d0 | aborted | 129m | 1.1M/7k | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-29 | ZUIMG1 | 46bc | incomplete | ? | ? | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 10-29 | QUYFPJ | e8a3 | success | 12m | 11.6M/80k | 577k | 156k | 227k | 1.1M | - | 367k | ? | - | - | - | - | - | - |
| 10-30 | G668EK | e826 | success | 14m | 8.2M/91k | 221k | 953k | 678k | 307k | - | 73k | 612k | - | 1.2M | 158k | - | 861k | 271k |
| 10-30 | Y5F720 | e826 | aborted | 2963m | ? | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 11-02 | P6CA3U | 9b79 | partial | 16m | 8.8M/113k | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 11-03 | HYT8JX | c320 | partial | 14m | 7.8M/94k | 452k | 1.3M | 1.2M | 1.4M | - | 96k | ? | - | - | - | - | - | - |
| 11-03 | 863SNK | c320 | failure | ? | ? | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 11-03 | DTTVF0 | c320 | aborted | 50m | ? | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 11-04 | 019TAZ | 5011 | partial | 22m | 29.6M/133k | 521k | 158k | 78k | 163k | - | 83k | ? | - | 1.9M | 1.9M | - | 1.9M | 1.9M |

## Attribution coverage notes

Per-step token attribution is missing or unreliable for most runs. Of 27 records, 14 hold no run-level token totals at all (aborted/incomplete/failure records), and only 9 hold any per-step numbers. Specific gaps:

- **step-04-gather-meeting-context** is unattributed ("?") in 4 of the 6 recent runs that otherwise have step data (10-29, 11-03, 11-04, and 10-22 5C4OEY). This is the single most consistent per-step gap.
- **step-01-load-context** is unattributed or "stale-window" in the 10-21, 10-22, and 10-26 records.
- **10-19 (IA1AX8)**: every step used `lenient_fallback` and shows flat duplicated values (418,613 tokens assigned identically to 8 steps; 5,249,805 to 2 steps). These are shares of a total, not measured per-step usage. Treat the whole per-step row as unreliable.
- **Zeros** (10-21 steps 01.5/05/06/07/08; 10-26 O84R10 steps 05-08; 10-23 step-07): `windowed-partition` matched zero tokens to steps that demonstrably ran (they have durations and complete status). Zeros are attribution misses.
- **11-04 (019TAZ)**: steps 05-08 each carry the identical 1,875,532 in / 5,827 out and durations of ~191,500s (~53 hours) against a 22-minute run. The window attribution is corrupted for the back half of this run; only the run-level total is trustworthy.
- **10-30 (G668EK)** has the cleanest full per-step coverage, but every step duration is an identical 83.1s (an even split of the 831s run), so step timing there is allocated, not measured. Token values do vary per step and look plausible.
- Runs with zero recorded steps but valid run-level totals (IP36P9, P6CA3U, L9PFZ9, VXWWK6, BK458M): the harness captured cost but never wrote step records.

## Summary

- **Volume and trend**: 13 records carry run-level totals. Median run is ~8.0M input tokens (excluding the outlier below). The lightest full run was 10-21 at 2.5M; late-window runs trend heavier: 11.6M (10-29), 8.2M (10-30), 8.8M (11-02), 7.8M (11-03), 29.6M (11-04). Output tokens are consistently tiny (~1% of input), so input/context volume is the entire cost story.
- **Dominant steps** (from the runs with credible attribution, chiefly 10-30 G668EK and 11-03 HYT8JX): step-05-synthesize-briefing leads on 10-30 (1.2M), followed by step-01.2-unified-data-pull (~1.0-1.3M on both days), step-01.5-calendar-pull (0.7-1.2M), and step-02-gather-data (0.3-1.4M). On 10-26 the step-04.5 watchtower handoff took 4.7M, the largest single-step attribution in the window. Steps 03 and 06 are consistently cheap (<400k).
- **Anomalies**: the aborted 10-23 run (L9PFZ9) recorded 226.2M input / 1.23M output tokens, roughly 28x the median run, with no step records to explain it. The 10-30 aborted duplicate (Y5F720) shows a 2,963-minute duration, a record left open for two days before close-out. 10-27's "success" (YB6YAM) is a 22-second run covering only steps 07-08, a completion-check pass, not a real boot.
- **Outcome mix**: 4 genuine full successes (10-19, 10-21, 10-29, 10-30), 6 partial, 8 incomplete, 6 aborted, 1 failure, plus the nominal 22s success on 10-27. Retry stacking is common: 10-22, 10-26, 10-27, 10-30, and 11-03 each burned two to four sessions to get one boot through.

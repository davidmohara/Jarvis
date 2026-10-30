---
type: working-archive
task_id: "session"
session_id: "master-2026-10-26-150000"
agent-source: master
created: 2026-10-26T15:00:00-05:00
expires: 2026-10-28T15:00:00-05:00
status: archived
context: "Boot token performance analysis updated with the 2026-10-26 run — 2026-10-26"
date: 2026-10-26
source_file: memory/working/2026-10-26-boot-token-analysis.md
tags:
  - master
  - briefing
  - calendar
  - omnifocus
  - plaud
  - boot
  - rigby
  - knox
related_people:
salience:
  score: 10
  last-promoted-check: 2026-10-30
  promoted: true
---

# Boot Token Performance Analysis — 2026-10-26 (supersedes 2026-10-23 note)

## What was requested and produced

David asked for the boot token comparison table across recent runs (memory note: `memory/working/2026-10-23-091858-master-boot-token-analysis.md`, which pre-committed to expanding after the 10/26 and 10/27 boots). Delivered via a read-only eval-harness analysis subagent (111K tokens); tables and findings below. All five fixes routed to Rigby on 2026-10-26.

## Aggregate comparison

Only 10/23 and 10/26 are like-for-like (master own ~15% both runs). 10/13 (88% unattributed) and 10/19 (98% unattributed) are not usable as boot-cost baselines; 10/21 and 10/22 structurally understate (master own = 0). Dollar costs not comparable: same model priced ~$0.54/M on 10/23 vs ~$0.06/M on 10/26 (pricing/routing change, not efficiency).

| Date | Input | Output | Status | Attribution |
|---|---|---|---|---|
| 10/13 | 11.77M | 72.6K | success | poor (lenient_fallback) |
| 10/19 | 16.95M | 87.1K | success | poor (lenient_fallback) |
| 10/21 | 2.54M | 9.2K | success | partial, understated |
| 10/22 | 4.47M | 31.3K | partial | none |
| 10/23 | 5.87M | 66.2K | partial | good, first fully-attributed |
| 10/26 | 12.21M | 141.7K | partial | mixed, timestamps broke it |

## Per-step, 10/23 vs 10/26 (eval-record basis, authoritative; harness task notifications are turn-end context size, not spend)

| Step | 10/23 in / out | 10/26 in / out | Δ input |
|---|---|---|---|
| 01.5 calendar | 372K / 7.4K | 1,141K / 25.5K | +207% |
| 01.2 data pull | 591K / 11.1K | 565K / 9.2K | −4% |
| 02 gather | 586K / 8.1K | 1,027K / 17.1K | +75% |
| 03 verify | 347K / 3.9K | 273K / 1.5K | −21% |
| 04 meeting ctx | 656K / 5.0K | 1,098K / 10.6K | +67% |
| 04.5 + 05-08 briefing | 1,529K / 20.1K | 4,646K / 59.6K | +204% |
| Knox no-op ingest | 817K / 8.8K | 1,651K / 13.8K | +102% |
| Master own | 912K / 1.8K | 1,805K / 4.3K | +98% |
| Total | 5.87M / 66.2K | 12.21M / 141.7K | +108% |

Wall clock halved (2,167s → 1,142s). Two regressed targets: briefing block now 38% of run (04.5 merged into the 05-08 agent); Knox no-op at ~24 turns for a zero-recording outcome.

## Root causes

1. **Fabricated step timestamps**: every 10/26 step file stamped with invented round-minute times (05-08 stamped 22 min after boot ended). Eval harness derives attribution windows from these stamps — this collapsed 10/26 attribution and null'd step-01.
2. **Stale state.yaml carry-over**: `phase2-2026-10-23-superseded` block (7KB, 28% of accumulated-context) plus duplicate prior-run/phase1 keys survived the "discarded" claim.
3. **Watchtower daily run unmeasured**: no eval record; guardrail passes on the spawn, not the result; its 14:32-14:52 run sits outside the 12.2M total.
4. Step-level rows on 10/26 must not be summed (repeat and >100% windows on XKL3HO/UMLAM9/V42X7P).

## Routed to Rigby (2026-10-26)

1. Real timestamp stamping + verifier rejects future stamps
2. Split step-04.5 back out of the briefing agent (tighten workflow.md 05-08 dispatch wording)
3. Eval record for watchtower daily
4. Purge superseded state.yaml block + fix the discard mechanism
5. Knox single-turn no-op preflight before persona/vault walk

## Follow-up

- Reminder rem-20261023T141926-H6H5JB still surfaces at the 2026-10-28 boot for the expanded analysis; Tuesday 10/27 boot gives the second fully-attributed data point post-fix.
- 10/26 eval records: master O84R10; steps DBUNBC (01.5), 1JQI7K (01.2), XKL3HO (02), UMLAM9 (03), V42X7P (04), LHF7TO (04.5-08 merged), VKOMMT (Knox); Knox no-op ES64TT, plaud-discover CV37G4.

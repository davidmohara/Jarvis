---
type: semantic-pattern
domain: operational
tags:
- pipeline-review
confidence: medium
created: '2026-06-18'
last-updated: 2026-09-03
synthesized-from:
  - memory/episodic/co-sell-pipeline-2026-08-24-001532.md
- co-sell-pipeline-2026-06-15-143245.md
  - memory/episodic/co-sell-pipeline-20260629-001245.md
synthesized-from:
  - memory/episodic/morning-briefing-2026-06-11-062152.md
  - memory/episodic/dream-summary-2026-06-12.md
  - memory/episodic/co-sell-pipeline-2026-09-17-184500.md
  - memory/episodic/pipeline-snapshot-2026-09-17-184500.md
last-updated: 2026-09-20
---
## Pattern Summary

Recurring `pipeline-review` activity observed in episodic memory.

## Evidence

- 2026-08-27 | co-sell-pipeline-2026-08-24-001532.md | tags: pipeline-review, chase, omnifocus, rock4, quarterly-rocks, one-texas, revenue, pipeline, co-sell | score: 10

- 2026-07-02 | co-sell-pipeline-20260629-001245.md | tags: pipeline-review, chase, omnifocus, one-texas, pipeline, co-sell | score: 10
### 2026-06-18 run
- [2026-06-15] `co-sell-pipeline-2026-06-15-143245.md` (score:6)
- memory/episodic/morning-briefing-2026-06-11-062152.md (score 10)
- memory/episodic/dream-summary-2026-06-12.md (score 10)
- 2026-06-25: memory/episodic/co-sell-pipeline-2026-06-15-143245.md (tags: pipeline-review, chase, pipeline, rock)
- 2026-06-25: memory/episodic/morning-briefing-2026-06-11-062152.md (tags: briefing, chief, dream-summary, pipeline-review, revenue-tracker)
- 2026-06-25: memory/episodic/dream-summary-2026-06-12.md (tags: dream-summary, jarvis, daily-review, pipeline-review, plaud-ingest)

## Implications

- 2026-08-27: 1 entries reinforce relevance of `pipeline-review` cluster (Rock 4 co-sell snapshot, $8.49M gap, 56.6% uncovered). Confidence held at medium (unchanged) — one new entry doesn't clear the bar for escalation.

### 2026-09-03 — Nightly promotion
Sources this cycle:
- `memory/episodic/co-sell-pipeline-2026-08-31-001500.md` (score 5) — tags: pipeline-review, chase, co-sell, pipeline, rock4, scorecard. Aug 31 AM snapshot claimed Rock 4 CLOSED at $20.43M combined (136.2% of $15M target). Same-day PM correction run (see co-sell-pattern.md) found this figure was fabricated — live PowerBI won revenue was $3.42M/7 opps, not $17.34M/76 opps as reported. Gap actually $8.49M remaining (56.6%), not closed.

Notable: this is the first entry in this cluster where the AM and PM snapshots of the same day directly contradict each other, with the AM figure confirmed fabricated rather than stale or miscached. Cross-reference co-sell-pattern.md's 2026-09-03 entry for the correction-run details and the root-cause fix (hard-fail gate when Chrome MCP is unavailable). Confidence held at medium — one contradicted entry doesn't by itself change the cluster's confidence, but it's a data-integrity flag worth carrying forward.

### 2026-09-10 — Nightly promotion
Sources this cycle:
- `memory/episodic/co-sell-pipeline-2026-09-07-000000.md` (score 9) — tags: pipeline-review, chase, co-sell, pipeline, revenue, rock4, leads. Sept 7 Rock 4 co-sell snapshot: $8.57M remaining of $15M target (57.2% gap), combined progress $6.43M (43%). Houston leading on conversion (67% of won revenue, $3.07M) but thin on pipeline generation (only 31%, $565K). Dallas stalled — $1.22M pipeline but won conversion flat at $1.51M, momentum lost post-close. Austin dormant — 8 opps, $50K pipeline, $0 won. Total pipeline ($1.84M) dangerously thin against the $15M target; trajectory estimate ~$6-7M by Q2 end, 14% gap-closure probability without partner acceleration.

Consistent with the fabricated-figure correction this cluster tracked on 09-03 — no repeat of that failure mode here, this snapshot reads as a straightforward (if concerning) live pull. Confidence held at medium — the Dallas-stalled and Austin-dormant findings are new operational detail worth watching for whether either moves next cycle, not yet enough evidence on their own to escalate.
- 2026-07-02: 1 entries reinforce relevance of `pipeline-review` cluster. Watch for further co-occurrence.
- 2026-06-24: New episodic cluster (pipeline-review, 2 entries) reinforces pattern.
_TBD — pattern just emerged. Watch for stability over the next 2-3 dream cycles before drawing conclusions._

### 2026-09-20 — Nightly promotion
Sources this cycle:
- `memory/episodic/co-sell-pipeline-2026-09-17-184500.md` (score 10) — tags: pipeline-review, chase, rock4, pipeline, co-sell. Sept 17 live PowerBI pull (data updated 9/16/26): co-sell pipeline Dallas $1.32M/8 opps, Houston $565K/3, Austin $50K/1 = $1.94M/12 combined. Won co-sell: Dallas $1.52M/3, Houston $3.07M/5, Austin $0 = $4.59M/8. Rock 4 progress: $6.53M combined vs. $15M target — gap $8.47M (56.5% remaining), essentially flat against the 09-07 reading ($8.57M/57.2% gap). Dallas partner mix: Confluent $785.6K/2, Microsoft $373.95K/4, SAP $298.75K/2, Scrum.org $43K/1.
- `memory/episodic/pipeline-snapshot-2026-09-17-184500.md` (score 7) — tags: pipeline-review, chase, pipeline. Same-date live pull: total pipeline Dallas $43.15M/90 opps, South Texas $24.11M/74 (Austin $13.75M/40, Houston $10.36M/34). 90-day weighted: Dallas $13M/73, South Texas ~$6M (Austin $3M/33, Houston $3M/24).

Rock 4's $8.47M gap has held essentially flat for six weeks (09-07: $8.57M, now $8.47M) — a $100K move, not meaningful progress at the current pace against a $15M target. The pipeline-snapshot entry adds new context this cluster hasn't carried before: total (non-co-sell) pipeline is nearly 6x the co-sell figure ($67M combined Dallas+South Texas vs. $1.94M co-sell), and 90-day weighted pipeline ($13M Dallas, ~$6M South Texas) dwarfs the co-sell-specific weighted numbers — confirming Rock 4's gap is a co-sell-channel-specific shortfall, not a general pipeline-generation problem. Held confidence at medium; the flat six-week gap is worth flagging as a stall risk if it doesn't move by the next full co-sell snapshot.

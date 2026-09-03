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
- 2026-07-02: 1 entries reinforce relevance of `pipeline-review` cluster. Watch for further co-occurrence.
- 2026-06-24: New episodic cluster (pipeline-review, 2 entries) reinforces pattern.
_TBD — pattern just emerged. Watch for stability over the next 2-3 dream cycles before drawing conclusions._

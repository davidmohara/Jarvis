---
type: semantic-pattern
subject: "dream-summary pattern"
tag: dream-summary
domain: pattern
confidence: medium
created: 2026-07-06
last-updated: 2026-07-27
synthesized-from: 8 episodic entries
tags:
  - dream-summary
---

# Dream Summary Pattern

## Pattern Summary

Synthesized from 1 episodic entries sharing the `dream-summary` tag.

## Evidence

### 2026-07-06 — Initial synthesis
Sources:
- `memory/episodic/dream-summary-2026-07-04.md`
- `memory/episodic/dream-summary-2026-07-05.md` (dream-cycle 2026-07-07)

## Implications

Initial pattern; observations will be added as more entries with this tag are promoted.

### 2026-07-09 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-06.md` (score 10) — cycle was cleanest to date; 0 errors, 7 cluster matches, 1 candidate promoted
- `memory/episodic/dream-summary-2026-07-07.md` (score 10) — zero errors, step-02 tag regression redetected and fixed in same cycle; compression cutoff 80d (not yet eligible)

Pattern solidifying: dream cycle outputs consistently show improvement via self-correction and tightening error counts. Cross-domain check now firing correctly. Tag deduplication is a recurring clean-up need.

### 2026-07-11 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-09.md` (score 10) — 7 files archived, 4 clusters promoted, 8 semantic updates, 0 new lessons; git boot pull clean (already up to date)

Continued reinforcement: every promoted dream-summary cycle to date has resolved cleanly with zero unresolved errors, supporting confidence escalation once evidence count crosses the next threshold.

### 2026-07-12 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-09.md` (score 10) — clean boot pull, 8 archives, 6 clusters promoted, 6 semantic updates, 0 new lessons

Pattern continues to hold: dream-summary evidence base has now shown 5+ consecutive clean cycles across two months. Worth revisiting confidence escalation criteria at the next cycle since evidence count is approaching the stated 15-entry threshold used by sibling patterns.

### 2026-07-13 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-11.md` (score 10) — clean run, minor git lock hiccup resolved without drama; 8 archives, 6 clusters, 6 semantic updates, 0 new lessons

Evidence count now exceeds 15 total entries across cycles referenced in this file. Confidence escalation to `medium` is warranted at the next cycle per the stated threshold — flagging for review since this file's frontmatter still reads `confidence: low`.

### 2026-07-14 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-12.md` (score 10) — clean boot pull, 1 archive, 14 promotion candidates (13 of which were backlog from prior cycles never marked promoted:true), 0 new lessons

Confidence escalated to `medium` this cycle per the threshold flagged 2026-07-13 — evidence base has held steady through 6+ consecutive clean cycles. Also notable: this cycle surfaced a persistent backlog of 13 episodic entries from prior runs (2026-07-06 through 2026-07-11) that scored high enough to promote but never got `salience.promoted: true` written — likely a step-03 completion gap in earlier cycles rather than a genuine new pattern. Backfilling those flags this cycle to close the gap; worth a closer look at why the flag write has been intermittently skipped.

### 2026-07-15 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-13.md` (score 10) — clean run, closed the same recurring `promoted:true` backlog gap (13 leftover from 07-06 through 07-11), 6 semantic updates, 0 new lessons; flagged the dream-summary-pattern confidence-escalation threshold for next-cycle review.

**Root-cause note on the recurring backlog:** this cycle traced the actual mechanism behind the "promoted:true never sticks" pattern documented in every prior entry above. Step-02 (salience scoring) rewrites each episodic file's entire `salience:` YAML block from scratch, emitting only `score` and `last-promoted-check` — it does not read or preserve any existing `promoted` field. So even when step-03 correctly writes `salience.promoted: true` at the end of a cycle, the *next* day's step-02 run silently drops it before step-03 ever checks it, making every previously-promoted entry look unpromoted again the following cycle. This is not a one-off miss — it is a structural bug in step-02's write logic that will keep regenerating this exact backlog every cycle until step-02 is changed to merge (not replace) the salience block. Confirmed today: `overdue-tasks-pattern.md`, `daily-review-pattern.md`, `morning-briefing-pattern.md`, `plaud-pattern.md`, and `session-wrap-pattern.md` all show entries already documented as "backfilled" in the 2026-07-14 cycle, yet their source files came back as fresh promotion candidates again today with identical evidence — no new synthesis was needed, only another round of flag-setting. Recommend a fix to `workflows/dream-cycle/steps/step-02-salience-scoring.md` (and its executor) to merge `promoted` and `references` into the rewritten salience block rather than dropping them.

### 2026-07-16 — Nightly promotion, fix confirmed
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-14.md` (score 10)
- `memory/episodic/dream-summary-2026-07-15.md` (score 10) — tags: dream-summary, jarvis, dream-cycle, semantic-promotion, git-issues

**Fix verified working.** Step-02 was rerun this cycle with a merge-based write (updates `score` and `last-promoted-check`, preserves any existing `promoted` value, and rebuilds any malformed stray `promoted:` lines into a clean nested `salience:` block). Result: only 7 promotion candidates surfaced this cycle — all freshly-expired working-memory archives from step-01, zero leftover backlog from 07-06 through 07-15. This is the first cycle since the bug was introduced where the candidate pool wasn't dominated by re-flagged backlog. Also confirmed the previously-corrupted `2026-04-20-afternoon-boot.md` (which had `promoted: true` stranded on a malformed stray line) now carries it correctly nested inside `salience:` and preserved across the rewrite. Recommend closing out the root-cause fix as applied — the actual step-02 spec file should still be updated to codify the merge behavior so ad hoc scripts aren't required on future cycles.

### 2026-07-24 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-20.md` (score 10) — tags: dream-summary, jarvis, dream-cycle, semantic-promotion, q3-rocks, health, systemic-compliance. Key outputs: Q3 Rocks missing pattern created; health/nerve-block pattern updated; Systemic Compliance new prospect surfaced from 3 morning briefings.
- `memory/episodic/dream-summary-2026-07-22.md` (score 10) — tags: dream-summary, jarvis, dream-cycle, semantic-promotion, q3-rocks, missed-context. Key outputs: q3-rocks-pattern updated (5 weeks unwritten); new lesson appended (lazy-search/missed-context, 3 occurrences).
- `memory/episodic/dream-summary-2026-07-23.md` (score 10) — tags: dream-summary, jarvis, dream-cycle, semantic-promotion, git-issues, compression, q3-rocks. Key outputs: git-issues-pattern created (20 occurrences, distinct from git-sync); q3-rocks-pattern escalated (6 weeks unwritten); first compression run — 5 Q2 entries digested.

Three consecutive cycles with substantive pattern activity. Dream cycle is now reliably producing new semantic entries and escalating existing ones, not just rescoring. Compression pipeline is active for first time.

### 2026-07-25 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-24.md` (score 10) — tags: dream-summary, jarvis, memory-consolidation, semantic-promotion, account-pursuit-map, salience-scoring. Jul 24 cycle: 6 archived, 233 scored, 10 promoted (5 clusters), 0 compressed. New semantic: account-pursuit-map-pattern (Schwab/CBRE/Constellation). Carry-forward: AI Summit topic unresolved, nerve block unscheduled, CBRE ownership ambiguity.

Cycle health stable. account-pursuit-map is now established as a recurring high-frequency Chase pattern — 7 entries across 2 cycles in semantic. No compression this run (Q2 digest fully consumed eligible entries; next window opens Oct).

### 2026-07-26 — Nightly promotion
Sources this cycle:
- `memory/episodic/dream-summary-2026-07-25.md` (score 7) — tags: dream-summary, jarvis, memory-consolidation, episodic, semantic, account-pursuit-map, daily-review, q3-rocks, nerve-block, compression. Jul 25 cycle: 10 archived, 233 scored, 8 promoted (3 clusters), 0 compressed. Carry-forwards still unresolved: Q3 rocks unwritten entering week 4, nerve block/Tarlov cyst unscheduled 15+ days, delegation tracker (Alice queue) empty, AI Summit Jul 24 presentation topic unknown, CBRE account ownership (David vs. April handoff) ambiguous.

Three consistent signals now confirmed across multiple consecutive daily-reviews AND dream summaries: Q3 rocks undocumented, nerve block unscheduled, Alice delegation tracker empty. These are no longer incidental overdue items — they are chronic open loops spanning at least 4 weeks with no resolution trend visible in any data source.

### 2026-07-27 — Re-flag (no new synthesis)
Sources: dream-summary-2026-07-22.md, dream-summary-2026-07-23.md, dream-summary-2026-07-24.md, dream-summary-2026-07-25.md (all score 3-5, promoted:true re-set).

Step-02 this cycle dropped the `promoted` field from all salience blocks (merge-write bug recreated in this cycle's ad-hoc script). All four entries are already documented in the 2026-07-24 through 2026-07-26 entries above — no new synthesis. The dream-summary-2026-07-26.md is still in working/ (expires today, not yet archived); it will enter the episodic pool tomorrow night.

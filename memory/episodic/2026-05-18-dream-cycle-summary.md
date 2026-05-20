---
type: working-archive
expires: 2026-05-19
status: archived
salience:
  score: 0
  references: []
  last-promoted-check: 2026-05-20
  promoted: false
---
# Dream Cycle Summary — 2026-05-18

**Session:** dream-cycle-2026-05-18-030847

## What happened

Archived 7 expired working memory entries to episodic — the May 8 briefing, May 12-15 briefings, May 15 wrap, and the May 16 dream summary. Of those 7, only 2 had tag metadata populated. The May 15 manual morning briefing scored 10 on the salience pass and promoted into the existing `briefing-travel-calendar-pattern` semantic entry, taking it to 22 evidence sources and 33 implications at high confidence. The other newly archived files scored 0 — same automated-boot tag-schema gap flagged on May 13.

Score distribution across 54 episodic entries: 0:18, 1:3, 7:1, 10:32. The 32-at-cap saturation is the 22nd consecutive run with this pattern. Score-algorithm fix has been deferred for 14 consecutive runs.

Error log scan found three categories at threshold over the last 30 days: process-skip/protocol-skip (6 occurrences), data-accuracy/stale-cache (5), and assumption-error/wrong-assumption (3). All three patterns are already in LESSONS.md as April 18 entries. No new lessons appended.

Compression skipped — oldest episodic entry is 30 days old, cutoff is 90.

## System notes

**Git sync succeeded today.** First clean sync in 21 consecutive runs. Working tree is clean. The chronic unstaged-changes block has cleared, suggesting someone (David or Cowork itself) processed the backlog between yesterday's run and today.

**Filesystem deletion remains blocked.** All 7 source files in `memory/working/` were marked `status: archived` rather than deleted because the sandbox blocks file deletion in that directory. Copies are in `memory/episodic/`. This is the 22nd consecutive run with this limitation. The orphaned files don't cause correctness problems (they get skipped on subsequent runs) but they accumulate.

**Automated-boot tag-schema gap persists.** Of the 7 working files archived this run, 5 had no `tags` field — the automated boot path is still writing untagged frontmatter. The manual May 15 boot has tags and scored 10. Until the automated template is fixed, every scheduled run produces an entry invisible to salience scoring.

**Pattern signal is degrading.** The single new promoted entry is the smallest cluster contribution since pattern inception. The briefing-travel-calendar pattern incorporated 16 sources from April 20 to May 5, then 5 sources through May 13, and just 1 source over the past 5 days. The pattern is correct and rich but the input stream has narrowed to roughly one manual boot per week.

## Recommendation

Three open improvements continue to accumulate cost:

1. **Fix the automated-boot tag schema.** Update the automated briefing template to populate `tags` from the same dimensions the manual boot uses (calendar themes, OmniFocus categories, travel state). Without this the pattern stops growing.
2. **Recalibrate salience scoring.** 14-run-deferred problem. The cap-at-10 saturation makes the score signal useless for differentiation among the high-tag entries.
3. **Backfill or reset orphaned working-memory files.** 39 already-archived files sit in `memory/working/`. They're skipped correctly but represent operational debt. Either get the deletion path working or build a sweep skill that ignores them more efficiently.

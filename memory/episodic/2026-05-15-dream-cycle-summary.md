---
type: working-archive
expires: 2026-05-16
status: archived
date: 2026-05-15
tags:
- dream-cycle
- meta
salience:
  score: 0
  last-promoted-check: '2026-05-17'
---

# Dream Cycle Summary — 2026-05-15

Clean run with one structural issue worth surfacing. Archived two expired working entries to episodic (dream-summary-2026-05-13 and the May 12 automated morning briefing). Scored 44 episodic entries — the salience distribution is unchanged from the prior 18 runs (9 at score 0, 3 at score 1, 1 at score 7, 31 at the score-10 ceiling). Score inflation has now persisted across 19 consecutive runs without intervention.

No semantic promotion candidates this run. Every entry that meets the score-3 threshold already has `promoted: true` from prior cycles, so the cluster pass produces nothing. Error log scan over the last 30 days returned only 4 entries (wrong-assumption x2, data-accuracy x1, routing-error x1) — none of them meet the 3+ threshold for adding a new LESSONS.md pattern. Compression remained skipped because the oldest episodic entry is 27 days old; the workflow doesn't compress under 90 days.

Three issues continue to compound and need a live session to resolve:

1. **Score inflation algorithm.** The 2-tag/30-day co-occurrence rule auto-promotes nearly every briefing-tagged entry to the maximum. Semantic output is mechanically valid but informationally null. This is now deferred 8 consecutive runs and is the single largest blocker on memory system utility.

2. **Git sync blocked, 19th consecutive run.** `git pull --rebase` fails with "You have unstaged changes" because the dream cycle itself writes to tracked files (dream.log, episodic frontmatter) before the rebase. Roughly 4 weeks of memory evolution (April 22 forward) is local-only. The workflow's step-05 commits at the end but the up-front pull never succeeds. Either the pre-flight pull needs to move after a stash or the workflow needs to assume offline operation.

3. **Orphaned working-memory files.** 39 files in `memory/working/` are marked `status: archived` but were never moved to episodic — leftovers from prior runs. Step-01 only processes `status: active`, so they sit there indefinitely. Either a one-time cleanup pass or a workflow tweak (also archive previously-flagged `archived` items) would clear this.

No new semantic entries created. No new lessons appended. Run committed locally; push deferred per long-standing condition.

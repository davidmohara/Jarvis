---
type: working-archive
expires: 2026-05-18
status: archived
salience:
  score: 0
  last-promoted-check: 2026-05-19
---

# Dream Cycle Summary — 2026-05-17

Functionally a clean run, but the same three structural issues continue compounding without intervention. Archived one expired working entry (dream-summary-2026-05-15) to episodic. 47 episodic entries scored — salience distribution is identical to yesterday plus one new zero (0:12, 1:3, 7:1, 10:31). Twenty-first consecutive run with the score-10 ceiling pinned at 31 entries.

Zero promotion candidates again. Every entry that meets the score-3 threshold has `promoted: true` from prior cycles, so the cluster pass produces nothing. Error log scan over the last 30 days returned 14 entries across 6 categories; `process-skip` (5) and `assumption-error` (3) clear the 3+ threshold but both patterns are already represented in LESSONS.md (the April 18 "Process Skip on Boot Sequence" and "Wrong Assumptions Leading to Bad Diagnoses" entries). No new lessons appended. Compression remained skipped because the oldest episodic entry is 29 days old; the workflow doesn't compress under 90 days.

Four issues now compound and need a live session to resolve:

1. **Score inflation algorithm.** The 2-tag/30-day co-occurrence rule auto-promotes nearly every briefing-tagged entry to the maximum. Semantic output is mechanically valid but informationally null. Deferred 9 consecutive runs and remains the single largest blocker on memory system utility.

2. **Git sync blocked, 21st consecutive run.** `git pull --rebase` fails with "You have unstaged changes" because the dream cycle itself writes to tracked files before the rebase. Roughly 4 weeks of memory evolution (April 22 forward) is local-only. The workflow's step-05 commits at the end but the up-front pull never succeeds. Either the pre-flight pull needs to move after a stash, or the workflow needs to assume offline operation.

3. **Stale .git/index.lock.** A zero-byte index.lock from the 2026-05-16 03:09 run is still present and cannot be removed in the sandbox (filesystem permission denied). This means any `git rm`, `git add`, or `git commit` from this session will fail until the lock is manually cleared. The step-05 git commit step almost certainly failed for the same reason yesterday.

4. **Orphaned working-memory files.** 37 files in `memory/working/` are marked `status: archived` but cannot be moved or deleted from this sandbox — filesystem permission denied on `rm`/`mv`. Today's archival had to fall back to leaving the source file in place with status: archived flagged. Step-01's preservation rule keeps skipping them, so they sit indefinitely. A one-time cleanup pass from a privileged context is needed, or the workflow needs to switch to soft-delete semantics permanently.

No new semantic entries created. No new lessons appended. Run completed; git commit/push will likely fail per item 3.

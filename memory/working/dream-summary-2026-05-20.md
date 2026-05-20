---
type: working
expires: 2026-05-21
status: active
---

# Dream Cycle Summary — 2026-05-20

**Session:** dream-cycle-2026-05-20-030908

## What happened

Archived one expired working file (dream-summary-2026-05-18) to episodic. The May 19 dream summary is not yet expired (expires today, end of day). Source-file deletion failed again — sandbox blocks `rm` in `memory/working/`, so the source was marked `status: archived` and a copy was written to episodic. That's the 24th consecutive run with the same deletion-block error.

Salience pass scored 56 episodic entries. Distribution: 0:20, 1:3, 7:1, 10:32 — effectively unchanged from yesterday (32 entries pinned at the score-10 ceiling). Zero promotion candidates this run because every score>=3 entry already has `promoted: true` from a prior cycle. This is the 11th-plus consecutive run with zero promotions and a saturated high-score band. The score algorithm continues to need recalibration — the cap-at-10 saturation has erased differentiation among the high-tag entries.

Error log scan found three categories at threshold over the last 30 days: process-skip/protocol-skip (6), data-accuracy/stale-cache (5), and assumption-error/wrong-assumption (3). All three patterns are already in LESSONS.md as April 18 entries. No new lessons appended.

Compression skipped — oldest episodic entry is 32 days old, cutoff is 90.

## System notes

**Git sync clean at boot.** No index.lock present. The branch was up to date with origin/main and `git status` showed three pre-existing local modifications (golf-booking preview, daily-review state, morning-briefing state) plus three untracked files. None blocked execution.

**Filesystem deletion remains blocked.** 39+ already-archived working-memory files continue to accumulate in `memory/working/`. They are skipped correctly on subsequent runs but represent operational debt.

**Automated-boot tag-schema gap persists.** Of the 56 episodic entries, 14 still have no `tags` field and 4 have no `date` field. The automated boot path is still producing untagged briefings invisible to salience scoring.

**Zero-byte boot file found.** `memory/working/2026-05-18-073333-session-boot-morning-briefing.md` is empty (0 bytes, no frontmatter). Likely an interrupted boot. Skipped as unparseable.

## Recommendation

Three improvement items continue to accumulate cost — same list as yesterday and the day before:

1. **Fix the automated-boot tag schema.** The pattern input stream has narrowed to roughly one manual boot per week because scheduled-task briefings write no tags.
2. **Recalibrate salience scoring.** 11+ runs of zero promotions and a pinned ceiling at 32 entries. The score signal is dead.
3. **Clear or hide the orphaned working-memory files.** Either get the deletion path working or build a sweep skill that suppresses already-archived files from the working-memory directory listings.

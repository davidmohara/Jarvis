---
type: working-archive
expires: 2026-05-26
status: archived
date: 2026-05-25
source_file: memory/working/dream-summary-2026-05-25.md
tags:
- dream-summary
- briefing
- omnifocus
- boot
- semantic-promotion
- score-inflation
- dream-cycle
- git-issues
- error-patterns
- lessons
related_people: null
salience:
  score: 10
  last-promoted-check: 2026-07-04
  promoted: true
---
# Dream Cycle Summary — 2026-05-25

Routine run, no surprises. Memory phases all completed. The chronic blockers from the past month continue: source-deletion sandbox restriction (28th consecutive run blocking removal of expired working-memory copies after they're archived to episodic) and the stale `.git/index.lock` plus uncommitted changes that prevent `git pull --rebase` and any commit/push at the end.

**What happened in memory:**
- Archived 1 file: `dream-summary-2026-05-23.md` (newly expired today). Source marked `status: archived` in place; copy written to `memory/episodic/`.
- Scored 65 episodic entries (up from 63 yesterday — two new entries since last cycle).
- Score distribution: 0:30, 1:1, 6:1, 7:1, 8:7, 9:2, 10:23. The score-10 ceiling continues drifting down (31 → 24 → 23 over the last three runs) as previously-promoted entries fall outside the 30-day co-occurrence window. Nothing new is climbing into the high band because tag overlap from new entries is limited.
- Zero promotion candidates again. Every entry with score >= 3 (33 total) already carries `salience.promoted: true` from earlier cycles. Semantic promotion is functionally idle — has been for 15+ runs.
- Error log scan (last 30 days): process-skip:13, data-accuracy:6, routing-error:4, stale-context:3. All four categories already covered by existing entries in `memory/LESSONS.md`. No new appends per preservation-over-aggression.
- Compression skipped — oldest episodic entry is only 37 days old, well under the 90-day threshold.

**The two blockers David needs to clear:**
1. Run `rm -f .git/index.lock && git add -A && git commit -m "dream-cycle: 2026-05-25" && git push origin` from your machine. This unblocks both the boot-time git pull AND the end-of-cycle commit. Same fix needed every run.
2. The score-inflation pattern is real but the fix has been deferred 15+ consecutive runs. Worth a deliberate conversation about whether the salience algorithm needs a redesign — right now it's mostly measuring "how many briefing files share routine tags," which inflates everything into the top bucket and then leaves nothing to promote.

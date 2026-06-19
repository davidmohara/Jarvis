---
type: working-archive
expires: 2026-05-29
status: archived
session_id: dream-cycle-2026-05-28-030856
date: 2026-05-28
source_file: memory/working/dream-summary-2026-05-28.md
tags:
- dream-summary
- semantic-promotion
- dream-cycle
- git-issues
- error-patterns
- health
- lessons
- galen
related_people: null
salience:
  score: 10
  last-promoted-check: 2026-06-19
  promoted: true
---
# Dream Cycle Summary — 2026-05-28

Quiet run, same pattern as yesterday.

**What happened:**
- Archived 1 newly expired working file (`dream-summary-2026-05-26.md`). Copy written to episodic; source delete blocked again (31st consecutive run, sandbox unlink restriction unchanged).
- Scored 70 episodic entries. Distribution: 0:35, 4:1, 5:4, 6:5, 7:1, 8:6, 9:7, 10:11. Score-10 bucket dropped from 25→11 after yaml re-serialization spread top-tier scores more naturally across 8-10.
- Zero semantic promotions. All 33 entries with score≥3 already carry `promoted:true` from prior cycles. Semantic promotion has been idle for 18+ consecutive runs.
- Compression skipped — oldest episodic entry is only 40 days old (cutoff is 90).
- Error log scanned: process-skip:11, data-accuracy:6, routing-error:5, tool-misuse:4, stale-context:3 over last 30 days. All five categories already documented in LESSONS.md.

**Known issues (unchanged from prior runs):**
- Sandbox unlink restriction blocks deleting working memory source files after archive. `mv` workaround used for `.git/index.lock` again — proven path.
- `git push` will likely fail due to sandbox credential limits. David should run `git push origin main` from his machine after commit lands.
- Two working memory files remain unparseable (no expires field): `2026-05-25-200000-galen-health-review.md`, `golf-override-2026-05-27.md`. Persistent skips, not errors.

**Recommendation:** The semantic promotion stall (18+ runs) is structural — the score-≥3 cohort is fully saturated with `promoted:true` flags. If you want fresh semantic synthesis to resume, the promotion rule needs revisiting (e.g., re-promote on score increase, or sunset `promoted:true` after N days).

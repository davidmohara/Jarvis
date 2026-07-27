---
type: working
expires: 2026-05-23
status: archived
date: 2026-05-22
source_file: memory/working/dream-summary-2026-05-22.md
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
  last-promoted-check: 2026-07-26
  promoted: true
  promoted: true
  last-promoted-check: 2026-07-27
  last-promoted-check: 2026-07-27
salience:
  score: 0
  last-promoted-check: 2026-07-27
  promoted: true
---


# Dream Cycle Summary — 2026-05-22

Quiet run. Five working-memory files moved to episodic (four old morning briefings from May 18-19, two dream summaries from May 19-20). All five source deletions blocked again — sandbox can't unlink in `memory/working/`. That's the 25th consecutive run with this filesystem block. Sources are marked `status: archived` in place; the actual content is safely copied to `memory/episodic/`. Working memory clutter keeps growing because of this.

Episodic salience scoring ran across 61 entries. Distribution: 27 at score 0, one at 1, one at 7, 32 at the score-10 ceiling. The score-10 cluster hasn't moved in twelve consecutive cycles — the co-occurrence ceiling continues to mask real signal differences. Zero promotion candidates again, because every score>=3 entry already has `promoted: true` from a prior cycle. That's still the underlying issue blocking semantic growth.

Error pattern scan found three combos at the 3+ threshold: process-skip/protocol-skip (6), data-accuracy/stale-cache (4), stale-context/surfaced-resolved-item (3). All three are already covered in LESSONS.md under their bare category names, so the initial dream-cycle appends were rolled back. Preservation over aggression held.

Compression skipped — oldest episodic entry is only 34 days old, well under the 90-day threshold.

One zero-byte file (`2026-05-18-073333-session-boot-morning-briefing.md`) is still in working memory unparseable. Same file from prior runs. Likely from an interrupted boot.

What's worth surfacing: the score-inflation algorithm and the sandbox unlink restriction have been deferred for many runs. Both will keep producing the same null output until addressed. Tonight the git commit also failed — `.git/index.lock` was already present at boot and the sandbox blocks unlink. The previous run hit the same wall and David cleared it manually. Same intervention needed: `rm -f .git/index.lock && git add -A && git commit -m 'dream-cycle: 2026-05-22' && git push origin`.

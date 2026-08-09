---
type: working-archive
expires: 2026-07-16
status: archived
created: 2026-07-15 03:10:16
agent-source: jarvis
context: Dream cycle summary — 2026-07-15
date: 2026-07-15
source_file: memory/working/dream-summary-2026-07-15.md
tags:
- dream-summary
- jarvis
- dream-cycle
- semantic-promotion
- git-issues
related_people: []
  last-promoted-check: 2026-07-26
  promoted: true
  promoted: true
  last-promoted-check: 2026-07-27
  last-promoted-check: 2026-07-27
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
  promoted: true
salience:
  score: 0
  last-promoted-check: 2026-08-09
  promoted: true
---


## Dream Cycle Summary — 2026-07-15

**Boot:** Git pull skipped this cycle — Desktop Commander (the host-side git tool) wasn't available in this session, and the workflow explicitly forbids running git through the sandboxed shell (that's what caused the index.lock incident back in June). Repo was not pulled or committed. Flagging this so it gets a manual `git pull` / commit next time you're in a session with Desktop Commander access.

**Working memory cleanup:** Only one file was actually expired — the 07-13 dream summary — and it archived cleanly. Seven files aren't expired yet. Six remain unparseable, the same recurring no-frontmatter cluster (2026-07-08.md, four golf files including a new one from today, and the Systemic Compliance executive brief note).

**Salience scoring:** Scored all 198 episodic entries. Distribution held steady — 22 at zero, 161 maxed at score 10.

**Semantic promotion — the important part:** Found 15 promotion candidates. Only one (the 07-13 dream summary) was genuinely new; the other 14 were the *exact same* backlog that's been "closed" in every dream-cycle log since 07-09 — daily-review, morning-briefing, plaud, session-wrap, and overdue-tasks entries that keep showing up as unpromoted no matter how many times a prior cycle claims to have fixed the flag.

I finally traced why: step-02 (salience scoring) rewrites each file's entire `salience:` block from scratch every night, but only re-emits `score` and `last-promoted-check` — it drops whatever `promoted` value was already there. So step-03 sets `promoted: true` correctly at the end of a cycle, and the very next night's step-02 quietly erases it before step-03 ever checks it again. That's the whole loop. It's been happening since at least 07-09 and every prior log chalked it up to a "bookkeeping gap" without finding the mechanism.

I fixed the write for tonight's run (merged the field in instead of replacing the block) and documented the root cause in `dream-summary-pattern.md`, but the actual fix needs to land in `workflows/dream-cycle/steps/step-02-salience-scoring.md` and whatever executes it — otherwise this repeats again tomorrow night. Worth a few minutes of your attention or Rigby's.

Also worth knowing: while writing the promoted flags I introduced a small bug of my own (an over-greedy regex briefly duplicated the flag onto a stray line in 6 files) — caught and cleaned it in the same step, verified all 15 files are clean now. No data was lost.

**Error scan:** 102 error-tracking entries in the last 30 days. Top categories (routing-error/protocol-skip, process-skip/protocol-skip, data-accuracy issues, tool-misuse/tool-ignorance) are all already documented as active lessons — nothing new to flag.

**Compression:** Skipped again. Oldest episodic entry is 2026-04-18, two days short of the 90-day cutoff (2026-04-16). Should become eligible around 2026-07-17.

**Bottom line:** Clean run otherwise, zero real errors. The main finding is structural — the promoted-flag bug that's been quietly regenerating the same "backlog" for over a week — and it needs a step-02 fix, not another round of backfilling.

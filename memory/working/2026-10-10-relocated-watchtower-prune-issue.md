# Relocated: watchtower dormancy-prune standing flag

Origin: `workflows/watchtower/steps/daily-step-07-prune.md` frontmatter `note:` field (removed 2026-10-10 during Phase A commentary cleanup).
Date relocated: 2026-10-10.
Reason: standing operational flag, not an instructional frontmatter field. State lives outside step frontmatter; flag retained here until reconciled.

---

source-activity.json only tracks 22 of the 30+ active entries in sources.yaml (last maintained through the 2026-06-29 batch); most entries show last_surfaced: null purely because they predate ledger upkeep, not because they've gone quiet. Mass-evaluating dormancy against a stale ledger risked retiring sources that are simply untracked, not silent. Skipped mass retirement this run — updated last_surfaced only for the 3 sources (CIO Dive, Dallas Innovates, Hacker News) that demonstrably surfaced today.

Flag for Rigby: source-activity.json needs a reconciliation pass against the full sources.yaml registry before dormancy pruning can be trusted.

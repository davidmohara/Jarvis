---
type: working-archive
task_id: "session"
session_id: "harper-2026-10-20-133000"
agent-source: harper
created: 2026-10-20T13:30:00-05:00
expires: 2026-10-22T13:30:00-05:00
status: archived
context: "Obsidian draft/Ghost live-post reconciliation — 55 drafts flipped, metadata backfilled — 2026-10-20"
date: 2026-10-20
source_file: memory/working/2026-10-20-133000-harper-obsidian-ghost-reconciliation.md
tags:
  - harper
  - rigby
  - session
related_people:
salience:
  score: 0
  last-promoted-check: 2026-10-26
---

**What was requested/produced:** David asked to reconcile Obsidian `_`-prefixed drafts against live Ghost posts. Harper scanned 128 underscore-prefixed files across Mind/, Mind/Posts/, Mind/Articles/ and matched against all 105 Ghost posts.

**Results:**
- 55 files flipped: `_` prefix removed, `status: Posted`, and (follow-up round, David-approved) `published_url` + `published_date` backfilled per the canonical protocol (workflows/content-approval/references/obsidian-note-update.md). 110 frontmatter writes, all OK. Slug remaps (17 files) used canonical Ghost URLs, spot-verified.
- 1 corrupted frontmatter fence repaired (`Mind/Posts/fde-table-stakes-now-what.md`).
- Left as drafts: 2 Ghost-scheduled (Love With Your Presence, 10-22; your-business-has-a-dashboard-you-dont, 10-21 — next reconciliation flips after they go live), 4 still Ghost drafts, 4 ambiguous near-misses verified distinct, 67 no counterpart.

**Action items / follow-ups:**
- workflows/content-approval/pending-drafts.json stale (many "pending" entries live on Ghost; cleanup step not running) — Rigby investigating in parallel this session.
- No Ghost writes. Nothing committed yet.

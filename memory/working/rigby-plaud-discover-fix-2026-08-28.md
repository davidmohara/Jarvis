---
date: 2026-08-28
session: rigby-plaud-discover-fix
type: work-summary
tags: [rigby, plaud-discover, plaud-ingest, error-tracking, capability-fix, bug-fix]
---

# Rigby — plaud-discover false-positive fix — Session Summary

## What was done
Fixed a recurring plaud-discover bug (repeat occurrence: `err-20260826T190948-QQMBTP` then
`err-20260828T140747-814VN9`) where the skill reported 127 of 128 Plaud recordings as "new"
when only ~7 genuinely were, and never populated `accumulated-context.new-recordings` per
step-01's requirement.

## Root cause (confirmed against live filesystem, not just theory)
`skills/plaud-discover/SKILL.md` step 3's staging staleness rule unconditionally re-queued any
top-level file in `~/Downloads/transcript-staging` older than 24h as "new," with **no
vault-dedup check first**. Checked the folder directly: 121 top-level `.md` files, 120 older
than 24h, every one a duplicate of a file already triaged into `_not_new_archive/` (277 files).
120 stale duplicates ≈ the 127 false positives reported. Also found Tier 3 dedup assumed staged
filenames follow `plaud_<file_id>*.md` — real files are `plaud_<title>.md`, so that check never
fired. Both compound the still-open `err-20260826T190948-QQMBTP` issue: "vault unreadable" fell
back to silently proceeding without dedup instead of aborting.

Ruled out (via file mtimes/git history, not just assumption): `workflows/plaud-ingest/discover.py`
and `process_discovery.py`, two Aug 10 leftover debug scripts that dedup against a hardcoded
stale vault filename list — not referenced by any current workflow doc, not touched today.
Flagged as a landmine for future cleanup but out of scope for this fix (lives in `workflows/`,
not `skills/`).

## What changed
`skills/plaud-discover/SKILL.md`:
1. Staging scan excludes `_not_new_archive/` and any subfolder — top-level only.
2. Staged files must clear Tier 1 (file_id) / Tier 2 (title fuzzy match) vault dedup before the
   staleness rule can apply; already-ingested leftovers get flagged for manual cleanup instead
   of silently re-queued.
3. Fixed Tier 3's broken filename-pattern assumption.
4. Vault-unreadable failure mode changed from silent proceed-without-dedup to abort-and-report.
5. Step 5 now requires the full per-recording list (not a summary count) written to
   `state.yaml accumulated-context.new-recordings` before advancing past step-01.

Tracked in `evolutions/.pending-changes.json` as `work-20260828-plaud-discover-false-positive-fix`.
Both error-tracking entries updated to `fix_status: applied` with full fix detail.

Per David's explicit instruction, cleared `workflows/plaud-ingest/state.yaml`'s
`status: blocked` → `status: ready` and handed off to Master/Knox (via SendMessage) to re-run
step-01 discovery as live verification of the fix, with an explicit sanity check: result should
land near the last verified baseline (7 new out of 127), not near-total re-flagging. If it does,
Knox is instructed to re-block rather than trust the output.

## Outstanding / not done
- Fix not yet verified via a live end-to-end discovery re-run — handed to Master/Knox, awaiting
  their result.
- Did not commit changes. `skills/git/SKILL.md` requires Desktop Commander for all git ops;
  Desktop Commander was not available in this session. Repo also had unrelated concurrent
  changes from other active sessions (`data/*`, `workflows/boot/*`) at the time — did not want
  to sweep those into a commit blind. Someone with Desktop Commander access should commit:
  `skills/plaud-discover/SKILL.md`, `evolutions/.pending-changes.json`,
  `systems/error-tracking/entries/err-20260826T190948-QQMBTP.json`,
  `systems/error-tracking/entries/err-20260828T140747-814VN9.json`,
  `workflows/plaud-ingest/state.yaml`.
- `workflows/plaud-ingest/discover.py` and `process_discovery.py` (stale debug scripts, hardcoded
  vault snapshot from Aug 5) should probably be deleted or quarantined — attractive nuisance,
  named exactly like the real discovery step. Not done — outside this fix's scope (`workflows/`
  ownership, not `skills/`).

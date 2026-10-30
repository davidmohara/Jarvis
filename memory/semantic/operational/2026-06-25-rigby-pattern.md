---
type: semantic
domain: operational
confidence: low
created: 2026-06-25
last-updated: 2026-10-30
tags:
  - rigby
synthesized-from:
  - memory/episodic/dream-summary-2026-05-30.md
  - memory/episodic/daily-review-2026-05-28-163825.md
---
# Rigby Pattern

## Pattern Summary

Recurring rigby activity observed across 2 episodic entries within the 30-day salience window. Promoted by dream cycle on 2026-06-25.

## Evidence

- 2026-06-25: memory/episodic/dream-summary-2026-05-30.md (tags: dream-summary, jarvis, briefing, boot, semantic-promotion)
- 2026-06-25: memory/episodic/daily-review-2026-05-28-163825.md (tags: daily-review, chief, briefing, calendar, omnifocus)


### 2026-06-28 — promoted from cluster 'rigby'
- 2026-06-26 — Dream cycle 2026-06-26 — tapered run; surface YAML corruption discovery from prior promotion writes. (score 10) [source: memory/episodic/dream-summary-2026-06-26.md]

## Implications

- rigby is a meaningful operational signal — appears frequently enough across distinct sessions to warrant a semantic record.
- Track for stability: if this tag continues to dominate clusters across cycles, consider whether it's a useful pattern or a noise tag (e.g., session-boot, briefing) that should be filtered.

## Evidence (added 2026-10-26)

- 2026-10-20-120000-rigby-conventions-migration-closed.md (score 5): conventions-migration closed from 172 WARN to 0 WARN / 0 FAIL with 48 David-approved exceptions (review_after 2027-01-17/20); 23 file splits, master.md cut from 627 to 44 lines. About 70 files left uncommitted pending a push conflict with another agent's clone.
- 2026-10-20-150000-rigby-content-approval-rework.md (score 4): content pipeline redesigned after pending-drafts.json rot (sweep never executed, zero eval records). Discovery became the tracker custodian, approval gates retired, tracker reconciled from 48 to 2 entries.

## Implications (added 2026-10-26)

- Rigby's large builds finish but leave uncommitted file piles waiting on a human (push conflict with a second agent), which is the same commit-friction theme as the git-issues pattern and the controller's 10-13 feedback that the git path is too heavy.
- Scheduled sweeps that never run are invisible for months; zero eval records for a workflow is a stronger rot signal than any failure. Worth a standing check for scheduled workflows with no eval history.
- Exceptions granted with a review date (47 of 48 re-raise as WARN on 2027-01-20) need a calendar owner or they will resurface as noise.

## Evidence (added 2026-10-30)

- rigby-watchtower-daily-wiring-2026-10-26.md (score 10): Watchtower daily had not written since 09-08 because only the morning-briefing workflow invoked it, and boot had replaced that workflow. Rigby added a boot handoff step and closed several ledger risks (shared daily/weekly state, append-only ledger, vault write method).
- 2026-10-26-163000-rigby-boot-token-fixes.md (score 10) with rigby-impact-2026-10-26-boot-token-fixes.md (score 9): five boot token-performance fixes across 22 tracked files (real-timestamp hard rule, step split-out, Watchtower eval record, boot state purge, Knox no-op preflight). Rigby also over-globbed during cleanup and deleted tracked files; all 33 were restored through ies-git.
- 2026-10-27-185500-rigby-step-04.5-removal.md (score 3): the Watchtower handoff step lived about half a day before David removed it from boot. Stale references inside workflows/watchtower/ and unpackaged ADD entries in evolutions/.pending-changes.json were queued as follow-ups.

## Implications (added 2026-10-30)

- A build can be correct and still be reversed. The 10-26 Watchtower wiring was removed within a day, so the real acceptance test is David's reaction at the next boot, not the validation checklist. Ask before wiring new work into boot.
- Reversals leave residue: stale invoker references and net-zero evolution entries need a cleanup owner or they accumulate as noise.
- Broad cleanup globs are a recurring Rigby risk. The 33-file restore worked because the files were tracked; untracked scratch state is unrecoverable, so cleanup should enumerate paths rather than glob.

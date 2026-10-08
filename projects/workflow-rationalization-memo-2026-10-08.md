# Workflow Rationalization Memo (Phase 0, Stage 5 Remediation)

**Date:** 2026-10-08 · **Scope:** all 58 workflow dirs · **Method:** eval-record counts and recency (`systems/eval-harness/runs/`), state.yaml status and last completed-at, skill-library overlap

## Decision: Stage 4 candidate set

**Certify these 4** (sustained, eval-tracked, recent usage):

| Workflow | Eval records | Last eval | Last state.yaml completion |
|----------|-------------:|-----------|----------------------------|
| daily-review | 58 | 2026-09-29 | (scheduled cadence) |
| boot | 45 | 2026-10-08 | 2026-10-08 |
| plaud-ingest | 31 | 2026-09-28 | 2026-10-08 |
| morning-briefing | 18 | 2026-09-29 | (scheduled cadence) |

**Drop weekly-review** from the submission set: 0 eval records ever, state.yaml never-started. Cover note to Tim explains the 4-not-5 rationalization.

## Usage picture (58 dirs)

- **Sustained use (5+ evals, recent):** the 4 candidates above, plus dream-cycle (58), system-eval (20, stale since 2026-08-08), shutdown-cleanup (5).
- **Occasional use (1-3 evals):** boot-verification (2), client-meeting-prep (2), content-pipeline (2), error-improvement (3), golf-preview (2), one-on-one-prep, partner-meeting-prep, podcast-prep, talking-points, watchtower, content-approval, content-discovery, golf-booking.
- **Zero eval records ever: 34 dirs.** Several of these completed runs pre-harness (state.yaml shows complete: account-pursuit-map, comp-tracker, one-texas-scorecard, rock1-revenue-monthly, rock4-pipeline-weekly, pipeline-review, episode-prep-generator).

## Consolidation / removal candidates (flagged, not blocking certification)

Removal requires David's approval plus a `rigby-impact` reference scan before any deletion.

1. **weekly-review** → drop or fold into the `quinn-weekly-review` skill, which already carries the weekly review prep flow.
2. **card-review / card-walkthrough / card-which** → the `chase-card-*` skills own this domain; all three dirs are never-started. Remove.
3. **client-meeting-prep vs calendar-prep** → both map to existing skills (`chase-client-prep` retired into client-meeting-prep workflow; `chief-prep` exists). calendar-prep is idle with 0 evals. Consolidate to one prep path.
4. **content-calendar / content-approval / content-discovery / content-pipeline** → overlap with the `harper-content*` skills and the watchtower flow. One content pipeline should survive; the rest fold in.
5. **training-module-runner / training-onboarding / training-status** → the `shep-training` skill owns this. All never-started. Remove or fold.
6. **morning-briefing vs boot step-05** → boot already synthesizes the briefing (state.yaml shows briefing delivered by boot). Verify whether morning-briefing adds a distinct scheduled path or duplicates boot; if duplicate, consolidate during Phase 1's step rewrite.
7. **daily-review vs shutdown-cleanup vs dream-cycle** → three end-of-day-ish flows with overlapping closure duties. Keep all three for now (each has real usage) but clarify boundaries in the Phase 5A manifest.

## Notes

- Eval records are the reliable usage signal; state.yaml is not (scheduled/cadence workflows don't always update it, and pre-harness completions show blank).
- The skills library, not the workflow dirs, is where most occasional flows actually run today. Workflow dirs that never started and duplicate an existing skill are the cleanest removals.
- This memo satisfies Phase 0 of `projects/stage5-certification-remediation.md`. Consolidations above are non-blocking to certification and queue behind Phases 1-6.

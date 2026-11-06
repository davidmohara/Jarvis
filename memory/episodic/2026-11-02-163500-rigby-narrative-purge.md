---
type: working-archive
task_id: "session"
session_id: "rigby-2026-11-02-163500"
agent-source: rigby
created: 2026-11-02T16:35:00-06:00
expires: 2026-11-04T16:35:00-06:00
status: archived
context: "Rigby purged narratives from workflows/boot/workflow.md and inventoried the tree for the same violation (err-20261102T212336-DWG2OK) — 2026-11-02"
date: 2026-11-02
source_file: memory/working/2026-11-02-163500-rigby-narrative-purge.md
tags:
  - rigby
  - briefing
  - plaud
  - boot
  - dream-cycle
  - credit-cards
  - chase
  - knox
related_people:
salience:
  score: 10
  last-promoted-check: 2026-11-06
  promoted: true
---

# Narrative Purge — boot workflow.md trimmed, tree inventoried

## Standing rule (David, err-20261102T212336-DWG2OK)

There must NEVER be narratives in workflow or skill files themselves. No dated incident stories, no err-/eval-ID provenance, no token war stories, no merge history. Narratives live in memory/ and documentation. Workflow and skill files carry operative rules only. Also: no references-doc parking spots or pointers to stories from inside the workflow.

## Part 1: workflows/boot/workflow.md purged

- 160 → 148 lines; lints 0 fail / 0 warn / 0 acknowledged; no conventions-exceptions entry needed (supersedes the open size-exception question from work-20261102-192758).
- Removed: 2026-10-26 superseded-block story, 57-turn/6.27M story + eval citation, step-02.5/06.5 merge history, 10-30/11-02 turn counts, 25%-outside-attribution-window sentence, 2026-10-26 stamp anecdote, 42-Bash-calls anecdote, 2026-10-29 token-spike sentence, err-20261027T184315-93PIYQ citation.
- Converted to bare rules: fresh-run reset, dedicated-subagent dispatch, CONTEXT BUDGET directives, Watchtower exclusion, Edit/Write-only rule, real-clock rule, 80k-per-turn TURN BUDGET principle (dates dropped, principle kept).
- Header count fixed 7 → 10 steps. Em-dashes removed. Additional rules consolidated 3 → 2.
- Verified: literal workflow.md string x7, no-other-step-file lines x5, "verbatim and unabridged" x2, boot.json static assertions survive, frontmatter parses, boot-verify.py completion exit 0, zero narrative-pattern grep hits.
- Pending-changes: work-20261102-212800.

## Part 2: tree inventory (no edits, awaiting David)

- **A. err-/eval-ID citations in instructional text (~21 files/lines)** — mechanical strip. Notably workflows/card-review, golf-booking (IDs in gate-table cells), boot steps 01.5/02/03/04/05, content-discovery 48H RETRY RULE, plaud-ingest steps.
- **B. Dated narratives and token war stories (~14 lines)** — mechanical strip. Notably plaud-ingest workflow (1.65M/8.8M token stories), boot step-01 (804K fork story), step-04 (2M-token run stories), card-walkthrough, dream-cycle destructive-push story, skills/git 2026-10-18 recurrence, knox-search, remarkable-upload, rigby-eval-grade, rigby-integrity.
- **C. Needs judgment (dated state/verification provenance, not stories)** — card-walkthrough "verified live" notes, content-discovery approval provenance, chase-card-offers-* dated portal-state notes, plaud-transcripts change note, rigby-integrity staleness note.
- **E. Traceability flag** — stripping leaves bare rules with no in-file why: account-pursuit-map OFS-collision rule, golf-booking gate table, plaud-ingest "FAILURE MODE PREVENTED" bullets, plaud-speaker-id non-negotiable rules, morning-briefing error-log pointer, git wrapper recurrence count.
- **D. False-positive classes** (no action): frontmatter state blocks, fenced JSON samples, format examples, deliberate ID demos.

## Part 3: linter guard (assessment only, not implemented)

- Proposed: NARRATIVE_ID_RE (err-/eval- full-ID pattern) + NARRATIVE_DATE_RE (provenance-verb + date), applied to SKILL.md and workflows/**/*.md, frontmatter skipped, fenced code stripped, e.g./Example lines excluded.
- Severity: WARN (keeps report mode exit 0); optionally add to build_gate_extra so NEW artifacts fail while backlog warns. Not unconditional FAIL (would block all builds until sweep lands).
- Narrower option: ship ID regex only first (high precision, ~25 findings), add date rule after the sweep.
- Should land together with the sweep, not before it.

## Decisions pending David

1. Greenlight mechanical A+B sweep (~25 files).
2. Category C one-offs: decision each (dated operational state notes).
3. Category E: decide whether a rule sentence absorbs the failure mode before the ID goes.
4. Linter rule: implement with the sweep, WARN-only vs build-gate-fail for new artifacts.

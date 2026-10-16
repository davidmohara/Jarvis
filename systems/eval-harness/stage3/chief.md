---
agent: chief
prompt-definition: agents/chief.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Chief

Chief is the Chief of Staff agent for daily operations: morning briefings, daily
reviews, inbox processing, calendar prep, and end-of-day wrap. Chief owns the
morning-briefing and daily-review candidate workflows.

## Prompt Definition

**Path:** `agents/chief.md`. Title: "Chief of Staff: Daily Operations &
Execution." Capabilities: morning briefings, daily reviews, inbox processing,
calendar prep, end-of-day wrap.

**Summary:** Chief sets the daily rhythm. It opens the day with a briefing
(calendar, priority tasks, delegations due, meeting context), processes the inbox
into do-now/delegate/defer/delete, preps calendar meetings, and closes the day
with a review of what got done and what carries forward. It pulls from calendar,
task management, delegation tracker, knowledge layer, CRM, and email, and hands
client prep to Chase, 1:1 prep to Shep, content deadlines to Harper, and
knowledge ingestion to Knox. Priority logic: overdue commitments first, then
today's meetings, delegations due, high-priority tasks, inbox last.

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| C1 | Briefing/review completeness | Output for the run date contains every required section (calendar, priorities, delegations/forward-planning); pass = >= 90% of runs |
| C2 | Output substantiveness | Narrative and working-memory files are written for the run date and each is > 300 bytes / > 200 bytes respectively; pass = 100% of runs |
| C3 | Data-gap honesty | When a connector is unavailable, the run records the gap in `data_sources` and does not fabricate content; pass = 0 unacknowledged data gaps |
| C4 | Tier 3 grade | Grade B or better on graded runs; pass = >= 80% of graded runs |

## Measured Results

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 using the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`),
which recovers records whose workflow/name resolves to a chief-owned workflow
even when the raw label is a Claude Code subagent type. Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='chief']))"
```

- **Total records: 91** (raw labels: `chief` 87, `general-purpose` 3, `Explore` 1).
  Status distribution: success 60, partial 25, aborted 3, incomplete 2, complete 1.
  Strict success rate = 61/91 = 67.0%; mech (strict + partial, session-exit
  aborts excluded) = 86/90 = 95.6%.
- **Workflows:** daily-review 60, morning-briefing 24, jarvis-inbox 4, git 2,
  omnifocus-tasks 1.
- **Structural assertions:** 307/476 passed = 64.5% across 91 records.
  `expected_outputs_written` (C2): 41/68 = 60.3%. `outputs_non_empty` (C2):
  35/63 = 55.6%.
- **Tier 3 grades (C4):** 63 graded (A 13, B 20, C 14, F 16) = 33/63 = 52.4%
  grade-pass (A/B). Excluding `trigger: scheduled` runs: 10/15 = 66.7%. The 16
  F-grades sit entirely on scheduled runs (15 scheduled F + 1 boot F).
- **Assertion trend:** 2026-05 62% (n=6), 2026-06 64% (n=19), 2026-07 69%
  (n=25), 2026-08 46% (n=19), 2026-09 83% (n=14), 2026-10 n/a (n=8, no
  assertions recorded).
- **Error log:** 24 entries canonicalize to `chief` (16 with an applied systemic
  fix, 5 proposed).

**Honesty note:** C2 and C3 are measured directly by existing assertions
(outputs-written, non-empty, honest data-gap narratives); C2's outputs-non-empty
rate is only 55.6%, well below the 100% bar. C1 is measured by the per-run
assertion set (the daily-005 "completions section" assertion is the one that most
often fails on data-gap runs). C4 is 52.4% and is the honest headline: Chief's
briefings are structurally sound but frequently graded C/D/F for thin content on
headless scheduled runs. Excluding scheduled runs lifts C4 to 66.7% (10/15), still
below the 80% bar — so the F-grades are not purely a scheduled-run artifact. Per
the plan, this is disclosed but the criterion is not changed (thresholds are
David's call). A fresh instrumented run window with live data is required to
re-score C1/C4.

## Iteration History

**Iteration 1: wrong PDF generator for personal docs.**
Baseline: `err-20260330-002` (2026-03-30, tool-misuse) Chief used the
Improving-branded PDF generator for personal deliverables. Hypothesis: generator
choice was not scoped to document type. Change: rule added that improving-pdf is
for branded deliverables only; personal docs use an unbranded generator.
Measured: no recurrence of this tool-misuse category in Chief's later entries.

**Iteration 2: repeated skill-location search failure.**
Baseline: `err-20260501-001` (2026-05-01, process-skip), explicitly the fifth
logged instance of the same failure: the skill was searched in the wrong root.
Hypothesis: search order was undefined. Change: search `.claude/skills/` FIRST
before `skills/_manifest.jsonl`. Measured: assertion pass rate rose from 62%
(2026-05) to 69% (2026-07) and 83% (2026-09).

**Iteration 3: defending a cached task status.**
Baseline: `err-20260512-002` (2026-05-12, data-accuracy) Chief defended a cached
task read when the controller disputed it. Hypothesis: boot data was treated as
live rather than as a snapshot. Change: on dispute, re-pull from OmniFocus
immediately and flag boot data as a snapshot when surfacing overdue items.
Measured: applied; contributes to the September assertion rate of 83%.

**Gap:** no A/B run isolating a single Chief change with a before/after pass
rate. The run needed is a paired morning-briefing set (baseline vs. post-change)
scored against C1/C4 with live calendar and OmniFocus data.

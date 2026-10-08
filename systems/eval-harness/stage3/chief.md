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

Mined from `systems/eval-harness/runs/*.json` on 2026-10-08. Repro:

```
python3 -c "import json,glob;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if d.get('agent')=='chief']))"
```

- **Total records: 82.** Status distribution: success 57, partial 23,
  incomplete 2. Completion (success) rate = 57/82 = 69.5%.
- **Workflows:** daily-review and morning-briefing dominate; earliest record
  2026-05-24, latest 2026-09.
- **Structural assertions:** 306/470 passed = 65.1% across 82 records.
- **Tier 3 grades:** 59 graded (A 11, B 19, C 13, F 16) = 30/59 = 50.8%
  grade-pass (A/B).
- **Assertion trend:** 2026-05 62% (n=6), 2026-06 64% (n=19), 2026-07 69%
  (n=25), 2026-08 48% (n=18), 2026-09 83% (n=14). Net improvement May to
  September despite an August dip.
- **Error log:** 25 entries tagged `chief` (16 with an applied systemic fix,
  5 proposed).

**Honesty note:** C2 and C3 are measured directly by existing assertions
(outputs-written, non-empty, honest data-gap narratives). C1 is measured by the
per-run assertion set (the daily-005 "completions section" assertion is the one
that most often fails on data-gap runs). C4 uses Tier 3 grades as the direct
measure. The 50.8% grade-pass rate is below the C4 threshold and is the honest
headline: Chief's briefings are structurally sound but frequently graded C/D/F
for thin content on headless scheduled runs. A fresh instrumented run window is
required to re-score C1/C4 against thresholds with live data.

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

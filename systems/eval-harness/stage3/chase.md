---
agent: chase
prompt-definition: agents/chase.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Chase

Chase is the revenue agent: pipeline reviews, account strategy, client meeting
prep, win/loss analysis, account pursuit maps, and credit-card optimization.

## Prompt Definition

**Path:** `agents/chase.md`. Title: "Closer: Revenue, Pipeline & Client
Strategy." Capabilities: pipeline reviews, account strategy, client meeting prep,
win/loss analysis, lead tracking.

**Summary:** Chase owns revenue and client strategy. It runs pipeline health
checks, deep-dives accounts (history, contacts, competitive landscape, playbook),
builds pursuit maps for new business, preps client meetings email-first (verify
the reason for the call, research attendees, disambiguate company identity,
produce calibrated talking points and landmines), and debriefs won/lost deals.
It also runs the card-optimizer task portfolio.

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| H1 | Prep-sheet completeness | Client/meeting prep includes attendee research, account context, and talking points; pass = >= 90% of preps |
| H2 | Reason-for-call verification | Prep verifies the reason for the call from the email thread before drawing conclusions; pass = 100% of client preps |
| H3 | Data-grounding (no fabricated pipeline) | All pipeline/account figures trace to a live CRM or PowerBI read; pass = 0 unsourced figures |
| H4 | Tier 3 grade | Grade B or better on graded runs; pass = >= 80% of graded runs |

## Measured Results

Mined from `systems/eval-harness/runs/*.json` on 2026-10-08. Repro:

```
python3 -c "import json,glob;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if d.get('agent')=='chase']))"
```

- **Total records: 3.** Status distribution: success 2, aborted 1. Workflows:
  `partner-meeting-prep` (`eval-20260624T155626-B8WRE2`), `co-sell-pipeline`
  (`eval-20260831T150120-LBC9T0`), `client-meeting-prep`
  (`eval-20260921T222024-S5B1MP`, aborted).
- **Structural assertions:** 14/15 passed = 93.3% across 3 records.
- **Tier 3 grades:** 1 graded (A) = 1/1 = 100% grade-pass.
- **Error log:** 24 entries tagged `chase` (4 with an applied systemic fix,
  15 proposed), plus one `chase-client-prep` entry. Chase has a high error count
  relative to its 3 eval records, which reflects that most Chase work ran before
  or outside the instrumented eval path.

**Honesty note:** 3 records is far too few to claim a stable pass rate. H1-H3
are not directly asserted by the existing records; the 93.3% is the generic
structural assertion set. The one graded run is an A. What is required: a fresh
instrumented window of client-meeting-prep and co-sell-pipeline runs (target >=
10 each) scored against H1-H4, including at least one prep where the reason for
the call is ambiguous to test H2.

## Iteration History

**Iteration 1: conclusions from truncated email summaries.**
Baseline: `err-20260513-003` (2026-05-13, process-skip) Chase drew conclusions
from search-result summaries instead of reading the full email. Hypothesis:
summary fields were treated as authoritative. Change: always call `read_resource`
on the most relevant email URI before concluding. Measured: applied.

**Iteration 2: missing attendee thread context in prep.**
Baseline: `err-20260720T144623-LSBA9A` (2026-07-20, missed-context) prep sheets
were built without querying the connected email account for the introduction or
most recent thread. Hypothesis: attendee context defaulted to CRM only. Change:
always query email/calendar for the introduction or most recent thread before
falling back. Measured: applied; this is the change that most directly supports
H2.

**Iteration 3: over-trusting a sub-agent completion claim.**
Baseline: `err-20260730T184626-C1AMS0` (2026-07-30, under-delivery) a sub-agent's
"zero remaining mentions" claim was not spot-checked. Hypothesis: sub-agent
verification claims were accepted at face value. Change: spot-check specific
verification claims against the actual artifact. Measured: applied.

**Gap:** no before/after pass rate isolating any single Chase change. The run
needed is a paired client-meeting-prep set (pre-change vs. post-change) scored on
H1-H2 with live email and CRM data.

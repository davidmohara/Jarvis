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

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 using the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`),
which recovers records whose workflow/name resolves to a chase-owned workflow.
Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='chase']))"
```

- **Total records: 6** (raw labels: `chase` 3, `general-purpose` 1, `rigby` 1,
  `claude` 1). Status distribution: success 2, partial 1, aborted 2, incomplete 1.
  Strict success rate = 2/6 = 33.3%; mech = 3/5 = 60.0%.
- **Workflows:** client-meeting-prep 3, partner-meeting-prep 1,
  account-pursuit-map 1, co-sell-pipeline 1.
- **Structural assertions:** 15/19 passed = 78.9% across 6 records.
- **Tier 3 grades:** 1 graded (A) = 1/1 = 100% grade-pass.
- **Error log:** 24 entries canonicalize to `chase` (4 with an applied systemic
  fix, 16 proposed). Chase has a high error count relative to its 6 eval records,
  which reflects that most Chase work ran before or outside the instrumented eval
  path.

**Honesty note:** 6 records is still far too few to claim a stable pass rate. H1-H3
are not directly asserted by the existing records; the 78.9% is the generic
structural assertion set. The one graded run is an A (H4 passes on n=1, which is
not evidence). What is required: a fresh instrumented window of client-meeting-prep
and co-sell-pipeline runs (target >= 10 each) scored against H1-H4, including at
least one prep where the reason for the call is ambiguous to test H2.

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

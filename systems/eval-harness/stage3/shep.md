---
agent: shep
prompt-definition: agents/shep.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Shep

Shep is the people agent: 1:1 prep, delegation tracking, follow-up nudges, team
health pulse, and development plans.

## Prompt Definition

**Path:** `agents/shep.md`. Title: "Coach: People, Delegation & Development."
Capabilities: 1:1 prep, delegation tracking, follow-up nudges, team health pulse,
development plans.

**Summary:** Shep owns people and delegation. It builds 1:1 prep sheets by
researching M365 email, calendar, Teams chat, OmniFocus tasks, and the Obsidian
vault for the person, tracks active delegations with overdue flags, drafts
calibrated follow-up nudges, and assesses team health from 1:1 frequency,
delegation completion, and coaching notes. Delegation changes are mirrored into
OmniFocus.

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| S1 | 1:1 prep completeness | Prep sheet contains interaction threads, open action items, and talking points in the mandatory format; pass = 100% of preps |
| S2 | Delegation sync fidelity | Every delegation change is mirrored in OmniFocus with no drift; pass = 0 drift events |
| S3 | Nudge calibration | Follow-up nudges match the required tone tier (gentle reminder vs. escalation); pass = >= 90% |
| S4 | Tier 3 grade | Grade B or better on graded runs; pass = >= 80% of graded runs |

## Measured Results

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 using the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`),
which recovers records whose workflow/name resolves to a shep-owned workflow.
Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='shep']))"
```

- **Total records: 12** (raw labels: `general-purpose` 6, `shep` 5, `Explore` 1;
  6 recovered by the 2026-10-16 transcript-attribution fix). Status distribution:
  success 4, aborted 7, failure 1. Strict success rate = 4/12 = 33.3%; mech =
  4/12 = 33.3%.
- **Workflows:** one-on-one-prep 4, shep-1on1-prep 2. Earliest 2026-08-24,
  latest 2026-10-16.
- **Structural assertions:** 2/2 passed = 100% — but only 2 of the 12 records
  carry any assertion block (both are 2026-10-09 `shep-1on1-prep` runs with the
  generic signal/status checks). S1 has no assertion coverage.
- **Tier 3 grades:** 0 graded.
- **Assertion trend:** 2026-08 n/a (n=2, no assertions), 2026-10 100% (n=10, 2
  with assertions).
- **Error log:** 2 entries canonicalize to `shep` (both proposed).
- **Git history:** 9 commits touch `agents/shep.md`.

**Honesty note:** Shep has 12 records but no grades, and only 2 carry any
assertion block, so no stable pass rate can be claimed. The 100% assertion figure
is 2 generic checks, not S1. S1-S3 are effectively unmeasured; the 2 `shep`
error-log entries are not evidence of correctness. What is required: a fresh
instrumented window of at least 10 1:1 preps scored against S1, a delegation-sync
check that compares OmniFocus against the delegation tracker over a set of
changes to test S2, and a nudge-calibration review to test S3.

## Iteration History

**Iteration 1: 1:1 skill added.** Baseline: `agents/shep.md` gained the
`shep-1on1-prep` skill (commit `8560a51f`, 2026-06-16). Hypothesis: a mandatory
research sequence and output format would standardize prep sheets. Change: added
`skills/shep-1on1-prep/SKILL.md` with the format and sequence. Measured: one
recorded success (`eval-20260824T141251-5CDIXW`); no pass-rate delta available.

**Iteration 2: routing handoff defined.** Baseline: `agents/chief.md` handoff
behavior now routes 1:1 preps to Shep explicitly and forbids using Chase's
client-meeting-prep template for internal 1:1s. Hypothesis: separating internal
1:1 prep from external client prep prevents template misuse. Change: routing rule
added. Measured: no measured delta; iteration evidence pending.

**Iteration 3 (pending).** Baseline: no assertions or grades for Shep. The run
needed is a fresh instrumented batch of >= 10 1:1 preps with S1 assertions wired,
plus a delegation-sync A/B against OmniFocus for S2.

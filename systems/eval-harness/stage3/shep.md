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

Mined from `systems/eval-harness/runs/*.json` on 2026-10-08. Repro:

```
python3 -c "import json,glob;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if d.get('agent')=='shep']))"
```

- **Total records: 2.** Status distribution: success 2. Workflows:
  `shep-1on1-prep` (`eval-20260824T141251-5CDIXW`), `one-on-one-prep`
  (`eval-20260827T173100-AZ4CQR`).
- **Structural assertions:** 0/0. The two records carry no structural assertion
  block, so there is no assertion pass rate to report.
- **Tier 3 grades:** 0 graded.
- **Error log:** 0 entries tagged `shep`.
- **Git history:** 9 commits touch `agents/shep.md`.

**Honesty note:** Shep has 2 records, no assertions, and no grades, so no pass
rate can be claimed. Both recorded runs succeeded. S1-S3 are not measured at all;
the absence of any `shep` error-log entries is not evidence of correctness, it is
evidence that Shep work has not been error-logged. What is required: a fresh
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

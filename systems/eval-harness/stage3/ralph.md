---
agent: ralph
prompt-definition: agents/ralph.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Ralph

Ralph is the verification agent: it receives a task manifest and checks whether
each claimed task actually ran, returning a verdict table. Ralph is an agent (he
has a first-class definition at `agents/ralph.md`), not a workflow. He also has a
supporting workflow at `workflows/boot-verification/` that spawns him with the
boot task manifest.

## Prompt Definition

**Path:** `agents/ralph.md` (frontmatter: `name: ralph`, description: "General
purpose verification agent. Accepts any list of tasks or workflows, validates
that each one was genuinely executed... Not tied to any specific workflow.").
Supporting workflow: `workflows/boot-verification/workflow.md` (frontmatter
`agent: ralph`, model sonnet).

**Summary:** Ralph is adversarial verification. Given a manifest of tasks with
claimed statuses and evidence paths (state file, log, output artifact), he reads
the evidence and returns one of four verdicts per item: Verified, Unverified,
Skipped, or Not applicable. His principles: evidence over assertion, silence is
not a pass, no re-runs, no spawning, speed. He returns a table and one summary
line ("All verified: proceed." or "Re-run required: [tasks].").

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| A1 | Verdict-table completeness | Every manifest item receives a verdict (no silent omissions); pass = 100% of items covered |
| A2 | False-positive rate | Zero tasks marked Verified without a qualifying evidence artifact; pass = 0 false positives per run |
| A3 | Unverifiable-on-silence discipline | Missing/unreadable evidence yields Unverified, never Verified; pass = 100% of missing-evidence cases |
| A4 | Boot-verification gate | Boot verification runs to completion and returns a verdict table before the next phase proceeds; pass = 100% of boot runs |

## Measured Results

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 using the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`),
which now resolves the `boot-verification` sub-agent records to Ralph (workflow
owner) even though their raw label is `general-purpose`. Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='ralph']))"
```

- **Total records: 16** (raw labels: `general-purpose` 13, `Explore` 3). 2 are
  recovered via `workflow: boot-verification`; the other 14 by the 2026-10-16
  transcript-attribution fix. Status distribution: success 2, aborted 13,
  failure 1. Strict success rate = 2/16 = 12.5%.
- **Records:** the 2 boot-verification spawns `eval-20260823T174826-98HPVA`
  (aborted) and `eval-20260823T174957-Y47934` (success) plus 14 previously
  unattributed Ralph spawns (2026-10-08..2026-10-15).
- **Structural assertions:** 0/0 — no record carries an assertion block, so
  A1-A3 have no assertion coverage and there is no pass rate to report.
- **Tier 3 grades:** 2 graded (B 1, F 1) = 1/2 = 50.0% grade-pass.
- **Workflow state:** `workflows/boot-verification/state.yaml` exists (last
  updated 2026-08-23); the workflow is present but stale.
- **Error log:** 0 entries canonicalize to `ralph`.
- **Git history:** 3 commits touch `agents/ralph.md`.

**Honesty note:** The attribution layer recovers Ralph's 16 records (previously
reported as 2), but none carry assertions, so no pass rate can be reported for
A1-A3; two carry Tier 3 grades (1 B, 1 F). What is required: (1) instrument
A1-A3 as assertions, and
(2) run boot verification on at least 5 boots with a seeded manifest containing
at least one known-missing artifact to test A2/A3 (false positive and silence
discipline).

## Iteration History

**Iteration 1: agent definition created.** Baseline: before `agents/ralph.md`,
verification had no defined persona or verdict protocol. Hypothesis: a dedicated
skeptical verifier would catch false "done" claims. Change: added `agents/ralph.md`
with the four-verdict protocol and the "Are you really done?" test. Measured:
boot verification is now a defined phase (see `workflows/boot-verification/`).
No before/after pass rate exists.

**Iteration 2: boot-verification workflow wiring.** Baseline: `workflows/
boot-verification/workflow.md` spawns Ralph with the Phase 2 manifest. Hypothesis:
running Ralph automatically at boot catches unverified steps. Change: workflow
wired to spawn Ralph and gate the next phase on his verdict. Measured: two
execution traces (one success, one abort) on 2026-08-23; too few and
unattributed to compute a rate.

**Iteration 3 (pending).** Baseline: no measured false-positive rate. Hypothesis:
an adversarial manifest with a deliberately missing artifact will reveal whether
Ralph marks Verified on silence. Change: seed such a manifest. Measured:
iteration evidence pending, fresh A/B run required. The run needed is a paired
boot-verification set: one clean manifest, one manifest with a known-missing
artifact, both scored on A1-A3.

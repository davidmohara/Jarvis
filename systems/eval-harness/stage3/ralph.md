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

Mined from `systems/eval-harness/runs/*.json` and `workflows/boot-verification/`
on 2026-10-08.

- **Eval records tagged `ralph`: 0.** No run in the harness is attributed to
  Ralph by agent name. This is the honest headline: Ralph has no measured pass
  rate yet.
- **Boot-verification evidence (indirect):** two harness records exist under the
  label `general-purpose` with `name: boot-verification`
  (`eval-20260823T174826-98HPVA`, status aborted; `eval-20260823T174957-Y47934`,
  status success). These are sub-agent spawn records that lost the `ralph` agent
  attribution, so they cannot be scored against A1-A3 as-is.
- **Workflow state:** `workflows/boot-verification/state.yaml` exists (last
  updated 2026-08-23); the workflow is present but stale.
- **Error log:** 0 entries tagged `ralph`.
- **Git history:** 3 commits touch `agents/ralph.md`.

**Honesty note:** Ralph has no graded records and no assertion coverage, so no
pass rate can be reported. The two boot-verification records above are the only
execution trace and are misattributed. What is required: (1) fix sub-agent
attribution so boot-verification runs record `agent: ralph`, (2) instrument A1-A3
as assertions, and (3) run boot verification on at least 5 boots with a seeded
manifest containing at least one known-missing artifact to test A2/A3 (false
positive and silence discipline).

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

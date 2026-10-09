---
agent: quinn
prompt-definition: agents/quinn.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Quinn

Quinn is the strategy agent: strategy building, quarterly rock reviews, goal
alignment, initiative tracking, leadership prep, and weekly review prep.

## Prompt Definition

**Path:** `agents/quinn.md`. Title: "Strategist: Goals, Planning & Alignment."
Capabilities: strategy building, quarterly rock reviews, goal alignment,
initiative tracking, leadership prep.

**Summary:** Quinn owns strategy and alignment. It coaches through rigorous
strategy development (diagnose the challenge, find the crux, build the kernel of
diagnosis/guiding policy/coherent actions, stress-test via create-destroy,
sharpen into a 2-minute action agenda), reviews quarterly rocks, maps current
activity against goals to surface drift, tracks initiatives, and preps
leadership/board materials.

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| Q1 | Strategy-kernel presence | Every strategy output states a diagnosis, a guiding policy, and coherent actions; pass = 100% |
| Q2 | Bad-strategy detection | Output flags bad-strategy patterns (goals-as-strategy, fluff, template thinking) when present; pass = >= 90% |
| Q3 | Goal-grounding | Rock/alignment outputs reference the actual quarterly objectives file; pass = 100% |
| Q4 | Tier 3 grade | Grade B or better on graded runs; pass = >= 80% of graded runs |

## Measured Results

Mined from `systems/eval-harness/runs/*.json` on 2026-10-08. Repro:

```
python3 -c "import json,glob;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if d.get('agent')=='quinn']))"
```

- **Total records: 1.** Status distribution: success 1. Workflow:
  `quinn-strategy` (`eval-20260917T184939-W7I1DH`).
- **Structural assertions:** 4/4 passed = 100% across 1 record.
- **Tier 3 grades:** 0 graded.
- **Error log:** 0 entries tagged `quinn`.
- **Git history:** 9 commits touch `agents/quinn.md`.

**Honesty note:** A single record cannot support a pass-rate claim. The 4/4
assertion result is one run of the generic structural set, not Q1-Q3. Quinn's
weekly-review workflow is explicitly dropped from the candidate set (and retired 2026-10-09: the live flow is the quinn-weekly-review skill; the workflow dir was removed after a reference check) (0 eval
records ever, never-started `state.yaml`). What is required: a fresh instrumented
window of at least 10 strategy and rock-review runs scored against Q1-Q3, and a
review of the strategy output against the quarterly objectives file to test Q3.

## Iteration History

**Iteration 1: strategy skill added.** Baseline: `agents/quinn.md` gained the
`quinn-strategy` skill (commit `f86aec37` and the strategy action-agenda
methodology). Hypothesis: a structured kernel would raise output quality above
generic advice. Change: added the diagnosis/guiding-policy/coherent-actions
methodology with create-destroy stress-testing. Measured: one recorded success;
no pass-rate delta available.

**Iteration 2: weekly review prep added.** Baseline: `quinn-weekly-review` skill
added (commit `c0b8c2eb`) to assemble rock progress, delegation status, OmniFocus
health, and drift assessment. Hypothesis: a pre-staged review would improve the
controller's weekly review. Change: added the skill. Measured: no eval records
were ever produced for weekly-review; it was dropped from the candidate workflow
set. Iteration evidence pending.

**Iteration 3 (pending).** Baseline: no assertions or grades for Quinn. The run
needed is a fresh instrumented batch of >= 10 `quinn-strategy` runs with Q1-Q2
assertions (kernel presence, bad-strategy flagging) wired.

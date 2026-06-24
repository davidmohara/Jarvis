# IES Eval Harness — Implementation Plan

**Multi-Trial Reliability + Reference Solutions**
Prepared for David O'Hara · June 24, 2026

---

## 1. Summary

This plan implements the top two recommendations from the eval-framework assessment: multi-trial execution with pass@k / pass^k reliability scoring, and reference solutions for capabilities. Both map directly to the practices in Anthropic's "Demystifying evals for AI agents."

The work is sequenced so multi-trial lands first (it converts the harness from "did it work once" to "how reliably does it work"), followed by reference solutions (which make a failing eval unambiguous: agent error versus eval bug). Reference solutions are inexpensive here because outputs already persist to conventional on-disk locations, so the mechanism is a pinned copy plus a pointer rather than new capture infrastructure.

Decisions locked for this plan: trials default to **3**; reference files live **per-capability under** `systems/eval-harness/references/` and are promoted automatically on **positive controller feedback**; reliability passes run **weekly**; the pass^k gate is **tiered** — fully unattended capabilities must clear **1.0** (all 3 trials pass), all other gated capabilities clear **0.70**; references are kept for **live-mode capabilities** too.

**Answer to your structural question: yes — both abilities can be added structurally, without rewriting any workflow.** Multi-trial is a wrapper around the existing run path plus a new aggregation field on the eval record. Reference promotion hooks into the controller-feedback step you already perform at exit, so no workflow needs to know it is being referenced.

---

## 2. What we are building on

Two record-producing paths exist today, and the plan respects both:

- **Cowork / scheduled path** — `close-eval-record.py` writes a thin record (single `step-auto`, mechanical tier only) when a workflow finishes. This is where daily unattended workflows like morning-briefing and the rock reviews land.
- **Rigby benchmark path** — `rigby-capability-build` runs the `executor` subagent, saves output to `iteration-N/<eval>/<config>/run-1/`, grades via `grader.md`, and aggregates via `aggregate_benchmark.py` (which already computes mean and stddev across `run-1`, `run-2`, …).

The key existing asset: `aggregate_benchmark.py` already iterates over `run-*` directories and computes mean/stddev. The multi-trial work is largely about producing more than one `run-N` per eval and surfacing the right reliability metric, not about building aggregation from scratch.

Outputs already persist to known locations — `memory/working/<name>-*.md` for workflows, `workflows/<name>/steps/` for step artifacts, and Rigby `run-1/` directories for builds. That is what makes reference solutions cheap.

---

## 3. Workstream A — Multi-Trial Reliability

### 3.1 Objective

Run each gated eval k times (default k=3), capture per-trial outcomes, and compute two metrics the article defines:

- **pass@k** — probability of at least one success in k attempts. Rises with k. Useful where one good result is enough.
- **pass^k** — probability that all k trials succeed. Falls with k. This is the metric that matters for capabilities you depend on running correctly every time without supervision.

For a system David relies on daily, pass^k is the gate. A morning briefing that works 2 times in 3 is a failing capability even though pass@1 looks fine.

### 3.2 Scope — which capabilities get multi-trial

Do not multi-trial everything; it multiplies runtime and token cost. Target the capabilities where reliability is the actual product requirement:

| Tier | Capabilities | Trials | Gate |
|------|-------------|--------|------|
| Fully unattended / scheduled | morning-briefing, daily-review, rock1-revenue-monthly, rock4-pipeline-weekly, follow-up-nudges, inbox-processing | 3 | **pass^k = 1.0** (all 3 must pass) |
| On-demand, high-stakes | client-meeting-prep, pipeline-review, presentation-builder | 3 | pass^k ≥ 0.70 + manual review |
| Everything else | remaining workflows / skills | 1 | existing single-run |

The split is enforced per capability, not globally. The fully-unattended tier runs without your supervision, so anything short of 3-for-3 is a failing capability. The high-stakes on-demand tier still has you in the loop, so 0.70 plus a manual look is the right bar.

### 3.3 Non-determinism handling

The authoring guide already flags the MCP-context problem: live calendar/CRM data makes trials non-reproducible. Multi-trial makes this sharper — three trials against live data measure data drift, not agent reliability. Therefore:

- Multi-trial gating runs in **`mcp_mode: fabricated`** only. Context is embedded in the eval prompt so all k trials see identical inputs and any variance is genuinely the agent.
- `mcp_mode: live` evals stay single-trial and remain integration-breakage canaries, not reliability measurements.

### 3.4 Implementation steps

1. **Add a trial-count parameter to the run path.** Extend the Rigby run invocation (and a new thin wrapper for the Cowork path) to accept `--trials N`, writing to `run-1/ … run-N/` exactly as `aggregate_benchmark.py` already expects. No change to the executor itself.
2. **Write a reliability scorer.** New script `scoring/reliability.py` that reads the k per-trial pass/fail verdicts (from each `run-N/grading.json` or each trial's assertion result) and emits `pass_at_k` and `pass_hat_k`. For small k, compute pass^k exactly from the per-trial verdicts rather than the analytic estimate.
3. **Extend the eval record schema.** Add a `reliability` block under `assessment` (see 3.5). Update `schema.md` in the same commit so docs and code stay in sync — the assessment flagged a docstring/schema drift in `score_eval.py`; fix that drift here too.
4. **Wire the tiered pass^k gate.** In `score_eval.py`, add a hard gate: for records tagged `gate:reliability`, `pass_hat_k < threshold` forces `gate_status: fail`, alongside the existing safety/bias overrides. The threshold is read **from the record's `reliability.threshold`** (1.0 for the fully-unattended tier, 0.70 otherwise) rather than a global constant — `score_eval.py` already supports per-record gate overrides, so this is a property of the capability's tier. Composite score is unchanged; this is an additional override, not a reweight.
5. **Surface it in the dashboard.** Add a reliability column (pass@k / pass^k, k, and a small per-trial outcome strip) to `generate-dashboard.py` output so the trend is visible per capability.

### 3.5 Schema addition

```json
"reliability": {
  "trials": 3,
  "mcp_mode": "fabricated",
  "per_trial": ["success", "success", "failure"],
  "pass_at_k": 1.0,
  "pass_hat_k": 0.667,
  "gated": true,
  "tier": "unattended",
  "threshold": 1.0
}
```

### 3.6 Cost note

Three trials on ~6 unattended capabilities is the bulk of the added cost. Reliability passes run **weekly** as a scheduled job rather than on every execution. The daily scheduled run still writes its normal single record; the weekly reliability measurement is a separate job that reuses the fabricated-context eval prompts. A weekly cadence keeps cost bounded and is frequent enough to catch a regression before it has run unsupervised for long. Set it up with `mcp__scheduled-tasks__create_scheduled_task` once the scorer exists.

---

## 4. Workstream B — Reference Solutions

### 4.1 Objective

Give each gated capability a known-good accepted output that passes all its assertions. Per the article's Step 2, this proves the task is solvable and that the graders are configured correctly. When a future run fails, the reference disambiguates: if the reference still passes the graders but the new run does not, the agent regressed; if the reference also fails, the eval itself broke.

### 4.2 Why this is structurally easy here

Outputs already land in deterministic locations. A reference solution is therefore two cheap things: a pinned copy of an accepted output, and a metadata pointer recording what it was, when, and at which workflow version. Nothing about the workflows needs to change — promotion attaches to the controller-feedback signal you already give at session exit.

### 4.3 Storage layout

Per-capability under the eval harness, co-located with assertions and scoring so they version together:

```
systems/eval-harness/references/
  morning-briefing/
    reference.md          # pinned copy of the accepted output
    reference.meta.json   # pointer + provenance
  client-meeting-prep/
    reference.md
    reference.meta.json
```

Pointer file:

```json
{
  "capability": "morning-briefing",
  "source_eval_id": "eval-20260623T021234-DH9VSD",
  "source_path": "memory/working/morning-briefing-2026-06-23.md",
  "promoted_on": "2026-06-23T14:05:00Z",
  "promoted_by": "controller_feedback:positive",
  "workflow_version_hash": "2a045accfec69bac",
  "assertions_passed_at_promotion": "5/5"
}
```

### 4.4 Promotion mechanism

Promotion is automatic on positive controller feedback, reusing the exit-behavior rating sweep already defined in `CLAUDE.md`:

1. At exit, when you rate a run **positive**, the rating is written back to the eval record's `controller_feedback` (this already happens).
2. A new `promote-reference.py` fires on that write: it copies the run's output file to `references/<capability>/reference.md`, writes `reference.meta.json`, and records the workflow `version_hash`. It only promotes if the run's assertions passed — a positive rating on a run with failing assertions is logged but **not** promoted, and surfaced to you.
3. Promotion **overwrites** the prior reference (latest-accepted wins) but archives the previous one to `references/<capability>/history/` so you can diff drift over time.

Manual override remains available: `promote-reference.py --capability X --eval-id Y` lets you pin any specific run by hand if the automatic signal is wrong.

### 4.5 How references get used

- **Grader calibration** — when grading a new run, the grader subagent can be handed the reference as the "known-good" exemplar, sharpening pass/fail judgments on subjective capabilities (the article's calibration point).
- **Eval-health check** — a periodic job re-runs each capability's assertions against its own reference. If a reference stops passing its own assertions, the eval drifted and needs attention — a regression in the grader, not the agent.
- **Blind comparison anchor** — the comparator can A/B a new run against the reference to detect quality regression even when assertions still pass.

### 4.6 Implementation steps

1. Create `systems/eval-harness/references/` with a README documenting the layout and the meta schema.
2. Write `promote-reference.py` (copy + meta-write + assertion gate + history archive + manual override flag).
3. Hook the exit-sweep feedback write so a positive rating triggers promotion. Keep it idempotent — re-rating the same run positive should not re-archive.
4. Add an `eval-health` check that re-runs assertions against each reference and reports drift.
5. Optionally pass the reference path into `grader.md` and `comparator.md` inputs for capabilities that have one.

---

## 5. Sequencing and effort

| Phase | Work | Depends on | Rough effort |
|-------|------|-----------|--------------|
| A1 | Trial-count param + `reliability.py` scorer | — | Half day |
| A2 | Schema + `score_eval.py` gate + docstring fix | A1 | Half day |
| A3 | Dashboard reliability column | A2 | Half day |
| B1 | `references/` scaffold + meta schema + README | — | 1–2 hours |
| B2 | `promote-reference.py` + exit-sweep hook | B1 | Half day |
| B3 | `eval-health` drift check | B2 | Half day |
| V | Verify: backfill references for 6 unattended caps, run a 3-trial pass on each, read transcripts | A3, B3 | 1 day |

A and B are independent and can proceed in parallel. The article's most-repeated instruction — read the transcripts — is the verification phase: a green pass^k or a freshly pinned reference means nothing until you have read a couple of the underlying trials and confirmed the grading was fair.

### 5.1 Suggested order

Start with A1–A2 (the reliability scorer and gate), because that is the change that alters what "passing" means and is the higher-value of the two. Land B1–B2 next so the first capabilities you multi-trial also get a pinned reference from their first positive rating. Defer A3/B3 (dashboard and drift surfacing) until the core is proven on one capability end-to-end.

---

## 6. Resolved decisions

All three open questions are settled:

- **Reliability cadence — weekly.** A scheduled weekly job runs the fabricated-context reliability passes; daily executions are untouched (see 3.6).
- **pass^k threshold — tiered.** Fully unattended capabilities must clear **1.0** (all 3 trials pass); all other gated capabilities clear **0.70**. Enforced per record via `reliability.threshold`, not a global constant (see 3.2, 3.4 step 4).
- **References for live-mode capabilities — kept.** Live-only capabilities get a reference from a positive-rated real run. The reference is still a useful grader-calibration exemplar and blind-comparison anchor; its assertion coverage is weaker than a fabricated-context capability's, so the eval-health drift check (4.5) carries less weight for these and is treated as advisory rather than gating.

---

*No code has been written. This is a plan for review.*

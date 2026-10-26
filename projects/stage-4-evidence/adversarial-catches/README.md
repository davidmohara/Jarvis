# Adversarial Catch Log

**Created:** 2026-10-16 · **Maintained by:** Rigby
Referenced from `agents/adversarial-isolation.md` and `projects/stage-5-submission/index.md`.

## Purpose

A **catch** is a case where a producing agent's recorded claim was contradicted by
ground truth the adversarial layer re-derived independently. The adversarial layer
is Ralph (`agents/ralph.md`, the `workflows/*-verification/` sub-workflows) plus the
verification assertions that read a run's own record (`boot-004`, `morning-008`,
`daily-007`, `plaud-002`) or the on-disk artifact. This log records those catches in
a stable, machine-readable form so the isolation doc's claims are backed by evidence
rather than narrative.

The bar for an entry (from the isolation doc's evidence plan): a claim in a
`state.yaml` or eval record that a check **re-derived from raw state** contradicts.
Assertion false-positives and ordinary measurement gaps are NOT catches and must not
be logged here.

## Files

| File | Role |
|------|------|
| `catches.jsonl` | **Canonical.** One JSON object per line, machine-readable. |
| `catches.md` | Human-readable rendering of the same entries. Keep in sync with the JSONL. |

## Record format

Each catch carries these fields:

| field | meaning |
|-------|---------|
| `id` | Stable id, `CATCH-NN`. |
| `date` | ISO date the catch was recorded. |
| `workflow` | Producing workflow, or `eval-harness` for a harness defect. |
| `producing_agent` | Agent whose recorded claim was wrong (or `eval-harness`). |
| `claim` | What the producing agent / harness recorded (verbatim where possible). |
| `ground_truth` | What the verifier found by re-deriving from raw state. |
| `caught_by` | The assertion id, verification step, or check that caught it. |
| `evidence` | Record ids / file paths that substantiate the catch. |
| `disposition` | What happened: `fixed (<commit>)`, `quarantined`, `recorded-sentinel`. |
| `status` | `open` \| `fixed` \| `quarantined`. |

## How to run the verification

The assertions live in `systems/eval-harness/assertions/{workflow}.json` and are
evaluated by `systems/eval-harness/assertion_checks.py` (`run_assertions`). The
adversarial-verification assertions read the eval record's own `guardrails` array,
not the workflow's self-report:

- `boot-004-guardrail-checkpoint-ran` (checkpoint `pre-completion-review`)
- `morning-008-adversarial-verification-ran` (checkpoint `adversarial-verification`)
- `daily-007-adversarial-verification-ran` (checkpoint `adversarial-verification`)
- `plaud-002-adversarial-verification-ran` (checkpoint `adversarial-verification`)

To re-derive current truth over a window of records:

```
cd <IES root>
python3 - <<'PY'
import sys, json, glob, re
from pathlib import Path
sys.path.insert(0, "systems/eval-harness")
import yaml
from assertion_checks import run_assertions
IES = Path(".").resolve(); ADIR = IES / "systems/eval-harness/assertions"
for f in sorted(glob.glob("systems/eval-harness/runs/**/eval-2026*.json", recursive=True)):
    d = json.load(open(f))
    wf = d.get("workflow") or d.get("name")
    if wf not in {"boot","morning-briefing","daily-review","plaud-ingest"}: continue
    s = run_assertions(ADIR, wf, d, IES, agent=d.get("agent"), yaml_module=yaml)
    fails = [r["assertion"] for r in s.get("assertion_results",[]) if r.get("passed") is False]
    if fails: print(f, d.get("status"), fails)
PY
```

## Honest status (2026-10-16)

**The log is thin: five catches. One is a harness defect (`CATCH-01`); the other four
are the same class, a record that claims `status: success`/`complete` while its
adversarial-verification (or guardrail) checkpoint is absent from the record's own
`guardrails` array, so the assertion fails it.** The strongest is `CATCH-01` (the
harness mislabeled six completed specialist runs as `aborted`/`general-purpose`). The
other four are real but narrow: the candidate-workflow records in the 2026-10-06..16
window that reached a terminal status mostly carry the guardrail; the failures are the
records that skipped it (pre-wiring runs, partial runs, and quarantined phantom stubs).
That is exactly the class the Phase 4A wiring was built to surface, and the assertions
now fail such a run rather than letting it pass silently.

No catch in this log was fabricated. Where a check found nothing, nothing was recorded.

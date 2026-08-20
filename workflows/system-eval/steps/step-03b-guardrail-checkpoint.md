---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 03b: Guardrail Checkpoint — Review Grading Before It Drives the Gate

## MANDATORY EXECUTION RULES

1. Grades assigned in step-03 feed directly into step-04's composite score, which determines `gate_status`. A bad grade — one that inflates a genuinely broken run or fails a genuinely good one — corrupts the gate. This checkpoint is the adversarial review of the grader's own output, since Rigby cannot review itself in step-03.
2. You MUST record the checkpoint result via `guardrail-checkpoint.py` before proceeding.
3. `escalate` HALTS system-eval before scoring runs on the suspect grade(s) — the eval-harness workflow that is itself supposed to be the source of truth cannot let a bad grade propagate silently.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** Grades and `grader_notes` written in step-03, plus the `grade_distribution` tally
**Output:** Guardrail checkpoint result recorded; workflow proceeds to step-04 (pass/flag) or halts (escalate)

---

## YOUR TASK

### Review checklist

1. **Grade-notes consistency** — for a sample of graded records (at least the ones tallied as `A` or `F` this run — the extremes are where a bad grade does the most damage), does `grader_notes` actually name a specific assertion result or output detail, per step-03's own requirement? A grade with generic notes ("looks fine") is a red flag.
2. **No-output-found handling** — did every record in `no_output_found` get graded `D` or `F` per step-03's rule, rather than something more generous?
3. **Distribution sanity** — does `grade_distribution` look plausible given recent system-eval runs, or does it show an anomalous swing (e.g., everything suddenly graded `A` after a run of mixed grades) that suggests the grader skipped its review step?
4. **Self-grading violation check** — confirm no record for `system-eval` itself was graded this run (step-03's rule #6 exists specifically to prevent this).

### Decision

- **No issues** → `pass`.
- **A borderline note or two, not affecting the gate outcome** → `flag`, note it, proceed.
- **A grade with no evidentiary basis, a `no_output_found` record graded generously, or a self-grading violation** → `escalate`. Do not let step-04 compute composite scores from an untrustworthy grade until this is corrected.

### Record the result

```bash
python3 systems/eval-harness/guardrail-checkpoint.py system-eval pre-score-review step-03-grade <pass|flag|escalate> "<one-line reason>"
```

### Advance state

If `pass` or `flag`: update `state.yaml` `current-step: step-04-score`. (step-03 set `current-step: step-03b` on its own completion — this step is the one that must move it forward, or a resume-from-interruption right after this step would re-run the checkpoint indefinitely rather than proceeding to scoring.)

### If escalating

System-eval is fully autonomous with no controller approval gate (per workflow.md's architecture) — but an escalation here overrides that. Set `state.yaml` to `aborted` with a note naming the specific record(s) at issue, and surface it in the closing summary the next time a controller session runs system-eval or reviews the dashboard. Do not silently downgrade the escalation to a `flag` just because autonomy is the default mode.

---

## SUCCESS METRICS

- Every system-eval run has one guardrail checkpoint result recorded before scoring.
- No ungrounded grade has ever driven a `gate_status` because this checkpoint passed it.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `guardrail-checkpoint.py` fails to write | Note the gap in the analysis report from step-05; proceed only if manual review found nothing. |

---

## NEXT STEP

If `pass` or `flag`: [Step 04 — Score](step-04-score.md).
If `escalate`: set state.yaml to `aborted`, log the reason, and stop.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

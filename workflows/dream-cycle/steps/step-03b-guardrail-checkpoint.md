---
status: complete
started-at: 2026-08-30T08:18:00Z
completed-at: 2026-08-30T08:19:00Z
outputs:
  result: pass
  reason: "0 compression candidates this cycle -- the 5-entry backlog tracked across 08-26 through 08-29 was cleared by David's live-approved compression immediately after the 08-29 run (4 top-level episodic files deleted into memory/episodic/digests/2026-Q2-digest.md). No new low-score/old-date entries have accumulated since. All 3 of this cycle's promotion candidates correctly excluded (they carry promoted:true and would be excluded from any future candidate set regardless). Step-03's writes were substantive evidence appends across all 3 target files, not stubs."
model: sonnet
---

<!-- system:start -->
# Step 03b: Guardrail Checkpoint — Review Before Deletion

## MANDATORY EXECUTION RULES

1. Step-04 deletes source files once their digest entry is written — this is the one irreversible action in dream-cycle. This checkpoint reviews the promotion/compression plan before any deletion happens.
2. You MUST record the checkpoint result via `guardrail-checkpoint.py` before proceeding.
3. `escalate` HALTS the workflow before step-04 deletes anything. Preservation over aggression is the workflow's stated architecture — when in doubt, this checkpoint should err toward escalating, not passing.

---

## EXECUTION PROTOCOL

**Agent:** Jarvis
**Input:** Salience scores from step-02, promotion decisions from step-03
**Output:** Guardrail checkpoint result recorded; workflow proceeds to step-04 (pass/flag) or halts (escalate)

---

## YOUR TASK

### Review checklist

1. **Promoted-entry exclusion** — does the compression candidate set (which step-04 will build) correctly exclude every entry where `salience.promoted == true` or `salience.score >= 2`? Spot-check a sample against step-02's scores.
2. **Volume sanity** — is the number of compression candidates consistent with normal dream-cycle runs, or does it look anomalously large (a sign something upstream mis-scored a batch of entries as low-salience)?
3. **Semantic promotion quality** — did step-03 actually write substantive semantic entries, or does anything look like a stub that lost information from its source episodic entries?

### Decision

- **No issues** → `pass`.
- **A small number of borderline entries, not clearly wrong** → `flag`, note it, proceed — the 5-entry safety threshold and promoted/score exclusions in step-04 remain the backstop.
- **A promoted or high-salience entry appears in the candidate set, or the volume looks anomalous** → `escalate`. Do not let step-04 delete anything until this is resolved.

### Record the result

```bash
python3 systems/eval-harness/guardrail-checkpoint.py dream-cycle pre-deletion-review step-03-semantic-promotion <pass|flag|escalate> "<one-line reason>"
```

### Advance state

If `pass` or `flag`: update `state.yaml` `current-step: step-04`. (step-03 set `current-step: step-03b` on its own completion — this step is the one that must move it forward to `step-04`, or a resume-from-interruption right after this step would re-run the checkpoint indefinitely rather than proceeding.)

### If escalating

Write to `memory/dream.log`: `escalated: guardrail checkpoint halted before step-04 — [reason]`. Do not proceed to step-04. Surface to David at next session boot rather than blocking the nightly run indefinitely — dream-cycle runs unattended, so there is no controller to ask in the moment. Leave `state.yaml` at `status: aborted` with a note so the next session surfaces it via the aborted-run protocol.

---

## SUCCESS METRICS

- Every dream-cycle run has one guardrail checkpoint result recorded before any deletion.
- No promoted or high-salience entry has ever been deleted because this checkpoint passed one it shouldn't have.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `guardrail-checkpoint.py` fails to write | Log to `memory/dream.log` directly; proceed only if manual review found nothing, otherwise escalate per above. |

---

## NEXT STEP

If `pass` or `flag`: read fully and follow `steps/step-04-episodic-compression.md`.
If `escalate`: halt, log to `memory/dream.log`, and leave state.yaml aborted for the next session to surface.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

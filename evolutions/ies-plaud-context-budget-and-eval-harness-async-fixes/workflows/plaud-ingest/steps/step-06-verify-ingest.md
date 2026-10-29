---
status: completed
started-at: "2026-10-28T17:21:00Z"
completed-at: "2026-10-28T17:30:00Z"
model: sonnet
outputs:
  verification_result: flag
  discovered: 2
  ingested: 2
  silent_drops: 0
---

<!-- system:start -->
# Step 06: Adversarial Verification: Ingestion Accounting

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline in the coordinator's session. Knox runs the deterministic reconcile first and spawns Ralph only on anomaly.
**Input:** `workflows/plaud-ingest/state.yaml` accumulated-context (`new-recordings`, `ingested-notes`, `staged-files`, `recording-classification`, `pending-recordings`), step outputs, `~/Downloads/transcript-staging/` listing
**Output:** reconciliation verdict (script) or Ralph's verdict table (anomaly path); an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Reconcile script: `workflows/plaud-ingest/verify/ingest-reconcile.py`
- Verification workflow (anomaly path only): `workflows/plaud-ingest-verification/workflow.md`
- Lens: ingestion accounting, zero silent drops
- Manifest:
  - ingest-state: `workflows/plaud-ingest/state.yaml`
  - staging-dir: `~/Downloads/transcript-staging/`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Judge ONLY the anomalies the reconcile script flagged; for each, decide real-finding or explained-by-context.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py plaud-ingest adversarial-verification step-05b-share-with-alice <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a silent drop (a recording in the discovered set with no outcome) or uncleaned staging

## YOUR TASK

Script-first, mirroring `workflows/boot/verify/boot-verify.py`'s replacement of LLM verification in boot. The accounting this step exists for — discovered file_ids vs outcome sets vs vault on disk vs staging — is a deterministic set diff; an LLM re-derives the same table at 1-2.5M input tokens per run.

1. **Run the reconcile:**

   ```bash
   python3 workflows/plaud-ingest/verify/ingest-reconcile.py
   ```

   It prints the verdict table (Recording | Outcome | Verdict) and exits 0 when every discovered file_id is accounted for, every claimed note is on disk, and staging holds nothing from this run.

2. **On exit 0 (clean):** do NOT spawn Ralph. Record the result exactly as the protocol's recording steps specify:
   - `python3 systems/eval-harness/guardrail-checkpoint.py plaud-ingest adversarial-verification step-05b-share-with-alice pass "ingest-reconcile.py clean: N discovered, N accounted, zero silent drops"`
   - Write `accumulated-context.adversarial-verification` to state.yaml (`verdict: all-accounted`, `result: pass`, `findings: []`, `lens: "ingestion accounting, zero silent drops"`, plus a `method: ingest-reconcile.py` field so the record shows the verdict came from the deterministic pass).
   - Set this step complete and `state.yaml` `status: complete`, `current-step: step-06`.

3. **On exit 1 (anomalies):** spawn Ralph per `reference/adversarial-verify-protocol.md`, but with a tight brief — judge ONLY the flagged anomalies from the script output (paste them), deciding for each whether it is a real finding or explained by context already in state.yaml. Ralph does not rebuild the full accounting; the script's table is the accounting. Then:
   - Derive the checkpoint result from Ralph's judgment of the anomalies: a confirmed silent drop or uncleaned staging is `escalate`; explained anomalies are `flag` (or `pass` if every anomaly dissolved).
   - Record via the guardrail call and the state.yaml block above (with `method: ingest-reconcile.py + ralph`), exactly as the protocol specifies.
   - On `flag` or `escalate`: surface to David in one line `[Knox]: Ingest verification found [N] issue(s): [summary]. Recorded on the eval record.`
   - On `pass` or `flag`: set this step complete and set `state.yaml` `status: complete`, `current-step: step-06`.

This step overrides the protocol's always-spawn-Ralph rule for plaud-ingest: the script is the first pass, Ralph is the anomaly path. The protocol's other rules stand unchanged (no self-verified fixes, findings recorded as-is, Ralph never re-runs or rewrites anything).

---

## NEXT STEP

This is the final step. When complete, set `state.yaml` `status: complete`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

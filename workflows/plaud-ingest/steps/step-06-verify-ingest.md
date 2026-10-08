---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Ingestion Accounting

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/plaud-ingest-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own ingest. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before recording the result.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT re-ingest, re-share, or delete anything to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph accounts for recordings. He does not fix, re-run, or re-ingest anything.

---

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline in the coordinator's session. Knox spawns Ralph.
**Input:** `workflows/plaud-ingest/state.yaml` accumulated-context (`new-recordings`, `ingested-notes`, `staged-files`, `recording-classification`, `pending-recordings`), step outputs, `~/Downloads/transcript-staging/` listing
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this ingest run: every recording it discovered and what happened to it.
- This step does not re-process anything. It reconciles the discovered set against the outcome sets.
- A recording present at discovery but absent from every outcome list is a silent drop: the exact failure this lens exists to catch.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/plaud-ingest-verification/workflow.md
   Manifest:
     ingest-state: workflows/plaud-ingest/state.yaml
     staging-dir: ~/Downloads/transcript-staging/
     run-date: <YYYY-MM-DD>
   Task: Account for every discovered recording against the outcome lists and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Recording | Discovered | Outcome | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ → `pass`.
   - Any ⚠️ that is a benign, logged deferral → `flag`.
   - Any ⚠️ that is a silent drop (a recording in the discovered set with no outcome) or uncleaned staging → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py plaud-ingest adversarial-verification step-05b-share-with-alice <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-accounted" | "findings"
       result: "pass" | "flag" | "escalate"
       discovered_count: N
       findings: [list of unaccounted recordings, or empty]
       lens: "ingestion accounting, zero silent drops"
   ```

6. **Surface findings.** If `flag` or `escalate`, surface to David in one line: `[Knox]: Ingest verification found [N] issue(s): [summary]. Recorded on the eval record.`

7. **Update step frontmatter and state.yaml:** set this step `status: complete`, `completed-at`, `outputs.verification_result`; set state.yaml `status: complete`, `current-step: step-06`.

---

## SUCCESS METRICS

- Ralph was spawned (separate agent, distinct lens) and his verdict table received intact
- An `adversarial-verification` checkpoint result is recorded
- The verdict summary is written to state.yaml
- Any silent drop is surfaced to David, not silently absorbed

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph fails to spawn | Record `result: flag` with reason "adversarial verification unavailable, Ralph not spawnable"; note it in the final report. Do not self-verify in place of Ralph. |
| Ralph returns a partial table | Record the partial result and note which recordings were missing from the verdict. Do not suppress it. |
| `guardrail-checkpoint.py` fails to write | Still write the verdict summary to state.yaml; note the recording gap in the final report. |

---

## NEXT STEP

This is the final step. When complete, set `state.yaml status: complete`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

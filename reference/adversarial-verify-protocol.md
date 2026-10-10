# Adversarial Verification Protocol

Canonical scaffold for workflow terminal verification steps (step files named `step-*-adversarial-verify.md` or `step-0N-verify-*.md`). Every workflow's adversarial-verify step keeps only its workflow-specific parameters (lens, manifest fields, checkpoint reason) plus this pointer:

> Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters below.

---

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with the workflow's verification workflow (`workflows/<name>-verification/workflow.md`). Do NOT self-verify, and do NOT let the producing agent grade its own work. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before closing the run.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit the run's outputs or state to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state. He does not fix, re-run, or re-write anything.

## EXECUTION PROTOCOL

**Agent:** the workflow's producing agent, spawned by the coordinator, never executed inline. It spawns Ralph.
**Input:** the run's step frontmatter `outputs`, the workflow's `state.yaml`, the lens-specific recorded state.
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to `state.yaml`.

## CONTEXT BOUNDARIES

- Scope is this run's accounting: every item the workflow claims, re-derived from recorded state, with no silent drops.
- This step does not re-execute the workflow. It checks whether each claim is supported.
- Findings are a report, not a retry. A finding is surfaced and recorded.

## SEQUENCE

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/<name>-verification/workflow.md
   Manifest:
     <the workflow's manifest fields: step output paths, state file paths, run-date>
   Task: <the workflow's lens task, one sentence>.
   ```

2. **Receive Ralph's verdict table** (Item | Workflow claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified or not-applicable → `pass`.
   - Any minor mismatch → `flag`.
   - Any unsupported claim or silent drop → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py <workflow-name> adversarial-verification <previous-step> <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to `state.yaml`** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-accounted" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims or silent drops, or empty]
       lens: "<the workflow's lens, one line>"
   ```

6. **On `escalate`:** halt and surface to the controller: "[<agent>]: <workflow-name> verification found [N] unsupported item(s): [summary]. Holding for your review." Wait for instruction.

7. **On `pass` or `flag`:** update step frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`) and `state.yaml` (`current-step: null`), then close the run.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph fails to spawn | Record `result: flag` with reason "adversarial verification unavailable, Ralph not spawnable"; note it in the closing summary. Do not self-verify in place of Ralph. |
| Ralph returns a partial table | Record the partial result and note which items were missing. Do not suppress it. |
| `guardrail-checkpoint.py` fails to write | Still write the verdict summary to `state.yaml`; note the recording gap in the closing summary. |

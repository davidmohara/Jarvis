---
status: complete
started-at: '2026-10-19T21:29:30Z'
completed-at: '2026-10-19T21:31:00Z'
guardrail-result: flag
---

<!-- system:start -->
# Step 07: Guardrail Review & Verify Completion

## MANDATORY EXECUTION RULES

1. You MUST run the consolidated verifier script. It performs the pre-completion guardrail mechanics (formerly step-06.5: freshness, briefing currency, leakage scan) AND the completion gate (frontmatter status of every prior step) in one deterministic pass.
2. You MUST record the guardrail result via `guardrail-checkpoint.py`. Recording is not optional.
3. This step is a hard gate. Boot is NOT complete until this step passes.
4. LLM judgment is only exercised when the script flags anomalies, or when reviewing whether the synthesized briefing misrepresents the gathered data. Do not redo the script's mechanical checks by hand.

---

## EXECUTION PROTOCOL

**Agent:** boot subagent (Master persona), spawned by the coordinator at boot start (see `workflow.md`).
**Input:** `accumulated-context` from all prior steps; step frontmatter on disk
**Output:** Guardrail result recorded; verification report; boot marked complete only if clean

---

## YOUR TASK

1. **Run the consolidated verifier** from IES root:

   ```bash
   python3 workflows/boot/verify/boot-verify.py completion
   ```

   This checks: pull-file freshness and health, morning-briefing currency,
   credential-shaped-string leakage scan, and the frontmatter status of every
   prior step (PASS = `status: complete`).

2. **Content judgment (brief, only what the script can't see):**
   - Does the step-05 briefing plausibly reflect the gathered data? (Stale context presented as live is an `escalate`.)
   - Did step-06's workflow scan produce a sane result (not everything-in-progress, not nothing-at-all when `_active.yaml` has entries)?

3. **Record the guardrail result:**
   - Script clean + judgment clean → `pass`
   - Minor data quirk → `flag` with a one-line note
   - Briefing misrepresents data or scan clearly broken → `escalate`

   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py boot pre-completion-review step-06-scan-workflows <pass|flag|escalate> "<one-line reason>"
   ```

   On `escalate`: surface the finding to David, but still complete the gate so the session isn't blocked. The risk here is bad context shaping the session, not an irreversible write.

4. **Apply the gate:**
   - **PASS** (script exit 0, no escalation): surface the report, then:
     - Set this step's `status: complete`, `completed-at` now
     - Record `state_status` in state.yaml `accumulated-context`
     - **Update `workflows/boot/state.yaml`: `status: complete`, `current-step: null`, `completed-at` now. This write is mandatory; it closes boot's eval-harness record.**
   - **FAIL** (any step frontmatter not complete): leave boot `status: in-progress`, set `current-step` to the first failed step, surface the failure table, await instruction.

5. **Report format (PASS):**
   > ✓ Boot verification passed. All steps completed. Guardrail: {pass|flag|escalate} — {reason}

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| boot-verify.py crashes | Fall back to reading each step's frontmatter manually. Note the script failure as an error-log entry. |
| A step file is missing | FAIL. Surface it. |
| guardrail-checkpoint.py fails to write | Note the gap to David; proceed with the gate. |
| Step shows in-progress/not-started/skipped | FAIL, surface for re-execution. |

---

## NEXT STEP

Read fully and follow: `step-08-knox-completion-check.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

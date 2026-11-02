---
status: complete
started-at: '2026-11-02T16:21:55Z'
completed-at: '2026-11-02T16:22:12Z'
guardrail-result: flag
---

<!-- system:start -->
# Step 07: Guardrail Review & Verify Completion

## MANDATORY EXECUTION RULES

1. You MUST run the consolidated verifier script. It performs the pre-completion guardrail mechanics (formerly step-06.5: freshness, briefing currency, leakage scan) AND the completion gate (frontmatter status of every prior step) in one deterministic pass.
2. You MUST record the guardrail result via `guardrail-checkpoint.py`. Recording is not optional.
3. This step is a hard gate. Boot is NOT complete until this step passes.
4. LLM judgment is only exercised when the script flags anomalies, or when reviewing whether the synthesized briefing misrepresents the gathered data. Do not redo the script's mechanical checks by hand.
5. **Do NOT read `boot-verify.py` source.** Invoke it. It is the authority on what it checks.
6. **If it exits 0, do NOT run it again** at the end of boot or before the handback. One invocation per gate.

---

## EXECUTION PROTOCOL

**Agent:** briefing subagent (Master persona), spawned by the coordinator after step-04 completes (see `workflow.md`).
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
   - **PASS** (script exit 0, no escalation): surface the report, then write per the WRITE PROTOCOL below.
   - **FAIL** (any step frontmatter not complete): leave boot `status: in-progress`, set `current-step` to the first failed step, surface the failure table, await instruction.

5. **Report format (PASS):**
   > ✓ Boot verification passed. All steps completed. Guardrail: {pass|flag|escalate} — {reason}

---

## WRITE PROTOCOL (this block is the entire bookkeeping cost for this step)

The PASS branch closes boot. All three state writes and the frontmatter stamp land in ONE turn, carrying four values: `status: complete`, `current-step: null`, `completed-at`, and `state_status`.

1. One clock read: `date -u +%Y-%m-%dT%H:%M:%SZ`. Reuse that exact value for state and frontmatter.
2. **Edit 1**: `workflows/boot/state.yaml`, anchored on the `status: in-progress` line → `status: complete`. No grep, no re-read. **Match the whole line including its line break:** the string `status: in-progress` can also appear inside a prose value in a state file, and the Edit tool refuses a non-unique `old_string`.
3. **Edit 2**: anchored on the line `current-step: step-06-scan-workflows.md`. Step-05 set it and step-06 does not advance it, so that is the value on disk at entry. Replace it with `completed-at: '<clock>'` on its own line followed by `current-step: null`. This adds the top-level `completed-at` key (absent on a fresh run) and nulls the pointer in one edit. If the line reads something else, anchor on whatever `current-step:` value is there rather than reading the file.
4. **Edit 3**: anchored on the literal `accumulated-context:` line: insert `state_status` directly beneath it. Same anchor every step uses. Match the whole line including its line break.
5. **Edit 4**: this step file's frontmatter: `status: complete`, `completed-at` = the same clock value. Issued last, in the same turn.
6. Issue all four Edits as parallel tool calls in one turn. Never `cat` state.yaml. Never Write state.yaml.

Why four Edits and not one: the four keys are not contiguous, and `session-id` / `session-started` / `original-request` sit between two of them with run-varying values, so no single literal `old_string` can span them without reintroducing a read. Turn count is the cost driver, not call count: one turn holds all four.

**`state_status` value:** one line, 200 characters max, for example `"complete: gate passed, guardrail flag, all 8 steps complete; boot closed <clock>; record <eval-id>"`.

**The `workflows/boot/state.yaml` close is mandatory. The step-07 guardrail verifier asserts it.**

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

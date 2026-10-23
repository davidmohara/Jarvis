---
status: complete
started-at: '2026-10-22T11:46:08Z'
completed-at: '2026-10-22T11:46:08Z'
---

<!-- system:start -->
# Step 03: Measure & Verify Phase 2

## MANDATORY EXECUTION RULES

1. You MUST run the consolidated verifier script. It performs the Phase 2 context measurement (formerly step-02.5) AND the mechanical manifest verification (formerly step-03's Ralph spawn) in one deterministic pass.
2. If the script exits clean (exit 0), verification is DONE. Do NOT spawn Ralph. Record the result and return.
3. If the script reports anomalies (exit 1), spawn Ralph (`workflows/boot-verification/workflow.md`) with a tight brief covering the flagged items only. Ralph's role is judgment on degraded data, not re-running mechanics the script already checked.
4. Any item Ralph marks as failed must be re-run once before step-04 begins.
5. This step never loads the master persona (`agents/master.md`) or `SYSTEM.md`, never runs STATE CHECK, and never walks other steps. The next-step chain was removed on 2026-10-22 because it let one long-lived boot subagent carry ~495k input tokens into this step for a 1,014-token output (eval-20261021T151330-QNQLC5).

---

## EXECUTION PROTOCOL

**Agent:** dedicated verify subagent, spawned by the coordinator (Master) with a tight single-purpose brief.
**Input:** Phase 2 outputs in `data/` and `accumulated-context` in state.yaml
**Output:** Measurement snapshot + verification verdict, recorded in state.yaml

---

## YOUR TASK

1. **Run the consolidated verifier** from IES root (this Bash call is the step's one script execution — the Edit-not-Bash rule applies to state/frontmatter writes, not to running the verifier):

   ```bash
   python3 workflows/boot/verify/boot-verify.py phase2
   ```

   This captures the context-size measurement (snapshot written to
   `systems/boot-instrumentation/measurements/`) and checks every Phase 2 pull
   file for existence, freshness (<24h), non-emptiness, parseability, and
   reported status.

2. **On exit 0 (clean):** record in state.yaml `accumulated-context` (Edit tool):
   ```yaml
   verification_results: "pass — boot-verify phase2 clean (measurement + manifest, no LLM verification needed)"
   ```

3. **On exit 1 (anomalies):** spawn Ralph with a tight brief — `Workflows/boot/workflow.md step-03 verification: judge ONLY the flagged items from boot-verify.py phase2 ([paste the flagged list]). For each, decide accept-as-degraded or require-re-pull. Do not read or execute any step file beyond this mandate.` For each item:
   - Degraded data source (pull failed/stale/empty): Ralph decides whether to accept as degraded or require re-pull.
   - Re-run any task Ralph marks failed, once. Update accumulated-context.
   - Record Ralph's verdict summary in `verification_results`.
   - If Ralph is unavailable, self-verify the flagged items and note "self-verified" in the verdict.

4. **Surface the measurement** in your final message in compact form:
   ```
   [Instrumentation] Phase 2: {size_kb} KB (~{tokens} tokens) — verification: {clean | N anomalies}
   ```

5. **Update step frontmatter:** `status: complete`, `completed-at` now — Edit tool.
6. **Update state.yaml:** `current-step: step-04-gather-meeting-context.md` — Edit tool.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| boot-verify.py crashes | Fall back to manual check: confirm each pull reported a status in accumulated-context. Note the script failure as an error-log entry. Proceed. |
| A re-run task fails again | Record as degraded data. Do not loop; one re-run per task. |

---

## RETURN TO COORDINATOR

This is the END of your mandate. Do not read `step-04-gather-meeting-context.md` or any other step file — the coordinator spawns the dedicated meeting-context subagent for step-04 after you return. Your final message is a short status report: verification verdict (clean or N anomalies + Ralph's summary if he ran), the one-line instrumentation measurement, and any failure. Then stop.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

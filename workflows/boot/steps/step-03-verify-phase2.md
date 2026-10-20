---
status: complete
started-at: '2026-10-19T21:00:00Z'
completed-at: '2026-10-19T21:05:00Z'
---

<!-- system:start -->
# Step 03: Measure & Verify Phase 2

## MANDATORY EXECUTION RULES

1. You MUST run the consolidated verifier script. It performs the Phase 2 context measurement (formerly step-02.5) AND the mechanical manifest verification (formerly step-03's Ralph spawn) in one deterministic pass.
2. If the script exits clean (exit 0), verification is DONE. Do NOT spawn Ralph. Record the result and proceed.
3. If the script reports anomalies (exit 1), spawn Ralph (`workflows/boot-verification/workflow.md`) to judge the flagged items only. Ralph's role is judgment on degraded data, not re-running mechanics the script already checked.
4. Any item Ralph marks as failed must be re-run once before step-04 begins.

---

## EXECUTION PROTOCOL

**Agent:** boot subagent (Master persona), spawned by the coordinator at boot start (see `workflow.md`).
**Input:** Phase 2 outputs in `data/` and `accumulated-context` in state.yaml
**Output:** Measurement snapshot + verification verdict

---

## YOUR TASK

1. **Run the consolidated verifier** from IES root:

   ```bash
   python3 workflows/boot/verify/boot-verify.py phase2
   ```

   This captures the context-size measurement (snapshot written to
   `systems/boot-instrumentation/measurements/`) and checks every Phase 2 pull
   file for existence, freshness (<24h), non-emptiness, parseability, and
   reported status.

2. **On exit 0 (clean):** record in state.yaml `accumulated-context`:
   ```yaml
   verification_results: "pass — boot-verify phase2 clean (measurement + manifest, no LLM verification needed)"
   ```
   Proceed to step 4.

3. **On exit 1 (anomalies):** spawn Ralph with the flagged list. For each item:
   - Degraded data source (pull failed/stale/empty): Ralph decides whether to accept as degraded or require re-pull.
   - Re-run any task Ralph marks failed, once. Update accumulated-context.
   - Record Ralph's verdict summary in `verification_results`.
   - If Ralph is unavailable, self-verify the flagged items and note "self-verified" in the briefing.

4. **Surface the measurement** to David in compact form:
   ```
   [Instrumentation] Phase 2: {size_kb} KB (~{tokens} tokens) — verification: {clean | N anomalies}
   ```

5. **Update step frontmatter:** `status: complete`, `completed-at` now.
6. **Update state.yaml:** `current-step: step-04-gather-meeting-context.md`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| boot-verify.py crashes | Fall back to manual check: confirm each pull reported a status in accumulated-context. Note the script failure as an error-log entry. Proceed. |
| A re-run task fails again | Record as degraded data. Do not loop; one re-run per task. |

---

## NEXT STEP

Read fully and follow: `step-04-gather-meeting-context.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 02: Verify

## MANDATORY EXECUTION RULES

1. You MUST pass Ralph the full manifest from accumulated-context. Do not summarize or abbreviate it.
2. You MUST wait for Ralph's complete verdict table before proceeding. Do not advance on a partial response.
3. You MUST surface any ⚠️ or ❌ items to Master immediately. Do not bury them.
4. You MUST update state.yaml with the verdict summary before this step closes.
5. Do NOT re-run tasks yourself. That is Master's decision, not Ralph's and not this step's.

---

## EXECUTION PROTOCOL

**Agent:** Ralph — Verification Agent
**Input:** `phase2-manifest` from accumulated-context (built in step 01)
**Output:** Ralph's verdict table + a verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Ralph checks evidence. This step receives his verdict and surfaces it.
- Do not modify Ralph's verdict. Surface it as-is.
- The scope is exactly the six Phase 2 tasks in the manifest. Nothing more.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph** with the manifest from accumulated-context. Pass it as the full task manifest. Include today's date so Ralph can evaluate session-started timestamps.

   Ralph's spawn context:
   ```
   Agent: ralph
   Task: Verify the following Phase 2 boot task manifest. Check state files, logs, and working memory entries for each item. Return a verdict table.
   Manifest: [phase2-manifest from accumulated-context]
   Today's date: [YYYY-MM-DD]
   ```

2. **Receive Ralph's verdict table.** This is a table with columns: Task | Claimed Status | Verdict | Evidence / Gap. Plus one summary line.

3. **Surface the verdict to Master** exactly as Ralph returned it. No editing, no softening.

4. **If any items are ⚠️ Unverified or ❌ Skipped:**
   - Explicitly list them for Master
   - State: "Re-run required before Phase 3: [task names]"
   - Master decides which tasks to re-run and in what order

5. **If all items are ✅ or ➖:**
   - State: "All Phase 2 tasks verified. Proceed to Phase 3."

6. **Update state.yaml:**
   ```yaml
   status: complete
   current-step: step-02
   ```
   Also write the verdict summary to accumulated-context:
   ```yaml
   accumulated-context:
     verdict-summary: "all-verified | re-run-required"
     rerun-required: [list of task names, or empty]
   ```

---

## SUCCESS METRICS

- Ralph's verdict table received and surfaced intact
- All six Phase 2 tasks appear in the table
- Any ⚠️ or ❌ items explicitly listed for Master
- state.yaml updated with verdict summary

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph fails to spawn | Surface to Master: "Ralph spawn failed — boot verification skipped. Recommend treating all Phase 2 tasks as ⚠️ Unverified and proceeding with caution." Update state.yaml status to aborted. |
| Ralph returns a partial table (fewer than six tasks) | Surface the partial table. Note which tasks are missing from the verdict. Do not suppress the partial result. |
| Ralph is unresponsive | Wait up to one retry. If still unresponsive, treat as Ralph spawn failure above. |

---

## NEXT STEP

This is the final step. Return Ralph's verdict to Master. Workflow complete.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

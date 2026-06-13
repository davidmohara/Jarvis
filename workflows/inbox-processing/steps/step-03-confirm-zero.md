---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Confirm Zero

## MANDATORY EXECUTION RULES

1. You MUST re-query the task inbox to verify zero. Do not trust the tally alone.
2. You MUST report the final disposition breakdown. The controller needs the numbers.
3. You MUST check for new items that arrived during processing. Inbox zero means zero, not "zero when we started."
4. If new items exist, you MUST loop back to step 02. No declaring victory with items remaining.
5. Do NOT end the workflow until the live inbox count is zero.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** Disposition tally from step 02, live task inbox state
**Output:** Final confirmation report. Inbox zero or loop back.

---

## YOUR TASK

### Sequence

1. **Re-query task inbox** via the task management API.
   - Pull all incomplete inbox tasks (same query as step 01).
   - Count them.

2. **Compare to expected state:**
   - Expected: 0 items (all processed in step 02)
   - If 0: proceed to final report
   - If > 0: identify the new items

3. **If new items arrived during processing:**
   ```
   Inbox not yet at zero. X new items arrived during processing:

   1. "New task name"
   2. "Another new task"

   Looping back to triage these.
   ```
   - Return to step 02 with only the new items. Do not re-process already-triaged items.
   - Add new item count to the running tally.

4. **Final report** (only when live inbox = 0):

   ```
   INBOX ZERO.

   Processed: X items total

   Breakdown:
   - Do (today):    X items
   - Delegated:     X items
   - Deferred:      X items
   - Decide:        X items
   - Reference:     X items
   - Deleted:       X items

   Notable actions:
   - [List any delegations added with person and due date]
   - [List any decision files created]
   - [List any items flagged for agent routing]
   ```

5. **Surface any agent handoffs** flagged during triage:
   ```
   Agent routing flagged during triage:
   - Chase: [item] — revenue/pipeline context
   - Shep: [item] — people/delegation context
   - Harper: [item] — content/communication context
   - Quinn: [item] — strategic alignment context
   ```

   If no handoffs were flagged, skip this section.

---

## SUCCESS METRICS

- Live task inbox count verified at zero
- Final disposition breakdown reported with accurate numbers
- Any new items caught and processed (loop back completed)
- Agent routing flags surfaced for controller awareness

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management API query fails on verification | Report: "Cannot verify inbox zero — task management query failed. Based on triage tally, X items were processed." Proceed with tally-based report. |
| Infinite loop — items keep arriving | After 3 loops, report: "Items keep arriving faster than we can process. X items processed so far. Recommend completing remaining items in a follow-up session." End workflow. |
| Tally doesn't match processed count | Flag the discrepancy. "Tally shows X processed but started with Y. Z items may have been missed." List any unaccounted items. |

---

## WORKFLOW COMPLETE

Inbox processing is done. No further steps.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

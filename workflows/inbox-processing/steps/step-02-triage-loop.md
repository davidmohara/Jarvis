---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 02: Triage Loop

## MANDATORY EXECUTION RULES

1. You MUST present every inbox item to the controller. No silent dispositions.
2. You MUST recommend a disposition for each item. Never present without a recommendation.
3. You MUST wait for controller confirmation or adjustment before executing any disposition.
4. You MUST batch related items when possible. Five "delete" items get presented as one batch, not five separate prompts.
5. You MUST execute the disposition immediately after confirmation. Do not queue — act, then move to the next item.
6. Do NOT skip items. Every item gets a disposition or the inbox is not at zero.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** Inbox items from step 01, quarterly objectives, delegation tracker
**Output:** Each item triaged and executed. Running tally of dispositions.

---

## CONTEXT BOUNDARIES

- Prioritization is against quarterly rocks. Items that serve a rock get weighted toward Do or Defer. Items that serve no rock get weighted toward Delete or Reference.
- Age matters. Items older than 7 days should be flagged — if it sat this long, question whether it matters.
- Batch aggressively. Group by project, by person, by disposition type. The controller's time is the bottleneck.

---

## YOUR TASK

### Pre-Loop: Batch Analysis

Before entering the item-by-item loop, do a quick scan of all items and identify batching opportunities:

- **Same-project items**: Group items that belong to the same project or initiative.
- **Same-person items**: Group items related to the same person (delegate candidates).
- **Obvious deletes**: Group items that are clearly outdated, duplicates, or no longer relevant.
- **Quick wins**: Group items that can be handled in under 2 minutes.

Present batches first, individual items second.

### Loop: For Each Item (or Batch)

1. **Present the item:**
   ```
   [X of Y] — "Task name"
   Note: [note content, if any]
   Age: X days
   Rock alignment: [which rock it serves, or "none"]
   ```

2. **Recommend a disposition** with brief rationale:

   | Disposition | When to Recommend |
   |-------------|-------------------|
   | **Do** | Serves a rock + time-sensitive. Can be done today. |
   | **Delegate** | Someone else should own this. Name the person. |
   | **Defer** | Serves a rock but not urgent. Suggest a project and due date. |
   | **Decide** | Ambiguous, complex, or high-stakes. Needs structured thinking. |
   | **Reference** | Not actionable but worth keeping. Name the destination file. |
   | **Delete** | No rock alignment, no urgency, no value. Just clutter. |

   Example:
   ```
   Recommendation: DEFER — assign to "One Texas" project, due 2026-03-01.
   Rationale: Supports Rock 2 but no urgency. Schedule it.
   ```

3. **Ask for confirmation:**
   ```
   Confirm, or adjust? [Do / Delegate / Defer / Decide / Reference / Delete]
   ```

4. **Execute the confirmed disposition:**

   | Disposition | Execution Steps |
   |-------------|----------------|
   | **Do** | Assign to project via the task management API. Set due date to today. Flag the task. Add to today's priority list. |
   | **Delegate** | Add row to `delegations/tracker.md` (task, person, today's date, due date, status: Waiting). Create or update task with person tag and due date. Mark original inbox task complete. |
   | **Defer** | Assign to project via the task management API. Set due date as agreed. Mark original inbox task complete if moved. |
   | **Decide** | Create decision file: `decisions/YYYY-MM-DD-slug.md` from template. Mark inbox task complete. Note: "Decision file created — add to next review." |
   | **Reference** | File content into the appropriate reference doc or knowledge base. Mark inbox task complete in the task management system. |
   | **Delete** | Mark task complete in the task management system. No further action. |

5. **Update the running tally:**
   ```
   disposition_counts:
     do: N
     delegate: N
     defer: N
     decide: N
     reference: N
     delete: N
     processed: N of TOTAL
   ```

6. **Move to next item.** Repeat until all items are processed.

### Batch Presentation Format

When presenting batches (e.g., 4 items that are all deletes):
```
BATCH: 4 items — recommended DELETE

1. "Old task name" (14 days, no rock alignment)
2. "Another old task" (9 days, duplicate of existing project task)
3. "Outdated item" (21 days, event already passed)
4. "Vague note" (11 days, no actionable content)

Delete all 4? Or pull any out for different handling?
```

### Handoff Rules

During triage, flag items that need agent routing:
- Revenue/pipeline item detected → note for **Chase** handoff
- People/team item detected → note for **Shep** handoff
- Content/communication item detected → note for **Harper** handoff
- Strategic/goal item detected → note for **Quinn** handoff

Do not route during triage — just flag. The controller decides routing after disposition.

---

## SUCCESS METRICS

- Every inbox item presented with a recommendation
- Controller confirmed or adjusted every disposition
- Every disposition executed immediately after confirmation
- Running tally accurate throughout
- Batching used where 3+ items share disposition or context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management API call fails during execution | Report the error. Note the item as "unprocessed" and continue to next item. Retry failed items at the end. |
| Controller wants to skip an item | Allow it. Mark as "skipped" in the tally. Revisit skipped items after all others are processed. |
| Controller changes mind on a previous disposition | Note it. If the previous action can be undone (e.g., re-open a completed task), do it. If not (e.g., decision file already created), note the correction. |
| Item is ambiguous — no clear disposition | Present the options honestly. "This one could go either way. Do or Defer?" Let the controller decide. |

---

## NEXT STEP

When all items are processed (including any retries and skipped items), read fully and follow: `step-03-confirm-zero.md`

---

## Deep Analysis Protocol

Before entering the per-item triage loop, reason about the inbox as a system — not just individual items. The relationships between items matter more than any single item's disposition.

### When to Invoke

After the Pre-Loop Batch Analysis scan, before presenting the first batch or item to the controller.

### Reasoning Chain

1. **Cross-item relationship scan**: Which inbox items are actually about the same thing? An item about "follow up with Nada" and another about "Microsoft partner overlap" may be the same work stream. Group them before presenting.
2. **Rock alignment sweep**: Map each item against quarterly rocks. Items that serve no rock aren't automatically deletes — but they need a higher bar. Reason about which items are genuinely important vs. urgent noise.
3. **People load awareness**: Before recommending delegations, consider what's already on each person's plate (from the delegation tracker). Recommending 3 new items to someone with 5 overdue delegations is not a recommendation — it's a pile-on.
4. **Age-significance interaction**: A 14-day-old item with no rock alignment is probably a delete. But a 14-day-old item that blocks a rock is a failure mode, not just stale — escalate the urgency.
5. **Batch strategy**: Based on the above reasoning, plan the presentation order. Lead with the batches that are easiest to clear (obvious deletes, quick wins), then present the items that need real thought.
6. **Decision items identification**: Flag any items that are actually decisions masquerading as tasks. "Think about pricing strategy" is not a task — it's a decision file waiting to happen.

### What This Produces

- Smarter batching that groups by actual relationship, not just keyword similarity
- Delegation recommendations that account for current people load
- Age-urgency reasoning that distinguishes "stale and irrelevant" from "stale and critical"
- A presentation order that maximizes the controller's decision velocity
<!-- system:end -->

<!-- personal:start -->
## Tool Binding: Structured Reasoning

Use `sequential-thinking` MCP to execute the Deep Analysis Protocol reasoning chain above.
<!-- personal:end -->

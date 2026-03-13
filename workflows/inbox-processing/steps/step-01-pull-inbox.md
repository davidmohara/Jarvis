<!-- system:start -->
# Step 01: Pull Inbox

## MANDATORY EXECUTION RULES

1. You MUST pull every incomplete inbox task from the task management system before proceeding. No partial pulls.
2. You MUST capture both the task name and note for each item. Notes contain critical context.
3. You MUST load quarterly objectives before presenting any items. Triage without rocks context is guessing.
4. You MUST load the delegation tracker for current delegation awareness.
5. Do NOT begin triaging in this step. This step is data gathering only.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** Task inbox, quarterly objectives, delegation tracker
**Output:** Complete inbox inventory with item count, stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- Pull inbox tasks only. Do not pull project tasks, flagged tasks, or due-today tasks.
- Include task creation date if available — age is a triage signal.
- Quarterly objectives are the prioritization lens. Every triage recommendation in step 02 maps back to these.

---

## YOUR TASK

### Sequence

1. **Pull all inbox tasks** via the task management API.
   - Capture: task name, task note, creation date
   - Query for **incomplete** inbox/unfiled tasks only — filter out completed items
   - See `reference/omnifocus-commands.md` for the correct query syntax
   - Return each task's name, note/description, and creation date

2. **Count inbox items.** Store the total. This is the starting number for the final report.

3. **Load quarterly objectives** — read `context/quarterly-objectives.md`.
   - Extract the current rocks (name, key results, status).
   - These are the filter for every triage decision in step 02.

4. **Load delegation tracker** — read `delegations/tracker.md`.
   - Note active delegations and who owns them.
   - This prevents duplicate delegations and informs routing.

5. **Present the inbox summary to the controller:**
   ```
   Inbox: X items to process.

   Current rocks:
   1. [Rock name] — [status]
   2. [Rock name] — [status]
   ...

   Active delegations: Y items across Z people.

   Ready to triage. Moving to disposition loop.
   ```

6. **Store all data** in working memory:
   ```
   inbox_data:
     total_items: N
     items:
       - name: ...
         note: ...
         created: YYYY-MM-DD
         age_days: N
     rocks: [...]
     active_delegations: [...]
   ```

---

## SUCCESS METRICS

- All inbox tasks captured with names, notes, and creation dates
- Quarterly objectives loaded and summarized
- Delegation tracker loaded
- Total item count presented to controller

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management system unavailable / API error | Report error. Cannot proceed — inbox processing requires the task management system. Stop workflow. |
| Empty inbox | Report: "Inbox is already at zero. Nothing to process." End workflow. |
| Quarterly objectives file missing | Warn: "No quarterly objectives loaded — triage will lack prioritization context." Proceed but flag that recommendations will be weaker. |
| Delegation tracker missing | Warn: "Delegation tracker not found." Proceed — delegate dispositions will need manual routing. |

---

## NEXT STEP

Read fully and follow: `step-02-triage-loop.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

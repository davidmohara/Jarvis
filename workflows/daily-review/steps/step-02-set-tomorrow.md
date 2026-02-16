# Step 02: Set Tomorrow — Priorities and Prep

## MANDATORY EXECUTION RULES

1. You MUST ask the controller for tomorrow's top 3 priorities before suggesting anything.
2. You MUST check carry-forwards from step 01 — if the controller ignores an item that's rock-aligned, push back once.
3. You MUST check tomorrow's calendar for meetings that need prep. Flag them.
4. You MUST check the delegation tracker for anything overdue or due tomorrow. Surface it.
5. Do NOT accept a priority list where none of the top 3 align with quarterly rocks without challenging it. One push. Then respect the decision.
6. Do NOT proceed to step 03 until the controller confirms their top 3.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Mode:** Interactive — ask, challenge, confirm
**Input:** Capture data from step 01, delegation tracker, quarterly objectives, tomorrow's calendar
**Output:** Confirmed top 3 priorities and prep flags stored in working memory for step 03

---

## CONTEXT BOUNDARIES

- Step 01 capture data is available in working memory. Use it.
- Quarterly objectives are the alignment benchmark. Read them if not already loaded.
- Tomorrow's calendar is forward-looking — pull it now for prep flags only.
- The controller sets priorities. Chief can challenge, but the controller decides.

---

## YOUR TASK

### Sequence

1. **Load context for challenge logic:**
   - Read `{project-root}/context/quarterly-objectives.md` — know the current rocks
   - Read `{project-root}/delegations/tracker.md` — check for overdue or due-tomorrow items
   - Pull tomorrow's calendar via M365 MCP — identify meetings that need prep

2. **Surface carry-forwards and overdue items:**
   ```
   Before we set tomorrow's priorities:

   Carry-forwards from today:
   - [item] (rock-aligned: yes/no)
   - [item] (rock-aligned: yes/no)

   Overdue delegations:
   - [task] — delegated to [person] — [X days overdue]

   Delegations due tomorrow:
   - [task] — delegated to [person]
   ```

3. **Ask the priority question:**

   **"What are tomorrow's top 3 priorities?"**

   Wait for the controller's response.

4. **Run the challenge checks:**

   **Rock alignment check:**
   - Map each priority against quarterly rocks
   - If 0 of 3 align: "None of these connect to your Q[X] rocks. Is that intentional, or should [rock-aligned carry-forward] be on this list?"
   - If 1+ align: note the alignment silently in the data

   **Carry-forward check:**
   - If a rock-aligned carry-forward from step 01 is missing from the top 3: "You carried forward [item] which ties to [rock]. Want it in the top 3?"
   - One prompt. If the controller says no, respect it.

   **Overdue delegation check:**
   - If there are overdue delegations: "You've got [X] overdue delegation(s). Should 'follow up with [person] on [task]' be a priority, or should I queue a nudge?"

5. **Flag tomorrow's calendar prep needs:**
   ```
   Tomorrow's calendar — prep flags:
   - [Meeting] at [time] — [type: client/1:1/partner] — needs prep? [yes/no]
   - [Meeting] at [time] — back-to-back warning
   ```

   For meetings that need prep:
   - Client meetings → note for Chase
   - 1:1s → note for Shep
   - Partner meetings → note for partner prep

6. **Confirm the final top 3:**

   "Confirmed top 3 for tomorrow:"
   ```
   1. [Priority 1] — [rock alignment note]
   2. [Priority 2] — [rock alignment note]
   3. [Priority 3] — [rock alignment note]
   ```

   "Lock these in?"

   Wait for confirmation.

7. **Store results** in working memory:
   ```
   tomorrow_data:
     date: YYYY-MM-DD (tomorrow)
     top_3:
       - priority: ...
         rock_aligned: true/false
         rock: [rock name or null]
       - priority: ...
         rock_aligned: true/false
         rock: [rock name or null]
       - priority: ...
         rock_aligned: true/false
         rock: [rock name or null]
     calendar_prep_needed:
       - meeting: ...
         type: client | 1:1 | partner
         agent: Chase | Shep | Chief
     overdue_delegations: [list]
     delegations_due_tomorrow: [list]
   ```

---

## SUCCESS METRICS

- Controller asked for top 3 before Chief suggests anything
- Carry-forwards surfaced and considered
- Rock alignment checked — challenged if 0/3 align
- Overdue delegations surfaced
- Tomorrow's calendar checked for prep needs
- Final top 3 confirmed by the controller

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Controller won't commit to top 3 | Accept "I'll figure it out in the morning." Note: "No priorities set — morning briefing will start from scratch." |
| Quarterly objectives file missing | Skip rock alignment check. Note: "No quarterly objectives loaded — skipping alignment check." |
| Delegation tracker empty or missing | Skip delegation checks. Proceed with priorities only. |
| Tomorrow's calendar unavailable | Skip prep flags. Note: "Calendar data unavailable for tomorrow." |
| Controller pushes back on challenge | Accept it. One push per item maximum. The controller owns their priorities. |

---

## NEXT STEP

Read fully and follow: `step-03-update-system.md`

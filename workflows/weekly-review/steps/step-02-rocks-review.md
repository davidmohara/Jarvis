# Step 02: Rocks Review

## MANDATORY EXECUTION RULES

1. You MUST read the current quarterly objectives before presenting anything. No guessing rock status.
2. You MUST review every rock individually. Do not summarize or batch them.
3. You MUST flag any rock with no activity in 2+ weeks. This is the drift alarm.
4. You MUST ask the controller to confirm or update status on each rock before proceeding.
5. Do NOT proceed to step 03 until every rock has a current status.

---

## EXECUTION PROTOCOL

**Agent:** Quinn (Strategy)
**Input:** Quarterly objectives file, daily reviews from step 01, calendar data if available
**Output:** Updated rock status for each quarterly objective, flags for at-risk items, stored in working memory

---

## CONTEXT BOUNDARIES

- Review only the current quarter's rocks from `context/quarterly-objectives.md`.
- Cross-reference with this week's daily reviews (from step 01) to identify rock-related activity.
- Do not introduce new rocks or suggest changes here. That happens in step 06 if needed.
- Do not deep-dive into project plans. This is a status check, not a planning session.

---

## YOUR TASK

### Sequence

1. **Load quarterly objectives.**
   - Read `context/quarterly-objectives.md`.
   - For each rock, capture: name, key results, current status, last update date.

2. **Cross-reference activity this week.**
   - Using daily reviews from step 01, identify which rocks had activity this week.
   - Check meeting notes or decisions from this week that relate to any rock.
   - Check task management system for tasks tagged or associated with each rock.

3. **Present each rock individually** using Quinn's voice:
   - Rock name and key results
   - Current status (on track, at risk, blocked, complete)
   - What moved this week (specific activities, not vague summaries)
   - What didn't move
   - **Flag** if no activity in 2+ weeks: "This rock hasn't moved in [X] weeks. That's drift, not patience."

4. **For each rock, ask the controller:**
   - "Is this status still accurate?"
   - "What needs to happen next week to keep this moving?"
   - If the controller updates the status, capture the new status.

5. **After reviewing all rocks, summarize:**
   - Rocks on track (green)
   - Rocks at risk (yellow) - with reason
   - Rocks blocked (red) - with blocker
   - Overall quarter health: "X of Y rocks are on track. The quarter is [healthy / at risk / in trouble]."

6. **Update quarterly objectives file** with any status changes the controller confirmed.

---

## SUCCESS METRICS

- Every rock reviewed individually with current status
- Activity this week mapped to specific rocks
- Stale rocks (2+ weeks without activity) flagged explicitly
- Controller has confirmed or updated status on each rock
- Quarterly objectives file updated if changes were made

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Quarterly objectives file not found | Report: "No quarterly objectives file found. Cannot review rocks. This needs to be created before the next review." Skip to step 03. |
| Controller doesn't know status of a rock | Flag it: "If you don't know the status, that's the status. This rock needs attention." Mark as at-risk. |
| All rocks are "on track" with no evidence | Challenge: "Everything's green but I can't find activity for [rock]. Green means progress, not just 'not failed yet.'" |
| Controller wants to add or change rocks | Note it for step 06: "Let's capture that as a priority-setting item. We'll revisit in the final step." |

---

## NEXT STEP

Read fully and follow: `step-03-delegation-review.md`

# Step 01: Capture — What Happened Today

## MANDATORY EXECUTION RULES

1. You MUST pull task management data (completed today, created today, inbox count) before asking the controller anything. Show up prepared.
2. You MUST check if a morning briefing exists for today and cross-reference its priorities against what actually happened.
3. You MUST ask all three capture questions and wait for responses. Do not fill in answers on the controller's behalf.
4. Do NOT skip to step 02 until the controller has answered all three questions.
5. Do NOT editorialize on the controller's answers in this step. Capture first, challenge in step 02.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Mode:** Interactive — gather data, then ask questions
**Input:** Task management data, today's calendar, morning briefing (if exists)
**Output:** Raw capture data stored in working memory for step 03

---

## CONTEXT BOUNDARIES

- Look at today only. Do not pull forward items from previous days unless they were explicitly on today's morning briefing.
- Calendar data is reference material — the controller decides what counted as a "win" from meetings.
- Completed tasks from the task management system are facts. Surface them, but the controller may have wins that aren't tracked there.

---

## YOUR TASK

### Sequence

1. **Pull task management data** via the task management API:
   - Tasks completed today (all projects)
   - Tasks created today (inbox and assigned)
   - Current inbox count
   - Flagged tasks still incomplete

2. **Pull today's calendar** via M365 MCP:
   - What meetings happened today (subject, attendees)
   - Note any meetings that were cancelled or rescheduled

3. **Check for morning briefing**:
   - Look for `{project-root}/reviews/daily/YYYY-MM-DD.md` or today's morning briefing output
   - If one exists, extract the "Top 3 priorities" that were set this morning
   - These become the cross-reference for what got done vs. what was planned

4. **Present reference data to the controller:**
   ```
   Here's what I can see from today:

   Tasks completed: [list from task management system]
   Tasks created: [list from task management system]
   Meetings: [list from calendar]
   Inbox: X items

   Morning priorities were:
   1. [priority from briefing, or "No morning briefing found"]
   2. ...
   3. ...
   ```

5. **Ask the three capture questions** (one at a time or batched based on controller preference):

   **Q1: "What got done today?"**
   - Let the controller add wins beyond what the task management system shows
   - Capture meeting outcomes, conversations, decisions made
   - Note anything that moved a quarterly rock forward

   **Q2: "What didn't get to?"**
   - Capture items that were planned but not completed
   - Note whether each is a carry-forward or a drop
   - Flag if any are tied to a quarterly rock

   **Q3: "Any blockers or things you're waiting on?"**
   - Capture items that are blocked by other people
   - Note who the blocker is and what's needed
   - Flag anything that should become a delegation or a nudge

6. **Store results** in working memory:
   ```
   capture_data:
     date: YYYY-MM-DD
     completed:
       - task: ...
         source: task-system | controller | meeting
         rock_aligned: true/false
     not_completed:
       - task: ...
         disposition: carry-forward | drop
         rock_aligned: true/false
     blockers:
       - item: ...
         blocked_by: [person]
         action_needed: delegation | nudge | escalation
     inbox_count: N
     morning_priorities_hit: X/3
   ```

---

## SUCCESS METRICS

- Task management data pulled before asking the controller anything
- Morning briefing cross-referenced (if it exists)
- All three questions asked and answered
- Each item captured with disposition (done, carry-forward, drop, blocked)
- Rock alignment noted for completed and incomplete items

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management system unavailable | Ask the controller to list completions manually. Note: "Task management data unavailable." |
| No morning briefing exists | Skip the cross-reference. Note: "No morning briefing to compare against." |
| Controller gives terse answers | Probe once: "Anything else? Meetings, conversations, decisions?" Then accept and move on. |
| Calendar data unavailable | Proceed without it. Note: "Calendar data unavailable — relying on controller recall." |

---

## NEXT STEP

Read fully and follow: `step-02-set-tomorrow.md`

<!-- system:start -->
# Step 06: Set Next Week's Priorities

## MANDATORY EXECUTION RULES

1. You MUST synthesize data from ALL previous steps before proposing priorities. This is the payoff.
2. You MUST propose 3-5 priorities for next week. Not 2. Not 7. Three to five.
3. You MUST connect each priority to a quarterly rock or critical responsibility. If it doesn't connect, challenge it.
4. You MUST get the controller's confirmation on the final priority list.
5. You MUST write the weekly review file before closing. The review is not done until it is written.
6. Do NOT allow the priority list to become a task list. Priorities are outcomes, not activities.

---

## EXECUTION PROTOCOL

**Agent:** Quinn (Strategy)
**Input:** All data from steps 01-05 (wins/misses/themes, rock status, delegation state, inbox/calendar audit, people health)
**Output:** Weekly review file written to `reviews/weekly/YYYY-Wxx.md`, priority list for next week

---

## CONTEXT BOUNDARIES

- Draw from everything surfaced in steps 01-05. This is the synthesis step.
- Priorities should be outcome-oriented: "Close the Confluent QBR prep" not "Work on Confluent stuff."
- Maximum 5 priorities. The controller can do 5 meaningful things in a week. More than that is a wish list.
- Connect every priority to a rock. If a priority doesn't map to a rock, ask: "Is this more important than your rocks right now?"
- Do not create tasks here. Priorities inform task creation, but that happens in the morning briefing.

---

## YOUR TASK

### Sequence

1. **Synthesize the review** using Quinn's voice.
   - Pull together key findings from each step:
     - **Step 01:** Themes from wins and misses
     - **Step 02:** Rock status - which are on track, which need help
     - **Step 03:** Delegation health - any systemic issues
     - **Step 04:** Inbox health and calendar shape for next week
     - **Step 05:** People who need attention

2. **Propose 3-5 priorities for next week.**
   - Each priority should be:
     - Specific and outcome-oriented
     - Connected to a quarterly rock or critical responsibility
     - Achievable in the coming week
     - Informed by what surfaced in the review
   - Present them in priority order.
   - For each, explain why: "This is priority #1 because Rock X hasn't moved in 3 weeks and you have a window on Tuesday."

3. **Validate with the controller:**
   - "Here's what I think next week should be about. What would you change?"
   - Let the controller add, remove, or reorder.
   - Push back if they add too many: "That's 7 priorities. Pick the 5 that matter most. The others can wait."
   - Push back if priorities don't align with rocks: "This doesn't connect to any of your quarterly objectives. Is it really a top-5 for the week?"

4. **Finalize the priority list.**
   - Capture the agreed-upon 3-5 priorities with rock alignment noted.

5. **Write the weekly review file.**
   - Create file at `reviews/weekly/YYYY-Wxx.md` (using current ISO week number).
   - Structure:

   ```markdown
   # Weekly Review — YYYY-Wxx

   ## Wins
   - [from step 01]

   ## Misses
   - [from step 01]

   ## Themes
   - [from step 01]

   ## Rocks Status
   | Rock | Status | This Week | Notes |
   |------|--------|-----------|-------|
   | [from step 02] | | | |

   ## Delegations
   - Active: [count]
   - Overdue: [count]
   - Actions taken: [nudge/escalate/close decisions from step 03]

   ## Inbox Health
   - Items: [count]
   - Oldest: [age]
   - Assessment: [from step 04]

   ## Calendar Next Week
   - Meetings: [count]
   - Prep needed: [list]
   - Concerns: [from step 04]

   ## People
   - [Key observations from step 05]

   ## Next Week's Priorities
   1. [Priority] — connects to [Rock]
   2. [Priority] — connects to [Rock]
   3. [Priority] — connects to [Rock]
   4. [Priority] — connects to [Rock/Responsibility]
   5. [Priority] — connects to [Rock/Responsibility]
   ```

6. **Close the review.**
   - Summarize in 2-3 sentences: the state of the quarter, the state of next week, and the one thing that matters most.
   - End with confidence: "Review complete. Next week is set. Go execute."

---

## SUCCESS METRICS

- 3-5 priorities established and confirmed by the controller
- Every priority connected to a rock or critical responsibility
- Weekly review file written with data from all 6 steps
- Controller leaves the review with clarity on next week

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Controller can't narrow to 5 priorities | Force the choice: "If you could only accomplish 3 things next week, what would they be? Start there." |
| Priorities don't align with any rocks | Challenge directly: "None of these connect to your quarterly objectives. Either the rocks are wrong or the priorities are. Which is it?" |
| Controller wants to skip writing the review file | Push back: "The review file is the artifact. Without it, this conversation evaporates. Takes 30 seconds to write." Write it. |
| Steps 01-05 data is incomplete | Work with what you have. Note gaps in the review file. Recommend closing those gaps before next week's review. |
| Controller is overwhelmed | Simplify: "Forget the list. What's the ONE thing that would make next week a win? Start there. We'll build from it." |

---

## WORKFLOW COMPLETE

The weekly review is done. The review file has been written. Next week's priorities are set.

Post-review actions that may be queued:
- Inbox processing (if inbox was flagged as large in step 04)
- Delegation nudges (from step 03 dispositions)
- 1:1 prep (from step 05 flags)
- Rock-related task creation (from step 02 and step 06)

These are separate workflows. The weekly review surfaces them; other workflows execute them.

---

## Deep Analysis Protocol

This is the most consequential reasoning step in the system — the priority list drives the entire next week. Before proposing priorities in sequence step 2, reason explicitly through competing signals using structured multi-step analysis.

### When to Invoke

After gathering all step 01-05 data and before presenting the priority proposal to the controller.

### Reasoning Chain

Work through these layers in order:

1. **Signal extraction**: What are the strongest signals from each prior step? (Wins/misses themes, rock momentum or stalls, delegation health, calendar shape, people dynamics)
2. **Contradiction check**: Which signals conflict? (e.g., "Rock 1 is stalled BUT there's a major client meeting Tuesday that could unblock it" or "Calendar is packed BUT the most important thing isn't on the calendar")
3. **Rock weighting**: Which rocks need the most attention THIS week based on actual evidence, not just status labels? A "green" rock with no activity in 2 weeks is not green.
4. **Calendar opportunity mapping**: What does next week's calendar create windows for? What does it make impossible?
5. **People factor**: Do any people dynamics change what should be prioritized? (Someone overwhelmed, someone going cold, a key relationship at risk)
6. **Priority synthesis**: Given all the above, what 3-5 outcomes would make next week a win? Rank them with explicit reasoning for why #1 beats #2.
7. **Rock alignment audit**: Does every priority connect to a rock or critical responsibility? If not, challenge it before presenting.

### What This Produces

- A priority list where the reasoning is surfaced, not hidden
- When the controller asks "why is this #1?", the thought chain is available
- Contradicting signals are resolved explicitly, not implicitly averaged away
- The adversarial check ("is this really a priority or just urgent noise?") happens before presentation
<!-- system:end -->

<!-- personal:start -->
## Tool Binding: Structured Reasoning

Use `sequential-thinking` MCP to execute the Deep Analysis Protocol reasoning chain above.
<!-- personal:end -->

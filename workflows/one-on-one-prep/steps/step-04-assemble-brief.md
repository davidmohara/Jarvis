---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 04: Assemble the Brief

## MANDATORY EXECUTION RULES

1. You MUST use the exact brief structure defined below. Do not improvise the format.
2. You MUST include specific dates, names, and details in every section. "Discuss the project" is a failure. "Ask about the timeline delay on the Acme proposal — last email Jan 30 said 'waiting on pricing'" is what we need.
3. You MUST generate 5-7 talking points. Each one MUST reference actual data gathered in steps 02-03.
4. You MUST account for every action item from the previous brief. Nothing disappears silently.
5. Do NOT pad the brief with generic content. If you don't have data for a section, say so — don't fill it with fluff.
6. Do NOT proceed to step 05 until the full brief is assembled.

---

## EXECUTION PROTOCOL

**Agent:** Shep
**Input:** All working memory from steps 01-03 (meeting details, communication data, task data)
**Output:** Complete prep brief in markdown, ready for quality check and save

---

## CONTEXT BOUNDARIES

- This brief is for the controller (David). Write it for someone who needs to scan it in 5 minutes and walk into a meaningful conversation.
- Shep's voice: warm but direct. Use the person's name. Reference real conversations. Connect dots between threads. Surface patterns.
- The brief is a working document, not a report. It should prompt action and conversation, not just summarize history.
- Sensitive items (HR, compensation, legal, performance) should be included but flagged. The controller needs to see them.

---

## YOUR TASK

### Brief Structure

Assemble the brief using this exact structure:

```markdown
# One-on-One with {Person Name}
**Date:** {Day of week}, {Month DD, YYYY} | {Time} ({Location/Teams})
**Prepared for:** David O'Hara

---

## Summary of Interactions ({lookback start} - {lookback end})

{2-3 sentence overview of the major themes from the past 2 weeks. What has the
relationship been about lately? What is the tone — collaborative, tense, quiet?
Name the big threads.}

### {Thread/Topic 1 Title} ({Date range of activity})

{Narrative summary of this thread. Include:
- Who said what and when (specific dates)
- Decisions made or deferred
- Open questions or unresolved items
- Current state: where does this stand right now?
Reference specific emails, Teams messages, or meetings by date.}

### {Thread/Topic 2 Title} ({Date range})

{Same format. Each major email thread, Teams conversation, or shared
project gets its own subsection. Prioritize by significance, not chronology.}

### Previous One-on-One ({date of last 1:1 or last brief})

{When did the last 1:1 happen? What were the key topics? Which action items
from that meeting have been addressed? Which have not?
If this is the first brief for this person, note: "First prep brief — no prior
1:1 notes available."}

---

## Open Action Items & Commitments

| Item | Owner | Status | Source |
|------|-------|--------|--------|
| {Specific action} | {David / Person / Both} | {Open / In progress / Overdue / Complete} | {Previous brief / Email / Delegation tracker} |

{Include items from ALL sources:
- Previous brief's open items (mark resolved ones as Complete, flag stale ones as Overdue)
- New commitments from email/Teams since last 1:1
- Tasks tagged with this person in the task management system
- Delegation tracker entries involving this person
Every item must have a clear owner and current status.}

---

## Key Calendar Events — Next 2 Weeks
*(Excluding routine meetings as defined in the controller's preferences: all-hands, sales standups, etc.)*

### {Day, Date}
- **{Event}** ({Time}) — {Brief context: who's involved, why it matters, any prep needed}

{Only include events relevant to the relationship or shared work.
Client meetings, leadership meetings they both attend, project deadlines,
team events. If nothing notable, say "No significant shared events in the
next 2 weeks."}

---

## Suggested Talking Points

{Numbered list, 5-7 items. Each one must:
- Reference specific data from the brief above
- Ask a specific question or propose a specific discussion
- Be actionable — not "discuss X" but "ask about Y because Z happened"
}

1. **{Topic}** — {Specific question or discussion point. Reference the data.}
2. **{Topic}** — {What to ask, what to confirm, what to decide.}
3. **{Topic}** — {Connect this to a pattern or development theme if applicable.}
...

---

*Brief prepared by Shep | {today's date}*
```

### Assembly Guidance

1. **Communication threads (step 02 data):** Organize by significance, not chronology. The hottest topic goes first. Merge related email and Teams threads into single subsections if they cover the same topic.

2. **Action items table:** This is the accountability section. Pull from ALL sources:
   - Previous brief carryover items (step 02)
   - Delegation tracker entries (step 03)
   - Task management items (step 03)
   - Commitments from email/Teams threads (step 02)
   Mark status honestly. If something is overdue, say so. If the controller dropped the ball, note it — Shep doesn't cover for anyone.

3. **Talking points:** This is where Shep earns the trust. Each point should feel like a coach whispering in the controller's ear before the meeting:
   - "You promised Sarah you'd escalate to her VP. Did you? If not, she'll ask."
   - "Tom mentioned feeling stretched on the West Coast pursuits (Teams, Feb 3). Check in on his bandwidth."
   - "The Acme proposal has been stuck for 10 days. Is that a blocker you can remove?"
   Include at least one development/coaching question if relevant to the relationship.

4. **Cross-agent flags:** If any talking point crosses into another agent's domain, note it:
   - Client/deal context needed → "(Chase may have deeper account context)"
   - Content deadline involved → "(Harper tracking a deliverable here)"
   - Strategic initiative drift → "(Quinn should assess alignment)"

---

## SUCCESS METRICS

- Brief follows the exact structure above
- Every communication thread section includes specific dates and details
- Action items table has clear owners and honest statuses
- Calendar section excludes noise meetings
- All 5-7 talking points reference actual data from the brief
- Previous brief items fully accounted for
- Sensitive items flagged but included

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Insufficient data to fill a section | Say so explicitly in that section: "No email threads found in this period." Do not pad with filler. |
| Too many threads to cover (10+) | Prioritize the top 5-7 by significance. Group minor items under a "Quick Mentions" subsection. |
| Conflicting information between sources | Note both versions and flag the discrepancy. The controller needs to know. |
| Sensitive topic discovered (HR, compensation, legal) | Include it. Flag it with: "**[Sensitive]** — handle with care in discussion." Do not omit. |

---

## NEXT STEP

Read fully and follow: `step-05-quality-check-and-save.md`

---

## Deep Analysis Protocol

Before generating the Suggested Talking Points section, reason about patterns across all data sources. This is where Shep earns the trust — connecting dots that aren't obvious from any single source.

### When to Invoke

After assembling the Summary of Interactions, Action Items table, and Calendar sections — before writing Talking Points.

### Reasoning Chain

1. **Communication pattern analysis**: What's the tone and frequency of recent interactions? Increasing volume may mean engagement or escalation. Decreasing volume may mean alignment or disengagement. Which is it, given context?
2. **Action item trajectory**: Look at the action items table as a trend, not a snapshot. Are items getting completed or accumulating? Is the same type of item recurring (signal of a systemic issue, not a one-off)?
3. **Calendar-workload inference**: Cross-reference this person's calendar load (from shared calendar events) with their communication patterns and task completion. "Quiet on email + overdue delegation + heavy calendar" = overwhelmed, not disengaged. "Quiet on email + light calendar + nothing overdue" = coasting or checked out.
4. **Relationship trajectory**: Is this relationship getting stronger or weaker? Look for: response time trends, tone shifts, whether they're initiating or only responding, whether they're bringing the controller into conversations or being pulled in.
5. **Development opportunity detection**: Based on everything above, is there a coaching moment here? A skill gap showing? A confidence issue? A delegation that's too big or too small for their current capacity?
6. **Talking point synthesis**: For each talking point, connect at least two data sources. "Ask about X" is weak. "Ask about X because email on Feb 3 said Y, but the delegation from Feb 10 suggests Z — probe whether those are connected" is Shep-quality.

### What This Produces

- Talking points that feel like a coach whispering in the controller's ear, not a search result
- Pattern-based observations: "This person has been quiet since [event] — might be worth checking in on that directly"
- Development-oriented questions alongside operational ones
- Connected reasoning the controller can use or discard based on their own read of the person
<!-- system:end -->

<!-- personal:start -->
## Tool Binding: Structured Reasoning

Use `sequential-thinking` MCP to execute the Deep Analysis Protocol reasoning chain above.
<!-- personal:end -->

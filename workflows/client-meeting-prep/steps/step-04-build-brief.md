---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 04: Build the Client Meeting Brief

## MANDATORY EXECUTION RULES

1. You MUST produce a complete brief following the fixed format. Do not skip sections — mark them "N/A" if data is unavailable.
2. You MUST include talking points with clear objectives. "Discuss the project" is not a talking point.
3. You MUST include a Landmines section. If there are no known sensitivities, say so explicitly.
4. You MUST define the desired outcome for this meeting. Every meeting has a purpose — name it.
5. You MUST include handoff routing for any follow-up needs identified during prep.
6. Do NOT pad the brief with filler. If a section is thin, keep it thin. Better to flag a gap than to manufacture content.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Meeting details from step 01, account context from step 02, external research from step 03
**Output:** Complete client meeting brief delivered to the controller

---

## CONTEXT BOUNDARIES

- The brief is a pre-meeting reference document. It should take 3-5 minutes to read.
- Talking points are not a script. They are conversation anchors with specific objectives.
- Landmines are not gossip. They are documented risks: known frustrations, past failures, sensitive topics, political dynamics.
- The desired outcome should be concrete and verifiable after the meeting.

---

## YOUR TASK

### Sequence

1. **Section 1: Meeting Header**
   ```
   # Client Meeting Brief — [Account Name]

   | Field | Detail |
   |-------|--------|
   | Date | YYYY-MM-DD |
   | Time | HH:MM - HH:MM |
   | Location | [physical / Teams / phone] |
   | Purpose | [new-business / active-deal / relationship / renewal / escalation / qbr] |
   | Prepared | YYYY-MM-DD by Chase |

   ### Attendees

   **Client / External:**
   | Name | Title | CRM Record | Last Interaction |
   |------|-------|------------|-----------------|
   | [name] | [title] | Yes/No | YYYY-MM-DD |

   **Internal:**
   | Name | Role | Account Role |
   |------|------|-------------|
   | [name] | [role] | relationship lead / technical / executive |
   ```

2. **Section 2: Account Snapshot**
   ```
   ## Account Snapshot

   | Metric | Value |
   |--------|-------|
   | Account tenure | N years |
   | Lifetime revenue | $X |
   | Active engagements | N ([brief descriptions]) |
   | Account owner | [name] |
   | Industry | [industry] |

   ### Relationship Map
   [Key Internal team <-> Client connections, noting strength and gaps]
   ```

3. **Section 3: Opportunity Status**
   ```
   ## Opportunity Status

   | Opportunity | Stage | Amount | Weighted | Close Date | Next Step |
   |-------------|-------|--------|----------|------------|-----------|
   | [name] | [stage] | $X | $X | YYYY-MM-DD | [step] |

   **Meeting-linked deal:** [name] — [1-2 sentence status summary]
   ```
   If no active opportunities: "No open opportunities. This is a relationship/prospecting meeting."

4. **Section 4: Attendee Profiles**
   ```
   ## Attendee Profiles

   ### [Name] — [Title], [Company]
   - **Background:** [role, tenure, previous companies of note]
   - **Last interaction:** [date, context]
   - **Relationship strength:** [strong / moderate / new / unknown]
   - **Notes:** [recent LinkedIn activity, conversation starters, shared connections]
   ```
   Include a profile for each external attendee. Keep each to 3-5 lines.

5. **Section 5: Recent Activity Summary**
   ```
   ## Recent Activity

   ### Key Email Threads
   - [Date] — [Subject]: [one-line summary, note any open commitments]

   ### Recent Meetings
   - [Date] — [Subject]: [key outcome or decision]

   ### Teams Threads
   - [Date] — [Topic]: [summary]

   ### Unfulfilled Commitments
   - [Commitment] — promised [date], status: [open/overdue]
   ```
   If any commitments are overdue: flag prominently. Walking into a meeting with outstanding promises is a landmine.

6. **Section 6: External Context**
   ```
   ## External Context

   ### Company News (Last 90 Days)
   - [Date] — [Headline] ([source]): [one-line impact summary]

   ### Executive Changes
   - [Name]: [old role] -> [new role] ([date])

   ### Financial Highlights
   [Revenue trend, guidance, stock movement — or "Private company"]

   ### Industry Trends
   - [Trend]: [implication for the conversation]
   ```

7. **Section 7: Talking Points**
   ```
   ## Talking Points

   1. **[Topic]**
      - Objective: [what you want to learn or accomplish with this point]
      - Context: [why this matters, what to reference]
      - Ask: [the specific question or statement]

   2. **[Topic]**
      - Objective: ...
      - Context: ...
      - Ask: ...

   [3-5 talking points, each with a clear objective]
   ```
   Talking points should be ordered by priority. Lead with the most important.

8. **Section 8: Landmines**
   ```
   ## Landmines

   - **[Topic to avoid or handle carefully]:** [why, what happened, how to navigate]
   - **[Known frustration]:** [context and recommended approach]
   ```
   Sources for landmines: escalation history, contentious email threads, CRM notes about complaints, known delivery issues, competitor comparisons gone wrong.
   If no landmines identified: "No known landmines. Standard engagement."

9. **Section 9: Desired Outcome**
   ```
   ## Desired Outcome

   **Primary:** [the one thing that makes this meeting a success]
   **Secondary:** [bonus outcomes if the conversation goes well]

   **Next step to secure before leaving:** [specific next step to propose — e.g., "schedule a follow-up with their CTO" or "send proposal by Friday"]
   ```
   Every meeting must end with a defined next step. If you leave without one, the deal stalls.

10. **Determine handoff routing:**
    ```
    ## Follow-Up Routing

    | Action | Route To | Notes |
    |--------|----------|-------|
    | [action] | [agent/workflow] | [context] |
    ```
    Common routing:
    - Meeting needs a deck or proposal → route to Harper (Communications)
    - Meeting involves team/people topics → check with Shep (People & Leadership)
    - Follow-up tasks generated → route to Chief (Operations) for task tracking
    - Post-meeting CRM update → route to Chief or flag for manual CRM entry

11. **Deliver the complete brief** to the controller.

---

## SUCCESS METRICS

- Complete brief following all 9 sections plus handoff routing
- Talking points are specific with objectives — not generic conversation topics
- Landmines section present (even if empty with explicit "none known")
- Desired outcome defined with a concrete next step to secure
- Every section sourced from actual data — no fabrication
- Brief is readable in 3-5 minutes

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Major data gaps across multiple sections | Deliver what you have. Add a "Data Gaps" section at the top listing what's missing and why. Better to know what you don't know. |
| Account is brand new (no history) | Focus the brief on attendee research, company context, and talking points. Note: "New account — no prior history. This is a discovery conversation." |
| Meeting is tomorrow morning and prep started late | Abbreviate: Meeting Header, Attendee Profiles, 3 Talking Points, Desired Outcome. Skip deep research. Speed over depth. |
| Controller disagrees with talking points | The brief is a recommendation. Controller overrides it. Note any adjusted points for post-meeting learning. |

---

## WORKFLOW COMPLETE

Client meeting brief delivered. No further steps.

### Handoff Rules

| Condition | Route To | Action |
|-----------|----------|--------|
| Meeting needs a deck or proposal | Harper (Communications) | Route content request with deal context, audience, and key messages |
| Meeting involves team or people topics | Shep (People & Leadership) | Check with Shep on org dynamics, team sentiment, or leadership alignment |
| Follow-up tasks generated post-meeting | Chief (Operations) | Capture tasks in task management system, update delegation tracker, schedule next steps |
| Deal status changed based on meeting | Chase (self) | Update pipeline data and trigger pipeline-review if material change |
| Meeting notes need to be filed | Chief (Operations) | Create meeting note in knowledge layer with outcomes and action items |

---

## Deep Analysis Protocol

Before building the Talking Points and Desired Outcome sections (steps 7 and 9 in the sequence), connect external context with internal context into strategic conversation objectives. This is the step that turns a meeting brief from a data dump into a strategic tool.

### When to Invoke

After assembling sections 1-6 (header through external context), before writing Talking Points.

### Reasoning Chain

1. **External signal mapping**: What do the company news, exec changes, and financial signals tell us about where this company is headed? What pain are they likely feeling right now?
2. **Internal signal mapping**: What does the CRM status, relationship history, and activity timeline tell us about where this deal/relationship stands? What has momentum? What's stalled?
3. **Signal connection**: Where do external and internal signals intersect? "Their CTO just changed (external) AND our proposal has been in Negotiation for 30 days (internal) = the new CTO may not know about or support this deal. Objective: get executive alignment before the deal dies in a leadership transition."
4. **Rock alignment**: Which quarterly rocks does this meeting serve? How can the conversation be steered toward outcomes that advance a rock, not just maintain the relationship?
5. **Competitive landscape inference**: Based on external context, is a competitor likely in play? What positioning signals should the controller listen for?
6. **Desired outcome reasoning**: Given all the above, what's the ONE thing that makes this meeting a success? Not "good conversation" — a concrete outcome. And what's the specific next step to propose before leaving?
7. **Landmine cross-check**: Do any of the talking points risk triggering a known landmine? Adjust the approach or add a navigation note.

### What This Produces

- Talking points with clear strategic objectives, not just conversation topics
- A desired outcome that's informed by both external market signals and internal deal dynamics
- Connected reasoning: "Ask about X because external signal Y + internal signal Z suggests this is the window"
- Talking points ordered by strategic value, not just conversation flow
<!-- system:end -->

<!-- personal:start -->
## Tool Binding: Structured Reasoning

Use `sequential-thinking` MCP to execute the Deep Analysis Protocol reasoning chain above.
<!-- personal:end -->

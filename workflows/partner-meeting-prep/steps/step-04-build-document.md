# Step 04: Build the Partner Meeting Prep Document

## MANDATORY EXECUTION RULES

1. You MUST assemble the document using the exact structure specified below.
2. You MUST include intentional blanks throughout -- sections marked for the partner to fill. This is a collaboration tool, not a one-way briefing.
3. You MUST include the account overlap table as the centerpiece, with both Internal Seller and Partner Rep columns.
4. You MUST include the office/space offering section.
5. You MUST include discussion topics with open-ended questions for the partner.
6. You MUST save to the knowledge base at `working directory/{Partner} - {YYYY-MM-DD}.md`.
7. Do NOT fill in partner-side columns with guesses. If you don't know, leave it blank and mark it for the partner.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** All working memory from steps 01-03
**Output:** Complete partner meeting prep document saved to knowledge layer

---

## CONTEXT BOUNDARIES

- This step is assembly and quality-check only. Do not make new data calls.
- The document is designed to be SHARED with the partner team. Write accordingly -- professional, collaborative tone.
- Intentional blanks are a feature, not a bug. The partner filling in their side is part of the value.
- Use Chase's voice for internal notes (talking points, strategy). Use neutral professional voice for the shareable sections.

---

## YOUR TASK

### Document Structure

Assemble the document using this structure:

```markdown
# {Partner} {Meeting Type} -- {Region/Scope}
**Meeting Prep -- One-Pager**

## Meeting Details

| | |
|---|---|
| **Date** | {Day}, {Month DD, YYYY} |
| **Time** | {Time} {Timezone} |
| **Location** | {Venue / Teams link} |
| **Format** | {QBR, co-sell planning, intro presentation, etc.} |
| **Partner Host** | {Name, Title} ({email}) |
| **Partner CC** | {Name} ({email}) |

## {Controller's Org} Attendees & Roles

| Name | Title | Covering |
|------|-------|----------|
| {Name} | {Title} | {What they'll present or cover} |

## {Controller's Org} Presence & Resources

{Controller's org} maintains offices and teams across {region} that are available
for joint events, workshops, and co-working:

| Location | Office | Available For |
|----------|--------|---------------|
| {City} | {Office name/address} | Workshops, lunch & learns, co-working, client events |

**We're happy to host partner events, joint workshops, or client meetings
at any of our locations.**

## Priority Accounts

### Group 1: Active Relationships (Joint Opportunity)

Accounts where {controller's org} has existing engagement and can drive joint impact
with {Partner}:

| Account | {Controller's Org} Seller | Partner Rep | Notes |
|---------|--------------------------|-------------|-------|
| {Account} | {Seller name} | {TBD - partner to fill} | {Engagement status, opportunity, key contacts} |

### Group 2: Target Accounts (Joint Pursuit)

Accounts {controller's org} is actively pursuing where {Partner} could accelerate access:

| Account | {Controller's Org} Seller | Partner Rep | Notes |
|---------|--------------------------|-------------|-------|
| {Account} | {Seller name} | {TBD - partner to fill} | {Pursuit status, what would help} |

### Group 3: Partner Accounts ({Controller's Org} Can Help)

Accounts where {Partner} has relationships and {controller's org} can add value:

| Account | {Controller's Org} Seller | Partner Rep | Notes |
|---------|--------------------------|-------------|-------|
| {TBD - partner to fill} | {TBD} | {Partner rep} | {TBD - partner to fill} |

## Upcoming Events

Events where joint presence, co-sponsorship, or client invitations could
create value. **Partner team: please add your events.**

### {Controller's Org} Events

| Event | Date | Location | Opportunity for {Partner} |
|-------|------|----------|---------------------------|
| {Event name} | {Date} | {City} | {Co-present, invite clients, sponsor, etc.} |

### {Partner} Events

| Event | Date | Location | Opportunity for {Controller's Org} |
|-------|------|----------|-------------------------------------|
| {TBD - partner to fill} | | | |

### Industry Events (Both Attending)

| Event | Date | Location | Notes |
|-------|------|----------|-------|
| {Event name} | {Date} | {City} | {Joint plans, booth sharing, client dinners} |

## Partner News & Updates

{3-5 bullet points of recent partner news with relevance to the relationship.}
{If none found: omit this section.}

## Discussion Topics

{Prepared questions -- a mix of strategic and tactical, with INTENTIONAL open-ended
questions for the partner to drive:}

1. {Specific topic with context}
2. {Account-specific question: "What are you seeing at {Account X}?"}
3. {Strategic question: "What's your priority for {next quarter}?"}
4. {Collaboration question: "Where do you see the best joint opportunity?"}
5. {Open: "What should we know about your roadmap?"}

## Action Items from Previous Meeting

{If prior notes exist: list action items and their status.}
{If no prior meeting: "First structured partner prep -- no prior action items."}

## Background & Relationship History

{How the relationship started, key milestones, previous meeting outcomes.}
{If first meeting: brief context on why this meeting is happening.}

## Important Notes

{Sensitive context: personnel changes, competitive dynamics, losses,
org changes, relationship dynamics to be aware of.}
{If none: omit this section.}
```

### Assembly Rules

1. **Account overlap table is THE artifact.** Spend the most care here. Every account should have:
   - Account name (verified against CRM where possible)
   - Controller's seller name (never blank for known accounts)
   - Partner rep column (blank is fine -- that's the point)
   - Meaningful notes (not just "active" -- what's the status, what's the opportunity)

2. **Discussion topics must be specific.** Not "discuss accounts" but "What are you seeing at AT&T since their reorg?" Reference actual data from steps 01-03.

3. **Intentional blanks are marked clearly.** Use `{TBD - partner to fill}` for partner-side data. Use the phrase "Partner team: please add/share..." for sections they should populate.

4. **Events have specific collaboration framing.** Not "both attending SXSW" but "SXSW -- joint client dinner opportunity, we have 6 mutual accounts in Austin."

5. **Previous meeting action items carry forward.** If a prior prep doc exists, extract the action items and note which are complete vs. outstanding. Outstanding items become discussion topics.

### Quality Checks

Before saving, verify:

- [ ] Meeting details complete (date, time, location, contacts)
- [ ] Account tables include Seller column for every known account
- [ ] Partner Rep columns present and clearly marked for partner to fill
- [ ] Group 3 exists with explicit invitation for partner input
- [ ] Events include both sides' tables
- [ ] Office/space offering included with relevant locations
- [ ] Discussion topics reference actual data (not generic)
- [ ] Intentional blanks are clearly marked
- [ ] Previous meeting action items included (if applicable)
- [ ] Sensitive notes included where relevant
- [ ] No stale data -- account statuses verified against CRM if possible

### Save and Deliver

1. **Save to knowledge base:** `working directory/{Partner} - {YYYY-MM-DD}.md`
2. **Open in knowledge base:** present the file to the controller
3. **Present summary to the controller:**
   ```
   Your {Partner} meeting prep is ready.

   Key numbers:
   - {N} accounts in the overlap table ({X} active, {Y} target, {Z} for partner to fill)
   - {N} events identified for joint planning
   - {N} discussion topics queued

   {One sharp insight: the single most important thing to know going in.}
   ```
4. **If shareable version needed:** Generate PDF via `npx md-to-pdf`

---

## SUCCESS METRICS

- Document assembled in the exact structure above
- Account overlap table complete with all three groups
- Intentional blanks present and clearly marked
- Discussion topics specific and data-backed
- Document saved to knowledge base
- Summary delivered to controller with key numbers

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Thin data across all sections | Deliver what you have. Be honest: "Data is thin on this partner. The meeting itself is the discovery opportunity. Here's the framework -- it'll be more valuable after the conversation." |
| Knowledge base save fails | Present the document inline. Offer to retry save or output as file. |
| Previous prep doc can't be read | Omit the action items section. Note: "Prior prep doc found but unreadable. Recommend reviewing manually before the meeting." |

---

## HANDOFF

After the document is delivered:

- If an account needs deeper strategy (large deal, competitive situation) --> route to **Chase** account-strategy task
- If the partner relationship involves executive engagement (C-level introductions, sponsor alignment) --> flag for **Shep**
- If follow-up actions were identified (emails to send, meetings to schedule) --> route to **Chief** for task tracking
- If the meeting requires a presentation or deck --> hand to **Harper**

---

## WORKFLOW COMPLETE

The partner meeting prep document has been delivered. The controller reviews, adjusts, and optionally shares with the partner team before the meeting.

# Step 04: Synthesize Briefing

## MANDATORY EXECUTION RULES

1. You MUST deliver the briefing in the exact format specified below. No freestyle.
2. You MUST lead with the most urgent items — overdue commitments first, always.
3. You MUST keep the briefing scannable in under 2 minutes. Bullets and tables. No paragraphs.
4. You MUST end with "What do you want to tackle first?"
5. Do NOT include data you don't have. If a source was unavailable, omit that section with a one-line note.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** All working memory from steps 01-03
**Output:** Structured morning briefing delivered to the controller

---

## CONTEXT BOUNDARIES

- This step is synthesis only. Do not make new data calls.
- Use Chief's voice: direct, efficient, occasionally sharp. No filler. No pleasantries beyond the opening line.
- The briefing is the deliverable. It should stand alone — the controller should not need to ask follow-up questions to understand their day.

---

## YOUR TASK

### Briefing Format

Deliver the briefing using this structure exactly:

```
## Morning Briefing — {Day of Week}, {Month DD, YYYY}

{One sharp opening line. State the shape of the day.}
{Example: "5 meetings, 2 need prep, 1 overdue delegation. Let's go."}

---

### Rocks — Q{N} {Year}

| Rock | Status |
|------|--------|
| {Rock 1 name} | {1-line status} |
| {Rock 2 name} | {1-line status} |
| ... | ... |

---

### Today's Calendar

| Time | Meeting | Context |
|------|---------|---------|
| {HH:MM} | {Subject} | {1-line: type, key attendee, or prep note} |
| ... | ... | ... |

{If back-to-back or 3+ video calls, add a warning line here.}

---

### Priority Actions

{Bulleted list. What MUST happen today. Derived from:}
{- Tasks due today}
{- Flagged tasks}
{- Items carried forward from yesterday's top 3}
{- Time-sensitive meeting prep}

---

### Delegations

| Item | Owner | Status |
|------|-------|--------|
| {Overdue items first, with days late} | {Name} | OVERDUE ({N} days) |
| {Due today items} | {Name} | Due today |

{If no overdue or due-today delegations: "All delegations on track."}

---

### Inbox & System

- **Task inbox:** {N} items {oldest: N days}
- **Yesterday's review:** {Completed | Missing}

---

### Relationships (Clay)

{Only include if Clay returned reminders, birthdays, or cold-contact flags.}
- **Upcoming birthdays:** {Name — date}
- **Reminders due:** {reminder text — contact name}
- **Going cold:** {contacts flagged with 60+ days no interaction who are strategically important}

{If nothing from Clay: omit this section entirely.}

---

### Card Alerts

{Only include if credit card deadlines or unused benefits were flagged in step 03.}
- **Expiring:** {credit name} — ${amount remaining} — {deadline}
- **Action needed:** {e.g., "Activate Discover Q2 categories by Apr 1"}
- **Offers expiring:** {vendor} — {card} — {value} — {days left}

{If nothing flagged: omit this section entirely.}

---

### Flags

{Anything that needs immediate attention. Examples:}
{- Meeting in < 60 min with no prep}
{- Overdue delegation > 3 days}
{- Inbox > 20 items}
{- 3+ video calls today}
{- Yesterday's review missing}
{If nothing to flag: "Nothing urgent. Clean day ahead."}

---

What do you want to tackle first?
```

### Synthesis Rules

1. **Priority ordering within sections:**
   - Calendar: chronological
   - Priority actions: urgency then importance
   - Delegations: overdue first (sorted by days late descending), then due today

2. **Context compression:**
   - Meeting context is 1 line max. Not a paragraph.
   - Rock status is 1 line max. Not a progress report.
   - Delegation notes are the status column only.

3. **Handoff flags** (embed in context column or flags section):
   - Client meeting today with thin context → "Recommend: run Chase prep"
   - 1:1 today with thin context → "Recommend: run Shep prep"
   - Content deadline approaching → "Flag for Harper"
   - Goal drift visible → "Escalate to Quinn"
   - Card benefit expiring within 7 days → "Chase card alert: [credit] expires [date]"

4. **Omit empty sections** rather than showing "None" — except Flags, which should always appear (either with items or "Nothing urgent. Clean day ahead.").

---

## SUCCESS METRICS

- Briefing delivered in the exact format above
- Scannable in under 2 minutes
- Most urgent items appear first in every section
- Handoff recommendations included where appropriate
- Ends with "What do you want to tackle first?"

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Missing calendar data | Omit Today's Calendar section. Add to Flags: "Calendar data unavailable — check manually." |
| Missing task data | Omit Priority Actions section. Add to Flags: "Task management system unavailable — task data missing." |
| All data sources failed | Deliver a minimal briefing: rocks + delegation tracker (read directly) + "Multiple data sources unavailable. Recommend manual check." |

---

## WORKFLOW COMPLETE

The morning briefing has been delivered. The controller drives from here.

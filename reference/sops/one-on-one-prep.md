# SOP: One-on-One Prep Brief

**Scope**: Internal Improving meetings only (David's direct reports, peers, leadership). Not for external/client meetings.

**Trigger**: David has an upcoming 1:1 with an Improver. Either requested explicitly or proactively prepared as part of daily/weekly prep.

**Output**: A prep brief saved to `zzClaude/Cowork/{Person Name} - {YYYY-MM-DD}.md` in Obsidian.

---

## Step 1: Identify the Meeting

Gather from calendar (via M365 MCP):
- **Who**: Full name of the person
- **When**: Date, time, duration
- **Where**: Teams, in-person, phone
- **Recurrence**: Is this a regular 1:1? (check auto-memory for cadences)

## Step 2: Gather Raw Data

Pull from the last 2 weeks (since the previous 1:1) across these sources:

| Source | Method | What to Look For |
|--------|--------|-------------------|
| Email threads | M365 MCP | Direct exchanges, forwarded items, action requests |
| Calendar | M365 MCP | Shared meetings, upcoming events involving both |
| Teams messages | M365 MCP | Chat threads, channel mentions |
| OmniFocus | osascript (Code) | Tasks tagged with person's name, delegated items |
| Obsidian vault | MCP (Code) | Person files, project notes, previous prep briefs |
| Previous prep brief | Obsidian `zzClaude/Cowork/` | Last brief's open items and talking points |

**M365 MCP search scope:**
- Email threads with [Person Name] from [2 weeks ago] to today
- Calendar events both attended or are both attending in next 2 weeks
- Teams direct messages and channel threads
- Exclude: "Come Together", "Sales 2.0", "Sales & Recruiting Meeting", "Improving Dallas Scrum", "Improving Daily Bench Report"

## Step 3: Assemble the Brief

Use this structure:

```markdown
# One-on-One with {Person Name}
**Date:** {Day of week}, {Month DD, YYYY} | {Time} ({Location/Teams})
**Prepared for:** David O'Hara

---

## Summary of Interactions ({date range})

{2-3 sentence overview of the major themes from the past 2 weeks.}

### {Thread/Topic 1 Title} ({Date range of activity})

{Narrative summary of this thread. Include key decisions, questions raised,
responses given, and current state. Name specific documents, amounts,
or details — don't be vague.}

### {Thread/Topic 2 Title} ({Date range})

{Same format. Each major email thread, Teams conversation, or shared
project gets its own subsection.}

### Previous One-on-One ({date})

{Note when the last 1:1 occurred and any carryover items.}

---

## Open Action Items & Commitments

| Item | Owner | Status |
|------|-------|--------|
| {Specific action} | {David / Person / Both} | {Open / In progress / Pending / Due date} |

{Include items from:}
- Previous brief's open items (check if resolved)
- New commitments made in email/Teams since last 1:1
- OmniFocus tasks tagged with this person
- Delegated items from delegations/tracker.md

---

## Key Calendar Events — Next 2 Weeks
*(Exclude routine meetings like Come Together, Sales & Recruiting, etc.)*

### {Day, Date}
- **{Event}** ({Time}) — {Brief context, who's involved, why it matters}

{Only include events relevant to the relationship or shared work.
Flag customer meetings, leadership meetings they both attend,
and deadlines.}

---

## Suggested Talking Points

{Numbered list, 5-7 items. Each one:}
1. **{Topic}** — {Specific question or discussion point. Reference the data.
   Don't just say "discuss X" — say what to ask, what to confirm, what to decide.}
```

## Step 4: Quality Checks

Before saving, verify:

- [ ] Every interaction thread has specific dates, names, and details (no vague summaries)
- [ ] Action items have clear owners and statuses
- [ ] Previous brief's open items are accounted for (resolved, carried forward, or escalated)
- [ ] Talking points reference actual data, not generic topics
- [ ] Calendar section excludes routine/excluded meetings per the prompt template
- [ ] No sensitive items are included without appropriate context (legal, HR, compensation — flag these but include them; David needs to see them)
- [ ] Tone is direct and useful, not padded

## Step 5: Save and Notify

1. Save to Obsidian: `zzClaude/Cowork/{Person Name} - {YYYY-MM-DD}.md`
2. Open in Obsidian: `show_file_in_obsidian`
3. Tell David: "Your {Person Name} 1:1 brief is ready. {One-line summary of the hottest topic}."

---

## Excluded Meetings (from prompt template)

These recurring meetings are noise for 1:1 prep — always exclude:
- Come Together
- Sales 2.0
- Sales & Recruiting Meeting
- Improving Dallas Scrum
- Improving Daily Bench Report

## Known Cadences

| Person | Meeting | Day |
|--------|---------|-----|
| Scott McMichael | one-on-one Scott McMichael | Thursdays |
| Ilse Perez | Touchpoint & Weekly Review | Fridays |
| Don McGreal | One-on-One with McGreal | Varies |
| Robyn Fuentes | (as needed) | — |
| Diana Stevens | (as needed) | — |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-11 | Initial SOP created from Scott McMichael 2026-02-12 brief example |

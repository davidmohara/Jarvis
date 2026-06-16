# Skill: 1:1 Prep
**Owner:** Shep  
**Trigger:** `1:1` / "prep for my 1:1 with [name]" / "build a 1:1 prep sheet for [name]"  
**Output format:** Markdown (`.md`) — vault-destined, never HTML or PDF  
**Output path:** `meetings/YYYY-MM-DD-{firstname}-{lastname}-1on1.md`

---

## Purpose

Build a substantive, research-backed prep sheet for an upcoming 1:1 with a direct report or internal stakeholder. The output must reflect real open threads, real recent interactions, and real action items — not generic placeholders. Every section must be earned by reading actual data sources.

This skill is for **internal 1:1 meetings only.** For external client or prospect meetings, route to Chase (`chase-call-prep` skill).

---

## Required Output Format

The output must exactly match the format established in `meetings/2026-03-03-mcgreal-1on1.md` and `meetings/2026-03-20-tim-rayburn-1on1.md`. Do not deviate. Do not use the five-section external call prep template.

### Section Order (mandatory)

```
# One-on-One with [Full Name]
**Date:** [Weekday, Month DD, YYYY] | [HH:MM AM/PM CT] ([Medium])
**Prepared for:** David O'Hara

---

## Summary of Interactions ([Date Range])

[2–4 sentence paragraph establishing overall pattern of recent interactions.
Named threads, key context, volume and nature of work together.]

### [Thread Name] ([Date Range])

[Full paragraph per thread. Named participants, what was discussed,
what was decided, what is still open. No bullet lists — prose only.
End with a bolded STATUS note if the thread is unresolved.]

### [Thread Name] ([Date Range])

[Repeat for each significant thread from the research window.]

---

## Open Threads Requiring Action

### [N]. ⚠️ [Short Thread Title] ([STATUS LABEL])

**Status**: [One-line state of play]
- [What happened]
- [What was said or decided]
- **Action needed**: [Specific action David must take]

[Repeat for each open item, numbered, with ⚠️ emoji]

---

## Open Action Items & Commitments

| Item | Owner | Status |
|------|-------|--------|
| [Action item] | [Name] | [Open / In Progress / **Open — today**] |

---

## Key Calendar Events — Next 2 Weeks
*(Optional — include only if there are notable upcoming events relevant to this person)*

### [Day, Month DD]
- **[Event Name]** ([Time]) — [Brief context]

---

## Suggested Talking Points

1. **[Bold lead sentence]** — [Supporting context and suggested framing. One short paragraph per point, tied directly to an open thread above. Never generic.]

2. **[Bold lead sentence]** — [...]

[4–7 talking points total]
```

### Format Rules

- **Prose, not bullets.** Interaction threads are paragraphs. Talking points are sentences. The only bullet lists allowed are inside "Open Threads Requiring Action" sub-items and the action items table.
- **⚠️ emoji** on every open thread that requires David's action.
- **STATUS labels** in parentheses after thread titles: `(NEEDS RESPONSE)`, `(UNREAD)`, `(IN PROGRESS)`, `(VERIFY)`, `(OPEN)`.
- **Bold "Action needed:"** at the end of every open thread that has a clear next step for David.
- **Talking points are tied to threads.** Never add a generic talking point that doesn't trace back to a real open item or interaction.
- **No prohibited sections:** No "Background / Who is X" preamble unless the person is new. No "Next Steps" section. No standalone "Notes" section. No "Proposed Agenda." No "Improving's Position."

---

## Research Sequence

Complete all searches before writing a single word of output. Do not draft from memory.

### Step 1: M365 Email (Primary Source)

Search for all email threads between David and the person, last 30 days minimum, extending to 60 days if recent volume is low.

```
mcp__b8c41a14-7a9b-4ea5-ab12-933ee04bc52f__outlook_email_search
  query: "from:{person} OR to:{person}"
  date range: last 30–60 days
```

**Extract from each thread:**
- Subject / topic
- Who initiated
- What was asked, proposed, or decided
- Whether a response is still needed (flag ⚠️)
- Any delegations or commitments made

### Step 2: M365 Calendar

Pull all shared calendar events and 1:1 meetings in the last 30–60 days.

```
mcp__b8c41a14-7a9b-4ea5-ab12-933ee04bc52f__outlook_calendar_search
  attendee: {person's email}
  date range: last 30–60 days + next 14 days
```

**Extract:**
- Dates and topics of past 1:1s (to establish cadence and last touchpoint)
- Any upcoming shared events in the next 2 weeks (for Key Calendar Events section)
- Meetings where this person was included on a relevant client or project topic

### Step 3: Obsidian Vault

Search the knowledge layer for prior 1:1 notes, coaching observations, and project mentions.

```
mcp__obsidian-local__search_vault_simple
  query: "{person's first name} {person's last name}"
```

Also check:
- `memory/episodic/people/` for any people profiles
- `memory/episodic/coaching/` for prior coaching notes
- Any prior `meetings/YYYY-MM-DD-{name}-1on1.md` files to find unresolved items from past preps

### Step 4: OmniFocus Tasks

Check for any tasks assigned to or delegated to this person, or tasks David owns that relate to them.

```
mcp__Control_your_Mac__osascript
  [AppleScript: filter OmniFocus for tasks containing person's name or associated project]
```

Flag anything overdue or approaching due date.

### Step 5: M365 Teams Chat (if available)

```
mcp__b8c41a14-7a9b-4ea5-ab12-933ee04bc52f__chat_message_search
  query: "{person's name}"
  date range: last 30 days
```

Extract significant decisions, requests, or action items from chat history.

### Step 6: reMarkable Notes (if available)

Check if any prior 1:1 handwritten notes exist that were synced via Knox. Search Obsidian for any Knox-imported notes tagged with this person's name.

---

## Pre-Write Gate

Before generating output, verify:

- [ ] M365 email search returned results (not just empty)
- [ ] Calendar search confirmed last 1:1 date and any upcoming events
- [ ] At least 2 named threads identified with enough detail to write prose summaries
- [ ] Action items table has at least 1 real item (not a placeholder)
- [ ] Talking points map 1:1 to identified open threads (no invented points)

If research returned thin results (< 2 threads, no recent contact), surface this to David before proceeding:
> "[Shep]: I found limited recent interaction with [Name] — only [N] email threads in the last 30 days and no prior 1:1 notes. I can build a prep sheet from what's here, but it will be thin. Want me to extend the search window or proceed with what's available?"

---

## Post-Write Validation Checklist

Run this check against the draft before delivering:

- [ ] **Format match**: Does the output match the mcgreal/tim-rayburn structure exactly? Header → Summary paragraph → Named threads with STATUS → Open Threads with ⚠️ → Action Items table → (optional Calendar Events) → Talking Points
- [ ] **No prohibited sections**: External call sections (Background, Company Overview, Improving's Position, Proposed Agenda) are absent
- [ ] **Prose threads**: Interaction threads are paragraphs, not bullet lists
- [ ] **⚠️ on every unresolved item**: Any thread needing David's action has the emoji and a bolded "Action needed:" line
- [ ] **Talking points are earned**: Each talking point traces to a named open thread — delete any that don't
- [ ] **No em dashes**: Replace all `—` with `:` or restructure the sentence
- [ ] **No first-person hedging**: "it appears", "it seems", "I believe" — cut these. State what the data shows
- [ ] **Named people**: Every person mentioned is referred to by name, not "the stakeholder" or "your contact"
- [ ] **Date range in header**: "Summary of Interactions (Apr 15 – Jun 15, 2026)" must reflect the actual research window
- [ ] **Action items have owners**: No action item in the table is ownerless

---

## Person-Specific Data Requirements

Some direct reports have mandatory data pulls that must be included in every 1:1 prep regardless of whether those topics appear in recent email threads. Treat these as additional research steps that run after the standard sequence.

### Robyn Fuentes — South Texas Market

Pull current South Texas pipeline and revenue data from PowerBI before writing the prep sheet.

**Revenue data** — Improving Enterprise Scorecard v4:

Check Obsidian cache first:
```
find memory/episodic/ -name "revenue-tracker-*.md" | sort -r | head -1
```
If cache exists and is within 30 days of today: use it. Skip PowerBI.
If stale or missing: open PowerBI via Chrome:
```
URL: https://app.powerbi.com/groups/me/reports/ff2db561-1548-4c6f-ae43-a3a927bd73e3/3c7c59c7edecc090aa27?experience=power-bi
Tool: mcp__Control_Chrome__open_url → mcp__Control_Chrome__get_page_content
Filter: South Texas region
Extract: MTD revenue, QTD revenue, vs. target
```

**Partner/co-sell pipeline** — Improving Sales Analytics:

Check Obsidian cache first:
```
find memory/episodic/ -name "co-sell-pipeline-*.md" | sort -r | head -1
```
If cache exists and is within 7 days of today: use it. Skip PowerBI.
If stale or missing: open PowerBI via Chrome:
```
URL: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/8a62865681ae18b5ec9b?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
Filter: Houston + South Texas (pull Dallas, Austin, Houston individually — do NOT use United States scope)
Extract: Partner pipeline by partner (Microsoft, Confluent, etc.), open opps, won revenue
```

Include as a standing section in the prep sheet:
- **Revenue:** MTD and QTD South Texas actuals vs. target
- **Pipeline:** Active South Texas pursuits — account, stage, estimated value, next action
- **Partner sales:** Partner-sourced pipeline in South Texas — partner name, deal stage, value

If PowerBI is inaccessible (login required, Chrome unavailable), note explicitly: "PowerBI unavailable this session — pull South Texas revenue and partner pipeline from Robyn directly."

### Don McGreal — Dallas Market

Pull current Dallas pipeline and revenue data from PowerBI before writing the prep sheet. Use the same two PowerBI reports as Robyn (Enterprise Scorecard v4 for revenue, Sales Analytics for co-sell), filtered for Dallas region.

**Revenue data:**

Check Obsidian cache first:
```
find memory/episodic/ -name "revenue-tracker-*.md" | sort -r | head -1
```
If within 30 days: use it. If stale or missing, open PowerBI:
```
URL: https://app.powerbi.com/groups/me/reports/ff2db561-1548-4c6f-ae43-a3a927bd73e3/3c7c59c7edecc090aa27?experience=power-bi
Filter: Dallas region
Extract: MTD revenue, QTD revenue, vs. target
```

**Partner/co-sell pipeline:**

Check Obsidian cache first:
```
find memory/episodic/ -name "co-sell-pipeline-*.md" | sort -r | head -1
```
If within 7 days: use it. If stale or missing, open PowerBI:
```
URL: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/8a62865681ae18b5ec9b?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
Filter: Dallas (pull Dallas individually — do NOT use United States scope)
Extract: Microsoft Partner GTM activity — PAL-tagged accounts, co-sell pipeline, partner-sourced deals
```

Include as a standing section:
- **Revenue:** MTD and QTD Dallas actuals vs. target
- **Pipeline:** Active Dallas pursuits — flag any F500 or dormant account reactivation (Don runs the weekly Sales Prospecting cadence)
- **Partner sales:** Dallas Microsoft Partner GTM activity — co-sell pipeline, PAL-tagged accounts, partner-sourced deals

If PowerBI is inaccessible, note explicitly: "PowerBI unavailable this session — pull Dallas revenue and partner pipeline from Don directly."

---

## Output Delivery

1. Write the file to `meetings/YYYY-MM-DD-{firstname}-{lastname}-1on1.md`
2. **Do not create a PDF.** This is a vault-destined Markdown file.
3. **Do not push to reMarkable.** 1:1 preps stay in the vault.
4. Present the file via `mcp__cowork__present_files`
5. Write a working memory entry to `memory/working/` confirming the prep was built, which threads were found, and any flags

---

## Common Errors to Avoid

| Error | Symptom | Correction |
|-------|---------|------------|
| Wrong template | Output has "Company Overview", "Proposed Agenda", or five external sections | Delete entirely, restart with correct format |
| Skipped research | Threads are vague or generic | Run full M365 search before writing |
| Bullets in threads | Interaction summaries use bullet lists instead of prose paragraphs | Rewrite as prose |
| Missing ⚠️ | Unresolved threads have no emoji or action needed | Add emoji and action |
| No source for talking point | Talking point that doesn't match any thread | Delete the talking point |
| Em dashes | `—` appearing anywhere in output | Replace or restructure |
| PDF generated | A `.pdf` was created alongside or instead of `.md` | Remove PDF, markdown only |

---

## SKILL COMPLETE

After delivering the prep sheet and writing the working memory entry, write the skill-run signal file:

**Path:** `systems/eval-harness/skill-runs/shep-1on1-prep-latest.json`

```json
{
  "skill": "shep-1on1-prep",
  "agent": "shep",
  "trigger": "<the name or trigger phrase used>",
  "started": "<ISO 8601 local timestamp at skill start>",
  "completed": "<ISO 8601 local timestamp at skill end>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": [],
  "person": "<full name of the person the prep was built for>",
  "output_file": "<relative path to the written .md file>"
}
```

If the skill failed (research returned no results and David declined to proceed, file write error, etc.), set `"status": "failure"` and populate `"error_ids"` with any logged error IDs.

Do not skip this write. The eval harness uses this file to confirm the skill ran.

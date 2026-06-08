# Skill: Call & Meeting Prep

**Skill ID:** `chase-call-prep`
**Owning Agent:** Chase
**Model:** sonnet
**Trigger Keywords:** `call prep`, `meeting prep`, `prep for`, `prep me for`, `prep my call`, `client prep`, `partner prep`, `prospect prep`

---

## Purpose

Produce a structured, pre-meeting prep sheet for any external call or client meeting. The output is always a Markdown file (vault-destined) using the canonical five-section template. This skill covers two contexts — same template, different depth:

| Context | When to Use | Depth Guidance |
|---------|-------------|----------------|
| **Call Prep** | First call, prospect, cold or warm intro, partner discovery | Research-heavy. Background/history section is the primary anchor. Company section is full. Agenda is exploratory. |
| **Meeting Prep** | Existing client or partner with deal context, follow-on meeting | Context-heavy. Lead with relationship history. Company section can be brief if well-known. Agenda is more specific. |

The template does not change between contexts. Depth and emphasis do.

---

## Canonical Template

Every prep sheet Chase produces MUST follow this structure exactly — five sections, in this order, no additions, no omissions.

### Section 1: Background / History

**What goes here:** Biographical and professional background on the external person(s) attending the meeting. Current role, career trajectory, relevant experience, any known relationship context with David or Improving.

**Exclusions:**
- Do NOT include background on Improving staff
- Do NOT include background on David
- Do NOT include background on people David already has an established relationship with (use relationship context in Improving's Position instead)
- If all attendees are internal, omit this section and note why

**Research source priority (Section 1):**
1. **LinkedIn** — primary source. Career history, current role, tenure, shared connections, recent activity.
2. **CRM** — check for any prior engagement history, past proposals, or deal context with Improving.
3. **Clay (Mesh)** — supplemental only. Use after LinkedIn and CRM are exhausted to fill gaps or add color from David's personal relationship data. Do not present Clay data as authoritative professional background.

**Depth by context:**
- Call Prep: Full research. Work through sources in priority order above. Surface anything that creates rapport or credibility.
- Meeting Prep: Shorter. Refresh only — what's changed since last touchpoint, any new signals.

---

### Section 2: Company Overview

**What goes here:** Overview of the external company — what they do, size/scale, industry position, relevant technology landscape, any known initiatives or pressures relevant to this meeting.

**Exclusions:**
- Do NOT include an overview of Improving
- Do NOT include an overview of companies David is otherwise affiliated with (subsidiaries, known partners where the relationship is already well-established)

**Research source priority (Section 2):**
1. **Company's own website** — primary source. Homepage, About, product/service pages, leadership, recent announcements.
2. **Web search** — news, press releases, analyst coverage, funding events, strategic moves.
3. **CRM** — prior Improving engagement history with this company, past proposals, account notes.
4. **Clay (Mesh)** — supplemental only. Use after the above are exhausted to surface any additional context David may have captured. Do not treat Clay as an authoritative company overview source.

**Depth by context:**
- Call Prep: Full overview. Work through sources in priority order above. Research recent news, tech stack signals, strategic priorities.
- Meeting Prep: Brief. Focus on what's changed since last meeting — new initiatives, org changes, competitive pressures.

---

### Section 3: Improving's Position

**What goes here:** What Improving brings to this specific meeting or relationship. Always present. Frame it relative to the external party's context established in Sections 1-2. Include:
- Relevant capabilities, practices, or offerings that apply to this account
- Prior engagement history if any exists (past projects, proposals, conversations)
- Any competitive considerations (where we win, where we're at risk)
- The specific value narrative for this meeting — what problem are we solving or advancing?

---

### Section 4: Proposed Agenda

**What goes here:** A suggested, timed agenda for the meeting. Framed as a proposal — not a script. David adapts it in the room.

Format: bullet list with time allocations. Total time must match the scheduled meeting length.

Example format:
```
- 0:00–0:05  Introductions / context setting
- 0:05–0:20  [Topic 1]
- 0:20–0:35  [Topic 2]
- 0:35–0:50  [Topic 3]
- 0:50–0:60  Next steps / close
```

**Depth by context:**
- Call Prep: Agenda is exploratory — discovery-oriented, open questions, room to go where the conversation leads.
- Meeting Prep: Agenda is specific — advances the deal or deepens the relationship toward a concrete outcome.

---

### Section 5: Talking Points

**What goes here:** 4-6 focused talking points David should hit during the meeting. Not a script — these are the ideas, hooks, or assertions worth making.

Each talking point is 1-3 sentences: the point itself plus brief supporting context. No more than 6. Fewer is better if they're sharp.

**Depth by context:**
- Call Prep: Points should open doors — curiosity-driven, positioning Improving without overselling.
- Meeting Prep: Points should advance the deal — concrete, specific, tied to the opportunity at hand.

---

## What Does NOT Belong in a Prep Sheet

The following sections are categorically prohibited. Do not add them under any circumstances, even if they seem helpful:

| Prohibited Section | Why |
|-------------------|-----|
| Action Items | Post-call artifact. Nothing to act on before the meeting happens. |
| Notes / Blank Notes | A placeholder for after the meeting. Not a prep artifact. |
| Follow-up Checklist | Post-call in nature. |
| Open Questions (as a standalone section) | Questions belong inside Talking Points or the Proposed Agenda. |
| Next Steps | Post-call. Belongs in the meeting notes, not the prep. |

If you catch yourself adding any of these, stop and remove them. They signal the prep sheet is drifting into meeting notes territory.

---

## Output Specification

**Format:** Markdown (`.md`)
**Destination:** `meetings/` directory, following the naming convention `YYYY-MM-DD-slug.md`
**Frontmatter:** Required. Include at minimum: `source`, `date`, `tags`, `attendees`

Example frontmatter:
```yaml
---
source: chase-call-prep
date: 2026-06-08
tags: [call-prep, client, prospect]
attendees:
  - Name, Title, Company
---
```

**Heading structure:**
```markdown
# [Meeting Title] — Call Prep

## Background / History
## Company Overview
## Improving's Position
## Proposed Agenda
## Talking Points
```

---

## Execution Steps

1. **Parse the request.** Identify: meeting type (call prep vs. meeting prep), attendees, company, scheduled date/time, known context.

2. **Determine research scope.**
   - Are attendees external? If yes, research Section 1 (Background) and Section 2 (Company).
   - Is this Improving or an affiliated company? Skip that section.
   - Is David already well-established with this person? Condense Section 1 to a relationship refresh only.

3. **Run research.** Follow source priority strictly:
   - **Section 1 (Background/History):** LinkedIn first, then CRM for relationship/engagement history, then Clay as a gap-filler only.
   - **Section 2 (Company Overview):** Company website first, then web search for news/signals, then CRM for account history, then Clay as supplemental only.
   - **Clay is never a primary source.** It adds color after authoritative sources are exhausted. Never present Clay data as definitive professional or company background.
   - Pull episodic memory for any prior engagement history relevant to Section 3.

4. **Draft the five sections** in order. Apply depth guidance for the context (call prep vs. meeting prep).

5. **Enforce the template.** Before writing the output file, do a final check:
   - Exactly five sections present?
   - No prohibited sections added?
   - Agenda time totals match scheduled meeting length?
   - Talking points are 4-6, no more?

6. **Write the file** to `meetings/YYYY-MM-DD-slug.md` using Desktop Commander.

7. **Confirm to David.** One line: what was written, where it lives. No summary of the prep content — he'll read the file.

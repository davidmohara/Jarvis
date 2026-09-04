---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 03: Build Detailed Prep Sheet

## MANDATORY EXECUTION RULES

1. You MUST include all sections: logistics, guest background, episode topic, questions, talking points, podcast guide reminders, and pre-filming checklist.
2. You MUST check `state.yaml`'s `sources_used` and merge whatever it contains — this is additive, not either/or. If it contains `episode-prep`, pull the questions/clusters from `gathered_data.episode_prep_source` (condense phrasing only, do not alter substance or invent new questions — those are grounded in a real conversation or dedicated research pass and outrank anything generated here). If it contains `sharepoint`, pull SharePoint's questions the same way as before. If it contains both, merge them per the Merge & Dedupe Rules below rather than picking one and discarding the other. If `sources_used` is empty, generate 8-10 suggested questions and clearly flag them as suggestions pending Janine's confirmation.
3. You MUST save the file to `meetings/podcast-prep/YYYY-MM-DD-guest-name.md` using the filming date.
4. You MUST personalize talking points to David's perspective — reference his experience, Improving's positioning, and relevant personal stories.
5. Do NOT skip sections even if data is thin. Use what's available and flag gaps.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Episode details (step 01) + gathered data (step 02)
**Output:** Detailed prep sheet saved to `meetings/podcast-prep/YYYY-MM-DD-guest-name.md`

---

## YOUR TASK

### Document Structure

Build the prep sheet with this structure (reference `meetings/podcast-prep/2026-03-09-robyn-fuentes.md` as an example):

```markdown
# Podcast Prep Sheet — Episode {N}: {Episode Title}

## Logistics

| Detail | Info |
|--------|------|
| **Date** | {Day of week}, {Month} {Day}, {Year} |
| **Time** | {Time range} CT |
| **Location** | MarketScale Podcast Studio, 901 Main Street, Suite 5300, Dallas |
| **Guest** | {Guest Name} ({Guest Title}) |
| **Host** | David O'Hara |
| **Producer** | Janine Jeanson |
| **Video/Marketing** | Kristin Johnson |
| **Podcast Name** | "The Improving Edge" |
| **Season** | Season 1, Episode {N} of 7 |

---

## Guest Background

**{Guest Full Name}** — {Title}, {Company}

{2-4 bullet points — if `episode-prep` is in `sources_used`, draw these primarily from `gathered_data.episode_prep_source.guest_research_brief` (already vetted and sourced by episode-prep-generator), backstopped by Clay/web research for anything it doesn't cover. Otherwise, draw from Clay + web research:}
- Professional background and expertise
- Current role and responsibilities
- Relevant experience for this episode's topic
- Personal interests / connection points (if available)

**Why they're on this episode:** {1-2 sentences connecting their expertise to the episode topic}

---

## Episode Topic

**"{Episode Title}"**

{Context paragraph from the episode map or Janine's framing}

Core themes:
- {Theme 1}
- {Theme 2}
- {Theme 3}
- {Theme 4}
- {Theme 5}

---

## Questions{ — merged from Episode Prep and/or SharePoint, per `sources_used`}

{Build this section by merging whatever `sources_used` contains — both sources feed the same document, they are never either/or:}

- **If `episode-prep` is in `sources_used`:** pull the questions and clusters from `gathered_data.episode_prep_source.questions_block` — condense phrasing only where needed to fit this document's format, do not alter the substance or invent new questions. Carry over follow-ups already present in the source rather than manufacturing new ones on top of transcript-grounded questions — those already reflect a real conversation.
- **If `sharepoint` is in `sources_used`:** pull SharePoint's questions with their topic groupings. For each question block that doesn't already have an equivalent from episode-prep, add follow-up prompts in italics — a **mechanism follow-up** for at least 2-3 questions ("How does that actually show up?" / "What does that look like in practice?") and a **devil's advocate challenge** for at least 1-2 questions ("Let me push back on that..." / "What would someone say who disagrees with you?"). These are optional prompts for David, not scripted questions.
- **If both are in `sources_used`:** merge per the Merge & Dedupe Rules below into one combined list — do not present two separate "Questions from Episode Prep" and "Questions from SharePoint" blocks side by side.
- **If `sources_used` is empty:** state plainly — "No question source exists for this episode yet (no episode-prep-generator output in `meetings/podcast-prep/`, and no SharePoint doc found)." Action: confirm with Janine whether she's building a SharePoint doc, and/or run `workflows/episode-prep-generator/workflow.md` for this guest. If going freeform, suggested questions below.

### Merge & Dedupe Rules (when both sources contributed)

1. **Read all questions from both sources before writing anything.** Don't merge incrementally question-by-question — see the full set from each source first so duplicates are caught up front.
2. **A question counts as a duplicate** if it asks the same underlying thing even when phrased differently (e.g., episode-prep's "walk us through what full trip-booking inside an AI assistant could look like" and a SharePoint question asking "how do you see this expanding into travel" are the same question). When two questions overlap, keep the one grounded in a real conversation or deeper research (episode-prep, when it exists) and drop the SharePoint duplicate — but if SharePoint's phrasing or framing is sharper, use SharePoint's wording with episode-prep's substance.
3. **Non-duplicate questions from both sources are combined**, organized under whichever thematic clusters make sense across the combined set (episode-prep's clusters if the merge leans heavily on that source, otherwise re-cluster around the episode's core themes).
4. **Preserve source-appropriate follow-ups.** Don't strip a mechanism/devil's-advocate follow-up that came with a SharePoint question just because it's now sitting next to an episode-prep question; don't invent a new follow-up for an episode-prep question that already has a transcript-grounded one.
5. **Note the merge in Notes/flags**, not in the Questions section itself — e.g. "3 of these questions came from episode-prep-generator (grounded in a 7/13 conversation), 4 from Janine's SharePoint doc, 1 duplicate dropped." Keep the Questions section itself clean and scannable; the provenance note belongs in the pre-filming checklist or a one-line footer, not interleaved with the questions.

---

## Suggested Questions (if no Janine doc arrives)

> **Question format:** Each block = primary question + optional follow-ups in italics.
> *Mechanism follow-up:* "How does that actually show up?" / "What does that look like in practice?"
> *Devil's advocate:* "Let me push back on that..." / "What would someone say who disagrees with you?"
> At least 2-3 questions should have a mechanism follow-up. At least 1-2 should have a devil's advocate challenge.

{Generate 8-10 questions if no SharePoint doc. Each should:}
{- Be numbered with a bold topic label}
{- Be phrased the way David would actually ask them — conversational, direct}
{- Cover the episode's core themes}
{- Include a **mechanism follow-up** for at least 2-3 questions — after the guest answers, David presses on the "how": "How does that actually show up?" or "What does that look like in practice?". Write the follow-up in italics beneath the primary question.}
{- Include a **devil's advocate challenge** for at least 1-2 questions — explicitly name the counter-position: "Let me push back on that for a second..." or "What would someone say who disagrees with you?". Write it in italics beneath the primary question.}
{- End with the standard closer: "What are a couple of takeaways you'd like the listeners to walk away with?"}

---

## David's Talking Points & Angles

{Personalized to David's experience and perspective:}
- **Personal experience:** {Something David has done or built related to this topic}
- **Improving angle:** {How Improving is positioned on this topic — capability, client work, differentiation}
- **Contrarian or fresh take:** {A perspective David can bring that the guest might not expect}
- **Story to tell:** {A specific anecdote David could share to make the conversation real}
- **Key frame:** {The one idea David wants the audience to walk away with}

---

## Podcast Guide Reminders (from Janine)

- **Tone:** Conversational, light, casual. Wide audience — avoid overly technical terms.
- **Speaking split:** 40% host (David) / 60% guest ({Guest First Name})
- **Duration:** Film ~1 hour, final cut is 25-35 min. Don't worry about mistakes — they edit.
- **Vibe:** Make it fun. Tell personal stories. Be human. The best episodes feel like two people having a real conversation, not an interview.
- **Format:** Unscripted. No teleprompter. Key topics as a guide, not a script.

---

## Pre-Filming Checklist

- [ ] Review this prep sheet before heading to studio
- [ ] {Any episode-specific action items — e.g., confirm question doc with Janine}
- [ ] Prep 1-2 personal stories related to {episode topic}
- [ ] Think about a {guest first name}-specific question — draw on their unique background
- [ ] Standard closer: "What are a couple of takeaways?" (per podcast sync)
- [ ] Arrive 15 min early for mic check and setup
```

### Writing Rules

1. **Questions sound like David.** Not academic. Not scripted. The way you'd ask over coffee. Direct, curious, with an edge. Every topic block should have at least one mechanism follow-up ("How does that actually show up?") and at least one devil's advocate challenge ("What would someone say who disagrees with you?"). These go in italics beneath the primary question — they're not separate questions, they're prompts David can use if the guest's answer stays too abstract or too safe.
2. **Talking points are specific.** Not "talk about AI" — instead "reference your experience building the Jarvis multi-agent system." Concrete, personal, usable.
3. **Flag everything uncertain.** Missing SharePoint doc? Flag it. Guest background thin? Flag it. Date unconfirmed? Flag it. Better to over-flag than to let David walk in unprepared.
4. **Keep it scannable.** Tables, bullets, bold headers. David reads this quickly before filming — it's not a novel.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Not enough guest background | Do a WebSearch for the guest's name + company. Pull LinkedIn summary, recent talks, articles. Flag: "Guest background from web search — verify accuracy." |
| Neither episode-prep nor SharePoint has questions, AND topic is vague | Generate questions anyway, but flag: "These are broad — you may want to sharpen them based on pre-filming conversation with {guest name}." |
| Episode-prep and SharePoint questions conflict in framing (not just duplicate, but contradictory angles) | Keep both if there's room; if not, flag the conflict in Notes and default to the episode-prep framing since it's grounded in a real conversation or deeper research. |
| Episode topic doesn't align with guest's expertise | Flag the mismatch. Suggest reframing the questions to bridge the guest's experience with the topic. |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py podcast-prep step-03-build-prep-sheet complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-04-build-pdf-sheet.md`
<!-- personal:end -->

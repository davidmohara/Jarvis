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
2. You MUST use SharePoint questions if available. If not, generate 8-10 suggested questions and clearly flag them as suggestions pending Janine's confirmation.
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

{2-4 bullet points from Clay + web research:}
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

## Questions from SharePoint

{If SharePoint doc found: reproduce all questions with their topic groupings. For each question block, add follow-up prompts in italics:
- A **mechanism follow-up** for at least 2-3 questions: "How does that actually show up?" or "What does that look like in practice?"
- A **devil's advocate challenge** for at least 1-2 questions: "Let me push back on that..." or "What would someone say who disagrees with you?"
These are optional prompts for David — not scripted questions — to use if the guest's answer stays too abstract or too safe.}

{If NOT found:}
**No question doc exists on SharePoint for this episode yet.**

Action: Confirm with Janine whether she's building one or if you're going freeform on this episode. If freeform, suggested questions below.

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
| No questions from SharePoint AND topic is vague | Generate questions anyway, but flag: "These are broad — you may want to sharpen them based on pre-filming conversation with {guest name}." |
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

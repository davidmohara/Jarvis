# Step 04: Build PDF-Format Prep Sheet

## MANDATORY EXECUTION RULES

1. You MUST reference the template at `reference/podcast-prep-pdf-template.md` for the exact format.
2. You MUST condense 10+ questions down to exactly 5 focused prompts + 1 wrap-up. Combine related questions. Phrase the way David would actually ask them.
3. You MUST include all 9 sections in order: header, intro script, season/episode, title, overview, key discussion topics table, prompting questions, remember bar, sportcoat line.
4. You MUST save to `meetings/podcast-prep/Episode {NN} - {Guest Name}.md` (zero-padded episode number).
5. Do NOT add extra sections. This is a single-page document — every word must earn its place.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Detailed prep sheet from step 03, PDF template from reference
**Output:** PDF-format markdown at `meetings/podcast-prep/Episode {NN} - {Guest Name}.md`

---

## YOUR TASK

### Read the Template

Read `reference/podcast-prep-pdf-template.md` for the exact format specification. Follow it precisely.

### Build the Document

The output file must follow this exact structure:

```markdown
# THE IMPROVING EDGE | {Guest Full Name}, {Guest Title}

---

## INTRO SCRIPT

Welcome to The Improving Edge. This is where we talk about how AI and technology actually show up in real organizations; what works, what doesn't, and what we're learning along the way. I'll be sharing conversations with people doing the work, turning innovation into outcomes.

---

**Season 1, Episode {N}**

# {Episode Title}

---

## Episode Overview

{2-3 sentences summarizing the episode's focus. First-person plural ("We'll discuss...", "We'll dig into..."). Cover key themes without being exhaustive.}

---

## Key Discussion Topics

| # | TOPIC | FOCUS |
|---|-------|-------|
| 1 | **{Topic Name}** | {1-2 sentence description} |
| 2 | **{Topic Name}** | {1-2 sentence description} |
| 3 | **{Topic Name}** | {1-2 sentence description} |
| 4 | **{Topic Name}** | {1-2 sentence description} |
| 5 | **{Topic Name}** | {1-2 sentence description} |

---

## Prompting Questions

1. **On {Topic}**
*"{Question phrased naturally, the way David would ask it}"*

2. **On {Topic}**
*"{Question}"*

3. **On {Topic}**
*"{Question}"*

4. **On {Topic}**
*"{Question}"*

5. **On {Topic}**
*"{Question}"*

6. **Wrap-Up**
*"What are a couple of takeaways you'd like the listeners to walk away with?"*

---

**REMEMBER: Keep it conversational (60% guest / 40% host) · Share personal stories · Have fun!**

---

Sportcoat: _______________________________
```

### Distillation Rules

The key skill here is **condensation**. The detailed prep sheet has 8-10+ questions. This document has exactly 5 + wrap-up. Here's how to distill:

1. **Group related questions.** If the detailed sheet has 3 questions about adoption barriers, combine them into one prompt that naturally leads the guest through the topic.

2. **Cut the obvious.** If a question would get answered naturally in the flow of conversation, cut it. Keep only the questions that need to be asked deliberately.

3. **Phrase for David.** Not "Could you elaborate on the challenges of..." — instead "What breaks when you try to do this at scale?" Direct, curious, slightly provocative. The questions should sound like David having a conversation, not reading a teleprompter.

4. **Order for flow.** Start broad (define the topic, set context), go deep in the middle (challenges, real examples, contrarian takes), end forward-looking (future, advice), then wrap up.

5. **The wrap-up is always the same:** "What are a couple of takeaways you'd like the listeners to walk away with?"

6. **Topic labels are 2-4 words.** Not sentences. "On Adoption Barriers" not "On The Challenges Organizations Face When Adopting AI."

7. **5 topics in the table should map to the 5 questions.** They're the same themes, just different formats — table gives the overview, questions give the prompts.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Fewer than 5 distinct topics | Broaden the themes. Split a big topic into two angles, or add a "Personal Take" or "Future Outlook" topic. |
| Questions sound too scripted | Rewrite them more casually. Read them aloud mentally — would David say this in a real conversation? |
| Document runs long (won't fit one page) | Tighten focus descriptions in the table. Shorten questions. Cut any word that isn't pulling its weight. |
| Template format unclear | Reference the existing example at `meetings/podcast-prep/Episode 02 - John Ruzick.md` for a real output. |

---

## NEXT STEP

Read fully and follow: `step-05-generate-pdf.md`

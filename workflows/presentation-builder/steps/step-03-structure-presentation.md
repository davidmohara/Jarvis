---
model: sonnet
---

<!-- system:start -->
# Step 03: Structure the Presentation

## MANDATORY EXECUTION RULES

1. You MUST use `source_material` from step 01 and `voice_profile` from step 02 to structure every slide.
2. You MUST create a slide-by-slide outline with title, key point, supporting content, speaker notes, and visual suggestion for each slide.
3. You MUST design the narrative flow using: hook → context → evidence → call to action.
4. You MUST write all content in the executive's voice — every word should sound like the executive.
5. You MUST include speaker notes for every content slide.
6. Do NOT include slide design, colors, or layout instructions. Output is text structure only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `source_material` from step 01, `voice_profile` from step 02
**Output:** `presentation_structure` — complete slide-by-slide text structure ready for delivery

---

## CONTEXT BOUNDARIES

- Output is **text structure only**. No PowerPoint, no Keynote, no Google Slides.
- Each slide has exactly one key point. If a slide needs two key points, split it into two slides.
- Speaker notes should give the executive what to say, not what is already written on the slide.
- Visual suggestions are directional, not prescriptive — "chart showing growth trend" not "bar chart with blue bars."

---

## YOUR TASK

### Sequence

1. **Plan the narrative structure.** Using the `narrative_arc` from step 01:

   | Narrative Position | Slide Type | Purpose |
   |-------------------|-----------|---------|
   | Hook | Opening slide | Grab attention. Start with the insight, the challenge, or the unexpected. |
   | Context | Background/situation slide(s) | Why now? Why this matters. |
   | Evidence | Data/proof slides | Support the key messages with evidence. |
   | Resolution | Recommendation/path forward | What does the evidence lead to? |
   | Call to action | Closing slide | What do you want the audience to do, decide, or believe? |

2. **Structure each slide.** For every slide in the deck:

   ```
   Slide [N]: [Slide Title]
   ---
   Key Point: [One clear, declarative sentence — the headline of this slide]
   Content:
     - [Supporting point 1]
     - [Supporting point 2]
     - [Supporting point 3 — max 3 bullets per slide]
   Speaker Notes: [What the executive says that is NOT on the slide — the story behind the data, the nuance, the personal context]
   Visual: [What visualization would strengthen this slide — chart type, image concept, diagram idea]
   ```

3. **Apply voice calibration.** Every title, key point, and speaker note must:
   - Match the `voice_profile.vocabulary` level
   - Reflect `voice_profile.sentence_style` (punchy vs. nuanced)
   - Lead with data or story per `voice_profile.data_orientation`
   - Avoid anything in `voice_profile.avoid`
   - Use `voice_profile.signature_phrases` where natural

4. **Quality-check the deck structure.**
   - Does it open with a hook that commands attention?
   - Is every slide earning its place? (No filler, no redundancy)
   - Does the narrative arc flow logically from hook to call to action?
   - Would the executive be comfortable saying the speaker notes aloud?
   - Is the closing slide a clear call to action?

5. **Store results** in working memory:
   ```
   presentation_structure:
     total_slides: N
     narrative_arc:
       hook_slide: N
       context_slides: [N, N]
       evidence_slides: [N, N, N]
       resolution_slide: N
       cta_slide: N
     slides:
       - number: 1
         title: ...
         key_point: ...
         content: [...]
         speaker_notes: ...
         visual_suggestion: ...
     voice_applied: true
   ```

---

## SUCCESS METRICS

- Complete slide-by-slide structure created
- Every slide has: title, key point, content bullets (max 3), speaker notes, visual suggestion
- Narrative arc flows: hook → context → evidence → resolution → call to action
- All content calibrated to executive's voice profile
- No slide has more than one key point

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Source material too thin for a full deck | Build what is possible. Note: "Source material supports [N] slides. To expand to a full deck, I need more content on [specific topics]." |
| No clear call to action in source material | Default to: "What do you want the audience to do next?" Include a placeholder CTA slide. Flag for executive review. |
| Voice profile not available | Default to professional-warm, balanced data/story. Proceed. |
| Conflicting messages in source material | Present the stronger message as primary. Note the conflict in speaker notes: "Alternative framing from source material: [X]." |

---

## NEXT STEP

Read fully and follow: `step-04-handoff-intake.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

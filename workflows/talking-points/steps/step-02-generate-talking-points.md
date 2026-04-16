---
model: sonnet
---

<!-- system:start -->
# Step 02: Generate Talking Points

## MANDATORY EXECUTION RULES

1. You MUST read `identity/VOICE.md` before generating any points. Voice calibration is non-negotiable.
2. You MUST generate 3-5 main talking points unless the event type specifies a different count.
3. Every talking point MUST include: main message, supporting evidence, suggested phrasing, and source reference.
4. You MUST generate 3-5 anticipated questions based on topic, audience, and knowledge layer context.
5. All points MUST match the executive's voice profile — phrasing must sound like the executive.
6. Do NOT format for context in this step. Generation only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `event_context` from step 01, `identity/VOICE.md`
**Output:** `talking_points` — complete set of calibrated talking points with evidence, phrasing, and Q&A stored in working memory for step 03

---

## CONTEXT BOUNDARIES

- Voice calibration means the executive should be able to read the suggested phrasing aloud and sound like themselves.
- Supporting evidence is real data, examples, or stories from the knowledge layer or domain context — not generic assertions.
- Anticipated questions should be based on topic, audience type, and any recent knowledge layer context, not just generic questions.
- Source references tell the executive where each point comes from — this builds confidence and allows verification.

---

## YOUR TASK

### Sequence

1. **Load and apply the voice profile.**
   - Read `identity/VOICE.md` — extract voice calibration rules for the event type.
   - For panel and media contexts: confirm the executive's communication style under pressure (assertive vs. measured, data-first vs. story-first).
   - Apply voice calibration to all phrasing suggestions.

2. **Generate 3-5 main talking points.** For each:

   ```
   Talking Point [N]:
   ---
   Main Message: [One clear, declarative statement — the executive's position on this topic]
   Supporting Evidence: [Data, example, or story from knowledge layer or domain context]
   Suggested Phrasing: [How the executive would say this in their natural voice]
   Source Reference: [knowledge layer entry / Chase / Quinn / Shep / Chief / provided context]
   ```

3. **Generate 3-5 anticipated questions.** For each:
   - Base questions on: topic, audience type, and knowledge layer context for the specific event
   - For each question, provide a prepared response in the executive's voice

   ```
   Anticipated Question [N]:
   ---
   Question: [What the audience/interviewer/moderator is likely to ask]
   Prepared Response: [The executive's answer, in their voice, 2-3 sentences]
   Bridge (if applicable): [If the question is hostile or off-topic: bridge phrase to redirect]
   ```

4. **Store results** in working memory:
   ```
   talking_points:
     event_type: [from event_context]
     voice_profile_applied: true
     points:
       - number: N
         main_message: ...
         supporting_evidence: ...
         suggested_phrasing: ...
         source_reference: knowledge-layer | chase | quinn | shep | chief | provided-context
     anticipated_questions:
       - number: N
         question: ...
         prepared_response: ...
         bridge: ... | null
   ```

---

## SUCCESS METRICS

- VOICE.md loaded and voice profile applied to all phrasing
- 3-5 talking points generated with: main message, evidence, phrasing, source reference
- 3-5 anticipated questions generated based on topic, audience, and knowledge layer context
- All phrasing calibrated to executive's natural voice
- Source attribution for every talking point

## FAILURE MODES

| Failure | Action |
|---------|--------|
| VOICE.md not found | Proceed with professional-warm default. Flag: "Voice profile unavailable — phrasing uses professional-warm default. Update VOICE.md for personalized calibration." |
| Insufficient data for evidence | Note: "Limited evidence available for [topic] — talking point relies on executive's position statement. Strengthen with data before the event." |
| Knowledge layer has no relevant entries | Generate points from provided context. Note: "No knowledge layer entries on this topic — adding to knowledge layer after the event is recommended." |
| Topic is politically sensitive or involves confidential information | Flag: "This topic may involve sensitive information. Review carefully before using." |

---

## NEXT STEP

Read fully and follow: `step-03-format-and-deliver.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
model: sonnet
---

<!-- system:start -->
# Step 02: Voice Calibration

## MANDATORY EXECUTION RULES

1. You MUST read `identity/VOICE.md` completely before any voice calibration.
2. You MUST extract the executive's language patterns, tone preferences, and communication style.
3. You MUST ensure every slide will sound like the executive — not generic AI content.
4. You MUST calibrate for the specific audience if known from source_material.
5. If VOICE.md does not exist, use context from prior Harper interactions, or ask for voice guidance.
6. Do NOT structure slides in this step. Voice calibration only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `source_material` from step 01, `identity/VOICE.md`
**Output:** `voice_profile` — executive voice calibration rules stored in working memory for step 03

---

## CONTEXT BOUNDARIES

- The executive's voice is sacred. Every word in the final presentation should sound like the executive wrote it.
- Voice calibration applies to: word choice, sentence structure, formality level, use of data vs. story, directness vs. nuance.
- Audience context from step 01 informs tone calibration — presenting to a board requires different register than a town hall.
- This step does not write any content. It extracts and codifies the rules for step 03.

---

## YOUR TASK

### Sequence

1. **Load the executive's voice profile.**
   - Read `identity/VOICE.md` completely.
   - Extract the following for presentation contexts:

   | Voice Element | What to Extract |
   |--------------|----------------|
   | Vocabulary level | Technical vs. accessible, industry jargon vs. plain language |
   | Sentence structure | Long and nuanced vs. short and punchy |
   | Formality | Formal, professional-warm, direct, casual |
   | Data orientation | Leads with data vs. leads with narrative/story |
   | Confidence level | Assertive and declarative vs. exploratory and questioning |
   | Signature phrases | Any recurring phrases, metaphors, or constructions the executive uses |
   | Things to avoid | Any language patterns, phrases, or tones explicitly called out as wrong |

2. **Calibrate for the presentation audience.** Based on `source_material.input_formats` and any audience context:

   | Audience Type | Tone Calibration |
   |--------------|-----------------|
   | Board / investors | Formal, data-driven, decisive. Every slide earns its place. |
   | Leadership team | Professional, direct, results-focused. Can include candor about challenges. |
   | Clients / prospects | Professional-warm, value-focused, clear benefits. |
   | All-hands / town hall | Accessible, energizing, narrative-driven. Human moments matter. |
   | External audience (keynote) | Polished, quotable, memorable. Story over data. |
   | Internal operational | Direct, efficient. No unnecessary polish. |

3. **Define communication brand consistency rules.** Extract what makes this executive's communication style distinctive:
   - Does the executive prefer to lead with data or with story?
   - Does the executive use specific frameworks (e.g., always starts with the "so what")?
   - What is the executive's signature closing style (call to action vs. inspiring close vs. summary)?

4. **Store results** in working memory:
   ```
   voice_profile:
     vocabulary: technical | accessible | mixed
     sentence_style: punchy | nuanced | mixed
     formality: formal | professional-warm | direct | casual
     data_orientation: data-first | story-first | balanced
     confidence_level: assertive | exploratory
     signature_phrases: [...]
     avoid: [...]
     audience_calibration:
       audience_type: board | leadership | client | all-hands | keynote | operational
       tone_adjustment: ...
     communication_brand:
       lead_style: data | story | problem-solution
       closing_style: call-to-action | inspiring | summary
   ```

---

## SUCCESS METRICS

- VOICE.md loaded and voice elements extracted
- Audience calibration applied
- Communication brand rules codified
- `voice_profile` stored in working memory for step 03

## FAILURE MODES

| Failure | Action |
|---------|--------|
| VOICE.md does not exist | Ask: "I don't have your voice profile yet. How would you describe your communication style? (e.g., direct and data-driven, or narrative-first and energizing?)" Use the executive's answer as the voice_profile. |
| VOICE.md exists but has no presentation guidance | Use general voice rules from VOICE.md. Default calibration: professional-warm, balanced data/story. |
| Audience unknown | Default to professional-warm. Note: "Audience not specified — calibrated to professional-warm default. Adjust if needed." |
| Conflicting voice signals in source material | Use VOICE.md as the authoritative source. Override conflicting signals from source material. |

---

## NEXT STEP

Read fully and follow: `step-03-structure-presentation.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

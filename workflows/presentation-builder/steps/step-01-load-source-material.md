---
model: sonnet
---

<!-- system:start -->
# Step 01: Load and Parse Source Material

## MANDATORY EXECUTION RULES

1. You MUST read all provided source material completely before doing any analysis.
2. You MUST accept input in any format: talking points, outlines, strategy documents, raw ideas, or handoff context.
3. You MUST extract key messages and supporting evidence from the material — do not simply summarize.
4. You MUST identify a narrative arc from the material. If one is not explicit, infer it.
5. If no source material is provided at all, STOP and ask the executive what they want the presentation to cover.
6. Do NOT calibrate voice or structure slides in this step. Load and parse only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Source material (any format), controller's request
**Output:** `source_material` — parsed content inventory with key messages, evidence, and narrative arc stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- Source material quality does not matter. Rough bullet points are as valid as a polished strategy doc.
- "Talking points" and "outline" are not mutually exclusive — treat overlapping formats as the same source.
- If multiple documents or inputs are provided, treat them as a unified source and resolve conflicts in favor of the most specific or recent content.
- This step is analysis only. No voice calibration, no slide structuring.

---

## YOUR TASK

### Sequence

1. **Receive and inventory the source material.** Identify what was provided:

   | Format Received | Description |
   |----------------|-------------|
   | Talking points | Bullet-form key messages, any level of completeness |
   | Outline | Hierarchical structure with sections and sub-points |
   | Strategy document | Formal or informal doc with objectives, context, and data |
   | Raw ideas | Unstructured brain dump, rough notes, or stream-of-consciousness input |
   | Handoff payload | Structured context from Chase (client data) or Quinn (strategic narrative). Note: store the raw handoff payload in working memory — full integration happens in step 04. |
   | Mixed / unknown | Combination of formats — treat as unified source |

2. **Extract key messages.** For each distinct topic or section in the source material:
   - Identify the main assertion or claim
   - Identify supporting evidence, data, or examples
   - Note any calls to action already present in the material

3. **Identify the narrative arc.** Determine the logical story flow:

   | Arc Element | What to Look For |
   |------------|-----------------|
   | Hook | Opening hook — what grabs attention? |
   | Context | Why does this matter? What is the situation? |
   | Evidence | What proof, data, or examples support the key messages? |
   | Call to action | What should the audience do, decide, or believe after? |

   If the narrative arc is not explicit in the source material, infer it from the content structure and context.

4. **Flag any gaps.** Note what is missing that would strengthen the presentation:
   - Missing data or evidence for key claims
   - Unclear call to action
   - Missing audience context (who is this for?)
   - No hook present

5. **Store results** in working memory:
   ```
   source_material:
     input_formats: [talking-points | outline | strategy-doc | raw-ideas | handoff | mixed]
     key_messages:
       - topic: ...
         main_assertion: ...
         supporting_evidence: [...]
         call_to_action: ... | null
     narrative_arc:
       hook: ... | inferred
       context: ...
       evidence: [...]
       call_to_action: ...
     gaps:
       - description: ...
         impact: high | medium | low
     slide_count_estimate: N
   ```

---

## SUCCESS METRICS

- All source material fully read and parsed
- Key messages extracted with supporting evidence for each
- Narrative arc identified (explicit or inferred)
- Gaps documented with impact assessment
- Working memory populated with `source_material` for step 02

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No source material provided | STOP. Ask: "What do you want this presentation to cover? Share your talking points, an outline, or your key ideas and I'll build the structure." |
| Source material is contradictory | Note the contradiction in `gaps`. Use the more specific or recent claim as primary. Flag for executive review. |
| Source material exists but has no clear message | Proceed with what is available. Flag: "Source material has no clear central message — I've inferred one. Review the narrative arc in step 03 before finalizing." |
| Audience not identified in source material | Note in `gaps`. Proceed — audience calibration happens in step 03. |

---

## NEXT STEP

Read fully and follow: `step-02-voice-calibration.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

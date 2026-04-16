---
model: sonnet
---

<!-- system:start -->
# Step 03: Content Recommendations

## MANDATORY EXECUTION RULES

1. You MUST analyze the executive's expertise tags from the knowledge layer before generating recommendations.
2. You MUST pull current strategic themes from Quinn's domain (rock topics, initiative focus areas).
3. You MUST identify content gaps in the calendar (topic areas or content types underrepresented).
4. You MUST generate at least 3 topic recommendations.
5. Do NOT deliver the calendar in this step. Recommendations only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `deadline_flags` from step 02, knowledge layer, Quinn domain context
**Output:** `recommendations` — topic suggestions with rationale stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Expertise tags are the executive's known areas of authority — content should reinforce the brand, not dilute it.
- Strategic themes from Quinn align content with the executive's current priorities — thought leadership and strategy should move together.
- Content gaps are identified by comparing recent publishing history to expertise areas (what are they known for but haven't published on recently?).
- Recommendations are suggestions, not assignments — the executive decides what to pursue.

---

## YOUR TASK

### Sequence

1. **Load expertise tags from the knowledge layer.**
   - Search knowledge layer for the executive's documented expertise areas and key themes.
   - Extract expertise tags: topics the executive is known for, speaks about, or wants to build authority in.
   - Note the last time content was published in each expertise area.

2. **Pull strategic themes from Quinn domain.**
   - Query Quinn's domain for: current quarterly rocks, active initiative topics, strategic priorities.
   - Map strategic themes to potential content angles: "If Rock 1 is [topic], what thought leadership content would reinforce that?"

3. **Search for recent industry trends.**
   - Use web search to identify trending topics in the executive's industry and expertise areas.
   - Look for timely hooks: industry events, regulatory changes, market shifts, competitor moves.
   - Note which trends align with the executive's expertise tags — these are high-value content opportunities.

4. **Identify content gaps.**
   - Compare expertise tags to published content in the current calendar period.
   - Flag expertise areas with no content in the past 60 days as content gaps.
   - Flag content types that are underrepresented (e.g., no podcasts in 3 months, no long-form articles this quarter).

5. **Generate topic recommendations.** For each recommendation:

   ```
   Recommendation [N]:
   ---
   Topic: [Specific content angle or title suggestion]
   Type: article | talk | podcast | social-post
   Rationale: expertise-tag | strategic-theme | content-gap | trend
   Expertise connection: [Which expertise area this reinforces]
   Strategic connection: [Which rock or initiative this aligns to]
   Suggested format: [Short-form, long-form, video, etc.]
   Urgency: high | medium | low
   ```

6. **Store results** in working memory:
   ```
   recommendations:
     expertise_tags: [...]
     strategic_themes: [...]
     content_gaps: [...]
     suggested_topics:
       - topic: ...
         type: ...
         rationale: expertise-tag | strategic-theme | content-gap | trend
         expertise_connection: ...
         strategic_connection: ...
         urgency: high | medium | low
   ```

---

## SUCCESS METRICS

- Expertise tags loaded from knowledge layer
- Strategic themes pulled from Quinn domain
- Content gaps identified by comparing history to expertise areas
- At least 3 topic recommendations generated with rationale
- `recommendations` stored in working memory for step 04

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Knowledge layer has no expertise tags | Proceed without tags. Ask: "What are your main areas of expertise or thought leadership focus?" Use the executive's answer for recommendations. |
| Quinn domain unavailable | Proceed without strategic themes. Note: "Quinn context unavailable — recommendations based on expertise and gaps only." |
| No content gaps identified (active, diverse calendar) | Generate recommendations based on upcoming trends or content type variety. Note: "Calendar is in good shape — recommendations are forward-looking." |
| Executive has no published content history | Recommend foundational thought leadership topics based on expertise tags and role. |

---

## NEXT STEP

Read fully and follow: `step-04-deliver-calendar.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

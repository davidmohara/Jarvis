---
model: opus
---

<!-- system:start -->
# Step 01: Event Context Analysis

## MANDATORY EXECUTION RULES

1. You MUST identify the event type before proceeding — it governs the entire content structure.
2. You MUST extract the audience, date, and key expectations from the user input or calendar.
3. If event type cannot be determined from input, ask the executive before proceeding.
4. Do NOT pull data or generate content in this step. Establish context only.
5. Determine whether a formal presentation (deck) is needed — this governs the Harper handoff in step 04.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** $ARGUMENTS (executive's request, event name/date), calendar (optional)
**Output:** `event_context` — event type, audience, key expectations, content requirements

---

## EVENT TYPE DETECTION

Detect event type from the executive's request:
- "board meeting" / "board prep" → `board-meeting`
- "quarterly review" / "QBR" / "Q[N] review" → `quarterly-review`
- "town hall" / "all-hands" / "all hands" → `town-hall`
- Other meeting types → treat as `quarterly-review` as default, note the assumption

## CONTENT EMPHASIS BY EVENT TYPE

| Event Type | Lead With | Include | Tone |
|------------|-----------|---------|------|
| `board-meeting` | Financial metrics, strategic risks | Revenue, pipeline, rock status, key decisions needed | Formal, data-driven, concise |
| `quarterly-review` | Progress against rocks, blockers | Initiative updates, team health, ops highlights, adjustments | Direct, balanced, action-oriented |
| `town-hall` | Wins, narrative, direction | Culture signals, strategic priorities, team recognition, vision | Inspiring, accessible, forward-looking |

---

## YOUR TASK

### Sequence

1. **Extract event information from $ARGUMENTS.**
   - Event name (e.g., "Q2 Board Meeting", "January Town Hall")
   - Event date (if provided)
   - Audience (if specified)
   - Any specific topics or concerns the executive wants addressed

2. **Classify event type.**
   - Apply event type detection rules above
   - If ambiguous: ask "Is this a board meeting, quarterly review, or town hall? This determines the format and emphasis."

3. **Determine presentation requirement.**
   - If the executive explicitly requests a presentation/deck: `presentation_needed = true`
   - If event type is `board-meeting`: `presentation_needed = true` (default)
   - Otherwise: `presentation_needed = false` (document format)

4. **Identify key audience expectations.**
   - Board: What decisions need to be made? What risks are they tracking?
   - Leadership team: What commitments were made last quarter? What's changing?
   - Org-wide: What do people need to believe and feel confident about?

5. **Store results** in working memory:
   ```
   event_context:
     event_name: ...
     event_type: board-meeting | quarterly-review | town-hall
     event_date: YYYY-MM-DD | null
     audience: board | leadership-team | company-wide | mixed
     key_topics: [...]
     presentation_needed: true | false
     content_emphasis: [metrics/risks | progress/blockers | narrative/wins]
     tone: formal | direct | inspiring
   ```

---

## SUCCESS METRICS

- Event type identified and confirmed
- Audience and key expectations established
- Presentation requirement determined
- Content emphasis mapped to event type

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Event type cannot be determined from input | Ask: "What type of event is this — board meeting, quarterly review, or town hall? This shapes the materials I build." |
| No event information provided | Ask for event name and date before proceeding. |
| Event date is in the past | Proceed with prep materials. Note: "This event date is in the past — proceeding with prep content as requested." |

---

## NEXT STEP

Read fully and follow: `step-02-cross-domain-aggregation.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

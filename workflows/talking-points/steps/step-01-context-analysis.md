---
model: sonnet
---

<!-- system:start -->
# Step 01: Context Analysis

## MANDATORY EXECUTION RULES

1. You MUST determine the event type before generating any talking points.
2. You MUST pull relevant context from the knowledge layer based on the event topic.
3. You MUST pull domain-specific context from other agent domains if the topic requires it.
4. You MUST identify the audience and key topics for the event.
5. If event type cannot be determined, ask one clarifying question before proceeding.
6. Do NOT generate talking points in this step. Context loading only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Executive's request, event details
**Output:** `event_context` — event type, audience, key topics, and domain context stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- Event type determines output format. Getting this right is the most important decision in this step.
- Knowledge layer is the primary source for past statements, positions, and expertise — check it before asking the executive for more context.
- Agent domain context (Chase, Quinn, Shep, Chief) is optional — pull only when the event topic clearly requires it.
- This step is context gathering only. No points, no phrasing, no structure.

---

## YOUR TASK

### Sequence

1. **Determine the event type.** Classify from the executive's request:

   | Event Type | Trigger Signals | Output Format |
   |------------|----------------|--------------|
   | `meeting` | "prep me for a meeting", "talking points for my call with X" | 3-5 bullets, action-oriented |
   | `panel` | "I'm on a panel", "moderating/speaking at [event]" | 1-minute structured points with bridge phrases |
   | `media` | "press interview", "podcast appearance", "journalist", "reporter" | Key messages with Q&A and pivots |
   | `podcast` | "going on a podcast", "podcast interview" | Key messages with Q&A and pivots (same as media) |
   | `internal-comms` | "town hall", "all-hands", "team meeting", "internal announcement" | Narrative with key themes |
   | `unknown` | Ambiguous request | Ask: "Is this for a meeting, panel, media interview, or internal communication?" |

2. **Pull knowledge layer context.** Search for:
   - Past statements or positions the executive has taken on the topic
   - Key expertise areas relevant to the event
   - Recent knowledge layer entries referencing the topic or related themes
   - Any prior talking points on the same or similar topic

3. **Pull domain-specific context if needed.** Based on the event topic:

   | Topic Signal | Agent Domain | What to Pull |
   |-------------|-------------|-------------|
   | Revenue, growth, pipeline, clients | Chase | Pipeline metrics, account wins, revenue narrative |
   | Strategy, goals, rocks, initiatives | Quinn | Rock status, strategic narrative, quarterly progress |
   | Team, culture, hiring, people | Shep | Team health, org highlights, people wins |
   | Operations, daily priorities, delivery | Chief | Operational wins, blockers resolved, capacity status |

4. **Identify key topics and themes.** From the event context and pulled data:
   - What are the 3-5 most important topics likely to come up?
   - What is the executive's known position on each topic?
   - What data or examples support each position?

5. **Store results** in working memory:
   ```
   event_context:
     event_type: meeting | panel | media | podcast | internal-comms
     event_name: ...
     event_date: ... | unknown
     audience: ...
     key_topics:
       - topic: ...
         executive_position: ...
         available_data: [...]
         knowledge_layer_refs: [...]
     domain_context:
       chase: ... | not-needed
       quinn: ... | not-needed
       shep: ... | not-needed
       chief: ... | not-needed
   ```

---

## SUCCESS METRICS

- Event type classified correctly
- Knowledge layer searched for topic-relevant context
- Domain context pulled where applicable
- Key topics identified with executive position and supporting data
- `event_context` stored in working memory for step 02

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Event type cannot be determined | Ask: "Is this for a meeting, a panel, a media interview, or internal communications?" Cannot format correctly without this. |
| Topic is not in the knowledge layer | Proceed with available context. Note: "No prior knowledge layer entries on [topic] — talking points will rely on executive's provided context." |
| Agent domain unavailable | Proceed without that domain's data. Note: "[Domain] data unavailable — talking points will exclude [domain] metrics." |
| Executive provides no context at all | Ask: "What's the event, and what are the 1-2 topics you most want to be ready for?" |

---

## NEXT STEP

Read fully and follow: `step-02-generate-talking-points.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

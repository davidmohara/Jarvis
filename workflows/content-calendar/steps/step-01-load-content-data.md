---
model: sonnet
---

<!-- system:start -->
# Step 01: Load Content Data

## MANDATORY EXECUTION RULES

1. You MUST load all content commitments from the task management layer before anything else.
2. You MUST check the Calendar MCP for event-linked content (talks, podcasts, speaking appearances).
3. You MUST recognize all four content types: article, talk, podcast, social-post.
4. You MUST load valid statuses only: draft, scheduled, published, cancelled.
5. If no content commitments exist, report it and prompt to create the first entry.
6. Do NOT flag deadlines or generate recommendations in this step. Load and inventory only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Task management layer, Calendar MCP
**Output:** `content_inventory` — complete list of content items with type, deadline, and status stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- Content items are stored as tasks in `tasks/todos/` with a content marker or tag.
- Event-linked content (talks, podcasts) has a corresponding calendar entry — always cross-reference.
- Status values are fixed: `draft`, `scheduled`, `published`, `cancelled`. No custom statuses.
- This step loads existing data only. No new items created here.

---

## YOUR TASK

### Sequence

1. **Load content items from the task management layer.**
   - Query `tasks/todos/` for all tasks tagged or categorized as content.
   - For each item, extract: type, topic, deadline, status, next_action.
   - Recognized content types:

   | Type | Examples |
   |------|---------|
   | `article` | Blog post, LinkedIn article, Forbes piece, newsletter, thought leadership essay |
   | `talk` | Keynote, conference session, workshop, fireside chat, panel |
   | `podcast` | Guest appearance, own podcast episode, recorded interview |
   | `social-post` | LinkedIn post, Twitter/X thread, short-form content piece |

2. **Cross-reference with Calendar MCP.**
   - Query Calendar MCP for upcoming speaking engagements, podcast appearances, and media dates.
   - Match calendar events to task management content items.
   - If a calendar event exists with no corresponding content task, create a content item entry and flag it as `status: draft` with `next_action: Create content for this event`.

3. **Validate statuses.** For each content item:
   - Confirm status is one of: `draft`, `scheduled`, `published`, `cancelled`.
   - If status is missing or unrecognized, default to `draft` and note the correction.

4. **Store results** in working memory:
   ```
   content_inventory:
     total_items: N
     items:
       - id: ...
         type: article | talk | podcast | social-post
         topic: ...
         deadline: YYYY-MM-DD
         status: draft | scheduled | published | cancelled
         next_action: ...
         calendar_event_id: ... | null
         source: task-management | calendar-only
   ```

---

## SUCCESS METRICS

- All content items loaded from task management layer
- Calendar events cross-referenced and matched
- Unmatched calendar events flagged as new content items
- All statuses validated
- `content_inventory` stored in working memory for step 02

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No content items in task management | Report: "No content commitments found. Ready to add your first content item — what are you working on? (Article, talk, podcast, or social post?)" |
| Calendar MCP unavailable | Proceed with task management data only. Note: "Calendar MCP unavailable — event-linked content may be incomplete." |
| Content item has no deadline | Include in inventory with `deadline: null`. Flag for deadline assignment in step 04. |
| Status is invalid | Default to `draft`. Note: "Status '[value]' not recognized for [topic] — defaulted to draft." |

---

## NEXT STEP

Read fully and follow: `step-02-deadline-management.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

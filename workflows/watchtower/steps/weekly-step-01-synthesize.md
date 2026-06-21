---
status: complete
started-at: "2026-06-20T12:00:00Z"
completed-at: "2026-06-20T12:05:00Z"
outputs:
  items_in_queue: 0
  themes_identified: 4
  used_fallback: true
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Pull from `accumulated-context.content_queue` — this is the week's content-worthy items as flagged by daily runs.
3. If content_queue is empty, check the past 7 days of `seen.jsonl` and re-score the top-scoring items as a fallback. Do not report "nothing to synthesize" without trying.
4. Synthesize into themes — do not simply re-list items. Look for patterns across items.
5. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | sonnet |
| Input | `accumulated-context.content_queue`, `config.yaml profile.lenses`, `identity/MEMORY.md` |
| Output | Synthesized themes written to `accumulated-context.weekly_themes` in `state.yaml` |

---

## CONTEXT BOUNDARIES

- Scope: synthesis and theme identification. No drafting, no source proposals.
- "Theme" = a pattern or through-line that cuts across 2+ items, or a single high-signal item significant enough to stand alone.
- Aim for 2–5 themes. More than 5 suggests insufficient filtering — collapse or drop.

---

## YOUR TASK

1. Read `accumulated-context.content_queue` from `state.yaml`. These are this week's content-worthy items (flagged `content_worthy: true` by daily step-03).

2. If `content_queue` is empty or has fewer than 2 items: pull `workflows/watchtower/seen.jsonl`, filter to entries from the past 7 days, and re-score the top 5 by consulting David's lenses in `config.yaml`. Use these as the working set and note in outputs that you used the fallback.

3. Group items by theme. A theme is a pattern, trend, or through-line that:
   - Cuts across multiple items, OR
   - Represents a single item of unusually high relevance (score ≥ 85).

4. For each theme, write a brief synthesis note (2–4 sentences): what the theme is, what items it draws from, and why it matters to David specifically.

5. Write themes to `accumulated-context.weekly_themes` in `state.yaml`. Schema:
   ```yaml
   - theme_id: <int, 1-based>
     theme_title: "string"
     synthesis: "string (2-4 sentences)"
     source_items: [<item titles>]
     content_angles: []   # populated by step-02
   ```

6. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     items_in_queue: <int>
     themes_identified: <int>
     used_fallback: <bool>
   ```

---

## SUCCESS METRICS

- At least one theme identified (or explicit "no themes" with reason if queue was genuinely empty after fallback).
- Each theme has a synthesis note tied to David's specific lenses — not generic observations.
- `weekly_themes` written to `state.yaml`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `content_queue` absent from state | Use fallback (seen.jsonl re-score); log it |
| `seen.jsonl` also empty (first-ever run) | Write "No items to synthesize this week — first run." and continue to step-02 with empty themes |
| More than 8 items in queue | Prioritize by score descending; synthesize the top 8 |

---

## NEXT STEP

`workflows/watchtower/steps/weekly-step-02-draft-angles.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

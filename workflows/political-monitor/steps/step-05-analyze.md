---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Analyze

## MANDATORY EXECUTION RULES

1. `counts` must use the exact keys below. The render script hard-validates them and will abort if any are missing or wrong type.

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** `clusters.json` and `harvest.json`
**Output:** `systems/political-monitor/runs/YYYY-MM-DD.json` and an updated `topic_history.json`

---

## YOUR TASK

Read `clusters.json` AND `harvest.json`. Do the authoritative SEMANTIC clustering yourself - the script under-merges short headlines, so re-group by actual topic. Then:

- **Shared topics** (left AND right both cover it): a one-paragraph neutral summary of the event; `left.framing` and `right.framing` (how each side covers it, with source links); a `correlation` 0-100 and a one-line neutral `correlation_label`.
- **Correlation rubric:** 85-100 same facts+framing; 65-84 agree on facts, diverge on emphasis; 40-64 same event, materially different framing; 20-39 sharply divergent narratives; 0-19 effectively two different stories.
- **gap_left / gap_right:** topics covered by exactly one side (center coverage does not disqualify a gap). One-paragraph summary + sources each. **Parity rule:** each side must have AT LEAST as many gap topics as there are shared topics (`gap_left >= shared`, `gap_right >= shared`). If you're short, re-analyze the beat-search items already in `harvest.json` semantically — relabel, re-cluster, or re-examine source grouping to surface additional left-only or right-only topics. Do NOT re-fetch; beat searches are your data source. If parity still isn't met after this semantic re-work, the coverage genuinely isn't there in the accessible sources — document why in the run output. Total size may grow.
- **Relevance (score before deciding what to present):** read `systems/political-monitor/topic_history.json`. For every topic (shared, gap_left, gap_right) compute a `topic_key` (slug of its 3-5 most distinctive keywords) and semantically match it against history entries whose `last_seen` is the previous run date. Match → `days_seen = history.days_seen + 1`; no match → `days_seen = 1`. Then `relevance = max(20, 100 - (days_seen - 1) * 30)`, with `relevance_label`: day1 "New — first appearance", day2 "Recurring — day 2", day3 "Recurring — day 3, losing novelty", day4+ "Long-running — persistent story, low novelty". Rewrite `topic_history.json`: update matched entries (`last_seen`, `days_seen`, `title_latest`), add new entries for `days_seen==1` topics, and prune any entry whose `last_seen` is more than 5 days old.
- **Stale topic suppression:** After scoring, drop any topic with `days_seen >= 3` from the final `shared_topics`, `gap_left`, and `gap_right` lists written to the run JSON. These topics are already captured in `topic_history.json` for decay tracking — they simply don't appear on the dashboard. If suppression would leave a section empty, mine the harvest for additional topics that are `days_seen <= 2` before falling back to a stale topic. Maintain the parity rule (`gap_left >= shared`, `gap_right >= shared`) on the post-suppression counts.
- **Final sort order:** `shared_topics` → sort by `correlation` descending (most-aligned stories at top). `gap_left` and `gap_right` → sort by `relevance` descending (freshest stories at top).
- Write `systems/political-monitor/runs/YYYY-MM-DD.json` matching the schema in the spec, including `topic_key`, `days_seen`, `relevance`, `relevance_label` on every topic.
- `counts` **must use these exact keys** (the render script hard-validates them and will abort if any are missing or wrong type):
  ```json
  "counts": {
    "total_items": <int>,
    "by_lean": { "left": <int>, "right": <int>, "center": <int> },
    "shared_topics": <int>,
    "gap_left": <int>,
    "gap_right": <int>
  }
  ```
  Do not use `items_harvested`, `shared`, or any other key names. These are the only accepted field names.
- Fill `sources_used`, `sources_muted`, `generated`, `window_hours`.

## NEXT STEP

Read fully and follow: `step-06-source-suggestions.md`
<!-- system:end -->

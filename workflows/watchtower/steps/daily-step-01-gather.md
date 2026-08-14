---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `config.yaml` and `sources.yaml` before issuing any fetch or search. Only fetch from `status: active` sources.
3. Collect from RSS feeds AND web searches. Do not skip either.
4. Do NOT score, dedupe, or summarize — that is steps 02-04.
5. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `sources.yaml` (active sources), `config.yaml` (profile/lenses) |
| Output | Raw candidate item list written to `accumulated-context.raw_items` in `state.yaml` |

---

## YOUR TASK

1. Read `workflows/watchtower/config.yaml`. Note `profile.lenses` and `outputs.obsidian_topic_tags` topic keys.

2. Read `workflows/watchtower/sources.yaml`. Extract all entries with `status: active`.

3. For each active source with a non-null `rss` URL: fetch the feed. Collect all items published within the last 48 hours.

4. For each topic (`ai-agentic`, `it-consulting`, `texas-regional`, `leadership`): run 2-3 targeted web searches using the corresponding lens from `config.yaml profile.lenses`. Collect results as candidate items.

5. Merge RSS items and web search results into a single flat list. Include duplicates — step-02 handles them.

6. Write the list to `state.yaml` `accumulated-context` under key `raw_items`. Schema per item:
   ```yaml
   - title: "string"
     url: "string"
     source_name: "string"
     published_date: "YYYY-MM-DD"   # ISO-8601; use today if unavailable
     topic: "ai-agentic|it-consulting|texas-regional|leadership"
     raw_snippet: "string (≤300 chars)"
   ```

7. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     item_count: <int>
     sources_fetched: <int>
     failed_sources: []
   ```

---

**On failure:** no active sources → log, still run web searches for all four topics; RSS unreachable → log to `outputs.failed_sources`, continue; web search empty → broaden query, log if still empty; `config.yaml` missing → abort with "[Knox]: Watchtower config.yaml not found. Cannot run."

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-02-dedupe.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

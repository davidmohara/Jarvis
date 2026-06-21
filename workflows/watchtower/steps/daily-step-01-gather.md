---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `config.yaml` and `sources.yaml` before issuing any fetch or search.
3. Only fetch from sources with `status: active` in `sources.yaml`.
4. Collect items from RSS feeds AND web searches. Do not skip either.
5. Do NOT score, dedupe, or summarize here — that is steps 02-04.
6. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `sources.yaml` (active sources), `config.yaml` (profile/lenses) |
| Output | Raw candidate item list written to `accumulated-context.raw_items` in `state.yaml` |

---

## CONTEXT BOUNDARIES

- Scope: fetch and collect only. No filtering, no scoring, no judgment calls.
- If an RSS feed is unreachable, log it in outputs.failed_sources and continue — do not abort.
- Web searches use David's lenses from `config.yaml profile.lenses` as query basis.
- Collect per item: `title`, `url`, `source_name`, `published_date`, `raw_snippet`.
- Published date: use ISO-8601 (`YYYY-MM-DD`). If unavailable, use today's date and note it.

---

## YOUR TASK

1. Read `workflows/watchtower/config.yaml`. Note `profile.lenses` and `outputs.obsidian_topic_tags` topic keys.

2. Read `workflows/watchtower/sources.yaml`. Extract all entries with `status: active`.

3. For each active source with a non-null `rss` URL: fetch the feed. Collect all items published within the last 48 hours (cast a wide net; dedupe narrows it in step-02).

4. For each topic (`ai-agentic`, `it-consulting`, `texas-regional`, `leadership`): run 2-3 targeted web searches using the corresponding lens from `config.yaml profile.lenses`. Collect results as candidate items.

5. Merge RSS items and web search results into a single flat list. Include duplicates — step-02 handles them.

6. Write the list to `state.yaml` `accumulated-context` under key `raw_items`. Schema per item:
   ```yaml
   - title: "string"
     url: "string"
     source_name: "string"
     published_date: "YYYY-MM-DD"
     topic: "ai-agentic|it-consulting|texas-regional|leadership"
     raw_snippet: "string (≤300 chars)"
   ```

7. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     item_count: <int>
     sources_fetched: <int>
     failed_sources: []  # list source names that errored
   ```

---

## SUCCESS METRICS

- At least one item collected per active source.
- Web searches executed for all four topic lenses.
- `raw_items` written to `state.yaml` accumulated-context.
- Zero items scored, filtered, or summarized — that is NOT this step's job.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No active sources in sources.yaml | Log warning; still run web searches for all four topics |
| RSS feed unreachable | Log to `outputs.failed_sources`; continue with remaining sources |
| Web search returns zero results | Broaden query slightly; log if still empty |
| `config.yaml` missing | Abort; surface: "[Knox]: Watchtower config.yaml not found. Cannot run." |

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-02-dedupe.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

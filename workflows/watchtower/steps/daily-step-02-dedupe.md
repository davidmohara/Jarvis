---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `seen.jsonl` before comparing. Create it if it does not exist (empty file).
3. Match on BOTH `url` AND `normalized_title` per `config.yaml dedupe.match_on`. An item is a duplicate if EITHER field matches within the lookback window.
4. Do NOT modify items — drop or keep only. Append NEW items to `seen.jsonl` after filtering, not before.
5. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `accumulated-context.raw_items` (from step-01), `seen.jsonl`, `config.yaml dedupe` settings |
| Output | Deduplicated item list written to `accumulated-context.deduped_items` in `state.yaml` |

---

## YOUR TASK

1. Read `workflows/watchtower/config.yaml`. Note `dedupe.lookback_days` (default 14) and `dedupe.match_on`.

2. Read `workflows/watchtower/seen.jsonl` (NDJSON). Schema per line: `{"url": "string", "normalized_title": "string", "seen_date": "YYYY-MM-DD"}`. Create empty file if missing.

3. Build a lookup set: all `seen.jsonl` entries where `seen_date` is within the last `lookback_days` days.

4. For each item in `accumulated-context.raw_items`:
   - Compute `normalized_title` (lowercase, strip punctuation, collapse whitespace).
   - If `url` OR `normalized_title` matches any seen entry → DROP. Otherwise → KEEP.

5. Write kept items to `accumulated-context.deduped_items` in `state.yaml` (same schema as `raw_items` plus `normalized_title`).

6. Append each kept item to `seen.jsonl`: `{"url": "...", "normalized_title": "...", "seen_date": "YYYY-MM-DD"}`

7. Write `outputs`:
   ```yaml
   outputs:
     raw_count: <int>
     dropped_count: <int>
     kept_count: <int>
   ```

---

**On failure:** `raw_items` missing → abort with "[Knox]: Step-01 did not produce raw_items. Re-run from step-01."; `seen.jsonl` parse error → treat as empty, log, continue; all items deduped → continue with empty list, this is valid.

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-03-score.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

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
3. Match on BOTH `url` AND `normalized_title` per `config.yaml dedupe.match_on`. An item is a duplicate if EITHER field matches an entry within the lookback window.
4. Do NOT modify items — drop them or keep them. No partial edits here.
5. Append NEW (non-duplicate) items to `seen.jsonl` after filtering — not before.
6. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `accumulated-context.raw_items` (from step-01), `seen.jsonl`, `config.yaml dedupe` settings |
| Output | Deduplicated item list written to `accumulated-context.deduped_items` in `state.yaml` |

---

## CONTEXT BOUNDARIES

- Scope: deduplication only. No scoring, no summarizing.
- Lookback window: `config.yaml dedupe.lookback_days` (default 14).
- `seen.jsonl` path: `workflows/watchtower/seen.jsonl`
- Normalized title: lowercase, strip punctuation, collapse whitespace.
- Items from today's run that pass deduplication are NEW — add them to `seen.jsonl`.

---

## YOUR TASK

1. Read `workflows/watchtower/config.yaml`. Note `dedupe.lookback_days` and `dedupe.match_on`.

2. Read `workflows/watchtower/seen.jsonl`. Parse as newline-delimited JSON. Each line has schema:
   ```json
   {"url": "string", "normalized_title": "string", "seen_date": "YYYY-MM-DD"}
   ```
   If the file does not exist, create it empty and treat the seen set as empty.

3. Build a lookup set: all entries from `seen.jsonl` where `seen_date` is within the last `lookback_days` days.

4. For each item in `accumulated-context.raw_items`:
   - Compute `normalized_title` (lowercase, strip punctuation, collapse whitespace).
   - Check against lookup set. If `url` OR `normalized_title` matches any seen entry → DROP.
   - If no match → KEEP.

5. Write kept items to `accumulated-context.deduped_items` in `state.yaml` (same schema as `raw_items` plus `normalized_title` field added).

6. Append each kept item to `seen.jsonl` as a new line:
   ```json
   {"url": "...", "normalized_title": "...", "seen_date": "YYYY-MM-DD"}
   ```

7. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     raw_count: <int>        # items coming in from step-01
     dropped_count: <int>    # duplicates removed
     kept_count: <int>       # items passing to step-03
   ```

---

## SUCCESS METRICS

- `deduped_items` written to `state.yaml` with count ≥ 0.
- `seen.jsonl` updated with all new items.
- No item appears in `deduped_items` that was in `seen.jsonl` within the lookback window.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `raw_items` missing from accumulated-context | Abort; surface: "[Knox]: Step-01 did not produce raw_items. Re-run from step-01." |
| `seen.jsonl` parse error | Treat as empty; log warning in outputs; continue |
| All items deduped (zero kept) | Continue with empty list; step-03 will produce an empty run — this is valid |

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-03-score.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

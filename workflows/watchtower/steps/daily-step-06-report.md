---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Keep the report short — under 150 words. David reads this as a surface, not a deep read.
3. Call out content-worthy items by name. David needs to know what's queued for the weekly run.
4. If today's run produced zero items, say so plainly. Do not pad.
5. Hand content-worthy items to the weekly queue by writing them to `accumulated-context.content_queue` in `state.yaml`.
6. Write `status: complete`, `completed-at`, and `outputs` when done. Set `state.yaml status: complete`.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `accumulated-context.summarized_items` (from step-04), `accumulated-context` full context |
| Output | Terminal report surfaced to David; `accumulated-context.content_queue` updated |

---

## CONTEXT BOUNDARIES

- Scope: final daily report and queue handoff only.
- This is the last step of the daily run. Close state cleanly.
- The content_queue is read by the weekly run's step-01.
- Do NOT start drafting hooks or outlines here — that is the weekly run.

---

## YOUR TASK

1. Tally the run:
   - Total items gathered (step-01 `item_count`)
   - Dropped as duplicates (step-02 `dropped_count`)
   - Dropped below awareness floor (step-03 `dropped_below_floor`)
   - Surviving awareness items
   - Content-worthy items

2. Write the terminal report to surface to David. Format:

   ```
   Watchtower — [DATE]
   [N] items surfaced | [N] content candidates

   Topics covered: [list topics that had items]
   Content queue additions: [item titles, one per line, or "none"]

   Dashboard available. Obsidian: Watchtower/Daily/[DATE].md
   ```

   If `accumulated-context.retirements_today` is non-empty, append:

   ```
   Sources retired (dormant 21d): [source name(s), comma-separated]
   ```

   If zero items: "Watchtower — [DATE]. No new items above the awareness floor today."

3. Write content-worthy items to `accumulated-context.content_queue` in `state.yaml`. This is the handoff to the weekly run. Schema per item: carry forward all fields from `summarized_items` for items where `content_worthy: true`.

   If `content_queue` already has entries from previous daily runs this week, APPEND — do not overwrite.

4. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     total_gathered: <int>
     total_surfaced: <int>
     content_queue_additions: <int>
     obsidian_note_path: "Watchtower/Daily/YYYY-MM-DD.md"
   ```

5. Set `state.yaml status: complete`.

---

## SUCCESS METRICS

- Report surfaced to David in under 150 words.
- `content_queue` in `state.yaml` updated with any new content-worthy items.
- `state.yaml status` set to `complete`.
- Run totals are accurate against step outputs.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `summarized_items` missing | Use step outputs from earlier steps to reconstruct counts; surface report with available data |
| `content_queue` write fails | Log; the items are still in `summarized_items` and recoverable |
| State already complete | Log; do not re-run the daily without David's instruction |

---

## NEXT STEP

End of daily run. Step order: step-05-capture → step-07-prune → step-06-report (this step).

Weekly run begins at `workflows/watchtower/steps/weekly-step-01-synthesize.md` on Monday.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

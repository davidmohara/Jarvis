---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Keep the report under 150 words. David reads this as a surface, not a deep read.
3. Call out content-worthy items by name. Do NOT draft hooks or outlines — that is the weekly run.
4. Write content-worthy items to `accumulated-context.content_queue` (APPEND if prior entries exist).
5. Write `status: complete`, `completed-at`, and `outputs` when done. Set `state.yaml status: complete`.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `accumulated-context.summarized_items` (step-04), full accumulated-context |
| Output | Terminal report surfaced to David; `accumulated-context.content_queue` updated |

---

## YOUR TASK

1. Tally the run from step outputs: total gathered, dropped as duplicates, dropped below awareness floor, surviving awareness items, content-worthy items.

2. Write the terminal report:

   ```
   Watchtower — [DATE]
   [N] items surfaced | [N] content candidates

   Topics covered: [list topics that had items]
   Content queue additions: [item titles, one per line, or "none"]

   Dashboard available. Obsidian: Watchtower/Daily/[DATE].md
   ```

   If `retirements_today` non-empty, append: `Sources retired (dormant 21d): [names, comma-separated]`

   If zero items: "Watchtower — [DATE]. No new items above the awareness floor today."

3. Write content-worthy items to `accumulated-context.content_queue` in `state.yaml`. Carry forward all fields from `summarized_items` where `content_worthy: true`. APPEND — do not overwrite prior daily entries.

4. Write `outputs`:
   ```yaml
   outputs:
     total_gathered: <int>
     total_surfaced: <int>
     content_queue_additions: <int>
     obsidian_note_path: "Watchtower/Daily/YYYY-MM-DD.md"
   ```

5. Set `state.yaml status: complete`.

---

**On failure:** `summarized_items` missing → reconstruct counts from earlier step outputs, surface report with available data; `content_queue` write fails → log (items recoverable from `summarized_items`); state already complete → log, do not re-run without instruction.

---

## NEXT STEP

End of daily run. Step order: step-05-capture → step-07-prune → step-06-report.

Weekly run begins at `workflows/watchtower/steps/weekly-step-01-synthesize.md` on Monday.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

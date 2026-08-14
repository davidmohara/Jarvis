---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `config.yaml outputs` section before writing anything to confirm paths and tag names.
3. Write the Obsidian daily note FIRST, then build the dashboard artifact.
4. Use the Obsidian MCP server for all vault writes — do NOT write vault files via filesystem tools.
5. Do NOT write content drafts here — that is the weekly run's job.
6. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `accumulated-context.summarized_items` (step-04), `through_line` and `consulting_read` (step-04b), `config.yaml outputs` |
| Output | Obsidian daily note at `Watchtower/Daily/YYYY-MM-DD.md`; live dashboard artifact |

---

## YOUR TASK

1. Read `config.yaml`. Extract `outputs.obsidian_awareness_folder`, `outputs.obsidian_source_tag`, `outputs.obsidian_topic_tags`, and `outputs.dashboard_artifact_title`.

2. Read `accumulated-context.through_line` and `accumulated-context.consulting_read` from `state.yaml` (produced by step-04b). If missing: `through_line` → `"No synthesis available."`, `consulting_read` → null. Do not abort.

3. Construct the Obsidian daily note for `Watchtower/Daily/<today>.md`.

   **Frontmatter:**
   ```yaml
   ---
   source: watchtower
   date: YYYY-MM-DD
   tags: [watchtower, <topic-tags for all items present>]
   item_count: <int>
   content_worthy_count: <int>
   ---
   ```

   **Body:** through-line blockquote first (always, even on zero-item runs), then items grouped by topic:
   ```markdown
   # Watchtower — YYYY-MM-DD

   > [through_line]

   ## AI / Agentic Systems
   ### [Item Title](url)
   *Score: XX | Source: source_name*
   [summary paragraph]
   ```
   Only include topic sections that have items. Append `[content candidate]` after the score line for content-worthy items.

4. Write the note to Obsidian via MCP. Overwrite if re-run on the same day.

5. Build the `watchtower_daily` dashboard artifact (HTML widget via `show_widget`):
   - **Through-line banner** at top (prominent — first thing eyes land on).
   - **Consulting-read callout** if non-null (titled "The consulting read"); omit entirely if null.
   - Run date and item count stat strip.
   - Items grouped by topic: title (linked), source, score, summary, `[content candidate]` badge on flagged items.
   - Style: muted/professional.

6. Write `outputs`:
   ```yaml
   outputs:
     obsidian_note_path: "Watchtower/Daily/YYYY-MM-DD.md"
     items_captured: <int>
     dashboard_built: true
     through_line_rendered: true
     consulting_read_rendered: <true|false>
   ```

---

**On failure:** `summarized_items` missing → abort with "[Knox]: Step-04 output missing. Re-run from step-04."; `through_line`/`consulting_read` missing → log, use fallbacks, continue; Obsidian MCP unavailable → write fallback to `workflows/watchtower/fallback/YYYY-MM-DD.md`; zero items → write minimal note (through-line + "No new items today.") and minimal dashboard; dashboard build fails → log, continue (Obsidian note is primary).

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-07-prune.md`

Note: step-07-prune runs between capture and report so retirements are available when step-06 writes the terminal summary.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

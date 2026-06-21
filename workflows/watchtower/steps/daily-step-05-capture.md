---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `config.yaml outputs` section before writing anything to confirm current paths and tag names.
3. Write the Obsidian daily note FIRST, then build the dashboard artifact.
4. Use the Obsidian MCP server for all vault writes — do NOT write vault files via filesystem tools.
5. Tag every note with `#watchtower` plus the per-topic tags from `config.yaml`.
6. Build/update the dashboard artifact using the `watchtower_daily` artifact title from config.
7. Do NOT write content drafts here — that is the weekly run's job.
8. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `accumulated-context.summarized_items` (from step-04), `accumulated-context.through_line` and `accumulated-context.consulting_read` (from step-04b), `config.yaml outputs` |
| Output | Obsidian daily note at `Watchtower/Daily/YYYY-MM-DD.md`; live dashboard artifact |

---

## CONTEXT BOUNDARIES

- Scope: write vault note and dashboard only. No scoring, no summarizing.
- Vault path: `Watchtower/Daily/YYYY-MM-DD.md` (today's date).
- Dashboard artifact: titled `watchtower_daily` per config. Overwrites the previous daily if re-run on the same day.
- Topic tags from `config.yaml outputs.obsidian_topic_tags` — map each item's `topic` field to the correct tag.

---

## YOUR TASK

1. Read `config.yaml`. Extract `outputs.obsidian_awareness_folder`, `outputs.obsidian_source_tag`, `outputs.obsidian_topic_tags`, and `outputs.dashboard_artifact_title`.

2. Read `accumulated-context.through_line` and `accumulated-context.consulting_read` from `state.yaml`. These were produced by step-04b. If either is missing, treat `through_line` as `"No synthesis available."` and `consulting_read` as null — do not abort.

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

   **Body — through-line first, then grouped by topic:**
   ```markdown
   # Watchtower — YYYY-MM-DD

   > [through_line value from accumulated-context]

   ## AI / Agentic Systems
   ### [Item Title](url)
   *Score: XX | Source: source_name*
   [summary paragraph]

   ## IT Consulting & Services
   ...

   ## Texas / Regional Business
   ...

   ## Leadership
   ...
   ```
   Only include topic sections that have items. Append `[content candidate]` after the score line for content-worthy items. The through-line blockquote appears at the top of the body, before any topic sections, on every run (including zero-item runs).

4. Write the note to Obsidian via MCP at the path constructed above. If the note already exists (re-run), overwrite it.

5. Build the `watchtower_daily` dashboard artifact (HTML widget via `show_widget`). Include:
   - **Through-line banner:** render `through_line` prominently at the top of the dashboard, below the title/date line, as the marquee element. Style: slightly larger text, distinct background strip or border — it should be the first thing eyes land on.
   - **Consulting-read callout:** if `consulting_read` is non-null, render it as a callout box (e.g., titled "The consulting read") below the through-line banner and above the item list. If `consulting_read` is null, omit the callout entirely — do not show an empty box.
   - Run date and item count stat strip.
   - Items grouped by topic, each with title (linked), source, score, summary, and a `[content candidate]` badge on flagged items.
   - Color: muted/professional. No flashy styling.

6. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     obsidian_note_path: "Watchtower/Daily/YYYY-MM-DD.md"
     items_captured: <int>
     dashboard_built: true
     through_line_rendered: true
     consulting_read_rendered: <true | false>
   ```

---

## SUCCESS METRICS

- Obsidian daily note exists at the correct path with correct frontmatter and tags.
- Through-line blockquote appears at the top of the Obsidian note body.
- Dashboard artifact built and visible with through-line banner rendered.
- Consulting-read callout rendered in dashboard when non-null; omitted when null.
- Every summarized item appears in the note under the correct topic section.
- No content drafts written (those belong to the weekly run).

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `summarized_items` missing | Abort; surface: "[Knox]: Step-04 output missing. Re-run from step-04." |
| `through_line` or `consulting_read` missing from accumulated-context | Log warning; substitute fallback strings (see step 2 above); do not abort |
| Obsidian MCP unavailable | Log warning; write note to `workflows/watchtower/fallback/YYYY-MM-DD.md` via filesystem as fallback |
| Zero summarized items | Write a minimal note (through-line only + "No new items today.") and a minimal dashboard — do not skip |
| Dashboard build fails | Log; continue — the Obsidian note is the primary output |

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-07-prune.md`

Note: The prune step runs between capture and report so that retirements from today's run are available when step-06 writes the terminal summary.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

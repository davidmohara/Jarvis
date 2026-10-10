---
status: complete
started-at: "2026-08-31T08:00:00Z"
completed-at: "2026-08-31T08:20:00Z"
outputs:
  artifact_updated: true
  artifact_id: watchtower-weekly
  themes_surfaced: 3
  candidates_surfaced: 3
  sources_proposed: 5
  tweets_surfaced: 10
  weekly_note_path: "Watchtower/Weekly/2026-W36.md"
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Keep the report under 200 words. This is a surface, not a brief.
3. Explicitly name each content candidate and each source proposal by name — David needs to act on these.
4. The report surfaces two action items: (a) review content candidates in Obsidian, (b) approve/reject source proposals in proposed-sources.md.
5. **UPDATE THE DASHBOARD ARTIFACT — PRE-FLIGHT REQUIRED.** Before writing a single line of report content:
   a. Read `config.yaml` → `outputs.weekly_dashboard_artifact_url` to get the artifact URL.
   b. Call `Artifact` with `action: "read"` and that URL to get the current HTML.
   c. Prepend a new `<div class="week-view active" id="view-wNN">` block for this week using this run's themes/drafts/proposals/tweets, update the `<select>` to include the new week option as first/selected, remove `active` from the previous week's block, update `runMeta` in the JS.
   d. Write the updated HTML to a temp file, then call `Artifact` with `action: "publish"`, `file_path: <temp path>`, `url: <artifact_url>`.
   e. **If publish is blocked** (Cowork session constraint — error contains "approval card"): write the full updated HTML to `workflows/watchtower/artifact-update/watchtower-weekly.html`. Log `artifact_updated: false`, `artifact_fallback_written: true`. Surface the fallback path to David.
   f. Do NOT call `mcp__cowork__list_artifacts` or `mcp__cowork__update_artifact` — these tools do not exist and have never existed.
   **This is non-negotiable. The dashboard is the primary way David reviews the week's output.**
6. Set `state.yaml status: complete` and clear `content_queue` after report is surfaced.
7. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | All accumulated-context from the weekly run |
| Output | Terminal report surfaced to David; `state.yaml` closed |

---

## CONTEXT BOUNDARIES

- Scope: final weekly report and state cleanup only.
- This is the last step of the weekly run. Close state cleanly.
- Do not start a new analysis or draft here.

---

## ⛔ ARTIFACT UPDATE GATE — DO NOT PROCEED PAST THIS LINE UNTIL COMPLETE

The artifact update mechanism is defined in MANDATORY RULE 5 above.

**You may not write the terminal report. You may not update `state.yaml`. You may not write `status: complete` to this file. Until the artifact update has been attempted (success, or confirmed Cowork block with fallback file written).**

---

## YOUR TASK

1. Collect from accumulated-context AND live file reads:
   - `weekly_themes` → theme titles
   - Step-02 `drafts_created`, `draft_paths`
   - Step-02b `weekly_tweets` → array of `{text, supporting_url, intent_url}` objects
   - Step-03 `proposed_count`, `batch_number`
   - Step-04 `weekly_note_path`
   - Read `dormant-sources.yaml` — collect any sources with `retired` date in the past 7 days.
   - **Read `workflows/watchtower/proposed-sources.md` now.** Scan every batch under `## Approval Queue`. A batch is "pending" only if at least one row in that batch has `Status` = `pending`. Do NOT trust prior context or dashboard banners — derive the pending batch list from the live file. This is the source of truth. If all rows in every batch are `approved` or `rejected`, there are no pending batches. Log the result as `pending_batches: [N, N, ...]` or `pending_batches: []` before proceeding.
   - **Read `workflows/watchtower/sources.yaml` now.** For every batch where `proposed-sources.md` shows an `approved` row, verify the approved source is present in `sources.yaml` with `status: active`. If any approved source is missing from `sources.yaml`, add it before writing the report and note `sources_added_to_registry: [name, ...]` in outputs.

2. Write the terminal report to surface to David. Format:

   ```
   Watchtower — Week [YYYY-Www]

   [N] themes synthesized | [N] content candidates | [N] sources proposed

   Content candidates ready:
   - "_<slug>.md" — <post title> (blog/linkedin/forbes)
   - ...

   Source proposals awaiting your yes/no:
   - Batch [N] in workflows/watchtower/proposed-sources.md
   (List only batches derived from the live proposed-sources.md read in step 1. If pending_batches is empty, write: "All source batches resolved.")

   Weekly note: Watchtower/Weekly/[YYYY-Www].md

   Tweets This Week:
   1. <tweet text>
      [Post to X →](intent_url)
   2. ...
   (continue for all 10 tweets)
   ```

   Render each tweet as its plain text on one line, followed by the `[Post to X →](intent_url)` markdown link on the next line. If `supporting_url` is present and non-null, also render `[Source →](supporting_url)` on the same line as the Post link. Follow with a blank line before the next tweet. This is what David sees in the dashboard — each tweet is a single click to post.

   If `weekly_tweets` is empty or absent, write: *No tweets generated this week.*

   If any sources were retired this week (dormant 21d), append:

   ```
   Sources retired this week (no signal in 21 days):
   - [source name] (added [date], retired [date])
   — revive by moving back to sources.yaml and adding to source-activity.json
   ```

   If zero candidates: "No content candidates this week."
   If zero proposals: "No new source proposals this week."
   If zero retirements: omit the retirements block entirely.

3. Clear `accumulated-context.content_queue` in `state.yaml` — the weekly run has consumed it.

4. Set `state.yaml status: complete`.

6. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     themes_surfaced: <int>
     candidates_surfaced: <int>
     sources_proposed: <int>
     tweets_surfaced: <int>   # count of tweets rendered in report (0-10)
     weekly_note_path: "Watchtower/Weekly/YYYY-Www.md"
     artifact_updated: <true | false>
   ```

---

## SUCCESS METRICS

- Report surfaced to David under 200 words (tweets section does not count toward word limit).
- Content candidate post titles named explicitly.
- Source proposals named/batched explicitly with the file path.
- **Tweets This Week section rendered** with all 10 tweets and clickable `[Post to X →]` intent links.
- **`watchtower-weekly` artifact updated** with this week's themes, drafts, proposals, and tweets.
- `content_queue` cleared in `state.yaml`.
- `state.yaml status: complete`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Any step output missing | Surface what is available; note what is missing; still close state |
| `state.yaml` write fails | Log; surface the report anyway — David has the information |
| Zero themes, candidates, and proposals | Surface: "Watchtower ran — nothing surfaced this week. Awareness floor may be too high, or source coverage is thin." |
| Dashboard artifact update fails | Log `artifact_updated: false` in outputs; surface: "Dashboard update failed — open `watchtower-weekly` artifact manually and it will show stale data until next run." |

---

## NEXT STEP

End of weekly run. Daily run resumes Tuesday.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

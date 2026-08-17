---
status: complete
started-at: "2026-08-17T07:55:00Z"
completed-at: "2026-08-17T08:10:00Z"
outputs:
  themes_surfaced: 3
  candidates_surfaced: 3
  sources_proposed: 3
  tweets_surfaced: 10
  weekly_note_path: "Watchtower/Weekly/2026-W34.md"
  artifact_updated: true
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Keep the report under 200 words. This is a surface, not a brief.
3. Explicitly name each content candidate and each source proposal by name — David needs to act on these.
4. The report surfaces two action items: (a) review content candidates in Obsidian, (b) approve/reject source proposals in proposed-sources.md.
5. **UPDATE THE DASHBOARD ARTIFACT — PRE-FLIGHT REQUIRED.** Before writing a single line of report content:
   a. Call `ToolSearch` with query `"select:mcp__cowork__list_artifacts,mcp__cowork__update_artifact"` to load the artifact tools. Do this FIRST. Not after the report. Not as an afterthought. FIRST.
   b. Call `mcp__cowork__list_artifacts` to find the `watchtower-weekly` artifact id and HTML path.
   c. Read the artifact HTML at the returned path.
   d. Prepend a new `<div class="week-view active" id="view-wNN">` block for this week using this run's themes/drafts/proposals/tweets, update the `<select>` to include the new week option, remove `active` from the previous latest week's block, update `runMeta` in the JS.
   e. Write the updated HTML to a temp file, then call `mcp__cowork__update_artifact` with `id: "watchtower-weekly"`.
   **This is non-negotiable. The dashboard is the primary way David reviews the week's output.**
   If the artifact update fails after a genuine attempt, log `artifact_updated: false` in outputs and surface: "Dashboard update failed — open watchtower-weekly artifact manually." Do not silently skip. Do not omit the ToolSearch pre-flight and then claim the tool was unavailable.
6. Set `state.yaml status: complete` and clear `content_queue` after report is surfaced.
7. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

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

## YOUR TASK

1. Collect from accumulated-context:
   - `weekly_themes` → theme titles
   - Step-02 `drafts_created`, `draft_paths`
   - Step-02b `weekly_tweets` → array of `{text, supporting_url, intent_url}` objects
   - Step-03 `proposed_count`, `batch_number`
   - Step-04 `weekly_note_path`
   - Read `dormant-sources.yaml` — collect any sources with `retired` date in the past 7 days.

2. Write the terminal report to surface to David. Format:

   ```
   Watchtower — Week [YYYY-Www]

   [N] themes synthesized | [N] content candidates | [N] sources proposed

   Content candidates ready:
   - "_<slug>.md" — <post title> (blog/linkedin/forbes)
   - ...

   Source proposals awaiting your yes/no:
   - Batch [N] in workflows/watchtower/proposed-sources.md

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

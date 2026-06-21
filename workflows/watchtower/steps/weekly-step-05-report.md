---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Keep the report under 200 words. This is a surface, not a brief.
3. Explicitly name each content candidate and each source proposal by name — David needs to act on these.
4. The report surfaces two action items: (a) review content candidates in Obsidian, (b) approve/reject source proposals in proposed-sources.md.
5. Set `state.yaml status: complete` and clear `content_queue` after report is surfaced.
6. Write `status: complete`, `completed-at`, and `outputs` when done.

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
   ```

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

5. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     themes_surfaced: <int>
     candidates_surfaced: <int>
     sources_proposed: <int>
     weekly_note_path: "Watchtower/Weekly/YYYY-Www.md"
   ```

---

## SUCCESS METRICS

- Report surfaced to David under 200 words.
- Content candidate post titles named explicitly.
- Source proposals named/batched explicitly with the file path.
- `content_queue` cleared in `state.yaml`.
- `state.yaml status: complete`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Any step output missing | Surface what is available; note what is missing; still close state |
| `state.yaml` write fails | Log; surface the report anyway — David has the information |
| Zero themes, candidates, and proposals | Surface: "Watchtower ran — nothing surfaced this week. Awareness floor may be too high, or source coverage is thin." |

---

## NEXT STEP

End of weekly run. Daily run resumes Tuesday.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: complete
started-at: "2026-08-03T07:05:00Z"
completed-at: "2026-08-03T07:12:00Z"
outputs:
  items_in_queue: 0
  themes_identified: 4
  dropped_as_continuing: 0
  used_fallback: true
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. **VERIFY ISO WEEK NUMBER FIRST.** Before writing any output, run `date +%V` to confirm the ISO week number for today's date. Store the confirmed week as `YYYY-Www` (e.g. `2026-W27`). Every file, note, and artifact this run writes uses this confirmed value. Do not derive or guess the week from the date manually — always use the system clock. This rule exists because a wrong week number propagated through an entire run (err-20260629T155429-PCC4BZ).
2. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
3. Pull from `accumulated-context.content_queue` — this is the week's content-worthy items as flagged by daily runs.
4. If content_queue is empty, check the past 7 days of `seen.jsonl` and re-score the top-scoring items as a fallback. Do not report "nothing to synthesize" without trying.
5. Synthesize into themes — do not simply re-list items. Look for patterns across items.
6. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | sonnet |
| Input | `accumulated-context.content_queue`, `config.yaml profile.lenses`, `identity/MEMORY.md` |
| Output | Synthesized themes written to `accumulated-context.weekly_themes` in `state.yaml` |

---

## CONTEXT BOUNDARIES

- Scope: synthesis and theme identification. No drafting, no source proposals.
- "Theme" = a pattern or through-line that cuts across 2+ items, or a single high-signal item significant enough to stand alone.
- Aim for 2–5 themes. More than 5 suggests insufficient filtering — collapse or drop.

---

## YOUR TASK

1. Read `accumulated-context.content_queue` from `state.yaml`. These are this week's content-worthy items (flagged `content_worthy: true` by daily step-03).

2. If `content_queue` is empty or has fewer than 2 items: pull `workflows/watchtower/seen.jsonl`, filter to entries from the past 7 days, and re-score the top 5 by consulting David's lenses in `config.yaml`. Use these as the working set and note in outputs that you used the fallback.

3. **DELTA CHECK — run this before finalizing any theme.** Read the prior two weeks' notes from `Watchtower/Weekly/` in Obsidian (or `workflows/watchtower/fallback/weekly/` if Obsidian was unavailable). For each candidate theme, explicitly ask: "Is this a new argument, or is this new data supporting an argument I already surfaced in the past two weeks?"

   - **New argument** = promote it as a theme.
   - **New data, same argument** = only promote if the new data materially changes the recommended action for David's audience (i.e., something they should now do differently). If it doesn't, flag it as a "continuing story" and drop it from themes. Note the drop in `outputs.dropped_as_continuing`.
   - **Same data reframed** = drop it entirely.

   The goal is that every theme this week teaches David's audience something they could not have learned from last week's content. Redundancy is a failure mode, not a safety net.

4. For each theme that passes the delta check, write a brief synthesis note (2–4 sentences): what the theme is, what items it draws from, why it matters to David specifically, and — critically — **what is new this week that wasn't true last week**.

5. Write themes to `accumulated-context.weekly_themes` in `state.yaml`. Schema:
   ```yaml
   - theme_id: <int, 1-based>
     theme_title: "string"
     synthesis: "string (2-4 sentences)"
     source_items: [<item titles>]
     content_angles: []   # populated by step-02
   ```

6. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     items_in_queue: <int>
     themes_identified: <int>
     dropped_as_continuing: <int>   # themes dropped because they were continuing stories, not new arguments
     used_fallback: <bool>
   ```

---

## SUCCESS METRICS

- At least one theme identified (or explicit "no themes" with reason if queue was genuinely empty after fallback).
- Each theme has a synthesis note tied to David's specific lenses — not generic observations.
- `weekly_themes` written to `state.yaml`.
- `accumulated-context` contains `delta_check_applied: true` — a run that skips the delta check fails this metric regardless of theme count.
- `dropped_as_continuing` is present in outputs and is an integer (zero is acceptable; absent is not).

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `content_queue` absent from state | Use fallback (seen.jsonl re-score); log it |
| `seen.jsonl` also empty (first-ever run) | Write "No items to synthesize this week — first run." and continue to step-02 with empty themes |
| More than 8 items in queue | Prioritize by score descending; synthesize the top 8 |
| Delta check drops all themes | Surface: "All candidate themes this week are continuations of prior weeks. Consider approving Batch [N] source proposals to broaden coverage." Then check whether any continuing-story theme has *new recommended action* strong enough to justify one slot. If yes, promote the strongest one only. |
| Delta check drops to fewer than 2 themes | Same as above — broaden by re-scoring seen.jsonl with stricter novelty filter, or surface fewer themes rather than padding with repeats. 1 strong new theme beats 4 redundant ones. |

---

## NEXT STEP

`workflows/watchtower/steps/weekly-step-02-draft-angles.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

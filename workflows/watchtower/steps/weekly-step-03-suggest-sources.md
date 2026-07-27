---
status: complete
started-at: "2026-07-20T07:32:00Z"
completed-at: "2026-07-20T07:38:00Z"
outputs:
  proposed_count: 5
  excluded_count: 37
  batch_number: 5
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. **CHECK THE KILL SWITCH FIRST.** Read `config.yaml`. If `source_suggestions.enabled` is `false`, skip this entire step: write `status: complete`, set `outputs.proposed_count: 0`, note `skipped: true` in outputs, and proceed to step-04. Do not propose anything, do not search, do not modify `proposed-sources.md`.
3. Read `sources.yaml` and `proposed-sources.md` before proposing anything — do not suggest sources already active or already pending.
4. Never write a source to `sources.yaml`. That is a human-gated action.
5. Only APPEND to `proposed-sources.md` under the current week's batch header. Do not rewrite previous batches.
6. Respect `config.yaml source_suggestions.max_per_week` — propose no more than that number.
7. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | sonnet |
| Input | `accumulated-context.weekly_themes`, `sources.yaml`, `proposed-sources.md`, `config.yaml source_suggestions` |
| Output | New proposals appended to `workflows/watchtower/proposed-sources.md` |

---

## CONTEXT BOUNDARIES

- Scope: propose new sources only. Never add them. Never approve them.
- Source discovery: use web search to find sources adjacent to this week's themes that are not already in `sources.yaml` or `proposed-sources.md`.
- Quality bar: only propose sources with consistent publication cadence, topical relevance, and ideally an RSS feed.
- Trust level is your judgment call — `high` for known publications with editorial standards, `med` for everything else.

---

## YOUR TASK

1. Read `config.yaml`. Note `source_suggestions.max_per_week` and `source_suggestions.require_approval` (always true).

2. Read `sources.yaml`. Extract the full list of active and paused source URLs/names.

3. Read `proposed-sources.md`. Extract all sources already in the approval queue (pending, approved, and rejected).

4. Build the exclusion set: all sources in steps 2 and 3.

5. Based on this week's themes from `accumulated-context.weekly_themes`, use web search to discover up to `max_per_week` candidate sources that:
   - Are NOT in the exclusion set.
   - Are relevant to one or more of David's topic lenses.
   - Publish regularly (weekly or more frequently).
   - Have a discoverable RSS feed (check for `/feed`, `/rss`, Substack, etc.).

6. For each candidate, assess:
   - `name`: publication or newsletter name
   - `url`: homepage
   - `rss`: feed URL if found, null if not
   - `topic`: best-fit topic key
   - `trust`: high | med
   - `why_relevant`: 1-2 sentences tying it to David's lenses or this week's themes

7. Append a new batch to `proposed-sources.md` under `## Approval Queue`:
   ```markdown
   ### Batch <N> — Weekly Run ([YYYY-MM-DD])

   | Name | URL | RSS | Topic | Trust | Why Relevant | Status |
   |------|-----|-----|-------|-------|--------------|--------|
   | <name> | <url> | <rss|null> | <topic> | <trust> | <why_relevant> | pending |
   ```
   Increment batch N from the last batch number in the file.

8. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     proposed_count: <int>
     excluded_count: <int>   # how many candidates were excluded (already known)
     batch_number: <int>
   ```

---

## SUCCESS METRICS

- No proposed source is in `sources.yaml` or already in `proposed-sources.md`.
- Proposal count does not exceed `max_per_week`.
- Each proposal includes a `why_relevant` explanation tied to David's actual lenses.
- `proposed-sources.md` updated; no existing content modified.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Web search returns no new candidates | Write "No new source proposals this week — all candidates already known." and continue |
| `proposed-sources.md` not found | Create it using the template from this workflow's file; log it |
| Candidate has no RSS feed | Include it anyway; set `rss: null`; note absence in why_relevant |

---

## NEXT STEP

`workflows/watchtower/steps/weekly-step-04-weekly-note.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

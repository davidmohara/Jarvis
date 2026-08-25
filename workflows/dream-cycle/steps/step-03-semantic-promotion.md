---
status: complete
started-at: 2026-08-25T03:09:00-05:00
completed-at: 2026-08-25T03:10:39-05:00
outputs:
  candidates_count: 1
  clusters_found: 1
  semantic_created: 0
  semantic_updated: 1
  promoted_entries: 1
  promotion_note: "Single candidate this cycle: plaud-ingest-2026-08-22-003000.md (score 3), this cycle's own step-01 archive. Matched existing memory/semantic/operational/2026-07-04-plaud-pattern.md by tag overlap — appended 2026-08-25 evidence entry, escalated confidence low->medium (evidence now spans 07-04 through 08-25, past the 15-entry threshold noted in the file's own Pattern Summary). Discovered and logged (err-20260825T081039-APAWBB) a live corruption bug in systems/dream-cycle/salience-score.py's merge-write regex; fixed only the touched file, did not patch the gated systems/ script or the other 288 affected files."
  cluster_actions:
    - {tag: plaud-ingest, domain: operational, size: 1, action: update, target: memory/semantic/operational/2026-07-04-plaud-pattern.md}
  error_categories_30d: "process-skip/protocol-skip:8, missed-context/context-blindness:4, assumption-error/wrong-assumption:4, tool-misuse/tool-ignorance:4, tool-misuse/wrong-assumption:3, lazy-search/available-data-not-used:3"
  error_total_30d: 86
  lessons_appended: 0
  lessons_note: "All 6 qualifying categories (3+ occurrences in 30d) already documented and active in LESSONS.md. No new lesson appended. 3 error entries with null category/failure_mode flagged for Rigby as malformed records."
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. **Never delete or overwrite existing semantic entries. Semantic memory is append-only.** Only append to `## Evidence` and `## Implications` sections.
2. New entries always start at `confidence: low` — never higher, regardless of evidence count.
3. Only promote entries where `salience.last-promoted-check` was set today — this confirms they were just scored in step-02.
4. Set `salience.promoted: true` on every source episodic file that contributes to a promotion — no exceptions.
5. Error pattern check is mandatory — do not skip even if promotion count is zero.
6. Update `state.yaml` current-step before moving to the next step — every time, no exceptions.

## GUARDRAIL 5: PROMOTION THRESHOLD

Before and after promotion, monitor threshold health across cycles:

1. **Load history:** Read `state.yaml.guardrails.promotion_history` (last 12 cycles)
2. **Record this cycle:** `{date, promoted: N, candidates_found: M}`
3. **Analyze trends:**
   - If last 4 cycles all have `promoted == 0 AND candidates_found > 0`: ESCALATE — "No promotions but candidates exist. Threshold too high? Consider lowering from 3 to 2."
   - If last 4 cycles all have `promoted == 0 AND candidates_found == 0`: LOG — "No candidates found (normal equilibrium if semantic memory complete)."
   - If promoted count > 50 in 4 cycles: LOG — "Active promotion cycle. Semantic memory growing."
4. **Record result:** `promotion_threshold_check: "pass"` or `"escalated"`, `last_4_cycles_promoted: {sum}`

## GUARDRAIL 6: SEMANTIC DEDUPLICATION

Before promoting any entry to semantic memory, check for duplicates:

1. **ID-based deduplication:**
   - For each candidate, check if ID already exists in `memory/semantic/*/`
   - If found: LOG "Duplicate detected: {id} already promoted. Skip."
   - Remove from promotion queue

2. **Title-similarity deduplication:**
   - For each candidate, compare title to all existing semantic entries
   - If similarity >= 80%: LOG "Possible duplicate: candidate vs. existing entry"
   - Add to review list for manual consolidation

3. **Tag overlap detection:**
   - If candidate shares 3+ tags with existing semantic entry AND title similarity >= 70%:
   - LOG "Semantic cluster overlap. Consider consolidating instead of separate promotions."
   - Add to consolidation queue

4. **Record deduplication results:**
   - `exact_duplicates_skipped: {count}`
   - `possible_duplicates_flagged: {count}`
   - `consolidation_candidates: {count}`
   - `deduplication_check: "pass"`

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Jarvis |
| Input | Episodic entries with `salience.score >= 3`, `salience.promoted == false`, `salience.last-promoted-check` = today; `systems/error-tracking/entries/*.json`; `memory/LESSONS.md` |
| Output | New or updated semantic entries in `memory/semantic/{domain}/`; `salience.promoted: true` written back to source episodic files; error patterns appended to `memory/LESSONS.md` if applicable |

## CONTEXT BOUNDARIES

- Promotion candidates: `salience.score >= 3` AND `salience.promoted == false` AND `salience.last-promoted-check` was set today (within last 24 hours).
- Domain inference: people/accounts tags → `relationships`; system/process tags → `operational`; industry/market tags → `domain-knowledge`; recurring behavioral patterns → `pattern`.
- Confidence escalation: `low → medium → high` based on total evidence count in the entry (not the cluster size).
- Error pattern check window: 30 days back from today. Threshold: 3 or more occurrences of the same error category.

## YOUR TASK

### Phase A: Semantic Promotion

1. Identify all promotion candidates from the episodic entry list built in step-02:
   - `salience.score >= 3`, AND
   - `salience.promoted == false`, AND
   - `salience.last-promoted-check` is today

2. Group candidates into clusters by shared tags. Each cluster = one potential semantic entry.

3. For each cluster:
   a. Determine domain: `relationships | operational | domain-knowledge | pattern`
      (infer from tags: people/accounts → relationships; system/process → operational;
      industry/market → domain-knowledge; behavioral patterns → pattern)
   b. Check `memory/semantic/{domain}/` for an existing entry with overlapping tags.
   c. **If existing entry found:**
      - Read it.
      - Synthesize new insights from the cluster not already present.
      - Append new material to the `## Evidence` and `## Implications` sections only.
      - Update `last-updated` and `synthesized-from` in frontmatter.
      - Increment confidence based on total evidence count: `low → medium → high`.
   d. **If no existing entry:**
      - Create new file in `memory/semantic/{domain}/`
      - Filename: `YYYY-MM-DD-{tag-slug}-pattern.md`
      - Write frontmatter + synthesis with `## Pattern Summary`, `## Evidence`, `## Implications` sections.
      - Set `confidence: low`.
   e. Set `salience.promoted: true` on all source episodic files in the cluster.

4. Record counts in `accumulated-context`:
   ```yaml
   clusters_found: N
   semantic_created: N
   semantic_updated: N
   promoted_entries: N
   ```

### Phase B: Error Pattern Check

5. Read every `systems/error-tracking/entries/*.json` file (or run `python3 systems/error-tracking/rebuild-log.py` for an aggregated view).

6. Identify any error category appearing 3 or more times in the last 30 days.

7. For each qualifying pattern:
   a. Read `memory/LESSONS.md`.
   b. If the pattern is not already present in LESSONS.md, append:
      ```
      ## {today} — {Pattern Title}
      Detected: {N} occurrences over {X} days
      Category: {error category}
      Pattern: {What keeps happening}
      Fix: {What agents should do differently}
      Status: active
      ```

8. Update `state.yaml`: set `current-step: step-03b`, update this step's frontmatter `status: completed` and `completed-at: {timestamp}`. (Not `step-04` — the guardrail checkpoint runs first; setting `step-04` here would let a resume-from-interruption skip the pre-deletion guardrail entirely.)

## SUCCESS METRICS

- All promotion candidates have been evaluated.
- No semantic entry was overwritten — only appended.
- All source episodic files in promoted clusters have `salience.promoted: true`.
- `clusters_found`, `semantic_created`, `semantic_updated`, and `promoted_entries` are written to `accumulated-context`.
- Error log was scanned and any qualifying patterns were added to LESSONS.md.
- `state.yaml` shows `current-step: step-03b`.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Existing semantic entry found but missing `## Evidence` or `## Implications` section | Append the sections. Do not overwrite any other content. |
| Semantic file write fails | Log error with file path. Continue with remaining clusters. |
| `salience.promoted: true` write fails on episodic source | Log error with file path. Continue. Do not abort promotion. |
| `systems/error-tracking/entries/` not found or empty | Log: `error-log-unavailable`. Skip error pattern check. Do not abort step. |
| `memory/LESSONS.md` not found | Create it with the new entry. Do not abort. |
| No promotion candidates found | Log `clusters_found: 0`. Proceed directly to error pattern check. |


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py dream-cycle step-03-semantic-promotion complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `steps/step-03b-guardrail-checkpoint.md`
<!-- system:end -->

<!-- personal:start -->
Before writing any semantic entry, read `reference/knowledge-layer.md` for the authoritative semantic entry schema.
<!-- personal:end -->

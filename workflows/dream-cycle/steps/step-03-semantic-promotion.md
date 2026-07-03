---
status: complete
started-at: 2026-07-03T03:12:30Z
completed-at: 2026-07-03T03:14:30Z
outputs:
  candidates_count: 139
  clusters_found: 32
  semantic_created: 2
  semantic_updated: 30
  promoted_entries: 35
  promotion_note: "Heavier cycle than baseline. Step-02 script rewrote the salience block without preserving prior `promoted: true` flags — all entries reverted to unpromoted, so this run reevaluated the full corpus rather than just newly-archived files. Operation was append-only per rules; no data lost. 2 new semantic entries created (overdue-tasks and boot patterns in operational domain), 30 evidence appends across 32 tag clusters. Self-detected error logged."
  cluster_actions:
    - {tag: omnifocus, domain: operational, size: 32, action: update}
    - {tag: calendar, domain: operational, size: 23, action: update}
    - {tag: chief, domain: operational, size: 16, action: update}
    - {tag: dream-summary, domain: operational, size: 14, action: update}
    - {tag: jarvis, domain: operational, size: 13, action: update}
    - {tag: daily-review, domain: operational, size: 11, action: update}
    - {tag: briefing, domain: operational, size: 10, action: update}
    - {tag: pipeline, domain: operational, size: 9, action: update}
    - {tag: dream-cycle, domain: pattern, size: 9, action: update}
    - {tag: leads, domain: operational, size: 8, action: update}
    - {tag: email, domain: operational, size: 8, action: update}
    - {tag: rock4, domain: operational, size: 8, action: update}
    - {tag: morning-briefing, domain: operational, size: 7, action: update}
    - {tag: semantic-promotion, domain: pattern, size: 7, action: update}
    - {tag: one-texas, domain: domain-knowledge, size: 6, action: update}
    - {tag: plaud, domain: operational, size: 6, action: update}
    - {tag: overdue-tasks, domain: operational, size: 6, action: create}
    - {tag: revenue, domain: operational, size: 6, action: update}
    - {tag: error-patterns, domain: pattern, size: 6, action: update}
    - {tag: travel, domain: operational, size: 5, action: update}
    - {tag: obsidian, domain: operational, size: 5, action: update}
    - {tag: co-sell, domain: operational, size: 5, action: update}
    - {tag: lessons, domain: pattern, size: 5, action: update}
    - {tag: boot, domain: operational, size: 4, action: create}
    - {tag: rock1, domain: operational, size: 3, action: update}
    - {tag: quarterly-rocks, domain: operational, size: 3, action: update}
    - {tag: chase, domain: operational, size: 3, action: update}
    - {tag: utb-board, domain: operational, size: 3, action: update}
    - {tag: lifebook, domain: operational, size: 2, action: update}
    - {tag: session-wrap, domain: operational, size: 2, action: update}
    - {tag: health, domain: operational, size: 2, action: update}
    - {tag: memory-pipeline, domain: operational, size: 2, action: update}
  error_categories_30d: "process-skip:14, routing-error:13, tool-misuse:13, format-violation:10, data-accuracy:10, missed-context:6, hallucination:5, assumption-error:5, data-interpretation:4"
  error_total_30d: 100
  lessons_appended: 0
  lessons_note: "All threshold-breaching categories already present in LESSONS.md; no new appends."
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. **Never delete or overwrite existing semantic entries. Semantic memory is append-only.** Only append to `## Evidence` and `## Implications` sections.
2. New entries always start at `confidence: low` — never higher, regardless of evidence count.
3. Only promote entries where `salience.last-promoted-check` was set today — this confirms they were just scored in step-02.
4. Set `salience.promoted: true` on every source episodic file that contributes to a promotion — no exceptions.
5. Error pattern check is mandatory — do not skip even if promotion count is zero.
6. Update `state.yaml` current-step before moving to the next step — every time, no exceptions.

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

8. Update `state.yaml`: set `current-step: step-04`, update this step's frontmatter `status: completed` and `completed-at: {timestamp}`.

## SUCCESS METRICS

- All promotion candidates have been evaluated.
- No semantic entry was overwritten — only appended.
- All source episodic files in promoted clusters have `salience.promoted: true`.
- `clusters_found`, `semantic_created`, `semantic_updated`, and `promoted_entries` are written to `accumulated-context`.
- Error log was scanned and any qualifying patterns were added to LESSONS.md.
- `state.yaml` shows `current-step: step-04`.

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

Read fully and follow: `steps/step-04-episodic-compression.md`
<!-- system:end -->

<!-- personal:start -->
Before writing any semantic entry, read `reference/knowledge-layer.md` for the authoritative semantic entry schema.
<!-- personal:end -->

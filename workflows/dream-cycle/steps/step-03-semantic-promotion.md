---
status: completed
started-at: 2026-05-15T03:10:15-05:00
completed-at: 2026-05-15T03:10:45-05:00
outputs:
  clusters_found: 0
  semantic_created: 0
  semantic_updated: 0
  promoted_entries: 0
  error_categories_30d: "wrong-assumption:2, data-accuracy:1, routing-error:1 (none meet 3+ threshold)"
  lessons_appended: 0
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
| Input | Episodic entries with `salience.score >= 3`, `salience.promoted == false`, `salience.last-promoted-check` = today; `systems/error-tracking/error-log.json`; `memory/LESSONS.md` |
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

5. Read `systems/error-tracking/error-log.json`.

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
| `systems/error-tracking/error-log.json` not found | Log: `error-log-unavailable`. Skip error pattern check. Do not abort step. |
| `memory/LESSONS.md` not found | Create it with the new entry. Do not abort. |
| No promotion candidates found | Log `clusters_found: 0`. Proceed directly to error pattern check. |

## NEXT STEP

Read fully and follow: `steps/step-04-episodic-compression.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

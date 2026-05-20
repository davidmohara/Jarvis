---
status: completed
started-at: 2026-05-20T03:11:00-05:00
completed-at: 2026-05-20T03:11:10-05:00
outputs:
  entries_compressed: 0
  digests_updated: 0
  compression_skipped: true
  compression_skip_reason: "All 56 episodic entries < 90 days old (oldest is 2026-04-18, 32 days)"
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. If fewer than 5 compression candidates exist, skip compression entirely. Log `compression_skipped: true`. Do not compress anything.
2. Never delete a source file until its digest entry has been successfully written and verified.
3. Batch all deletions to the end — mark files for deletion first, delete after all digests are written.
4. Never compress entries where `salience.promoted == true` — those have been promoted and must be preserved.
5. Never compress entries with `salience.score >= 2`.
6. Update `state.yaml` current-step before moving to the next step — every time, no exceptions.

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Jarvis |
| Input | Episodic entries where `date` < 90 days ago, `salience.score < 2`, `salience.promoted == false` |
| Output | Digest files updated in `memory/episodic/digests/`; source files deleted; counts logged |

## CONTEXT BOUNDARIES

- Compression candidates: `date` older than 90 days from today AND `salience.score < 2` AND `salience.promoted == false`.
- Digest files live in `memory/episodic/digests/` and are named `{YYYY-QN}-digest.md`.
- Quarter grouping: Q1 = Jan-Mar, Q2 = Apr-Jun, Q3 = Jul-Sep, Q4 = Oct-Dec.
- Digest entries are append-only — never overwrite or restructure existing digest content.
- The 5-entry safety threshold applies to the full candidate set, not per quarter.

## YOUR TASK

1. Identify all compression candidates:
   - `date` < 90 days ago, AND
   - `salience.score < 2`, AND
   - `salience.promoted == false`

2. **Safety check:** If total compression candidates < 5, set `compression_skipped: true` in `accumulated-context`. Log: `compression_skipped: too few candidates ({N})`. Skip to step 4 (state.yaml update).

3. If candidates >= 5, proceed:
   a. Group candidates by quarter (`YYYY-QN`).
   b. For each quarter group:
      - Check if `memory/episodic/digests/{YYYY-QN}-digest.md` exists.
      - If not: create it with a blank header: `# {YYYY-QN} Episodic Digest`.
      - Append a one-paragraph entry for each candidate:
        ```
        ### {date} — {subject} ({type})
        {2-sentence summary of the entry's content}
        ```
      - Mark each source file for deletion (build a deletion list — do NOT delete yet).
   c. After all digest writes are complete: delete all files in the deletion list.

4. Record counts in `accumulated-context`:
   ```yaml
   entries_compressed: N
   digests_updated: N
   compression_skipped: true|false
   ```

5. Update `state.yaml`: set `current-step: step-05`, update this step's frontmatter `status: completed` and `completed-at: {timestamp}`.

## SUCCESS METRICS

- If candidates < 5: `compression_skipped: true` is logged and no files were modified.
- If candidates >= 5: all candidate files have been summarized into digest files and deleted.
- No file was deleted before its digest entry was confirmed written.
- `entries_compressed` and `digests_updated` are written to `accumulated-context`.
- `state.yaml` shows `current-step: step-05`.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Digest file write fails | Log error. Do NOT delete the source file. Continue with other quarters. |
| Source file deletion fails after digest is written | Log error with file path. Leave file in place. Continue. Do not re-compress. |
| Entry has no `date` field | Skip it. Log path. Do not include in candidate count. |
| Entry has no `subject` or `type` field | Use filename as subject, `unknown` as type. Still compress if otherwise eligible. |
| `memory/episodic/digests/` directory not found | Create it. Then proceed. |

## NEXT STEP

Read fully and follow: `steps/step-05-logging.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

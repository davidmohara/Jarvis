---
status: complete
started-at: 2026-09-02T08:19:00Z
completed-at: 2026-09-02T08:20:00Z
outputs:
  candidates_count: 0
  entries_compressed: 0
  digests_updated: 0
  compression_skipped: true
  compression_skip_reason: "0 compression candidates this cycle (below the 5-entry safety threshold, GUARDRAIL 7 approval gate not even reached). Consistent with 08-30 through 09-01 -- nothing has re-accumulated since the 08-29 David-approved batch. No files modified."
prior-cycle-approved-followup:
  approved-at: 2026-08-29T11:58:00Z
  approved-by: david
  scope: "this 5-entry batch only, one-time — not a standing change to GUARDRAIL 7's approval requirement or the 5-entry threshold"
  entries_compressed: 5
  digests_updated: 1
  digest_file: memory/episodic/digests/2026-Q2-digest.md
  files_deleted:
    - memory/episodic/2026-04-30-dream-cycle-summary.md
    - memory/episodic/2026-05-04-dream-cycle-summary.md
    - memory/episodic/2026-05-08-session-index-build.md
    - memory/episodic/2026-05-15-dream-cycle-summary.md
    - memory/episodic/decisions/2026-05-27-185930-decision-rationale-error-improvement-2026-03-21-to-2026-05-27.md
  note: "David answered '1' to the three options offered in-conversation (approve this batch / lower the threshold / leave permanently manual). Digest entries appended to the existing 2026-Q2-digest.md before any deletion, per this step's ordering rule; all 5 source files deleted only after the digest write was confirmed. memory/episodic/decisions/ is now empty (only .gitkeep). See workflows/dream-cycle/state.yaml accumulated-context.step-04-2026-08-29-approved-followup for the full record."
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. If fewer than 5 compression candidates exist, skip compression entirely. Log `compression_skipped: true`. Do not compress anything.
2. Never delete a source file until its digest entry has been successfully written and verified.
3. Batch all deletions to the end — mark files for deletion first, delete after all digests are written.
4. Never compress entries where `salience.promoted == true` — those have been promoted and must be preserved.
5. Never compress entries with `salience.score >= 2`.
6. Update `state.yaml` current-step before moving to the next step — every time, no exceptions.

## GUARDRAIL 7: COMPRESSION THRESHOLD & PREVIEW

Before compressing any entries, monitor thresholds and get controller approval:

1. **Load compression history:** Read `state.yaml.guardrails.compression_history` (last 12 cycles)
2. **Record this cycle:** `{date, candidates_found: N, compressed: 0 (will update after preview)}`
3. **Analyze for drift:**
   - If last 12 cycles have `candidates_found > 0 BUT compressed == 0`: ESCALATE — "No compressions in 12 cycles. Threshold too high? Consider lowering age (>60d) or score (<3)."
   - If candidates_found > 100: LOG — "Large compression batch. Preview before proceeding."

4. **Show preview to controller (if candidates >= 5):**
   ```
   About to compress {candidates_found} entries into quarterly digests.
   Preview (oldest first, first 10 shown):
   - {date}: {title} [score={score}]
   - {date}: {title} [score={score}]
   ...
   
   These will be summarized into digests and removed from episodic/.
   Approve? (y/n)
   ```
   Wait for controller approval before proceeding.

5. **Record compression threshold result:**
   - `compression_threshold_check: "pass"`
   - `preview_shown: {bool}`
   - `controller_approved: {bool}`
   - Update history with final compressed count after compression completes

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


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py dream-cycle step-04-episodic-compression complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `steps/step-05-logging.md`
<!-- system:end -->

<!-- personal:start -->
Before writing any episodic entry, read `reference/knowledge-layer.md` for the authoritative episodic entry schema.
<!-- personal:end -->

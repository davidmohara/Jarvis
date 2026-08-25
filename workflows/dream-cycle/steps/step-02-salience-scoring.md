---
status: complete
started-at: 2026-08-25T03:07:00-05:00
completed-at: 2026-08-25T03:09:00-05:00
outputs:
  episodic_scanned: 289
  score_updates: 289
  no_tags: 206
  no_date: 38
  score_distribution: "0:207,1:4,2:3,3:4,4:4,5:4,6:4,7:4,8:3,9:1,10:51"
  window_entries: 63
  note: "Ran systems/dream-cycle/salience-score.py (committed version). read_errors:0, write_errors:0. pct_score_0=71.6% and pct_no_date=13.2% crossed guardrail thresholds — flagged in state.yaml as escalated but consistent with established baseline, not a fresh regression. IMPORTANT FINDING: while doing step-03 promotion work on this cycle's own step-01 output, discovered this script's merge-write regex can leave an orphaned indented 'promoted: false' line outside the salience: block instead of fully removing it — same signature found in 289/291 episodic files corpus-wide, meaning this bug has been running for many prior cycles, not introduced tonight. Logged as err-20260825T081039-APAWBB for Rigby. Script itself was NOT patched (systems/ is Rigby-gated); only the one file touched by step-03 was manually cleaned."
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Do NOT read or score files in `memory/episodic/digests/` — those are already compressed.
2. Score is a count of matching entries, capped at 10. Never exceed 10.
3. Write the updated frontmatter back to each file — do not skip the write even if score is 0.
4. Update `state.yaml` current-step before moving to the next step — every time, no exceptions.
5. "Last 30 days" is calculated from today's date, inclusive.
6. **MERGE the salience block — never replace it.** The write must preserve any existing `salience.promoted: true` field. Replacing the block wholesale silently drops `promoted: true` and causes every promoted entry to re-appear as a fresh candidate in step-03 the next cycle. Use `systems/dream-cycle/salience-score.py` — it implements the correct merge-write. Do NOT write an ad-hoc scoring loop inline.

## GUARDRAIL 3: SCORE DISTRIBUTION

After scoring all entries, analyze the distribution for anomalies:

1. **Calculate percentages:**
   - `pct_score_0 = (count_at_0 / total_scored) * 100`
   - `pct_score_10 = (count_at_10 / total_scored) * 100`

2. **Check for broken scoring:**
   - If `pct_score_0 >= 70`: ESCALATE — "Too many zero-score entries. Is scoring broken? Check tagging strategy."
   - If `pct_score_10 == 0 AND total_scored > 50`: ESCALATE — "No high-salience entries. Unusual pattern."

3. **Log distribution result:**
   - Record `score_distribution` (example: "0:206,1:2,2:5,...,10:51")
   - Record `distribution_check: "pass"` or `"escalated"`

## GUARDRAIL 4: METADATA QUALITY

During scoring, audit entry metadata:

1. **Track missing fields:**
   - Count entries with no `date` field
   - Count entries with no `tags` field

2. **Check for quality gaps:**
   - If `pct_no_date > 10`: ESCALATE — "High % of undated entries breaks recency scoring."
   - If `pct_no_tags >= 70 AND pct_no_tags < 100`: LOG WARNING — "Most entries untagged (expected for recently archived). Monitor for drift."
   - If `pct_no_tags > 30 AND pct_no_tags < 70`: LOG WARNING — "Unusual tag coverage. Review tagging patterns."

3. **Record audit results:**
   - `no_date: {count}`, `no_tags: {count}`
   - `metadata_check: "pass"` or `"warning"` or `"escalated"`
   - If escalated, include sample of affected entries in log

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Jarvis |
| Input | All files in `memory/episodic/` and subdirectories, excluding `memory/episodic/digests/` |
| Output | Updated `salience.score` and `salience.last-promoted-check` frontmatter on every episodic file; counts logged |

## CONTEXT BOUNDARIES

- Scope: `memory/episodic/` and all subdirectories, excluding `memory/episodic/digests/`.
- Matching criteria: another entry shares 2 or more tags with E AND was written within the last 30 days.
- Tags are read from the `tags` frontmatter field. If absent, treat as empty — the file scores 0 from that dimension.
- `related_people` is read for context building but is not used in the co-occurrence scoring calculation.

## YOUR TASK

**Run the scoring script:**

```bash
python3 systems/dream-cycle/salience-score.py
```

This handles all file I/O with the correct merge-write behavior. Parse its stdout for `episodic_scanned`, `score_updates`, `window_entries`, `no_date`, `no_tags`, and `score_distribution` to populate `accumulated-context`. If the script errors, fall back to the manual protocol below — but fix the script before the next cycle.

**Manual fallback (script unavailable only):**

1. Read ALL files in `memory/episodic/` (all subdirectories). Exclude `memory/episodic/digests/`.

2. Build an entry list:
   ```
   [{file_path, date, tags, related_people, salience_score}]
   ```

3. For each episodic entry E:
   a. Find all other entries where:
      - Entry shares 2 or more tags with E, AND
      - Entry's `date` field is within the last 30 days
   b. Set `E.salience.score` = count of matching entries, capped at 10.
   c. Set `E.salience.last-promoted-check` = today's date (YYYY-MM-DD).
   d. Write updated frontmatter back to the file.

4. Record counts in `state.yaml` under `accumulated-context`:
   ```yaml
   episodic_scanned: N
   score_updates: N
   ```

5. Update `state.yaml`: set `current-step: step-03`, update this step's frontmatter `status: completed` and `completed-at: {timestamp}`.

## SUCCESS METRICS

- Every file in `memory/episodic/` (excluding digests) has been read and scored.
- Every file has `salience.last-promoted-check` set to today.
- `episodic_scanned` and `score_updates` counts are written to `accumulated-context`.
- `state.yaml` shows `current-step: step-03`.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Episodic file has no `tags` field | Score it as 0 co-occurrences. Still write `salience.last-promoted-check`. |
| Episodic file has no `date` field | Exclude it from co-occurrence matching. Still write its score. Log path. |
| Frontmatter write fails on a file | Log the error with file path. Continue with remaining files. |
| `memory/episodic/` directory not found | Abort this step. Log: `step-02-failed: episodic directory not found`. Surface to controller. |


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py dream-cycle step-02-salience-scoring complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `steps/step-03-semantic-promotion.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

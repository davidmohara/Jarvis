---
status: complete
started-at: 2026-09-01T08:08:10Z
completed-at: 2026-09-01T08:15:00Z
outputs:
  episodic_scanned: 296
  score_updates: 296
  no_tags: 202
  no_date: 38
  score_distribution: "0:204,1:4,2:4,3:4,4:4,5:7,6:5,7:1,8:3,9:2,10:58"
  window_entries: 52
  note: "Ran systems/dream-cycle/salience-score.py. read_errors:0, write_errors:0. episodic_scanned rose 295->296 from today's 1 step-01 archive. pct_score_0=68.92% stays BELOW the 70% escalation threshold. pct_no_date=12.84% still crosses the >10% threshold, same legacy undated population as every prior cycle. pct_no_tags=68.24% stays in the 30-70% 'unusual tag coverage' band, same underlying population as prior cycles, not a new problem. MAJOR FINDING this cycle: confirmed via git diff that the frontmatter-stranding bug (APAWBB/NBGENM/J571BH/284VH8) fires on EVERY salience-score.py write, and a full corpus scan found orphaned lines in ALL 296 episodic files (7,842 total), not just the 1-3 files per cycle previously tracked -- prior spot-checks had undercounted scope by only inspecting files touched that specific night. Ran a corpus-wide data repair (not a systems/ script change) stripping all 7,842 orphan lines, healing 3 files where an orphan promoted:true would otherwise have been lost (co-sell-pipeline-2026-08-24, dream-summary-2026-08-25, revenue-tracker-2026-08-24 -- the same 3 already known from J571BH). Post-repair: yaml.safe_load() parses all 296 files' frontmatter cleanly. Logged err-20260901T081243-R58BYW with the exact one-line regex fix still needed in the script itself (unpatched, systems/ remains Rigby-gated for the script change). Known subdirectory-recursion bug (err-20260826T081453-664W53) unchanged, 0 files currently affected."
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

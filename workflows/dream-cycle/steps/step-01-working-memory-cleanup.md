---
status: complete
started-at: 2026-06-04T08:10:00Z
completed-at: 2026-06-04T08:10:20Z
outputs:
  working_archived: 2
  working_deleted: 0
  working_skipped: 78
  working_stranded: 0
  archived_files:
    - daily-review-2026-06-01-000000.md
    - morning-briefing-2026-06-01-061018.md
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Do NOT delete any working memory file unless its body is trivial (fewer than 3 substantive lines).
2. Do NOT archive a file unless `expires` < today AND `status: active` in frontmatter.
3. Files without a parseable `expires` field are skipped and flagged in the log — never deleted.
4. `README.md` is always excluded from processing.
5. Update `state.yaml` current-step before moving to the next step — every time, no exceptions.
6. **Move-on-write only.** Do not copy files then delete. Use `mv` (rename) for the working→episodic transfer. This is a single inode operation and succeeds in the sandbox even when `rm`/`unlink` does not.
7. Mutate frontmatter **before** moving. Write the updated file content to the source path first, then `mv` it to episodic. Never attempt `mv` on an un-mutated file.
8. Do NOT attempt `rm` on non-trivial files at any point. The only delete target is trivial-body files, and if that delete fails, fall back to leaving the file in place with `status: archived` — do not lose data.

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Jarvis |
| Input | All files in `memory/working/` (excluding `README.md`) |
| Output | Expired non-trivial files renamed to `memory/episodic/{fname}`; trivial files deleted if possible; counts logged to `accumulated-context` |

## CONTEXT BOUNDARIES

- Scope: `memory/working/` only. Do not read or modify episodic, semantic, or any other memory tier.
- "Trivial" means: empty file, placeholder text only, or fewer than 3 substantive lines of content (frontmatter lines do not count).
- "Non-trivial" means: 3 or more substantive lines in the content body below the frontmatter.
- Archived files receive `type: working-archive` and `salience.score: 0` added to their frontmatter before being renamed to episodic.
- Files that already have `status: archived` in frontmatter AND are still in `memory/working/` are dead accumulation from the old copy+delete pattern. They are NOT re-processed — skip them and log as `skipped_already_archived`.

## YOUR TASK

1. List all files in `memory/working/`. Exclude `README.md`.

2. For each file:
   a. Read the file. Parse `expires` and `status` fields from frontmatter.
   b. If `expires` field is absent or unparseable: skip the file. Add to log as `skipped_unparseable: [path]`.
   c. If `status` is already `archived`: skip. Log as `skipped_already_archived: [path]`. Do not touch.
   d. If `expires` >= today OR `status` is not `active`: skip the file. No action.
   e. If `expires` < today AND `status: active`:
      - Evaluate body content (lines below frontmatter delimiter).
      - **If non-trivial:**
        1. Update frontmatter in-place: set `status: archived`, add `type: working-archive`, add `salience.score: 0`.
        2. Write the mutated content back to the source file at `memory/working/{fname}`.
        3. Rename (mv) the source file to `memory/episodic/{fname}` — one operation.
        4. If rename fails: log error with path and reason. Leave the mutated file in `memory/working/`. Continue.
      - **If trivial:**
        1. Set `status: archived` in frontmatter. Write back to source file.
        2. Attempt to delete the file.
        3. If deletion fails: log error. Leave file in `memory/working/` with `status: archived`. Continue. Do not lose data.

3. Record counts in `state.yaml` under `accumulated-context`:
   ```yaml
   working_archived: N        # files successfully renamed to episodic
   working_deleted: N         # trivial files successfully deleted
   working_skipped: N         # files skipped (not expired, unparseable, or already_archived)
   working_stranded: N        # files mutated but left in working/ due to mv or rm failure
   skipped_already_archived: [list of paths]
   skipped_unparseable: [list of paths]
   stranded: [list of paths with error notes]
   ```

4. Update `state.yaml`: set `current-step: step-02`, update this step's frontmatter `status: completed` and `completed-at: {timestamp}`.

## SUCCESS METRICS

- All working memory files have been evaluated.
- No non-trivial file was lost — either it arrived in episodic/ or it remains in working/ with `status: archived` and a stranded log entry.
- `working_archived`, `working_deleted`, `working_skipped`, and `working_stranded` counts are written to `accumulated-context`.
- `state.yaml` shows `current-step: step-02`.
- Zero use of copy+delete. Every transfer was a rename.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| File has no `expires` field | Skip it. Log path to `skipped_unparseable`. Do not delete. |
| `expires` field is not a parseable date | Skip it. Log path to `skipped_unparseable`. Do not delete. |
| File already has `status: archived` | Skip it. Log to `skipped_already_archived`. Do not re-process. |
| Frontmatter write to source fails | Log error. Skip the file entirely. Do not attempt mv. Do not delete. |
| `mv` rename to episodic fails | Log error and path to `stranded`. Leave mutated file in working/. Continue with next file. |
| Trivial file deletion fails | Log error and path to `stranded`. Leave file in working/ with `status: archived`. Continue. |
| `memory/working/` directory not found | Abort this step. Log: `step-01-failed: working directory not found`. Do not proceed to step-02. Surface to controller. |

## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py dream-cycle step-01-working-memory-cleanup complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `steps/step-02-salience-scoring.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: completed
started-at: 2026-05-15T03:09:01-05:00
completed-at: 2026-05-15T03:09:30-05:00
outputs:
  working_archived: 2
  working_deleted: 0
  working_skipped: 41
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Do NOT delete any working memory file unless its body is trivial (fewer than 3 substantive lines).
2. Do NOT archive a file unless `expires` < today AND `status: active` in frontmatter.
3. Files without a parseable `expires` field are skipped and flagged in the log — never deleted.
4. `README.md` is always excluded from processing.
5. Update `state.yaml` current-step before moving to the next step — every time, no exceptions.

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Jarvis |
| Input | All files in `memory/working/` (excluding `README.md`) |
| Output | Expired files archived to `memory/episodic/` or deleted; counts logged to `accumulated-context` |

## CONTEXT BOUNDARIES

- Scope: `memory/working/` only. Do not read or modify episodic, semantic, or any other memory tier.
- "Trivial" means: empty file, placeholder text only, or fewer than 3 substantive lines of content (frontmatter lines do not count).
- "Non-trivial" means: 3 or more substantive lines in the content body below the frontmatter.
- Archived files receive `type: working-archive` and `salience.score: 0` added to their frontmatter before moving.

## YOUR TASK

1. List all files in `memory/working/`. Exclude `README.md`.

2. For each file:
   a. Read the file. Parse the `expires` field from frontmatter.
   b. If `expires` field is absent or unparseable: skip the file. Add to log as `skipped_unparseable: [path]`.
   c. If `expires` >= today OR `status` is not `active`: skip the file. No action.
   d. If `expires` < today AND `status: active`:
      - Set `status: archived` in frontmatter.
      - Evaluate body content (lines below frontmatter delimiter).
      - If non-trivial: add `type: working-archive` and `salience.score: 0` to frontmatter. Move file to `memory/episodic/`.
      - If trivial: delete the file.

3. Record counts in `state.yaml` under `accumulated-context`:
   ```yaml
   working_archived: N
   working_deleted: N
   working_skipped: N
   ```

4. Update `state.yaml`: set `current-step: step-02`, update this step's frontmatter `status: completed` and `completed-at: {timestamp}`.

## SUCCESS METRICS

- All working memory files have been evaluated.
- No file was deleted that had 3 or more substantive lines of content.
- `working_archived`, `working_deleted`, and `working_skipped` counts are written to `accumulated-context`.
- `state.yaml` shows `current-step: step-02`.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| File has no `expires` field | Skip it. Log path to `skipped_unparseable`. Do not delete. |
| `expires` field is not a parseable date | Skip it. Log path to `skipped_unparseable`. Do not delete. |
| File move to episodic fails | Log error. Leave file in working. Continue with next file. |
| File deletion fails | Log error. Leave file in place. Continue with next file. |
| `memory/working/` directory not found | Abort this step. Log: `step-01-failed: working directory not found`. Do not proceed to step-02. Surface to controller. |

## NEXT STEP

Read fully and follow: `steps/step-02-salience-scoring.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

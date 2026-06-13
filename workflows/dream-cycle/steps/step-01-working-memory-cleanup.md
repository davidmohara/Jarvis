---
status: complete
started-at: 2026-06-12T13:21:00Z
completed-at: 2026-06-12T13:22:30Z
outputs:
  working_archived: 13
  working_deleted: 0
  working_skipped: 78
  working_stranded: 0
  enrichment_method: "heuristic:13, llm:0"
  archived_files:
    - co-sell-pipeline-2026-06-01-000100.md
    - co-sell-pipeline-2026-06-08-000000.md
    - co-sell-pipeline-2026-06-09-133410.md
    - co-sell-pipeline-2026-06-09-133800.md
    - co-sell-pipeline-2026-06-09-140500.md
    - co-sell-pipeline-2026-06-09-142000.md
    - daily-review-2026-06-08-212450.md
    - morning-briefing-2026-06-08-095429.md
    - morning-briefing-2026-06-09-092323.md
    - plaud-ingest-2026-06-04-013000.md
    - revenue-tracker-2026-06-01-000000.md
    - revenue-tracker-2026-06-09-133407.md
    - session-work-2026-06-08-162353.md
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
9. **Enrichment is required for non-trivial archives.** Before mutating to `working-archive`, derive `date`, `tags`, `source_file`, and `related_people` from the file's frontmatter and body. The dream cycle's salience scoring depends on these fields; without them step-02 collapses to zero scores and step-03 finds zero promotion candidates. This was the proximate cause of the 2026-05-08 → 2026-06-09 tag-starvation gap.

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
        1. **Enrich frontmatter** (see "Enrichment Protocol" below): derive `date`, `source_file`, `tags`, `related_people`.
        2. Update frontmatter in-place: set `status: archived`, add `type: working-archive`, add `salience.score: 0`, and add the four enrichment fields from the previous step.
        3. Write the mutated content back to the source file at `memory/working/{fname}`.
        4. Rename (mv) the source file to `memory/episodic/{fname}` — one operation.
        5. If rename fails: log error with path and reason. Leave the mutated file in `memory/working/`. Continue.
      - **If trivial:**
        1. Set `status: archived` in frontmatter. Write back to source file.
        2. Attempt to delete the file.
        3. If deletion fails: log error. Leave file in `memory/working/` with `status: archived`. Continue. Do not lose data.

## ENRICHMENT PROTOCOL

For every non-trivial file being archived, derive and add these four fields to the frontmatter before the `mv`:

| Field | Source | Format |
|-------|--------|--------|
| `date` | The `created` field (truncate to YYYY-MM-DD). If `created` is absent, parse the filename prefix. If still unparseable, omit `date` and log `enrichment_no_date: [path]`. | `YYYY-MM-DD` (ISO date, no time) |
| `source_file` | `memory/working/{fname}` (the original path) | String |
| `tags` | **LLM-extracted** via `systems/dream-cycle/llm_tag_extractor.py`. Returns 5-10 lowercase kebab-case tokens. See "LLM Extraction" below. | YAML block list under `tags:` |
| `related_people` | **LLM-extracted** via the same call. Returns lowercase kebab-case names. Empty list if none. | YAML block list under `related_people:` |

### LLM Extraction (Primary Path)

Call the extractor via subprocess:

```python
from systems.dream_cycle.llm_tag_extractor import extract_enrichment, ClaudeAuthError

try:
    result = extract_enrichment(
        frontmatter=fm_text,
        body=body_text,
        filename=fname,
        model="haiku",   # fast and cheap; tag extraction doesn't need opus
    )
    date_val = result["date"]
    tags = result["tags"]
    people = result["related_people"]
except ClaudeAuthError:
    # claude -p not logged in — fall back to heuristic
    date_val, tags, people = _heuristic_enrichment(fm_text, body_text, fname)
except Exception as e:
    log_error("enrichment_failed", path, str(e))
    date_val, tags, people = _heuristic_enrichment(fm_text, body_text, fname)
```

The LLM uses haiku by default (fast, ~$0.001 per file). Prompt sends the corpus vocabulary as a strong preference list so co-occurrence matches stay aligned across files.

### Heuristic Fallback (Sandbox / Auth Failure)

If the LLM call fails (auth error, timeout, malformed response), fall back to the keyword-matching path in `systems/dream-cycle/backfill-episodic-tags.py`. The heuristic recovers ~80% of the LLM's tag quality and keeps the cycle running on machines without `claude -p` auth.

### Tag Quality Rules (LLM and Heuristic Both Enforce)

1. Always include the deliverable type as the first tag (`briefing`, `daily-review`, `dream-summary`, `session-wrap`, `pipeline-review`, etc.).
2. Always include the agent source if known (`chief`, `harper`, `knox`, `rigby`, `galen`, `sterling`, `shep`, `quinn`, `jarvis`) — pull from `agent-source` field.
3. Tags must be lowercase, kebab-case. No spaces, no underscores, no capitals.
4. Cap at 10 tags. Quality and reuse over quantity.
5. Minimum 3 tags even for generic content.

**Example enrichment block:**
```yaml
date: 2026-05-13
source_file: memory/working/2026-05-13-061200-session-boot-morning-briefing.md
tags:
  - briefing
  - chief
  - calendar
  - omnifocus
  - leads
  - travel
  - glc-chicago
related_people:
  - alice-mburu
  - ehren-seim
```

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

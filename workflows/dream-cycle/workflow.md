---
name: dream-cycle
description: Nightly memory consolidation — compress episodic, promote semantic
agent: jarvis
model: sonnet
---

<!-- system:start -->
# Dream Cycle Workflow

**Goal:** Consolidate nightly memory — archive expired working entries, score episodic salience, promote patterns to semantic memory, compress old low-value entries, and log results.

**Agent:** Jarvis

**Architecture:** Sequential 5-phase pipeline. Execute all phases in order. Log every action. Be conservative — when in doubt about whether to promote or compress an entry, leave it and note it in the log. **Preservation over aggression.**
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Working memory | All files in `memory/working/` | File system |
| Episodic memory | All files in `memory/episodic/` (excluding digests/) | File system |
| Semantic memory | Existing entries in `memory/semantic/` | File system |
| Dream log | Last run date | Read `memory/dream.log` |
| Error log | Recent error categories (last 30 days) | Read `systems/error-tracking/entries/*.json` (or `python3 systems/error-tracking/rebuild-log.py` for aggregated view) |
| Lessons | Existing pattern entries | Read `memory/LESSONS.md` |

### Paths

- `working_memory` = `memory/working/`
- `episodic_memory` = `memory/episodic/`
- `episodic_digests` = `memory/episodic/digests/`
- `semantic_memory` = `memory/semantic/`
- `dream_log` = `memory/dream.log`
- `error_log` = `systems/error-tracking/entries/` (per-entry files; aggregate via `systems/error-tracking/rebuild-log.py`)
- `lessons` = `memory/LESSONS.md`

### Pre-flight Checks

- Read `memory/dream.log` — confirm last run date. If last run was today, abort with log entry: `aborted: already ran today`.
- Get current local date/time via `osascript -e 'return (current date) as string'`.
- Record `session_id: dream-cycle-{YYYY-MM-DD-HHmmss}`.
- Get latest from origin: `git pull --rebase`. Handle any merge conflicts. Do NOT proceed until the folder is clean.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify: "[Dream Cycle]: Resuming from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Surface to controller: "[Dream Cycle]: Previous run was aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

| Step | File | Description |
|------|------|-------------|
| 01 | `steps/step-01-working-memory-cleanup.md` | Archive or delete expired working memory entries |
| 02 | `steps/step-02-salience-scoring.md` | Score all episodic entries by co-occurrence frequency |
| 03 | `steps/step-03-semantic-promotion.md` | Promote high-salience episodic clusters into semantic memory |
| 04 | `steps/step-04-episodic-compression.md` | Compress old low-salience episodic entries into quarterly digests |
| 05 | `steps/step-05-logging.md` | Write dream.log entry, conditionally surface summary, commit and push |

Read fully and follow: `steps/step-01-working-memory-cleanup.md` to begin.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

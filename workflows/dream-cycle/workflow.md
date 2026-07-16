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

- Check last run date via tail — the log is append-only and grows unboundedly; reading from line 1 returns the initialization entry, not the latest run:
  ```
  tail -30 memory/dream.log
  ```
  Parse the most recent `## YYYY-MM-DD` header. If last run was today, abort with log entry: `aborted: already ran today`. **Never use the Read tool on dream.log without an offset — it will return the first entry, not the last.**
- Get current local date/time via `osascript -e 'return (current date) as string'`.
- Record `session_id: dream-cycle-{YYYY-MM-DD-HHmmss}`.
- Get latest from origin via the git skill. **Read `skills/git/SKILL.md` before issuing any git command.** Per the skill, every git command is a separate atomic call and `git status` is forbidden (writes `.git/index.lock`).

  **CRITICAL — host-side only:** ALL git commands in this workflow MUST be issued via `mcp__Desktop_Commander__start_process` (host process). NEVER run `git` via the sandboxed `mcp__workspace__bash` tool. The sandbox runs as a different user against a FUSE mount; any `git` invocation there (including read-only ones like `git pull` or `git diff`) creates `.git/index.lock` files that neither the sandbox nor the host can unlink, blocking every subsequent git operation until manually cleared. This is the root cause of the recurring 2026-06-13 → 2026-06-21 lock blocker pattern. The fix is mechanical: choose the right tool, not the right command.

  Boot pull: one atomic Desktop Commander call to `cd /Users/davidohara/develop/jarvis && git pull --rebase`. Handle conflicts per the skill's Error Handling table. Do NOT proceed until clean.

  **Desktop Commander is always available for scheduled dream-cycle runs.** Do not assume it is unavailable because it does not appear in the initially visible tool list — deferred tools load lazily. If `mcp__Desktop_Commander__start_process` is not yet listed, call `ToolSearch` for it before concluding git operations must be skipped. Skipping the boot pull or the end-of-cycle commit/push on an unconfirmed "unavailable" assumption is itself a loggable error (see `err-20260716T133618-FUOKLP`) — not a safe default.
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

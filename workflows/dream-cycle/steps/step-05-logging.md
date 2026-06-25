---
status: complete
started-at: 2026-06-25T08:13:30Z
completed-at: 2026-06-25T08:14:30Z
outputs:
  dream_log_appended: true
  working_summary_written: true
  working_summary_reason: "semantic_created=38 + semantic_updated=23 — surface to Chief for visibility."
  git_commit: success
  git_push: success
  commit_sha: d558db2
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Always write the dream log entry — even if all counts are zero. The log is the audit trail.
2. Write the working memory summary only if `semantic_created > 0` OR `semantic_updated > 0` OR `errors > 0`. A clean run does not interrupt Chief.
3. Set `status: complete` and `current-step: null` in `state.yaml` before committing.
4. Commit and push all changes — this is not optional. A dream cycle that does not push has not finished.
5. If the git push fails, log the failure but do not set `status: not-started` — the run completed. Surface the push failure to the controller.

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Jarvis |
| Input | All counts from `accumulated-context` in `state.yaml`; session_id; current date/time |
| Output | Appended entry in `memory/dream.log`; optional `memory/working/dream-summary-{YYYY-MM-DD}.md`; `state.yaml` set to complete; git commit and push |

## CONTEXT BOUNDARIES

- Dream log format is append-only. Never edit or remove prior entries.
- The working memory summary expires the next day (`expires: {today + 1 day}`).
- The working memory summary is written for Chief to read at boot — write it clearly, not technically.
- `errors` count = total number of logged errors across all steps (file failures, skipped files flagged as errors, etc.).

## YOUR TASK

### Phase A: Write Dream Log Entry

1. Get current date/time and timezone.

2. Append the following block to `memory/dream.log`:
   ```
   ---
   ## {YYYY-MM-DD}T{HH:MM:SS} {TZ}
   session_id: {session_id from state.yaml}
   working_archived: {N}
   working_deleted: {N}
   episodic_scanned: {N}
   score_updates: {N}
   clusters_found: {N}
   semantic_created: {N}
   semantic_updated: {N}
   promoted_entries: {N}
   entries_compressed: {N}
   digests_updated: {N}
   errors: {N}
   summary: "{One sentence summary of what happened.}"
   ---
   ```

3. If any errors occurred during any phase, append immediately after the block:
   ```
   errors_detail:
     - phase: {step number}
       file: {path/to/file.md}
       error: "{Description of what went wrong}"
   ```

### Phase B: Working Memory Summary (Conditional)

4. If `semantic_created > 0` OR `semantic_updated > 0` OR `errors > 0`:
   - Write `memory/working/dream-summary-{YYYY-MM-DD}.md`:
     ```yaml
     ---
     type: working
     expires: {today + 1 day, YYYY-MM-DD}
     status: active
     ---
     ```
     Body: the log entry above, formatted for Chief to read — plain prose, not raw YAML.

5. If all counts are zero and no errors occurred: write nothing. Do not create the summary file.

### Phase C: Finalize

6. Update `state.yaml`: set `status: complete`, `current-step: null`. Update this step's frontmatter `status: completed` and `completed-at: {timestamp}`.

7. **MANDATORY: Read `skills/git/SKILL.md` in full before issuing any git command.** The skill is the only authorized path for git operations in Jarvis. It enforces the atomic-command rule (no `&&` chaining), forbids `git status` (which writes `.git/index.lock` and breaks the sandbox), requires Conventional Commits, and defines the session-end commit protocol. Do NOT use the inline snippets that existed in prior versions of this step — they predated the skill and chained commands with `&&`, which is now forbidden.

   **CRITICAL — host-side only:** Every git command MUST be issued via `mcp__Desktop_Commander__start_process` (host process). NEVER run git via the sandboxed `mcp__workspace__bash` tool. Sandbox git invocations create `.git/index.lock` files that neither user can unlink, blocking subsequent operations until manually cleared. If the boot-phase pull (workflow.md) was accidentally run via the sandbox, the lock will already exist by the time this step runs — surface to controller for manual host-side cleanup; do not attempt sandbox `rm -f .git/index.lock` (it will fail with "Operation not permitted").

   Execute the git skill's **Session-End Commit Protocol** exactly. Every command is a separate Desktop Commander call. Wait for each to return before the next. Commit message format:

   ```
   chore(memory): dream-cycle {YYYY-MM-DD} — archived {N}, promoted {N} to semantic ({pattern-summary}), {N} compressed
   ```

   If a command fails: stop, log the failure, surface to controller. Do not retry with workarounds. Do not run `rm -f .git/index.lock` or use `GIT_INDEX_FILE` — the 2026-06-13 destructive push originated from that workaround.

## SUCCESS METRICS

- `memory/dream.log` contains a new entry with today's date and all counts filled in.
- If notable activity occurred: `memory/working/dream-summary-{YYYY-MM-DD}.md` exists and expires tomorrow.
- `state.yaml` shows `status: complete` and `current-step: null`.
- All changes are committed and pushed to origin.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `memory/dream.log` not found | Create it, then append the entry. |
| Dream log write fails | Log error to controller. Do not proceed to git operations until log is written. |
| Working memory summary write fails | Log error. Do not abort finalization. |
| Git commit fails | Log failure. Still set `state.yaml` to complete. Surface to controller: "[Dream Cycle]: Run complete but git commit failed. Manual push required." |
| Git push fails after successful commit | Log failure. Surface to controller: "[Dream Cycle]: Committed but push failed. Run `git push origin` manually." |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

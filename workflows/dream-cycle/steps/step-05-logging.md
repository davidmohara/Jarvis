---
status: completed
started-at: 2026-10-09T12:01:00Z
completed-at: 2026-10-09T12:10:00Z
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Always write the dream log entry — even if all counts are zero. The log is the audit trail.
2. Write the working memory summary only if `semantic_created > 0` OR `semantic_updated > 0` OR `errors > 0`. A clean run does not interrupt Chief.
3. Set `current-step: step-06-adversarial-verify` in `state.yaml` before committing (do NOT set `status: complete` - the terminal adversarial verification step finalizes the state).
4. Commit and push all changes — this is not optional. A dream cycle that does not push has not finished.
5. If the git push fails, log the failure but do not set `status: not-started` — the run completed. Surface the push failure to the controller.

## GUARDRAIL 8: GIT ATOMICITY

Before and after git operations, verify state consistency to prevent partial commits:

### Pre-Commit Verification

1. **State file integrity:**
   - Read `memory/dream.log` — verify last entry is parseable and complete
   - Read `state.yaml` — verify valid YAML with all step results (01-05)
   - If any file is corrupted: ABORT git operations, set `status: needs-manual-review`, surface error to controller

2. **Dream log entry ready:**
   - Verify entry string prepared with all fields (counts, summary, errors)
   - Confirm formatting valid (markdown/YAML)
   - If malformed: ABORT git, set `status: needs-manual-review`

3. **Accumulated context complete:**
   - Verify `state.yaml.accumulated-context` has results from all 5 steps
   - Check guardrail metrics present (from all 8 guardrails)
   - If incomplete: ABORT git, set `status: needs-manual-review`

If all checks PASS:
   LOG: "✓ Pre-commit checks passed. State valid. Ready for git."

### Git Operations

4. **Execute session-end commit protocol** (via Desktop Commander, per skills/git/SKILL.md):
   - `git add -A` (stage all changes)
   - `git commit -m "chore(memory): dream-cycle {YYYY-MM-DD} — archived {N}, promoted {M}, compressed {P}"`
   - Verify commit succeeded (no errors)
   - If commit fails: LOG ERROR, set `status: needs-git-push`, STOP (do not attempt push)

5. **Execute git push:**
   - `git push origin main` (via Desktop Commander)
   - Verify push succeeded (fast-forward or up-to-date)
   - If push fails: LOG ERROR, set `status: needs-git-push`, CONTINUE (commit ok, push pending)

### Post-Commit Verification

6. **Verify consistency:**
   - Check that dream.log last entry matches state.yaml.session-id (within 5 minutes)
   - If mismatch: LOG ERROR "dream.log and state.yaml out of sync!"
   - Confirm no uncommitted changes remain with lock-free commands only (`git status` is forbidden — it writes `.git/index.lock`): `git diff --name-only HEAD` returning nothing
   - If uncommitted files exist: LOG WARNING "Uncommitted changes remain: {list}"

7. **Record atomicity status:**
   - `git_atomicity.pre_commit_check: "pass"`
   - `git_atomicity.commit_status: "success"` or `"failed"`
   - `git_atomicity.push_status: "success"` or `"pending"` or `"failed"`
   - `git_atomicity.atomicity_check: "pass"` (all succeeded) or `"partial"` (commit ok, push pending) or `"failed"`

### Recovery Paths

| Failure | Status | Recovery |
|---------|--------|----------|
| Pre-commit check fails | needs-manual-review | User manually reviews state files |
| Commit fails | needs-git-push | Retry `git commit` manually |
| Push fails after commit | needs-git-push | Retry `git push` manually |
| All succeed | complete | Workflow done |

## EXECUTION PROTOCOL

**Agent:** Jarvis, spawned by the coordinator, never executed inline

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

6. Update `state.yaml`: set `current-step: step-06-adversarial-verify`. Do NOT set `status: complete` here - the terminal adversarial verification step (step-06) finalizes the state once its verdict is recorded. Update this step's frontmatter `status: completed` and `completed-at: {timestamp}`.

7. **MANDATORY: Read `skills/git/SKILL.md` in full before issuing any git command.** The skill is the only authorized path for git operations in Jarvis. It enforces the atomic-command rule (no `&&` chaining), forbids `git status` (which writes `.git/index.lock` and breaks the sandbox), requires Conventional Commits, and defines the session-end commit protocol. Do NOT use the inline snippets that existed in prior versions of this step — they predated the skill and chained commands with `&&`, which is now forbidden.

   **CRITICAL — host-side only:** Every git command MUST be issued via `mcp__Desktop_Commander__start_process` (host process). NEVER run git via the sandboxed `mcp__workspace__bash` tool. Sandbox git invocations create `.git/index.lock` files that neither user can unlink, blocking subsequent operations until manually cleared. If the boot-phase pull (workflow.md) was accidentally run via the sandbox, the lock will already exist by the time this step runs — surface to controller for manual host-side cleanup; do not attempt sandbox `rm -f .git/index.lock` (it will fail with "Operation not permitted").

   Execute the git skill's **Session-End Commit Protocol** exactly. Every command is a separate Desktop Commander call. Wait for each to return before the next. Commit message format:

   ```
   chore(memory): dream-cycle {YYYY-MM-DD} — archived {N}, promoted {N} to semantic ({pattern-summary}), {N} compressed
   ```

   If a command fails: stop, log the failure, surface to controller. Do not retry with workarounds. Do not run `rm -f .git/index.lock` or use `GIT_INDEX_FILE` — the 2026-06-13 destructive push originated from that workaround.

8. **Open a pull request for every push to a non-default branch.** A push to a branch is not finished until a PR exists for it. This overrides the general "do not create a PR unless asked" default: David has standing-authorized it for every dream-cycle push.

   - **When it applies:** the pushed branch is not the repo's default branch (`main`). In a Claude Code Remote cloud session the push goes to the session's designated `claude/*` branch, so a PR is always required there. A host-side run that pushes straight to `main` has no PR to open; log `pr: not-applicable (pushed to default branch)`.
   - **Check first, never duplicate:** list open PRs with head = the pushed branch (`mcp__github__list_pull_requests`). If one is already open, the push updated it. Record its number and URL and do not create another.
   - **Create:** otherwise call `mcp__github__create_pull_request` with base `main`, head = the pushed branch. Load the tool via `ToolSearch` if it is not listed; do not conclude it is unavailable from one negative lookup (retry once, per the Deferred tool resolution guard in `SYSTEM.md`). Do not use `gh`; it is not available in cloud sessions.
   - **Title:** the commit subject line from step 7.
   - **Body:** check for a PR template (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, root, or `docs/`) and mirror its headings if one exists. Otherwise write a short body from this cycle's counts: archived, promoted, compressed, errors, step-03b verdict, and the Ralph/step-06 status (write "pending" because step-06 runs after this step). End the body with the attribution lines the session's system-reminder specifies.
   - **Do not** enable auto-merge, merge, or request reviewers. David merges.
   - **Record** `pr_status` (`created`, `existing`, `not-applicable`, or `failed`), `pr_number`, and `pr_url` in `state.yaml` `accumulated-context` and add a `pr:` line to the dream.log entry written in Phase A (append it to the entry; do not rewrite earlier lines).
   - **Push after the PR:** any commit made after the PR exists (for example the step-06 state finalization) lands on the same branch and updates the PR. Do not open a second one.
   - **If PR creation fails** (tool unavailable after retry, auth error, API error): log the error, set `pr_status: failed`, and surface to controller: "[Dream Cycle]: Pushed to {branch} but PR creation failed. Open a PR for {branch} manually." The cycle still counts as complete.

## SUCCESS METRICS

- `memory/dream.log` contains a new entry with today's date and all counts filled in.
- If notable activity occurred: `memory/working/dream-summary-{YYYY-MM-DD}.md` exists and expires tomorrow.
- `state.yaml` shows `current-step: step-06-adversarial-verify` (the terminal step finalizes `status: complete`).
- All changes are committed and pushed to origin.
- Every push to a non-default branch has an open PR (new or existing), recorded as `pr_status`, `pr_number`, `pr_url` in `accumulated-context`.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `memory/dream.log` not found | Create it, then append the entry. |
| Dream log write fails | Log error to controller. Do not proceed to git operations until log is written. |
| Working memory summary write fails | Log error. Do not abort finalization. |
| Git commit fails | Log failure. Still set `state.yaml` to complete. Surface to controller: "[Dream Cycle]: Run complete but git commit failed. Manual push required." |
| Git push fails after successful commit | Log failure. Surface to controller: "[Dream Cycle]: Committed but push failed. Run `git push origin` manually." Skip step 8 (no PR without a push). |
| PR already open for the branch | Record it as `pr_status: existing`. Do not create a second PR. |
| PR creation fails | Log failure, set `pr_status: failed`, surface to controller with the branch name. Do not retry with workarounds and do not abort the cycle. |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

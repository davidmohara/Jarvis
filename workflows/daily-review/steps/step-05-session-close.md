---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 05: Session Close — Index Update and Git Commit

## MANDATORY EXECUTION RULES

1. You MUST close the active session record in `memory/sessions/index.json` before committing.
2. You MUST follow the git skill protocol — atomic commands, no chaining, no `git status`.
3. You MUST use Desktop Commander (`mcp__Desktop_Commander__*`) for all git operations, never sandbox bash.
4. You MUST verify each git operation before proceeding to the next.
5. This step runs after all other daily-review steps are complete. It is the final operation.

---

## EXECUTION PROTOCOL

**Agent:** Chief (via Rigby for git operations)
**Mode:** Automated — no controller interaction required
**Input:** Session metadata from state.yaml, file changes from this session
**Output:** Session record closed, all changes committed and pushed to remote

---

## YOUR TASK

### Sequence

#### Phase 1: Close the Session Index

1. **Read the session index:**
   ```
   Read memory/sessions/index.json
   Parse as JSON array
   Get the last item (active session)
   ```

2. **Validate the active session:**
   - Confirm `closed: null` (session is open)
   - Confirm `id` matches current session ID from workflow state.yaml
   - If closed timestamp already exists, skip Phase 1 and proceed to Phase 2

3. **Update the active session record:**
   ```json
   {
     ...existing fields...,
     "closed": "<ISO 8601 timestamp — current time>",
     "current_topic": null
   }
   ```

4. **Check for unattributed files:**
   - Scan the topics array for any with `"flag": true`
   - If found, note in the workflow output: "Warning: unattributed files detected — [topic names]. Review before next session."
   - Do NOT rename them — surface to controller for manual review

5. **Write the updated session index:**
   - Verify JSON is valid
   - Write back to `memory/sessions/index.json`
   - Verify the write succeeded (file size > 100 bytes, valid JSON on re-read)

#### Phase 2: Git Commit (Following Git Skill Protocol)

**CRITICAL: Each command below is a separate, atomic call. Do not chain with `&&`, `||`, `;`, or pipes.**
**CRITICAL: Use Desktop Commander for ALL git operations — never sandbox bash.**

1. **Check for changed files** (separate call):
   ```bash
   git diff --name-only HEAD
   ```
   Capture the output. Review:
   - Identify temp artifacts to delete (`.html`, `.DS_Store`, `.fuse_hidden*`, root scripts)
   - Identify meaningful files to stage

2. **Delete temp artifacts** (if any exist — separate calls via Desktop Commander):
   - For each temp file from step 1:
     ```bash
     rm {path}
     ```
   Wait for each deletion to return before the next.

3. **Stage all changes** (separate call):
   ```bash
   git add -A
   ```
   Wait for completion.

4. **Review staged changes** (separate call):
   ```bash
   git diff --staged --name-only
   ```
   Verify the output includes only files you intend to commit. If credentials, secrets, or unwanted files appear:
   - STOP immediately
   - Do NOT commit
   - Surface to controller with specific file paths
   - Use `git reset HEAD {file}` (separate call) to unstage them

5. **Commit** (separate call):
   ```bash
   git commit -m "chore(chief): daily review — session closed, indices updated"
   ```
   Wait for completion. Output should show number of files changed, insertions, deletions.

6. **Push to remote** (separate call):
   ```bash
   git push origin main
   ```
   Wait for completion. If rejected (non-fast-forward):
   - Run `git pull --rebase origin main` (separate call)
   - Resolve any conflicts (surface to controller if conflicts exist)
   - Run `git push origin main` again (separate call)

#### Phase 3: Eval Record

Run the eval record close command:

```bash
python3 systems/eval-harness/close-eval-record.py \
  --name daily-review \
  --type workflow \
  --agent chief \
  --status {success|partial|failure} \
  --trigger manual \
  --started "{session_started from state.yaml}" \
  --steps "step-01-capture,step-02-set-tomorrow,step-03-update-system,step-04-root-audit,step-05-session-close"
```

Determine status:
- `success` — session closed, all files committed and pushed
- `partial` — session closed but push failed (committed locally)
- `failure` — could not close session or commit failed

---

## SUCCESS METRICS

- Session record in `memory/sessions/index.json` has `closed` timestamp and `current_topic: null`
- All new/modified files committed to git
- Git push to `origin main` succeeded
- Eval record written with status `success`

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Session index missing or malformed | Log error. Do not block workflow. Proceed to git commit. |
| Session already closed | Skip index update. Proceed to git commit. |
| Git diff returns untracked credentials | STOP. Do not commit. Surface paths to controller. Use `git reset HEAD {file}` to unstage. |
| Push rejected (non-fast-forward) | Pull with rebase, resolve conflicts (surface to controller if any exist), push again. |
| No changes to commit | Proceed. Still write eval record with `success`. |
| Unattributed files detected in session index | Surface warning to controller. Do NOT block workflow — they will be cleaned up in next session. |

---

## WORKFLOW COMPLETE

After the eval record is written and push succeeds, write `state.yaml` in the workflow directory:

```yaml
workflow: daily-review
agent: chief
status: complete
current-step: step-05
session-closed: true
```

This completes the daily review workflow. All changes are persisted, committed, and the session is formally closed.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

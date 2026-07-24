---
status: complete
started-at: 2026-07-24T13:03:50Z
completed-at: 2026-07-24T13:04:15Z
outputs:
  files_changed: 1
  files_committed:
    - workflows/content-pipeline/steps/step-02-approve.md
  commit_hash: 9d2375e
  push_status: success
  outcome: "SUCCESS: Content pipeline approval check state committed and pushed to origin main"
model: haiku
---

<!-- personal:start -->
# Step 03: Git Finalize — Commit Pipeline State

## MANDATORY EXECUTION RULES

1. You MUST commit all changes to `pending-drafts.json` and workflow state after every content-pipeline run.
2. You MUST follow the git skill protocol — atomic commands, no chaining, no `git status`.
3. You MUST use Desktop Commander for all git operations, never sandbox bash.
4. This step runs after both step-01 (discovery) and step-02 (approval) complete.

---

## EXECUTION PROTOCOL

**Agent:** Harper (via Rigby for git operations)
**Mode:** Automated — no controller interaction required
**Input:** pending-drafts.json changes, workflow state.yaml updates
**Output:** All pipeline state committed and pushed to remote

---

## YOUR TASK

### Sequence

#### Phase 1: Git Commit (Following Git Skill Protocol)

**CRITICAL: Each command below is a separate, atomic call. Do not chain with `&&`, `||`, `;`, or pipes.**
**CRITICAL: Use Desktop Commander for ALL git operations — never sandbox bash.**

1. **Check for changed files** (separate call):
   ```bash
   git diff --name-only HEAD
   ```
   Capture the output. Should include:
   - `workflows/content-pipeline/pending-drafts.json`
   - `workflows/content-pipeline/state.yaml`
   - Possibly: `systems/error-tracking/entries/*.json` (if errors occurred)

2. **Stage all changes** (separate call):
   ```bash
   git add workflows/content-pipeline/
   ```
   Wait for completion.

3. **Review staged changes** (separate call):
   ```bash
   git diff --staged --name-only
   ```
   Verify the output shows only workflow and pipeline files. If anything unexpected appears, stop here and surface to controller.

4. **Commit** (separate call):
   ```bash
   git commit -m "chore(harper): content-pipeline state update

Pending drafts and workflow state committed:
- {N} pending drafts tracked
- Ghost integrations synced
- Slack notifications logged"
   ```
   Wait for completion.

5. **Push to remote** (separate call):
   ```bash
   git push origin main
   ```
   If rejected (non-fast-forward):
   - Run `git pull --rebase origin main` (separate call)
   - Run `git push origin main` again (separate call)

---

## SUCCESS METRICS

- All workflow changes committed to git
- Push to `origin main` succeeded
- pending-drafts.json reflects current pipeline state

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Git diff returns unexpected files | Stop. Do not commit. Surface paths to controller. |
| Push rejected (non-fast-forward) | Pull with rebase and retry push. |
| No changes to commit | Proceed. Still consider run successful. |

---

## WORKFLOW CHECKPOINT

This step runs at the end of each content-pipeline agent run (discovery or approval). If this step completes successfully, the pipeline state is safely persisted.

No eval record is written by Harper — Rigby owns eval records. If this workflow is being observed by Rigby, the commit success is visible in git log.
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 05: Git Finalize — Commit Calendar State

## MANDATORY EXECUTION RULES

1. You MUST commit all changes to workflow state and any modified reference files after every content-calendar run.
2. You MUST follow the git skill protocol — atomic commands, no chaining, no `git status`.
3. You MUST use Desktop Commander for all git operations, never sandbox bash.
4. This step runs after step-04 completes.

---

## EXECUTION PROTOCOL

**Agent:** Harper (via Rigby for git operations)
**Mode:** Automated — no controller interaction required
**Input:** workflow state.yaml updates, reference/blog-ideas.md changes
**Output:** All calendar state committed and pushed to remote

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
   - `workflows/content-calendar/state.yaml`
   - Possibly: `reference/blog-ideas.md` (if new items added)
   - Possibly: `systems/error-tracking/entries/*.json` (if errors occurred)

2. **Stage all changes** (separate call):
   ```bash
   git add workflows/content-calendar/ reference/blog-ideas.md
   ```
   Wait for completion.

3. **Review staged changes** (separate call):
   ```bash
   git diff --staged --name-only
   ```
   Verify the output shows only workflow and reference files. If anything unexpected appears, stop here and surface to controller.

4. **Commit** (separate call):
   ```bash
   git commit -m "chore(harper): content-calendar state update

Calendar workflow state and recommendations committed:
- Calendar delivered with deadline flags
- {N} active content items
- {N} recommendations generated
- Task sync completed"
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
- Workflow state reflects current calendar status

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Git diff returns unexpected files | Stop. Do not commit. Surface paths to controller. |
| Push rejected (non-fast-forward) | Pull with rebase and retry push. |
| No changes to commit | Proceed. Still consider run successful. |

---

## WORKFLOW CHECKPOINT

This step runs at the end of each content-calendar workflow run. If this step completes successfully, the calendar state and recommendations are safely persisted.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- personal:start -->
# Step 02: Git Finalize — Commit Approval/Publish State

Carries forward the retired `workflows/content-pipeline/steps/step-03-git-finalize.md`'s logic.
Publishing and its git-related finalize step belong together: this workflow owns
`pending-drafts.json`'s lifecycle (cleanup, status transitions, publish records), so its
finalize step is the primary home for committing that file. See
`workflows/content-discovery/steps/step-02-git-finalize.md` for discovery's counterpart, which
also commits this same shared file when it appends new entries.

Before executing, write `status: in-progress` and `started-at` to this file's own frontmatter.

---

## YOUR TASK

**For ALL git operations, read `skills/git/SKILL.md` first.** This is the only authorized path
for commits, pushes, branch management, merges, and PR creation. No raw git commands outside
the skill.

1. **Diff check.** Identify changed files under:
   - `workflows/content-approval/` (pending-drafts.json, this workflow's own state.yaml, step frontmatter)
   - `reference/blog-ideas.md` (Published section move from step-01 Section 6a)

2. **Stage** the changed files above via the git skill.

3. **Commit** with a message following the pattern:
   ```
   chore(harper): content-approval cycle {ISO timestamp}
   ```
   Summarize in the body what happened this run (published/rejected/regenerated/edited counts,
   or "no new signals" if nothing changed).

4. **Push** per the git skill's standard flow.

5. Write `status: complete`, `completed-at`, and `outputs` (files_changed, files_committed,
   commit_hash, push_status, outcome) to this file's own frontmatter.

6. Update `state.yaml`: set `status: complete`, `current-step: null`, and record the same
   outputs in `accumulated-context`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Nothing to commit (clean no-op run) | This is a legitimate outcome. Log it, still write `status: complete` to state.yaml, skip the commit step. |
| Git push fails (network/auth) | Retry once per the git skill's retry guidance. If it still fails, log the failure in `outputs.push_status` and notify #jarvis: "content-approval git-finalize could not push — commit exists locally, needs manual push." |

## NEXT STEP

None — this is the last step in content-approval. The workflow is complete for this run.
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
model: haiku
---

<!-- personal:start -->
# Step 02: Git Finalize — Commit Resync/Edit State

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. All git operations run through `skills/git/SKILL.md` and the `ies-git` wrapper.

This workflow runs resync, cleanup, and editorial edits against `pending-drafts.json`, so this finalize step commits that file after an on-demand run. See
`workflows/content-discovery/steps/step-02-git-finalize.md` for discovery's counterpart — discovery is the tracker's scheduled custodian and also commits this same shared file after its daily run.

Before executing, write `status: in-progress` and `started-at` to this file's own frontmatter.

---

## YOUR TASK

**For ALL git operations, read `skills/git/SKILL.md` first.** This is the only authorized path
for commits, pushes, branch management, merges, and PR creation. No raw git commands outside
the skill.

1. **Diff check.** Identify changed files under:
   - `workflows/content-approval/` (pending-drafts.json, this workflow's own state.yaml, step frontmatter)

2. **Stage** the changed files above via the git skill.

3. **Commit** with a message following the pattern:
   ```
   chore(harper): content-approval cycle {ISO timestamp}
   ```
   Summarize in the body what happened this run (resynced/removed/edited counts,
   or "no changes" if nothing changed).

4. **Push** per the git skill's standard flow.

5. Write `status: complete` and `completed-at` to this file's frontmatter, and record outputs (files_changed, files_committed,
   commit_hash, push_status, outcome) in `state.yaml` `accumulated-context`.

6. Update `state.yaml`: set `status: complete`, `current-step: null`, and record the same
   outputs in `accumulated-context`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Nothing to commit (clean no-op run) | This is a legitimate outcome. Log it, still write `status: complete` to state.yaml, skip the commit step. |
| Git push fails (network/auth) | Retry once per the git skill's retry guidance. If it still fails, log the failure in `state.yaml` `accumulated-context.push_status` and notify #jarvis: "content-approval git-finalize could not push — commit exists locally, needs manual push." |

## NEXT STEP

None — this is the last step in content-approval. The workflow is complete for this run.
<!-- personal:end -->

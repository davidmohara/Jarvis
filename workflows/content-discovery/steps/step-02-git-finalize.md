---
status: in-progress
started-at: "2026-09-05T06:10:00Z"
completed-at: null
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 02: Git Finalize — Commit Discovery State

Adapted from the retired `workflows/content-pipeline/steps/step-03-git-finalize.md`, which
served both the discovery and approval halves of the old single workflow. Each split workflow
now runs its own copy of this step because both write to files that need committing
independently on their own schedule (discovery runs daily at 6am; approval runs 4x/day) — see
`workflows/content-approval/steps/step-02-git-finalize.md` for its counterpart.

Before executing, write `status: in-progress` and `started-at` to this file's own frontmatter.

---

## YOUR TASK

**For ALL git operations, read `skills/git/SKILL.md` first.** This is the only authorized path
for commits, pushes, branch management, merges, and PR creation. No raw git commands outside
the skill.

1. **Diff check.** Identify changed files under:
   - `workflows/content-discovery/` (this workflow's own state.yaml, step frontmatter)
   - `workflows/content-approval/pending-drafts.json` (the shared file — discovery appends
     entries to it in step-01)
   - `reference/blog-ideas.md` (Candidates table update from step-01 Step 10)
   - `content/improving-blog/*.md` (only if the IMPROVING BLOG PATH ran this cycle)

2. **Stage** the changed files above via the git skill.

3. **Commit** with a message following the pattern:
   ```
   chore(harper): content-discovery run {ISO timestamp}
   ```
   Summarize in the body what was drafted this run (new URLs/digests processed, posts created,
   or "no new content" if the run was a clean no-op).

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
| Git push fails (network/auth) | Retry once per the git skill's retry guidance. If it still fails, log the failure in `outputs.push_status` and notify #jarvis: "content-discovery git-finalize could not push — commit exists locally, needs manual push." |

## NEXT STEP

None — this is the last step in content-discovery. The workflow is complete for this run.
<!-- personal:end -->

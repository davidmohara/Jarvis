---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 03: Git Finalize — Commit Pipeline State

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. All git operations run through `skills/git/SKILL.md` and the `ies-git` wrapper.

Before executing, write `status: in-progress` and `started-at` to this file's own frontmatter.

---

## YOUR TASK

**For ALL git operations, read `skills/git/SKILL.md` first.** This is the only authorized path for commits, pushes, branch management, merges, and PR creation. No raw git commands outside the skill.

1. **Diff check.** Identify changed files under:
   - `workflows/content-pipeline/` (this workflow's state.yaml and step frontmatter)
   - `workflows/content-approval/pending-drafts.json` (the shared state file both pipeline steps wrote)
   - `workflows/content-discovery/` and `workflows/content-approval/` state files, if the delegated steps updated them this run

2. **Stage** the changed files above via the git skill.

3. **Commit** with a message following the pattern:
   ```
   chore(harper): content-pipeline run {ISO timestamp}
   ```
   Summarize in the body what this run did (drafted, published, rejected, or edited, or "no changes" if the run was a clean no-op).

4. **Push** per the git skill's standard flow.

5. Write `status: complete`, `completed-at`, and `outputs` (files_changed, files_committed, commit_hash, push_status, outcome) to this file's own frontmatter.

6. Update `state.yaml`: set `status: complete`, `current-step: step-04`, and record the same outputs in `accumulated-context`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Nothing to commit (clean no-op run) | This is a legitimate outcome. Log it, still write `status: complete` to state.yaml, skip the commit step, proceed to step-04. |
| Git push fails (network/auth) | Retry once per the git skill's retry guidance. If it still fails, log the failure in `outputs.push_status` and notify #jarvis: "content-pipeline git-finalize could not push; commit exists locally, needs manual push." |

## NEXT STEP

Read fully and follow: `step-04-adversarial-verify.md`
<!-- personal:end -->

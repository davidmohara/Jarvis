---
status: complete
started-at: "2026-09-17T03:49:10Z"
completed-at: "2026-09-17T03:50:30Z"
outputs:
  commit_sha: "0a8209f1"
  files_committed: 34
  files_committed_list:
    - "memory/working/omnifocus-data-2026-09-16-223600.md (new)"
    - "systems/eval-harness/runs/*.json (27 files — grading-sweep updates + 2 new 2026-09-17 records)"
    - "systems/eval-harness/skill-runs/git-latest.json"
    - "systems/eval-harness/skill-runs/rigby-eval-grade-latest.json"
    - "workflows/shutdown-cleanup/state.yaml"
    - "workflows/shutdown-cleanup/steps/step-01-purge-artifacts.md"
    - "workflows/shutdown-cleanup/steps/step-02-organize-deliverables.md"
    - "workflows/shutdown-cleanup/steps/step-03-gitignore-check.md"
  bookkeeping_commit_sha: "recorded in the follow-up state commit"
  temp_artifacts_staged: false
  pushed: false
model: sonnet
---

<!-- system:start -->
# Step 04: Commit Clean

## MANDATORY EXECUTION RULES

1. You MUST stage all modified and untracked files (except gitignored patterns).
2. You MUST write a commit message that summarizes the session's work, not just "cleanup."
3. You MUST verify that no temp artifacts are being staged before committing.
4. Do NOT push to remote unless the controller explicitly requested it.

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session. All git operations run through `skills/git/SKILL.md` and the `ies-git` wrapper.
**Mode:** Automated — no controller interaction needed
**Input:** Lock-free change lists, cleanup results from steps 01-03
**Output:** Clean commit, summary report to controller

---

## YOUR TASK

### Sequence

1. **List changes with lock-free commands only** (`git status` is forbidden — it writes `.git/index.lock`):
   - `git diff --name-only HEAD` — all changes vs HEAD
   - `git ls-files --modified --others --exclude-standard` — modified + untracked files

2. **Verify no temp artifacts** are in the staging area:
   - Cross-reference staged files against the purge patterns from step 01
   - If any temp files are staged, unstage them

3. **Stage all legitimate files** through the wrapper (transparent redirect or direct):
   ```bash
   python3 skills/git/scripts/ies-git add -A
   ```

4. **Write commit message:**
   - Conventional Commits format (`<type>(<scope>): lowercase imperative description`) — the wrapper lints this and refuses otherwise
   - Summarize the session's substantive work (not the cleanup)
   - If cleanup was the only action, describe what was cleaned and why

5. **Commit through the wrapper** (the wrapper also scans for credentials and audits the operation to `systems/eval-harness/git-ops.jsonl`):
   ```bash
   python3 skills/git/scripts/ies-git --ack-gated commit -m "<message>"
   ```

6. **Push, or hand off if rejected:** if the push is rejected because the remote has diverged, do NOT rebase from this session (the OneDrive-synced `.git` races multi-step git). Commit stays local; hand the pull-rebase and push to David's terminal.

6. **Report summary to controller:**
   ```
   Shutdown cleanup complete:
   - Purged: N temp artifacts
   - Organized: N deliverables verified (M renamed, K moved)
   - Gitignore: [updated with N patterns | no changes needed]
   - Committed: N files

   [any items flagged for review]
   ```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Nothing to commit | Report "Workspace clean — nothing to commit." |
| Commit fails (pre-commit hook) | Fix the issue, re-stage, create a new commit. Do not use --no-verify. |
| Large binary accidentally staged | Unstage it. Ask controller if it should be committed or gitignored. |

---

## WORKFLOW COMPLETE

Report the summary to the controller and confirm session close.
<!-- system:end -->


## WRITE WORKING MEMORY

Follow `reference/post-step-protocol.md` (Working Memory Write). Filename: `shutdown-cleanup-{YYYY-MM-DD}-{HHmmss}.md`; agent-source `chief`; compose the body from this step's output: key outputs, decisions, and any flags from the shutdown cleanup (3-5 bullets, under 200 words).

---
<!-- personal:start -->
<!-- personal:end -->

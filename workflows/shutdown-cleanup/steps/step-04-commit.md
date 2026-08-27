---
status: complete
started-at: "2026-08-27T20:12:00Z"
completed-at: "2026-08-27T20:20:00Z"
outputs:
  commit_sha: "536b6bf5"
  files_committed: 10
  temp_artifacts_staged: false
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

**Agent:** Master
**Mode:** Automated — no controller interaction needed
**Input:** Git status, cleanup results from steps 01-03
**Output:** Clean commit, summary report to controller

---

## YOUR TASK

### Sequence

1. **Run git status** to see all staged, unstaged, and untracked files

2. **Verify no temp artifacts** are in the staging area:
   - Cross-reference staged files against the purge patterns from step 01
   - If any temp files are staged, unstage them

3. **Stage all legitimate files:**
   - Modified files
   - New files created during the session
   - Deleted files (from purge step)
   - Renamed/moved files (from organize step)

4. **Write commit message:**
   - Summarize the session's substantive work (not the cleanup)
   - If cleanup was the only action, describe what was cleaned and why

5. **Commit**

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

After the workflow output has been delivered, write a working memory file to `memory/working/` using this filename pattern:

```
shutdown-cleanup-YYYY-MM-DD-HHmmss.md
```

where `YYYY-MM-DD-HHmmss` is the local date and time at the moment of writing. Use the session start time from `state.yaml` if available; otherwise use current time.

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "chief-{YYYY-MM-DD}-{HHmmss}"
agent-source: chief
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "Shutdown cleanup — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.

---
<!-- personal:start -->
<!-- personal:end -->

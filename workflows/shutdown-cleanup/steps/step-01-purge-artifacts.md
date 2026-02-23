<!-- system:start -->
# Step 01: Purge Temporary Artifacts

## MANDATORY EXECUTION RULES

1. You MUST scan the entire workspace for temp artifacts before deleting anything.
2. You MUST NOT delete files the controller created intentionally — only known temp patterns.
3. If uncertain whether a file is temp or intentional, leave it and note it in the summary.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Mode:** Automated — no controller interaction needed
**Input:** Workspace file listing
**Output:** List of deleted files

---

## YOUR TASK

### Sequence

1. **Scan for temp artifact patterns** across the workspace:

   | Pattern | What It Is |
   |---------|-----------|
   | `**/.DS_Store` | macOS folder metadata |
   | `**/.fuse_hidden*` | Stale FUSE mount artifacts |
   | `**/__pycache__/**` | Python bytecode cache |
   | `**/*.tmp` | Generic temp files |
   | `meetings/**/*.html` | Intermediate HTML from PDF generation |
   | Root-level `*.js`, `*.py`, `*.sh` | One-off scripts created during session |

2. **For each match:**
   - Verify it matches a known temp pattern (not a legitimate project file)
   - Delete the file
   - Record the deletion

3. **Store results** in working memory:
   ```
   purge_results:
     deleted:
       - path: ...
         reason: intermediate HTML | FUSE artifact | macOS metadata | temp script
     skipped:
       - path: ...
         reason: uncertain — flagged for review
     total_deleted: N
   ```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| File deletion fails (permissions) | Note the file and move on. Report in summary. |
| Uncertain file found | Do not delete. Add to skipped list with reason. |

---

## NEXT STEP

Read fully and follow: `step-02-organize-deliverables.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

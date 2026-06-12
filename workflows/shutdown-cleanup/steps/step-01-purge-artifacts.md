---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Purge Temporary Artifacts

## MANDATORY EXECUTION RULES

1. You MUST scan the entire workspace for temp artifacts before deleting anything.
2. You MUST NOT delete files the controller created intentionally — only known temp patterns.
3. If uncertain whether a file is temp or intentional, leave it and note it in the summary.
4. You MUST run the IES root-check (see below) — this is non-negotiable and runs every session.

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

4. **IES Root-Check — run this every session without exception:**

   List the top-level entries in the IES root directory and compare against the canonical allowlist below.

   **Canonical root entries (the complete list — nothing else belongs here):**

   | Entry | Type |
   |-------|------|
   | `CLAUDE.md` | file |
   | `SETUP.md` | file |
   | `SYSTEM.md` | file |
   | `evolution.manifest.json` | file |
   | `accounts/` | dir |
   | `agents/` | dir |
   | `archive/` | dir |
   | `briefs/` | dir |
   | `config/` | dir |
   | `contacts/` | dir |
   | `context/` | dir |
   | `contributions/` | dir |
   | `data/` | dir |
   | `decisions/` | dir |
   | `delegations/` | dir |
   | `evolutions/` | dir |
   | `hooks/` | dir |
   | `identity/` | dir |
   | `logs/` | dir |
   | `meetings/` | dir |
   | `memory/` | dir |
   | `people/` | dir |
   | `podcast/` | dir |
   | `presentations/` | dir |
   | `projects/` | dir |
   | `proposals/` | dir |
   | `reference/` | dir |
   | `reports/` | dir |
   | `reviews/` | dir |
   | `scripts/` | dir |
   | `skills/` | dir |
   | `specs/` | dir |
   | `systems/` | dir |
   | `tasks/` | dir |
   | `training/` | dir |
   | `workflows/` | dir |
   | `Remarkable/` | dir |
   | `YPO/` | dir |

   **For any entry NOT in this list:**
   - Flag it immediately with: `[ROOT ALERT] Non-canonical entry found: {name}`
   - Determine if it is a scratch workspace, leftover temp directory, or misplaced output
   - Move or delete it before proceeding — do not commit with it present
   - If genuinely uncertain, surface it to the controller for a disposition decision before committing

   **This check has failed silently twice** (Springline docx files June 2026, system-eval-workspace May–June 2026). A non-canonical root entry is always a mistake. There is no scenario where a new top-level directory is legitimately created and doesn't get moved within the same session.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| File deletion fails (permissions) | Note the file and move on. Report in summary. |
| Uncertain file found | Do not delete. Add to skipped list with reason. |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py shutdown-cleanup step-01-purge-artifacts complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-02-organize-deliverables.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

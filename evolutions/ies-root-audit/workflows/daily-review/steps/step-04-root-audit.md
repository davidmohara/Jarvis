---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Root Audit — Clean Up the Root Directory

## MANDATORY EXECUTION RULES

1. Never auto-delete anything. Present findings first, execute only after explicit confirmation.
2. Ignore known system files — see exclusion list below.
3. If nothing needs action, say so in one line and close the day.
4. This step does not block the daily review from being complete — the review is already written. This is housekeeping.

---

## EXECUTION PROTOCOL

**Agent:** Chief (via Rigby's Root Audit skill)
**Mode:** Interactive — present findings, wait for confirmation, then execute
**Input:** IES root directory file listing
**Output:** Root directory clean; any moved/deleted files noted

---

## EXCLUSION LIST

Do not flag these files — they belong at root:

- `CLAUDE.md`
- `SYSTEM.md`
- `README.md`
- `.gitignore`
- Any dotfile or dotfolder (`.git`, `.claude`, etc.)

---

## YOUR TASK

### 1. List root files

Glob for files at the IES project root (non-recursive). Exclude the items in the exclusion list.

### 2. Classify each file

| Classification | Criteria |
|---------------|----------|
| **Move** | File clearly belongs in a known folder (`meetings/`, `accounts/`, `people/`, `projects/`, `reports/`, `evolutions/`, `reviews/`, `delegations/`) — provide the recommended destination path |
| **Delete** | Clearly temporary: generated reports, working files, scratch outputs, files with names like `*_temp*`, `*_draft*`, `*_working*`, `research-report-*`, `*_sync_report*`. Also: any `.pdf` that has a matching `.md` with the same base name (meeting preps, call sheets, one-pagers) — PDF is regenerable, move the `.md` and delete the `.pdf`. |
| **Unknown** | Purpose unclear — present with file name, extension, last modified date, and a one-line best guess |

### 3. Present findings table

Group by action type. Example format:

```
## Root Audit

**Move (2)**
| File | Recommended Destination |
|------|------------------------|
| Kubota 2026 Account Plan.xlsx | accounts/kubota/ |
| 2026-03-20 Meeting Notes.md | meetings/ |

**Delete (1)**
| File | Reason |
|------|--------|
| research-report-davis-2026-03-20.md | Generated working file |

**Unknown (1)**
| File | Last Modified | Best Guess |
|------|--------------|------------|
| some-file.xlsx | 2026-03-15 | Possibly an account or reference doc |

Confirm to execute, or call out any changes.
```

If root is clean: "Root is clean. Nothing to move or delete."

### 4. Execute after confirmation

Once the controller confirms (in whole or with modifications):
- Create destination directories if needed
- Move files to confirmed destinations
- Delete files confirmed for deletion
- Report: "Done. X moved, Y deleted."

---

## SUCCESS METRICS

- All non-system root files reviewed
- Findings presented in grouped table
- No files moved or deleted without confirmation
- Root clean after execution

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Cannot read root directory | Skip audit. Note: "Root audit skipped — could not read directory." |
| File move fails | Note the failure inline. Do not halt — continue with remaining actions. |

---

## WORKFLOW COMPLETE

This is the final step of the daily-review workflow. No further steps to load.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

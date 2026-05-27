---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Apply Fixes

## MANDATORY EXECUTION RULES

1. You MUST read each target file before editing it — no blind writes.
2. You MUST apply fixes exactly as approved in Step 3 — no scope creep, no additional improvements.
3. You MUST update `fix_status` on every affected error entry immediately after applying its fix.
4. You MUST record every file modified in `accumulated-context.files_modified` in state.yaml.
5. You MUST NOT apply unapproved fixes — if you identify a new improvement while reading a file, log it as a new error entry and surface it in the next cycle.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** `approved_fixes` list from state.yaml
**Output:** Modified system files, updated entry fix_status, files_modified list in state.yaml

---

## YOUR TASK

### 1. Load the approved fix list

Read `accumulated-context.approved_fixes` from state.yaml. This is the authoritative list. Apply exactly these, nothing more.

### 2. For each fix: read, edit, verify inline

For each fix in the approved list:

**a. Read the target file** — confirm the insertion point exists as expected. If the file has changed since triage and the insertion point is missing or different, flag it before editing: "[Rigby]: Target file `[file]` looks different than expected. Confirm the insertion point before I edit."

**b. Apply the edit** — use the Edit tool with the exact change from the approved fix. If the fix adds a new rule block, place it at the correct section (Jarvis Operating Rules for SYSTEM.md rules, the relevant section in skill/workflow files).

**c. Update fix_status on all affected entries** — for every `entry_ids` listed under this fix, read the entry file and update `fix_status` from `"proposed"` to `"applied"`. Write the updated entry back.

**d. Record in state.yaml** — append to `files_modified`:
```yaml
    - file: "SYSTEM.md"
      fix_id: fix-001
      entry_ids_updated: ["err-20260401-007", "err-20260412-003"]
      edit_summary: "Added M365-only rule to Jarvis Operating Rules"
```

### 3. Taxonomy normalization (run once, after all other fixes)

After applying all approved content fixes, scan all entries with non-schema category values and normalize them. Valid categories per `systems/error-tracking/schema.md`:
`process-skip`, `routing-error`, `tool-misuse`, `data-accuracy`, `assumption-error`, `format-violation`, `missed-context`, `hallucination`, `over-engineering`, `under-delivery`

Common drift patterns:
- `wrong-assumption` → `assumption-error`
- `tool_misuse` (underscore) → `tool-misuse`
- `style-violation` → `format-violation`
- `misidentification` → `assumption-error`
- `process-failure` → `process-skip`
- `stale-context` → `assumption-error`

Also normalize `fixStatus` (camelCase) → `fix_status` (snake_case) on any entries using the old field name.

Record taxonomy normalization as a single entry in `files_modified`:
```yaml
    - file: "systems/error-tracking/entries/* (taxonomy)"
      fix_id: taxonomy-normalization
      entry_ids_updated: [list of normalized entry ids]
      edit_summary: "Normalized N entries with non-schema category names"
```

### 4. Handle Needs Your Call routing fixes (if approved)

If the controller approved routing table changes during Step 3:

Read `agents/routing.md` and `agents/master.md`. Apply the routing gate changes as approved — typically adding explicit routing rules that prevent Master from doing domain-specific agent work directly. These are structural edits to the routing logic, not just rule additions.

Flag these edits as higher-risk in `files_modified` with `risk: elevated` so Step 5 spends extra verification time on them.

---

## INSTRUMENTATION

After recording `files_modified` in state.yaml, append this step's timing:

```yaml
  step_timings:
    - step: step-04-apply
      started: <ISO-8601 UTC when this step began>
      completed: <ISO-8601 UTC now>
      files_modified_count: <N>
      entries_updated_count: <N>
```

---

## CONTEXT BOUNDARIES

- Apply fixes exactly as approved — nothing more
- If a fix reveals a related problem not in the approved list, log a new error entry and defer it to the next cycle
- Taxonomy normalization is always in scope (housekeeping, not a content change)

## SUCCESS METRICS

- All approved fixes applied to target files
- `fix_status` updated on all affected entries
- `files_modified` list complete in state.yaml
- No unapproved changes made

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Target file doesn't exist | Halt on that fix. Report to controller. Skip to next fix. |
| Insertion point not found | Surface the discrepancy to controller before editing. |
| Entry file can't be written | Report which entry failed. Continue with others. Note in state.yaml. |
| Fix produces a merge conflict (edit string not found) | Report exact file and line. Ask controller for guidance. Do not guess at alternate insertions. |

## NEXT STEP

[Step 05 — Verify](step-05-verify.md)
<!-- system:end -->

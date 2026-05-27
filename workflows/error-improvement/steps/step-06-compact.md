---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 06: Compact & Record

## MANDATORY EXECUTION RULES

1. You MUST only compact if Step 5 passed — no compaction after a failed verification.
2. You MUST log every file modified by this workflow to `evolutions/.pending-changes.json`.
3. You MUST write an episodic memory entry recording this improvement cycle.
4. Step 07 closes the workflow — do NOT set `status: complete` here.
5. Every pending-changes work item MUST include `"classification": "system"` — this workflow always produces system-level changes. Do not omit this field.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** Verified fix list from Step 5, compact eligibility from Step 5
**Output:** Compacted digests, pending-changes log updated, episodic memory entry written

---

## YOUR TASK

### 1. Run compaction on eligible months

For each month in `accumulated-context.compact_eligible_months`:

```bash
python3 systems/error-tracking/compact.py --execute --month YYYY-MM
```

Capture: entries archived, digest path written, any errors.

If no months are eligible: skip this section. This is normal when all active entries belong to the current month — note it and continue.

Update state.yaml:
```yaml
  months_compacted: ["2026-04"]
  entries_compacted: 48
```

### 2. Log to pending-changes

Read `evolutions/.pending-changes.json`. If the key is `pending` (list), append to that. If `work_items` (list), append to that. If missing entirely, create with `{"pending": []}`.

Append a work item for this error-improvement run:

```json
{
  "work_item_id": "error-improvement-YYYY-MM-DD",
  "created": "<ISO-8601 UTC>",
  "classification": "system",
  "description": "Error improvement cycle — [N] fixes applied, [N] entries compacted",
  "files": [
    {
      "path": "<file>",
      "action": "merge",
      "summary": "<one-line description of change>"
    }
  ]
}
```

Include every file in `accumulated-context.files_modified` plus any new digest files created in this step.

Write the updated pending-changes.json back.

### 3. Write episodic memory entry

Write to `memory/episodic/decisions/` — decision-rationale type.

Filename: `YYYY-MM-DD-HHmmss-decision-rationale-error-improvement-[period].md`

```yaml
---
type: decision-rationale
subject: "Error improvement cycle — [period covered]"
date: YYYY-MM-DD
tags: [system-improvement, error-tracking, rigby]
related-entities:
  projects: [ies-system]
  accounts: []
  people: []
  meetings: []
agent-source: rigby
salience:
  score: 0
  references: []
  last-promoted-check: YYYY-MM-DD
  promoted: false
---
```

Body — prose, not bullets:

```
## Error Improvement Cycle — [Period]

Rigby ran the full error-improvement workflow on [date]. The active log contained [N]
entries spanning [date range], with [N] patterns identified across [N] categories.

[Fixes applied — one sentence each, stating what changed and why.]

[Controller decisions on Needs Your Call items, if any.]

[What was deprioritized and why, if anything.]

[N] entries from [month list] were archived to monthly digests. [N] entries remain
active ([reasoning — current month, open routing-gate issues, etc.]).

Trend: [Improving / Stable / Degrading]. [One sentence on what the data shows.]
```

---

## INSTRUMENTATION

After writing the episodic memory entry, append this step's timing:

```yaml
  step_timings:
    - step: step-06-compact
      started: <ISO-8601 UTC when this step began>
      completed: <ISO-8601 UTC now>
      months_compacted: <list>
      entries_compacted: <N>
```

---

## SUCCESS METRICS

- Compaction completed (or "no months eligible" clearly noted)
- Pending-changes log updated with all files touched by this workflow
- Episodic memory entry written
- state.yaml updated with `months_compacted` and `entries_compacted`

## FAILURE MODES

| Failure | Action |
|---------|--------|
| compact.py --execute fails | Diagnose. Report. Do NOT force-delete entry files manually. |
| pending-changes.json malformed or unexpected structure | Read the file first, identify the actual list key, append correctly. If truly corrupt, reset to `{"pending": []}` and log the reset. |
| Episodic memory write fails | Note it. Proceed to Step 07 — the cycle is still complete. |

## NEXT STEP

[Step 07 — Summary](step-07-summary.md)
<!-- system:end -->

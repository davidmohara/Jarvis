---
name: rigby-capability-status
description: Show pending unpackaged capability changes — what has been built but not yet packaged as an evolution
context: fork
agent: general-purpose
model: sonnet
---

<!-- system:start -->
# Rigby — Capability Status

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Show the executive what capability changes have been built locally but not yet packaged as an evolution. This is the window into the pending changes log — what's ready to be shipped and what it would look like.

## Input

`$ARGUMENTS` — accepts:
- (no args) — show all pending work items
- `--work-id {id}` — show a specific work item
- `--clear {id}` — remove a work item from pending (use after manually packaging or abandoning)

## Process

### 1. Read Pending Changes

Read `evolutions/.pending-changes.json`.

If the file does not exist or `pending` array is empty:
```
No pending capability changes. Your evolution is clean.
```
Exit.

### 2. Display Pending Items

For each item in `pending`:

```
Work Item: {id}
{description}
Started: {started}

Files:
  + {path} — {description}   (action: add)
  ~ {path} — {description}   (action: merge)
  ● {path} — {description}   (action: replace)
  - {path} — {description}   (action: delete)

─────────────────────────────────────────────
```

Legend: `+` add, `~` merge (personal content preserved), `●` replace, `-` delete

### 3. Summary Footer

```
Total pending: {count} work item(s), {file_count} file(s)

To package: rigby package --pending
To include specific items: rigby package --pending --work-id {id} --work-id {id}
To clear an item: rigby status --clear {id}
```

### 4. Clear Mode

If `--clear {id}` is provided:
- Remove the matching work item from the `pending` array
- Write the updated `evolutions/.pending-changes.json`
- Confirm: `Cleared work item {id} from pending changes.`

Only clear a work item if the executive explicitly requests it or if the files have already been packaged via `rigby package --pending`.

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/rigby-capability-status-latest.json
```

Content:
```json
{
  "skill": "rigby-capability-status",
  "agent": "rigby",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill rigby-capability-status
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/rigby-capability-status.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Pending Log**: Read/Write `evolutions/.pending-changes.json`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

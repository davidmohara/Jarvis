---
name: rigby-error-compact
owning_agent: rigby
description: Compact the error tracking log by archiving resolved entries (fix_status=applied or deferred) into a structured digest file, then deleting the individual JSON files. Preserves the full signal — timeframes, categories, failure modes, severity distribution, pattern context — in a form useful for future analysis. Does NOT compact proposed or in-progress entries. Triggered by Rigby after a triage pass, during weekly review, or when entry count exceeds 100.
evolution: system
model: sonnet
trigger_keywords: [compact error log, archive errors, clean up error entries, error log maintenance]
trigger_agents: [rigby, quinn]
---

<!-- system:start -->
## Trigger Conditions

Run this skill when any of the following are true:
- Entry count in `systems/error-tracking/entries/` exceeds 100
- A triage pass has just completed (all Apply Now entries are `fix_status: applied`)
- Quinn calls this during weekly review after Rigby's analysis step
- David asks to compact, clean up, or archive the error log

**Never run during an active triage or analysis pass.** Compact only after fixes are applied and the analysis session is closed.

---

## What Compaction Preserves

Compaction is NOT deletion. Every resolved entry is summarized into a digest that retains:
- The time period covered
- Entry count by category and failure mode
- Severity distribution
- Agent attribution (who generated the most errors)
- Per-entry record of: id, date, category, failure_mode, severity, agent, description (1 sentence), correction (1 sentence), systemic_fix
- Pattern summaries (if patterns were identified in a prior analysis run)
- Source ratio (explicit vs self-detected)

What compaction discards: verbose field duplication, raw session IDs, redundant related_entries chains (collapsed into pattern refs instead).

The digest is the authoritative historical record after compaction. It must be complete enough that a future Rigby analysis can understand what happened in that period without re-reading individual files.

---

## Execution

### Step 1: Safety check

Run `python3 systems/error-tracking/rebuild-log.py --out /tmp/error-log-pre-compact.json`

Verify:
- No entries have `fix_status: proposed` or `fix_status: in-progress` — these are NOT eligible for compaction. If any exist, halt and report: "Cannot compact — [N] entries still have open fix status: [list ids]. Resolve or defer them first."
- Confirm total entry count. Report: "Compacting [N] entries."

If the entry count is below 50 and no explicit compaction was requested, report the count and ask if David wants to proceed anyway.

### Step 2: Determine compaction window

Compaction operates in **calendar month cohorts** — all entries from the same month are grouped together. Never split a month across digests.

Identify which months are fully resolved (all entries in that month have `fix_status: applied` or `fix_status: deferred`). The current month is never compacted — only months where the calendar month has closed.

Example: If today is 2026-05-27, eligible months are March 2026, April 2026, and earlier. May 2026 entries are NOT compacted yet (month not closed).

If no fully-closed months have resolvable entries, report: "No closed months with fully resolved entries — nothing to compact yet."

### Step 3: Build the digest

For each eligible month, produce a digest object:

```json
{
  "period": "2026-03",
  "period_label": "March 2026",
  "compacted_at": "<ISO-8601 UTC>",
  "entry_count": 39,
  "source_breakdown": {
    "explicit": 7,
    "self_detected": 32
  },
  "severity_breakdown": {
    "major": 4,
    "moderate": 18,
    "minor": 17
  },
  "category_breakdown": {
    "process-skip": 12,
    "routing-error": 10,
    "tool-misuse": 8,
    "data-accuracy": 5,
    "assumption-error": 4
  },
  "failure_mode_breakdown": {
    "protocol-skip": 18,
    "wrong-assumption": 9,
    "lazy-search": 6
  },
  "agent_breakdown": {
    "jarvis": 28,
    "master": 6,
    "chief": 5
  },
  "fix_status_breakdown": {
    "applied": 35,
    "deferred": 4
  },
  "patterns_identified": [
    {
      "category": "process-skip",
      "failure_mode": "protocol-skip",
      "occurrences": 12,
      "description": "Boot sequence Phase 2 steps skipped without reporting",
      "fix_applied": "Boot sentinel file + checklist enforcement (SYSTEM.md rule)"
    }
  ],
  "entries": [
    {
      "id": "err-20260321-001",
      "date": "2026-03-21",
      "category": "routing-error",
      "failure_mode": "protocol-skip",
      "severity": "moderate",
      "agent": "jarvis",
      "source": "explicit",
      "description": "Card optimization question handled directly instead of routing to Chase.",
      "correction": "All card selection questions routed through Chase Card Optimizer.",
      "systemic_fix": "Rule added to agents/master.md routing table.",
      "fix_status": "applied"
    }
  ]
}
```

**Entry truncation rule:** `description`, `correction`, and `systemic_fix` are trimmed to 1 sentence each in the digest. If the original is already 1 sentence, copy verbatim. If longer, take the first sentence only. Do not paraphrase — truncate.

### Step 4: Write the digest file

Write to `systems/error-tracking/digests/compact-YYYY-MM.json` for each month compacted.

If `digests/` directory doesn't exist, create it.

If a digest already exists for that month (re-compaction after adding entries), read it first, merge the new entries in chronologically, update all aggregates, and overwrite.

### Step 5: Verify digest integrity

Before deleting any source files, verify the digest is complete:

```python
# Pseudo-code — implement as a verification pass
source_ids = {e["id"] for e in entries_being_compacted}
digest_ids = {e["id"] for e in digest["entries"]}
assert source_ids == digest_ids, f"Missing IDs in digest: {source_ids - digest_ids}"
```

If the ID sets don't match, halt. Do NOT delete source files until verification passes.

### Step 6: Delete source entry files

After digest verification passes, delete the source JSON files for each compacted entry:

```bash
# Run via Bash or osascript
for each entry_id in compacted_entries:
    rm systems/error-tracking/entries/{entry_id}.json
```

Report the count deleted.

### Step 7: Update _meta.json

Read `systems/error-tracking/_meta.json`. Add or update:

```json
{
  "last_compacted": "<ISO-8601 UTC>",
  "compaction_history": [
    {
      "compacted_at": "<ISO-8601 UTC>",
      "period": "2026-03",
      "entries_compacted": 39,
      "digest_path": "systems/error-tracking/digests/compact-2026-03.json"
    }
  ]
}
```

If `compaction_history` already exists, append — don't replace.

### Step 8: Rebuild the active log

Run `python3 systems/error-tracking/rebuild-log.py --out /tmp/error-log-view.json`

Confirm the remaining entry count. Report the delta.

### Step 9: Report

```
## Error Log Compaction Complete

**Periods compacted:** [list of months]
**Entries archived:** [N] across [M] digest files
**Entries remaining (active):** [N] — [month range]

### Digest Summary

[For each month compacted:]
**[Month Year]** — [N] entries → `systems/error-tracking/digests/compact-YYYY-MM.json`
- Top category: [category] ([N])
- Top failure mode: [failure_mode] ([N])
- Severity: [major: N] [moderate: N] [minor: N]
- Agent generating most errors: [agent] ([N])
- Patterns captured: [N]

### Active Log State

[N] entries remain in `systems/error-tracking/entries/`:
- Oldest: [date] — [id]
- Most recent: [date] — [id]
- Open (proposed/in-progress): [N]
```

---

## Reading Digests in Future Analysis

When `rigby-error-analysis` runs and needs historical context:
1. Check `systems/error-tracking/digests/` for compact files covering prior periods
2. Load the relevant digest(s) alongside the active entries
3. Use `category_breakdown`, `failure_mode_breakdown`, and `patterns_identified` from the digest for trend analysis across periods
4. Reference individual digest entries by `id` if needed — they are stable identifiers

The digest format is intentionally compatible with the existing entry schema so `rebuild-log.py` could be extended to merge digest entries into the view if full historical detail is ever needed.

---

## Error Handling

| Failure | Action |
|---------|--------|
| Open fix_status entries found | Halt. List the open entries. Do not compact until resolved. |
| Digest write fails | Halt. Do not delete source files. Report error. |
| Digest verification fails (ID mismatch) | Halt. Do not delete source files. Surface the missing IDs. |
| `digests/` directory creation fails | Report and halt — likely a permissions issue. |
| Source file deletion fails for individual file | Continue with remaining deletions. Report which files could not be deleted. |

---

## SKILL COMPLETE

After the report is delivered, write the skill-run signal file:

```
systems/eval-harness/skill-runs/rigby-error-compact-latest.json
```

Content:
```json
{
  "skill": "rigby-error-compact",
  "agent": "rigby",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"scheduled"` if called from the weekly review, `"manual"` otherwise. Set `status` to `"partial"` if some months compacted but others failed, `"failure"` if nothing could be compacted. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill rigby-error-compact
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/rigby-error-compact.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
id: vault-freshness-check
name: Vault Freshness Check
owning_agent: rigby
model: haiku
context: inline
fairness: {applicable: false, reason: "Utility skill — reads a cache file for staleness, no differential treatment of people, no eligibility or scoring decisions."}
trigger_keywords:
  - cache check
  - freshness check
  - stale cache
  - skip the pull
---

<!-- system:start -->
# Vault Freshness Check

A generic "is this cached data fresh enough to skip a live pull" check against an Obsidian vault file. Any skill that pulls live data on a cadence (weekly, monthly) calls this **first**, before touching a slow/fragile live source (PowerBI, an API, a browser automation), so a fresh cache short-circuits the expensive pull.

This is not tied to PowerBI or any specific report. It works against any Obsidian vault file that accumulates dated entries over time.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Inputs

The calling skill must supply all of these explicitly — nothing here is hardcoded:

| Input | Type | Required | Description |
|-------|------|----------|--------------|
| `vault_file` | string | yes | Vault-relative path to the cache file, e.g. `Mind/One Texas/Rock 4 - Pipeline Snapshots.md` |
| `entry_heading_pattern` | string | yes | Regex/description of the heading that marks one dated entry, e.g. `^## Week of (\d{4}-\d{2}-\d{2}) — Pipeline Snapshot` or `^## (\d{4}-\d{2}-\d{2})` |
| `date_field_pattern` | string | no | If the entry date isn't captured in the heading itself, a pattern for a line inside the entry that carries it, e.g. `\*Pulled: (\d{4}-\d{2}-\d{2})` |
| `freshness_threshold_days` | integer | yes | Cache is fresh if the most recent matching entry's date is >= today minus this many days |
| `extra_staleness_rule` | string | no | Free-text additional condition that can force staleness even inside the threshold window (e.g. "if today is past the 10th of a new calendar month, and the most recent entry's month is not the most recently closed month, treat as stale regardless of age") |
| `extract_section_heading` | string | no | If the caller only wants one subsection out of the matched entry (e.g. `### Pipeline Health (Rock 1)`), the heading text of that subsection |
| `caller_label` | string | yes | Short label used in the status message reported back, e.g. `Chase/Pipeline` or `Chase/Revenue` |
| `obsidian_read_tool` | string | no | Which MCP tool to use to read the file. Default: `mcp__obsidian-local__get_vault_file`. Pass an override if the caller's environment binds Obsidian differently (e.g. `mcp__obsidian-mcp-tools__get_vault_file`). |

## Process

1. **Read the file.** Call `obsidian_read_tool` (default `mcp__obsidian-local__get_vault_file`) with `vault_file`. If the file doesn't exist or is empty, return `cache_status: "not_found"` immediately — the caller proceeds to a live pull.

2. **Find the most recent matching entry.** Scan the file for headings matching `entry_heading_pattern`. Entries are typically appended in chronological order, so the last match in the file is the most recent — but don't assume; parse each match's date and take the maximum.

3. **Resolve the entry date.** If `entry_heading_pattern` itself captures a date (a capture group in the regex), use it. Otherwise, search within that entry's text for `date_field_pattern` and use its capture group.

4. **Apply the threshold.** Compute `today - freshness_threshold_days`. If the entry date is on or after that cutoff, the cache is provisionally fresh.

5. **Apply `extra_staleness_rule` if given.** This is free text, not code — reason about it against the entry's content and today's date. If it indicates the entry should be treated as stale despite passing step 4, override to stale. Document which rule fired in the returned `notes` field.

6. **Extract the payload.** If `extract_section_heading` was given, pull just that subsection's text from the matched entry. Otherwise return the entry's full text.

7. **Return a result** to the caller:
   ```json
   {
     "cache_status": "hit | stale | not_found",
     "entry_date": "YYYY-MM-DD or null",
     "extracted_text": "the section/entry text, or null if stale/not_found",
     "notes": "which staleness rule fired, if any"
   }
   ```

## Caller Contract

On `cache_status: "hit"`:
- The caller outputs `extracted_text` in its own standard output format, noting the snapshot date.
- The caller reports: `[{caller_label}]: Using cached data from {entry_date} (within {freshness_threshold_days}-day window). Skipping live pull.`
- The caller stops — it does not proceed to its live-pull phase.

On `cache_status: "stale"` or `"not_found"`:
- The caller proceeds to its own live-pull phase (e.g. calling `powerbi-navigate-slicer` / `powerbi-extract-kpis`, or any other live source), then writes a fresh entry back to `vault_file` itself using the append tool of its choosing (this skill only reads — it never writes).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## SKILL COMPLETE

This is a pure read/decision helper invoked inline by a caller skill's own execution — it does not write its own eval-harness signal file. The caller skill's signal file (written via `eval-signal-write`) is what records the run; a cache-hit short-circuit is still a `"success"` for the caller.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/vault-freshness-check-latest.json
```

Content:
```json
{
  "skill": "vault-freshness-check",
  "agent": "vault",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill vault-freshness-check
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/vault-freshness-check.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

---
name: omnifocus-data
owning_agent: master
description: >
  Extract OmniFocus data: the canonical pull into `data/omnifocus-unified.json`
  plus shared read primitives (inbox, due/overdue, flagged, tags, active
  projects, counts). Use this skill whenever OmniFocus data is needed as input
  to something else, or when the user asks "what's on my plate", "check my
  tasks", "what's in my OmniFocus", "pull OmniFocus", or asks for inbox /
  flagged / due counts. Also the mandated path for boot step-01.2 Pull B and
  for any workflow that needs OmniFocus counts. For CREATING tasks, use
  `skills/omnifocus-tasks/SKILL.md` instead: that is a separate, gated skill.
model: sonnet
trigger_keywords: [omnifocus, tasks, inbox, flagged, due, counts]
trigger_agents: [master, chief, quinn, shep]
---

<!-- system:start -->
# OmniFocus Data

Canonical producer of `data/omnifocus-unified.json` and the single owner of
OmniFocus read logic. Every consumer reads the file this skill writes; no
consumer should hold its own OmniFocus query.

## Why this skill exists

OmniFocus is read by roughly thirty skills, six agents, and eight workflows.
Before this skill, its extraction logic was re-derived from scratch by an agent
on every boot, and four other files each carried their own copy of the query
logic. That drift produced real failures on 2026-09-16: a query that returned
247 completed tasks, and invented filter keys that shipped before being caught.

The fix is that the invariants below live in code, not in prose that each
consumer re-reads and re-interprets.

## Two paths, and which to use

| Need | Path |
|------|------|
| Ad-hoc interactive read by an agent | **OmniFocus MCP** (`query_omnifocus`, `list_tags`) when its tools are present |
| The canonical pull, counts, and anything unattended | **This skill's script** |

The script uses AppleScript, deliberately. The MCP depends on session state:
the server must be built, running, and connected before the session starts.
osascript has no such dependency. Boot runs unattended, so the canonical pull
must not depend on MCP availability. If you have the MCP, prefer it for
one-off lookups; always use the script for the pull.

## The script

```
skills/omnifocus-data/scripts/omnifocus_data.py
```

| Command | Purpose |
|---------|---------|
| `pull [--out PATH]` | Write the canonical data file. Never raises: on failure it writes `status: failed` and exits 1 |
| `counts [--json]` | `inbox_uncompleted`, `flagged_uncompleted`, `total_uncompleted`, `due_within_7` |
| `tags [--json]` | All tag names |
| `projects [--json]` | Active project names |
| `list --kind inbox\|due\|flagged [--json]` | Tasks of one kind |

Run it with `python3`. `--days N` shifts the due window (default 7).

## The pull

```bash
python3 skills/omnifocus-data/scripts/omnifocus_data.py pull
```

Writes `data/omnifocus-unified.json`. Report the outcome honestly: read the file
back and state `status` and `task_count`. A `status: failed` pull must be
surfaced as a degraded source, never passed over as an empty one.

## Invariants (do not violate)

1. **Every query carries the completed filter.** The inbox permanently holds
   roughly 247 completed tasks alongside ~8 incomplete ones, and OmniFocus
   "Clean Up" does NOT remove them. The filter lives in the query, not in a
   cleanup step. The script enforces this; if you hand-write a query, you must
   enforce it yourself.
2. **A failed pull is distinguishable from an empty one.** Always write and read
   `status`. Never let a failure look like a quiet day.
3. **One writer.** Only this skill writes `data/omnifocus-unified.json`. If you
   find another writer, that is a bug: consolidate it here.

## Failure handling

| Failure | Action |
|---------|--------|
| Script exits 1 | Read `error` from the output file and report it as a degraded source |
| `osascript` missing or unrunnable | The pull already writes `status: failed`; do not retry blindly. Report it |
| MCP tools absent | Expected in unattended runs. Use this script; do not report OmniFocus unreachable on that basis |
| Tags or projects empty | Treat as a real empty result, not an error |

## Task creation

Not here. Creating tasks is gated on project and tag assignment and lives in
`skills/omnifocus-tasks/SKILL.md`. Use this skill's `tags` and `projects`
commands to satisfy that gate's Step 1 if the MCP is unavailable.

---

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so
the eval harness captures this execution:

```
systems/eval-harness/skill-runs/omnifocus-data-latest.json
```

Content:

```json
{
  "skill": "omnifocus-data",
  "agent": "master",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if from
a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill
completed with degraded output, `"failure"` if it could not run at all. This
write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic
grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill omnifocus-data
```

This prints a compact block: a structure/content/quality assertion breakdown, a
deterministic % score, and a pass/fail gate status, computed from
`systems/eval-harness/assertions/omnifocus-data.json`. It always exits 0, even
when checks fail.

Include that printed block in your final response to the operator. A
qualitative (Tier 3) grade is added separately later via the end-of-day
`rigby-eval-grade` sweep; do not attempt to compute or claim one yourself.
<!-- system:end -->
